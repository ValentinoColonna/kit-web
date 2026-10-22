#!/usr/bin/env python3
# Kit rehacer-web · Valentino Colonna (@valentino.ia) · Licencia MIT · https://github.com/ValentinoColonna/kit-web
"""Audita la web actual de un negocio y escribe auditoria.md.

Uso:
    python3 auditar_web.py https://la-web-vieja.com [--salida auditoria.md] [--html]
    python3 auditar_web.py entrada/web-vieja.html [--salida auditoria.md] [--html]   (si el dueño pasa el archivo en vez del link)

Revisión heurística del HTML (no una evaluación completa del sitio) de lo que importa a un cliente y a Google: título, descripción, viewport, HTTPS,
teléfono y WhatsApp a un toque, dirección, horarios, redes, imágenes sin texto alternativo, peso de la página
y tecnología visible. Sin dependencias externas (solo Python 3). No ejecuta JavaScript: si la web es una app
que carga todo por JS, lo dice y el resultado es parcial.
"""
import argparse
import html
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"


class Lector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._en_title = False
        self.metas = {}
        self.h1 = []
        self.h2 = []
        self._en = None
        self.imgs = []
        self.links = []
        self.scripts_ext = []
        self.scripts_inline = 0
        self.jsonld = []
        self._en_jsonld = False
        self._en_codigo = 0
        self.texto = []
        self.viewport = None
        self.lang = None
        self.forms = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._en_codigo += 1
        a = dict(attrs)
        if tag == "html" and a.get("lang"):
            self.lang = a["lang"]
        if tag == "title":
            self._en_title = True
        if tag == "meta":
            nombre = (a.get("name") or a.get("property") or "").lower()
            if nombre:
                self.metas[nombre] = a.get("content", "")
            if nombre == "viewport":
                self.viewport = a.get("content", "")
        if tag in ("h1", "h2"):
            self._en = tag
        if tag == "img":
            self.imgs.append({"src": a.get("src", ""), "alt": a.get("alt")})
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "script":
            if a.get("src"):
                self.scripts_ext.append(a["src"])
            elif (a.get("type") or "").lower() == "application/ld+json":
                self._en_jsonld = True
            else:
                self.scripts_inline += 1
        if tag == "form":
            self.forms += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._en_title = False
        if tag in ("h1", "h2"):
            self._en = None
        if tag in ("script", "style"):
            self._en_jsonld = False
            self._en_codigo = max(0, self._en_codigo - 1)

    def handle_data(self, data):
        if self._en_title:
            self.title += data
        if self._en == "h1":
            self.h1.append(data.strip())
        if self._en == "h2":
            self.h2.append(data.strip())
        if self._en_jsonld:
            self.jsonld.append(data)
        if data.strip() and not self._en_codigo:
            self.texto.append(data.strip())


def bajar(url):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-AR,es;q=0.9"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            cuerpo = r.read()
            return r.geturl(), r.status, dict(r.headers), cuerpo, time.time() - t0, None
    except urllib.error.HTTPError as e:
        return url, e.code, dict(e.headers or {}), e.read() if e.fp else b"", time.time() - t0, str(e)
    except Exception as e:  # SSL, DNS, timeout
        return url, None, {}, b"", time.time() - t0, str(e)


def pagina_de_contacto(p, url_final):
    """Si la web tiene una página de contacto en el mismo dominio, la baja para sacar teléfono, dirección y horarios."""
    base = urllib.parse.urlparse(url_final)
    for l in p.links:
        if re.search(r"contact", l, re.I) and not l.lower().startswith(("mailto:", "tel:")):
            destino = urllib.parse.urljoin(url_final, l)
            if urllib.parse.urlparse(destino).netloc.replace("www.", "") == base.netloc.replace("www.", "") and destino.rstrip("/") != url_final.rstrip("/"):
                _, status, _, cuerpo, _, _ = bajar(destino)
                if cuerpo:
                    q = Lector()
                    try:
                        q.feed(cuerpo.decode("utf-8", "ignore"))
                    except Exception:
                        pass
                    return destino, q
    return None, None


