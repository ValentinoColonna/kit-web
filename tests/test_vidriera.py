"""Vidriera (P2) en un Chrome headless real: filtros, «sumar a la consulta», movimiento reducido y horario.
Usa el esqueleto verdadero con datos ficticios y un reloj simulado. Se salta (y lo dice) si no hay Chrome."""
import datetime
import json
import os
import re
import subprocess
import tempfile
import unittest

from util import PLANTILLA, buscar_chrome, leer

CHROME = buscar_chrome()
TZ_NEGOCIO = "America/Argentina/Buenos_Aires"
FILAS = ('<div data-dias="1" data-abre="20:00" data-cierra="02:00"><span>Lunes</span><b>20 a 02</b></div>'
         '<div data-dias="2,3" data-abre="9:00,16:00" data-cierra="13:00,20:00"><span>Martes y miércoles</span><b>9 a 13 y 16 a 20</b></div>')
PRODUCTOS = "".join(
    '<article class="prod" data-cat="%s"><div class="texto"><h3>%s</h3><div class="pie2"><div class="acc">'
    '<button class="sumar" type="button" data-nombre="%s" aria-pressed="false">+</button></div></div></div></article>' % (c, n, n)
    for c, n in (("Plantas", "Rosa"), ("Plantas", "Helecho"), ("Macetas", "Maceta azul")))
FILTROS = ('<button class="chip activo" type="button" data-filtro="*">Todo</button>'
           '<button class="chip" type="button" data-filtro="Plantas">Plantas</button><button class="chip" type="button" data-filtro="Macetas">Macetas</button>')


def epoch_ms(y, mo, d, h, mi, tz_offset_h):
    """Instante para una hora de pared con offset fijo (Buenos Aires = -3, sin horario de verano)."""
    dt = datetime.datetime(y, mo, d, h, mi, tzinfo=datetime.timezone(datetime.timedelta(hours=tz_offset_h)))
    return int(dt.timestamp() * 1000)


def armar(cfg, escenario):
    h = leer(os.path.join(PLANTILLA, "esqueleto-vidriera.html"))
    h = re.sub(r"<script[^>]+src=[^>]+></script>", "", h)          # sin CDN
    h = re.sub(r"<link[^>]+href=\"https?:[^>]*>", "", h)           # sin Google Fonts
    pre = """<script>(function(){var C=%s,T=window.__T={now:C.now,iv:[]},RD=Date;
window.Date=function(){var a=[].slice.call(arguments);return a.length?new (Function.prototype.bind.apply(RD,[null].concat(a)))():new RD(T.now)};
Date.prototype=RD.prototype;Date.now=function(){return T.now};Date.UTC=RD.UTC;Date.parse=RD.parse;
window.setInterval=function(f,ms){T.iv.push([f,ms]);return T.iv.length};
var mm=window.matchMedia.bind(window);window.matchMedia=function(q){return /prefers-reduced-motion/.test(q)?{matches:!!C.reduce,media:q,addEventListener:function(){},removeEventListener:function(){},addListener:function(){},removeListener:function(){}}:mm(q)};
if(C.stubGsap){window.gsap={registerPlugin:function(){},ticker:{lagSmoothing:function(){}}};window.ScrollTrigger={};}
})();</script>""" % json.dumps(cfg)
    h = re.sub(r"(<head[^>]*>)", lambda m: m.group(1) + pre, h, count=1)
    h = re.sub(r'<div class="horas rv"[^>]*>\{\{HORARIOS.*?\}\}</div>',
               lambda m: '<div class="horas rv" data-tz="%s">%s</div>' % (cfg.get("tz", ""), FILAS), h, flags=re.S)
    h = re.sub(r"\{\{FILTROS.*?\}\}", "", h, flags=re.S)
    h = h.replace('<button class="chip activo" type="button" data-filtro="*">Todo</button>', FILTROS, 1)
    h = re.sub(r'<article class="prod rv".*?</article>', lambda m: PRODUCTOS, h, count=1, flags=re.S)
    h = h.replace("</body>", "<script>try{%s}catch(e){document.body.setAttribute('data-err',String(e))}</script></body>" % escenario)
    return h