def auditar(url):
    if os.path.isfile(url):
        with open(url, "rb") as f:
            cuerpo = f.read()
        h = {"url": os.path.basename(url), "url_final": "archivo local", "status": 200, "segundos": 0.0, "bytes": len(cuerpo), "error": None, "local": True}
        headers = {}
        return analizar(h, cuerpo)
    if not re.match(r"^https?://", url):
        url = "https://" + url
    final, status, headers, cuerpo, segundos, error = bajar(url)
    h = {"url": url, "url_final": final, "status": status, "segundos": round(segundos, 2), "bytes": len(cuerpo), "error": error}
    if error and not cuerpo and url.startswith("https://"):
        # Probar sin HTTPS
        final2, status2, headers2, cuerpo2, segundos2, error2 = bajar("http://" + url[len("https://"):])
        if cuerpo2:
            h.update({"url_final": final2, "status": status2, "segundos": round(segundos2, 2), "bytes": len(cuerpo2), "error": None, "sin_https": True})
            cuerpo, headers = cuerpo2, headers2
    if not cuerpo:
        p = Lector()
        h["fallo"] = True
        return h, "", "", p, [("ERROR", f"No se pudo cargar la web: {h['error'] or h['status']}. No se pudo revisar nada. Probá de nuevo y revisá la dirección: un fallo de conexión no prueba que el negocio no tenga web")], ""
    if h["status"] and h["status"] >= 400:
        h["parcial"] = True
    return analizar(h, cuerpo)


def analizar(h, cuerpo):
    texto_html = cuerpo.decode("utf-8", "ignore")
    p = Lector()
    try:
        p.feed(texto_html)
    except Exception:
        pass
    texto = " ".join(p.texto)
    texto_portada = texto
    hallazgos = []
    # Primero se lee la página de contacto (si hay): los datos que están ahí no pueden figurar como faltantes.
    contacto_leido = None
    if not h.get("local"):
        destino, q = pagina_de_contacto(p, h["url_final"] or h["url"])
        if q is not None:
            h["contacto"] = destino
            contacto_leido = destino
            p.links += [l for l in q.links if l not in p.links]
            texto = texto + " | " + " ".join(q.texto)
    texto_min = texto.lower()
    if h.get("parcial"):
        hallazgos.append(("ERROR", f"La dirección respondió con error HTTP {h['status']}: lo que sigue es de esa página de error, no de la web del negocio"))

    def falta(cond, msg_bien, msg_mal):
        hallazgos.append(("OK" if cond else "FALTA", msg_bien if cond else msg_mal))

    titulo = html.unescape(p.title.strip())
    desc = html.unescape(p.metas.get("description", "")).strip()
    if h.get("local"):
        hallazgos.append(("INFO", "Archivo local: HTTPS y velocidad no se miden (hace falta el link publicado)"))
    else:
        falta(h["url_final"].startswith("https://") and not h.get("sin_https"), "Carga por HTTPS (candado)", "No carga por HTTPS: el navegador la marca como no segura")
    falta(bool(p.viewport), f"Declara viewport para celular ({p.viewport}). Eso no prueba que se vea bien: hay que mirarla en un celular", "No declara viewport: es probable que en el celular se vea como una web de escritorio achicada (hay que mirarla en un celular)")
    falta(10 <= len(titulo) <= 70, f"Título: «{titulo}» ({len(titulo)} caracteres)", f"Título ausente o fuera de medida: «{titulo}» ({len(titulo)} caracteres; ideal 10 a 70)")
    falta(50 <= len(desc) <= 170, f"Descripción para Google: «{desc[:90]}…» ({len(desc)} caracteres)", f"Descripción para Google ausente o fuera de medida ({len(desc)} caracteres; ideal 50 a 170)")
    falta(len(p.h1) == 1, f"Un solo H1: «{p.h1[0][:80]}»" if p.h1 else "", f"{len(p.h1)} H1 (tiene que haber exactamente uno que diga qué es el negocio)")
    tel_links = [l for l in p.links if l.lower().startswith("tel:")]
    wa_links = [l for l in p.links if "wa.me" in l or "api.whatsapp.com" in l or "whatsapp" in l.lower()]
    falta(bool(wa_links), f"WhatsApp a un toque ({wa_links[0] if wa_links else ''})", "No hay botón de WhatsApp (wa.me): el cliente tiene que copiar el número a mano")
    falta(bool(tel_links), f"Teléfono clickeable ({tel_links[0] if tel_links else ''})", "No hay teléfono con enlace tel:")
    hay_tel_texto = bool(re.search(r"(\+?\d[\d\s().-]{7,}\d)", texto))
    hallazgos.append(("INFO", "Hay un número de teléfono en el texto" if hay_tel_texto else "No se ve ningún número de teléfono en el texto"))
    hay_dir = any(k in texto_min for k in ["calle", "av.", "avenida", "ruta", "km", "local", "piso", "barrio", "cp "])
    mapa = [l for l in p.links if "maps" in l.lower() or "goo.gl/maps" in l.lower()]
    falta(hay_dir or mapa, "Hay dirección o enlace a Google Maps", "No se ve una dirección ni un enlace a Google Maps")
    hay_hor = any(k in texto_min for k in ["horario", "lunes", "lun a", "abierto", "hs", "hrs", "de 9", "de 8", "a 18", "a 20"])
    falta(hay_hor, "Dice los horarios", "No dice los horarios")
    redes = [l for l in p.links if any(r in l.lower() for r in ["instagram.com", "facebook.com", "tiktok.com", "linkedin.com", "youtube.com"])]
    hallazgos.append(("INFO", f"Redes enlazadas: {len(redes)}" + (f" ({', '.join(sorted({urllib.parse.urlparse(r).netloc for r in redes}))})" if redes else "")))
    sin_alt = [i for i in p.imgs if not (i.get("alt") or "").strip()]
    falta(not sin_alt, f"{len(p.imgs)} imágenes, todas con texto alternativo", f"{len(sin_alt)} de {len(p.imgs)} imágenes sin texto alternativo (Google no sabe qué muestran)")
    falta(bool(p.jsonld), "Tiene datos estructurados (JSON-LD) en el HTML", "No se detectó JSON-LD en el HTML (puede estar cargado por JavaScript o en otro formato): conviene confirmarlo con la prueba de resultados enriquecidos de Google")
    falta(bool(p.lang), f"Idioma declarado: {p.lang}", "No declara el idioma de la página")
    kb = h["bytes"] / 1024
    falta(kb < 300, f"Página de {kb:.0f} KB de HTML", f"HTML de {kb:.0f} KB (pesado para una página de negocio)")
    if not h.get("local"):
        hallazgos.append(("INFO", f"Respondió en {h['segundos']} s (solo el HTML, sin imágenes ni scripts)"))
    hallazgos.append(("INFO", f"Scripts externos: {len(p.scripts_ext)} · formularios: {p.forms}"))
    tech = []
    bajo = texto_html.lower()
    for marca, patron in [("WordPress", "wp-content"), ("Wix", "wix.com"), ("Squarespace", "squarespace"), ("Joomla", "joomla"), ("jQuery", "jquery"), ("Bootstrap", "bootstrap"), ("Elementor", "elementor"), ("Shopify", "shopify"), ("Google Sites", "sites.google"), ("Tienda Nube", "tiendanube"), ("Flash", ".swf")]:
        if patron in bajo:
            tech.append(marca)
    if tech:
        hallazgos.append(("INFO", "Tecnología visible: " + ", ".join(tech)))
    if len(texto_portada) < 200:
        hallazgos.append(("AVISO", "Casi no hay texto en el HTML: puede ser una web que carga todo por JavaScript; esta auditoría es parcial"))
    if contacto_leido:
        hallazgos.append(("INFO", f"Se leyó también la página de contacto ({contacto_leido}): el teléfono, WhatsApp, dirección y horarios se buscaron en las dos páginas"))
    palabras = len(texto.split())
    hallazgos.append(("INFO", f"Texto visible: unas {palabras} palabras"))
    return h, titulo, desc, p, hallazgos, texto