def ejecutar(cfg, escenario):
    ruta = os.path.join(tempfile.mkdtemp(prefix="kitweb-js-"), "v.html")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(armar(cfg, escenario))
    env = dict(os.environ, TZ="UTC")  # el visitante está en UTC, el negocio en Buenos Aires
    r = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-first-run", "--virtual-time-budget=3000", "--dump-dom", "file://" + ruta],
                       capture_output=True, text=True, timeout=90, env=env)
    m = re.search(r"data-res='([^']*)'", r.stdout) or re.search(r'data-res="([^"]*)"', r.stdout)
    err = re.search(r'data-err="([^"]*)"', r.stdout)
    if not m:
        raise AssertionError("el escenario no devolvió resultado (error: %s)\n%s" % (err.group(1) if err else "ninguno", r.stderr[-400:]))
    return json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&"))


ESTADO = "function est(){var c=document.querySelector('.cartel');return {estado:c.querySelector('b').textContent,detalle:c.querySelector('small').textContent,hoy:[].map.call(document.querySelectorAll('.horas .hoy span'),function(s){return s.textContent})}}"
FIN = "document.body.setAttribute('data-res',JSON.stringify(R));"

ESC_HORARIO = ESTADO + "var R={a:est()};" + FIN
ESC_REINICIO = (ESTADO + "var T=window.__T,R={a:est()};T.now+=%d;var ok=T.iv.filter(function(x){return x[1]<=60000});R.hay_intervalo=ok.length>0;ok.forEach(function(x){x[0]()});R.b=est();" + FIN)

ESC_CATALOGO = """
var R={},q=function(s){return document.querySelector(s)},qa=function(s){return [].slice.call(document.querySelectorAll(s))};
function vis(){return qa('.prod').map(function(p){return getComputedStyle(p).display!=='none'?p.dataset.cat:null}).filter(Boolean)}
R.sumar_visible=getComputedStyle(q('.sumar')).display!=='none';
qa('.chip')[1].click();R.filtro_plantas=vis();
qa('.chip')[2].click();R.filtro_macetas=vis();
qa('.chip')[0].click();R.filtro_todo=vis();
var b=qa('.sumar')[0];b.click();var barra=q('.consulta-barra');
R.barra_visible=!barra.hidden;R.cuenta=q('.cuenta').textContent;R.pressed=b.getAttribute('aria-pressed');R.href=decodeURIComponent(barra.querySelector('a').href);
q('.vaciar').click();R.barra_oculta_al_vaciar=barra.hidden;R.cuenta_final=q('.cuenta').textContent;
""" + FIN
NOW = epoch_ms(2026, 10, 20, 12, 0, -3)  # martes 20/10/2026 12:00 en Buenos Aires


@unittest.skipUnless(CHROME, "No hay Chrome: definí CHROME_BIN para correr las pruebas de JavaScript de Vidriera")
class Catalogo(unittest.TestCase):
    def comprobar(self, r):
        self.assertTrue(r["sumar_visible"], "el botón + de sumar no se ve")
        self.assertEqual(r["filtro_plantas"], ["Plantas", "Plantas"])
        self.assertEqual(r["filtro_macetas"], ["Macetas"])
        self.assertEqual(r["filtro_todo"], ["Plantas", "Plantas", "Macetas"])
        self.assertTrue(r["barra_visible"])
        self.assertEqual(r["cuenta"], "1")
        self.assertEqual(r["pressed"], "true")
        self.assertIn("- Rosa", r["href"])
        self.assertTrue(r["barra_oculta_al_vaciar"])
        self.assertEqual(r["cuenta_final"], "0")

    def test_sin_gsap(self):
        self.comprobar(ejecutar({"now": NOW, "tz": TZ_NEGOCIO}, ESC_CATALOGO))

    def test_con_movimiento_reducido_y_gsap_presente(self):
        self.comprobar(ejecutar({"now": NOW, "tz": TZ_NEGOCIO, "reduce": True, "stubGsap": True}, ESC_CATALOGO))

    def test_con_movimiento_reducido_sin_gsap(self):
        self.comprobar(ejecutar({"now": NOW, "tz": TZ_NEGOCIO, "reduce": True}, ESC_CATALOGO))