def datos_de_contacto(p, texto):
    """Lo que la web vieja ya dice del negocio, para proponer el brief (siempre a confirmar con el dueño)."""
    d = {}
    tels, vistos = [], set()
    for m in re.finditer(r"\+?\d[\d\s().-]{6,}\d", re.sub(r"\s{2,}", " | ", texto)):
        crudo = m.group(0).strip()
        digitos = re.sub(r"\D", "", crudo)
        if re.fullmatch(r"(?:(?:19|20)\d{2}\s*)+", crudo):
            continue  # años, no teléfonos
        if ":" in crudo or not (8 <= len(digitos) <= 15) or digitos in vistos:
            continue
        vistos.add(digitos)
        tels.append(crudo)
    tels += [l[4:] for l in p.links if l.lower().startswith("tel:") and re.sub(r"\D", "", l[4:]) not in vistos]
    if tels:
        d["Teléfonos"] = tels[:6]
    wa = []
    for l in p.links:
        m = re.search(r"(?:wa\.me/|phone=)(\d{8,15})", l)
        if m and m.group(1) not in wa:
            wa.append(m.group(1))
    if wa:
        d["WhatsApp (de los enlaces)"] = wa
    mails = sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", texto)) | {l[7:] for l in p.links if l.lower().startswith("mailto:")})
    if mails:
        d["Emails"] = mails[:4]
    frases = re.split(r"(?<=[.!?|•·\n])\s+|\s{2,}", texto)
    dirs = [m.group(0).strip(" -,.") for m in re.finditer(r"\b(?:Av\.?|Avda\.?|Avenida|Calle|Ruta|Bv\.?|Boulevard|Diagonal)\s+[^\d\n]{2,40}?\d{1,5}[^.\n]{0,70}", texto)]
    if dirs:
        d["Posible dirección"] = list(dict.fromkeys(dirs))[:3]
    hor = [f.strip() for f in frases if re.search(r"\b(lunes|martes|miércoles|jueves|viernes|sábado|sabado|domingo|horario|hs\.?|hrs)\b", f, re.I) and re.search(r"\d", f) and len(f) < 200]
    if hor:
        d["Posibles horarios"] = list(dict.fromkeys(hor))[:4]
    redes = sorted({l for l in p.links if any(r in l.lower() for r in ["instagram.com", "facebook.com", "tiktok.com", "linkedin.com", "youtube.com"])})
    if redes:
        d["Redes"] = redes[:6]
    return d


def escribir(ruta, h, titulo, desc, p, hallazgos, texto):
    ok = sum(1 for e, _ in hallazgos if e == "OK")
    faltas = sum(1 for e, _ in hallazgos if e == "FALTA")
    lineas = [f"# Auditoría de {h['url']}", "", f"Fecha: {time.strftime('%Y-%m-%d %H:%M')} · Estado HTTP: {h['status']} · URL final: {h['url_final']}", ""]
    if h.get("error"):
        lineas += [f"**No se pudo cargar:** {h['error']}", ""]
    if h.get("fallo"):
        lineas += ["**Resumen:** no se pudo revisar la web, así que no hay resultados. No sirve para afirmar nada del negocio.", "", "| Estado | Qué |", "|---|---|"]
    else:
        parcial = " **Ojo: la dirección dio un error HTTP; este resumen no describe la web del negocio.**" if h.get("parcial") else ""
        lineas += [f"**Resumen:** {ok} cosas bien · **{faltas} cosas que faltan** (abajo, marcadas FALTA).{parcial}", "", "| Estado | Qué |", "|---|---|"]
    for e, m in hallazgos:
        lineas.append(f"| {e} | {m} |")
    lineas += ["", "## Lo que dice la web (para el brief)", "", f"- **Título:** {titulo or '(vacío)'}", f"- **Descripción:** {desc or '(vacía)'}", f"- **H1:** {' / '.join(p.h1) or '(ninguno)'}", f"- **H2:** {' / '.join(x for x in p.h2 if x)[:300] or '(ninguno)'}", "", "Primeras 600 letras del texto visible:", "", "> " + texto[:600].replace("\n", " "), ""]
    datos = datos_de_contacto(p, texto)
    lineas += ["## Datos del negocio que dice la web vieja (confirmar con el dueño)", ""]
    if datos:
        for k, v in datos.items():
            lineas.append(f"- **{k}:** " + " · ".join(v))
    else:
        lineas.append("- No se encontraron teléfonos, emails, dirección ni horarios en el texto.")
    base = ruta[:-3] if ruta.endswith(".md") else ruta
    ruta_txt = base + "-texto-web-vieja.txt"
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(texto)
    lineas += ["", f"El texto visible completo quedó en `{os.path.basename(ruta_txt)}`, para armar el brief.", "", "## Cómo usar esto", "", "Cada FALTA es un punto para el brief y para la página nueva. Las INFO son contexto. Esta es una revisión heurística del HTML de la portada (y de la página de contacto, si la hay): no mide cómo se ve ni cómo anda en un celular, ni cómo la ve Google. Lo que la web dice del negocio se confirma con el dueño antes de reutilizarlo, y cada FALTA se mira a mano en la web antes de decírsela a nadie."]
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    return ok, faltas