@unittest.skipUnless(CHROME, "No hay Chrome: definí CHROME_BIN para correr las pruebas de JavaScript de Vidriera")
class Horario(unittest.TestCase):
    def test_tramo_que_cruza_medianoche_desde_el_dia_anterior(self):
        # lunes 20:00-02:00; el martes 01:00 todavía está abierto
        r = ejecutar({"now": epoch_ms(2026, 10, 20, 1, 0, -3), "tz": TZ_NEGOCIO}, ESC_HORARIO)
        self.assertEqual(r["a"]["estado"], "Abierto", r)
        self.assertEqual(r["a"]["detalle"], "Abierto hasta las 02:00", r)

    def test_despues_del_cierre_nocturno_y_antes_de_abrir(self):
        r = ejecutar({"now": epoch_ms(2026, 10, 20, 3, 0, -3), "tz": TZ_NEGOCIO}, ESC_HORARIO)
        self.assertEqual(r["a"]["estado"], "Cerrado", r)

    def test_usa_la_zona_horaria_del_negocio_no_la_del_visitante(self):
        # lunes 23:00 en Buenos Aires = martes 02:00 UTC (donde está el navegador de la prueba)
        r = ejecutar({"now": epoch_ms(2026, 10, 19, 23, 0, -3), "tz": TZ_NEGOCIO}, ESC_HORARIO)
        self.assertEqual(r["a"]["estado"], "Abierto", r)
        self.assertEqual(r["a"]["hoy"], ["Lunes"], r)

    def test_dos_turnos_en_el_mismo_dia(self):
        casos = [(10, 30, "Abierto"), (14, 30, "Cerrado"), (17, 0, "Abierto")]
        for h, m, esperado in casos:
            with self.subTest("%02d:%02d" % (h, m)):
                r = ejecutar({"now": epoch_ms(2026, 10, 20, h, m, -3), "tz": TZ_NEGOCIO}, ESC_HORARIO)
                self.assertEqual(r["a"]["estado"], esperado, r)

    def test_se_recalcula_cada_minuto(self):
        # martes 12:50 abierto (9-13); 20 minutos después ya cerró
        r = ejecutar({"now": epoch_ms(2026, 10, 20, 12, 50, -3), "tz": TZ_NEGOCIO}, ESC_REINICIO % (20 * 60000))
        self.assertTrue(r["hay_intervalo"], "no hay un temporizador de 60 s o menos")
        self.assertEqual(r["a"]["estado"], "Abierto", r)
        self.assertEqual(r["b"]["estado"], "Cerrado", r)

    def test_zona_ausente_no_rompe(self):
        r = ejecutar({"now": NOW, "tz": ""}, ESC_HORARIO)
        self.assertIn(r["a"]["estado"], ("Abierto", "Cerrado"))


if __name__ == "__main__":
    unittest.main()


@unittest.skipUnless(CHROME, "No hay Chrome: definí CHROME_BIN para correr las pruebas de JavaScript")
class SintaxisDeLasCinco(unittest.TestCase):
    def test_el_js_inline_de_cada_esqueleto_compila(self):
        """Un error de sintaxis en un <script> inline lo apaga en silencio: acá se compila cada uno."""
        fuentes = []
        for nombre in sorted(os.listdir(PLANTILLA)):
            if nombre.endswith(".html"):
                html = leer(os.path.join(PLANTILLA, nombre))
                for i, m in enumerate(re.finditer(r"<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>(.*?)</script>", html, re.S)):
                    fuentes.append({"archivo": nombre, "n": i, "src": m.group(1)})
        self.assertGreaterEqual(len(fuentes), 10)
        pagina = os.path.join(tempfile.mkdtemp(prefix="kitweb-js-"), "s.html")
        with open(pagina, "w", encoding="utf-8") as f:
            f.write("<body><script>var F=%s,E=[];F.forEach(function(x){try{new Function(x.src)}catch(e){E.push(x.archivo+'#'+x.n+': '+e.message)}});"
                    "document.body.setAttribute('data-res',JSON.stringify({errores:E,total:F.length}))</script></body>" % json.dumps(fuentes).replace("</", "<\\/"))
        r = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-first-run", "--dump-dom", "file://" + pagina], capture_output=True, text=True, timeout=90)
        m = re.search(r"data-res='([^']*)'", r.stdout) or re.search(r'data-res="([^"]*)"', r.stdout)
        self.assertTrue(m, r.stderr[-300:])
        res = json.loads(m.group(1).replace("&quot;", '"'))
        self.assertEqual(res["errores"], [])
        self.assertEqual(res["total"], len(fuentes))