def escribir_html(ruta, h, titulo, hallazgos):
    """Informe visual autónomo (sin dependencias), legible por un dueño de negocio: semáforo por hallazgo."""
    ok = [m for e, m in hallazgos if e == "OK"]
    faltas = [m for e, m in hallazgos if e == "FALTA"]
    infos = [m for e, m in hallazgos if e in ("INFO", "AVISO", "ERROR")]
    # Teaser: primero lo que más contactos cuesta (celular, WhatsApp, teléfono, Google, horarios), después el resto.
    prioridad = ["viewport", "WhatsApp", "tel:", "datos estructurados", "horarios", "HTTPS", "dirección", "Título", "Descripción", "H1", "imágenes", "idioma"]
    def rango(m):
        for i, k in enumerate(prioridad):
            if k.lower() in m.lower():
                return i
        return len(prioridad)
    teaser = sorted(faltas, key=rango)[:3]
    esc = html.escape
    filas = "".join(
        f'<li class="{ "falta" if e == "FALTA" else "ok" if e == "OK" else "info"}"><span class="punto"></span>{esc(m)}</li>'
        for e, m in hallazgos
    )
    if h.get("fallo"):
        teaser, cuerpo_resumen = [], "<li>No se pudo cargar la web, así que no hay nada que concluir. Volvé a intentarlo y revisá la dirección.</li>"
    elif h.get("parcial"):
        teaser, cuerpo_resumen = [], "<li>La dirección respondió con un error: esta revisión no describe la web del negocio.</li>"
    else:
        cuerpo_resumen = "".join(f"<li>{esc(t)}</li>" for t in teaser) or "<li>La revisión automática no encontró faltas en la portada. No es una evaluación completa: mirá la web a mano.</li>"
    teaser_html = cuerpo_resumen
    sin_datos = bool(h.get("fallo") or h.get("parcial"))
    doc = f"""<!DOCTYPE html><html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Auditoría de {esc(h['url'])}</title>
<style>
:root{{--ok:#1f8a4c;--mal:#c0392b;--neutro:#5b6770;--tinta:#1c2230;--papel:#f7f5f0}}
*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--papel);color:var(--tinta);line-height:1.5}}
main{{max-width:760px;margin:0 auto;padding:24px 16px 48px}}h1{{font-size:1.5rem;margin:0 0 4px}}.sub{{color:var(--neutro);font-size:.95rem;margin:0 0 20px}}
.resumen{{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 24px}}.caja{{flex:1 1 140px;background:#fff;border-radius:12px;padding:14px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.06)}}
.caja b{{display:block;font-size:2rem}}.caja.mal b{{color:var(--mal)}}.caja.ok b{{color:var(--ok)}}
h2{{font-size:1.1rem;margin:24px 0 8px}}ul{{list-style:none;padding:0;margin:0}}li{{background:#fff;border-radius:10px;padding:10px 12px 10px 36px;margin:6px 0;position:relative}}
.punto{{position:absolute;left:12px;top:15px;width:12px;height:12px;border-radius:50%;background:var(--neutro)}}.ok .punto{{background:var(--ok)}}.falta .punto{{background:var(--mal)}}
.teaser{{background:#fff;border-left:4px solid var(--mal);border-radius:10px;padding:12px 16px}}.teaser li{{background:none;padding:4px 0 4px 0;margin:0}}
footer{{color:var(--neutro);font-size:.85rem;margin-top:32px}}
</style></head><body><main>
<h1>Lo que le falta a la web de {esc(titulo if titulo and len(titulo) <= 50 else urllib.parse.urlparse(h['url']).netloc.replace('www.', ''))}</h1>
<p class="sub">{esc(h['url'])} · revisada el {time.strftime('%d/%m/%Y %H:%M')} · estado HTTP {esc(str(h['status']))}</p>
{"" if sin_datos else f'<div class="resumen"><div class="caja mal"><b>{len(faltas)}</b>cosas que faltan</div><div class="caja ok"><b>{len(ok)}</b>cosas bien</div><div class="caja"><b>{len(infos)}</b>observaciones</div></div>'}
<h2>{"Qué pasó" if sin_datos else "Lo primero que le cuesta clientes"}</h2><div class="teaser"><ul>{teaser_html}</ul></div>
<h2>Todo lo revisado</h2><ul>{filas}</ul>
<footer>Revisión heurística y automática del HTML de la página de inicio (y de la de contacto, si la hay). No es una evaluación completa del sitio: no mide cómo se ve en un celular, ni la velocidad real, ni las ventas ni las posiciones en Google. Hecha con el kit abierto «rehacer-web».</footer>
</main></body></html>"""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(doc)
    return teaser


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", help="link de la web vieja o ruta a un archivo .html")
    ap.add_argument("--salida", default="auditoria.md")
    ap.add_argument("--html", action="store_true", help="además, escribe auditoria.html (informe visual para mostrar al dueño)")
    a = ap.parse_args()
    h, titulo, desc, p, hallazgos, texto = auditar(a.url)
    ok, faltas = escribir(a.salida, h, titulo, desc, p, hallazgos, texto)
    for e, m in hallazgos:
        print(f"{e:6s} {m}")
    print(f"\nLISTO  {a.salida}: {ok} bien, {faltas} faltan")
    if a.html:
        ruta_html = a.salida[:-3] + ".html" if a.salida.endswith(".md") else a.salida + ".html"
        teaser = escribir_html(ruta_html, h, titulo, hallazgos)
        print(f"LISTO  {ruta_html} (informe visual)")
        if teaser:
            print("\nTEASER (mensaje de apertura, tres hallazgos):")
            for t in teaser:
                print(f"  - {t}")
    sys.exit(0 if h["status"] else 1)


if __name__ == "__main__":
    main()
