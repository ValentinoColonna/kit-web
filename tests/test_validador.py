"""Validador (P1): cada caso reproduce un falso positivo de la auditoría externa sobre c0b3c50."""
import re
import unittest

from util import EJEMPLO, correr, escribir_temp, leer

BASE = leer(EJEMPLO)
WA = "https://wa.me/5491155555555?text=Hola"


def validar(html, *flags):
    return correr("validar_sitio.py", escribir_temp(html), *flags)


def con(viejo, nuevo, html=BASE, todos=True):
    assert viejo in html, viejo
    return html.replace(viejo, nuevo) if todos else html.replace(viejo, nuevo, 1)


def ld(obj_json, html=BASE):
    return re.sub(r'(<script type="application/ld\+json">).*?(</script>)', lambda m: m.group(1) + obj_json + m.group(2), html, flags=re.S)


class Base(unittest.TestCase):
    def test_ejemplo_pasa_con_la_nueva_conclusion(self):
        cod, out = validar(BASE)
        self.assertEqual(cod, 0, out)
        self.assertIn("superó las comprobaciones automáticas", out)
        self.assertNotIn("lista para publicar", out)
        self.assertIn("A MANO", out.upper())  # lista concreta de lo que hay que revisar a mano


class JsonLd(unittest.TestCase):
    def test_solo_el_tipo_no_alcanza(self):
        cod, out = validar(ld('{"@context":"https://schema.org","@type":"LocalBusiness"}'))
        self.assertEqual(cod, 1, out)
        self.assertIn("telephone", out)

    def test_faltan_horarios(self):
        cod, out = validar(ld('{"@type":"Restaurant","name":"Ficticio","telephone":"+54 11 5555-5555","address":{"@type":"PostalAddress","streetAddress":"Calle Falsa 123"}}'))
        self.assertEqual(cod, 1, out)
        self.assertIn("openingHours", out)

    def test_campos_vacios_no_cuentan(self):
        cod, out = validar(ld('{"@type":"Restaurant","name":"","telephone":" ","address":{},"openingHours":[]}'))
        self.assertEqual(cod, 1, out)

    def test_graph_completo_pasa(self):
        j = '{"@context":"https://schema.org","@graph":[{"@type":"Dentist","name":"Ficticio","telephone":"+541155555555","address":{"@type":"PostalAddress","streetAddress":"Calle Falsa 123"},"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":"Monday","opens":"09:00","closes":"18:00"}]}]}'
        cod, out = validar(ld(j))
        self.assertEqual(cod, 0, out)


class Contactos(unittest.TestCase):
    def test_tel_sin_numero(self):
        h = con('href="tel:+541155555555"', 'href="tel:"')
        cod, out = validar(h)
        self.assertEqual(cod, 1, out)
        self.assertIn("tel:", out)

    def test_tel_con_letras(self):
        cod, out = validar(con('href="tel:+541155555555"', 'href="tel:pendiente"'))
        self.assertEqual(cod, 1, out)

    def test_whatsapp_de_otro_dominio_con_wa_me_en_la_ruta(self):
        h = con("https://wa.me/5491155555555", "https://example.invalid/wa.me/5491155555555")
        cod, out = validar(h)
        self.assertEqual(cod, 1, out)
        self.assertIn("WhatsApp", out)

    def test_whatsapp_con_wa_me_en_la_consulta(self):
        h = con("https://wa.me/5491155555555", "https://example.invalid/ir?u=https://wa.me/5491155555555")
        self.assertEqual(validar(h)[0], 1)

    def test_whatsapp_con_credenciales_falsas(self):
        h = con("https://wa.me/5491155555555", "https://wa.me@example.invalid/5491155555555")
        self.assertEqual(validar(h)[0], 1)

    def test_whatsapp_sin_numero(self):
        self.assertEqual(validar(con("https://wa.me/5491155555555", "https://wa.me/"))[0], 1)

    def test_api_whatsapp_sin_numero(self):
        self.assertEqual(validar(con("https://wa.me/5491155555555", "https://api.whatsapp.com/send?text=Hola"))[0], 1)

    def test_api_whatsapp_con_numero(self):
        cod, out = validar(con("https://wa.me/5491155555555", "https://api.whatsapp.com/send?phone=5491155555555&text=Hola"))
        self.assertEqual(cod, 0, out)


class Placeholders(unittest.TestCase):
    FORMATOS = ["[telefono pendiente]", "[Teléfono]", "[TELÉFONO]", "PENDIENTE-A-CONFIRMAR", "COMPLETAR", "Lorem ipsum dolor sit amet",
                "XXXX", "TODO", "[ completar acá ]", "{{TELEFONO_VISIBLE}}", "{{ TELEFONO }}"]

    def test_todos_los_formatos_bloquean(self):
        for f in self.FORMATOS:
            with self.subTest(f):
                h = con("<h1>", f"<p>{f}</p><h1>", todos=False)
                cod, out = validar(h)
                self.assertEqual(cod, 1, f"{f} no bloqueó:\n{out}")

    def test_en_borrador_son_avisos(self):
        h = con("<h1>", "<p>[telefono pendiente]</p><h1>", todos=False)
        cod, out = validar(h, "--borrador")
        self.assertEqual(cod, 0, out)
        self.assertIn("AVISO", out)

    def test_placeholder_en_atributos(self):
        for h in (con('alt="', 'alt="[foto pendiente] ', todos=False), con('<title>', '<title>[NOMBRE] ', todos=False)):
            self.assertEqual(validar(h)[0], 1)

    def test_json_ld_con_listas_no_es_placeholder(self):
        j = '{"@type":"Restaurant","name":"Ficticio","telephone":"+541155555555","address":{"@type":"PostalAddress","streetAddress":"Calle Falsa 123"},"openingHours":["Mo-Sa 09:00-20:00","Su 10:00-14:00"]}'
        cod, out = validar(ld(j))
        self.assertEqual(cod, 0, out)

    def test_placeholder_en_un_valor_del_json_ld(self):
        j = '{"@type":"Restaurant","name":"[NOMBRE]","telephone":"+541155555555","address":{"streetAddress":"Calle Falsa 123"},"openingHours":["Mo-Sa 09:00-20:00"]}'
        self.assertEqual(validar(ld(j))[0], 1)

    def test_corchetes_dentro_de_scripts_no_molestan(self):
        h = con("</body>", "<script>var a=[1,2,3];var b=a[0];var c=[x,y];</script></body>")
        cod, out = validar(h)
        self.assertEqual(cod, 0, out)


class Externos(unittest.TestCase):
    def test_script_con_la_cadena_permitida_en_la_ruta(self):
        h = con("</body>", '<script src="https://example.invalid/cdnjs.cloudflare.com/ajax/libs/gsap/payload.js"></script></body>')
        cod, out = validar(h)
        self.assertEqual(cod, 1, out)
        self.assertIn("example.invalid", out)

    def test_script_con_la_cadena_permitida_como_subdominio(self):
        h = con("</body>", '<script src="https://cdnjs.cloudflare.com.example.invalid/ajax/libs/gsap/x.js"></script></body>')
        self.assertEqual(validar(h)[0], 1)

    def test_script_con_credenciales_falsas(self):
        h = con("</body>", '<script src="https://cdnjs.cloudflare.com@example.invalid/ajax/libs/gsap/x.js"></script></body>')
        self.assertEqual(validar(h)[0], 1)

    def test_script_sin_esquema(self):
        h = con("</body>", '<script src="//example.invalid/payload.js"></script></body>')
        self.assertEqual(validar(h)[0], 1)

    def test_hoja_de_estilos_sin_esquema(self):
        h = con("</head>", '<link rel="stylesheet" href="//example.invalid/payload.css"></head>')
        cod, out = validar(h)
        self.assertEqual(cod, 1, out)
        self.assertIn("example.invalid", out)

    def test_hoja_de_estilos_con_google_fonts_en_otro_host(self):
        h = con("</head>", '<link rel="stylesheet" href="https://example.invalid/fonts.googleapis.com/css2?family=Inter"></head>')
        self.assertEqual(validar(h)[0], 1)

    def test_rel_con_mayusculas_o_varios_valores(self):
        h = con("</head>", '<link rel="Stylesheet preload" href="//example.invalid/p.css"></head>')
        self.assertEqual(validar(h)[0], 1)

    def test_import_en_css_inline(self):
        h = con("</head>", '<style>@import url("https://example.invalid/p.css");</style></head>')
        self.assertEqual(validar(h)[0], 1)

    def test_gsap_legitimo_pasa(self):
        h = con("</body>", '<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>'
                '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter"></body>')
        cod, out = validar(h)
        self.assertEqual(cod, 0, out)


class Horarios(unittest.TestCase):
    FILA = '<div class="horas"><div data-dias="1" data-abre="20:00" data-cierra="02:00"><span>Lunes</span><b>20 a 02</b></div></div>'

    def test_horario_dinamico_sin_zona_horaria(self):
        cod, out = validar(con("</body>", self.FILA + "</body>"))
        self.assertEqual(cod, 1, out)
        self.assertIn("data-tz", out)

    def test_horario_con_zona_horaria_pasa(self):
        h = self.FILA.replace('class="horas"', 'class="horas" data-tz="America/Argentina/Buenos_Aires"')
        cod, out = validar(con("</body>", h + "</body>"))
        self.assertEqual(cod, 0, out)

    def test_zona_horaria_inventada(self):
        h = self.FILA.replace('class="horas"', 'class="horas" data-tz="Narnia/Cair_Paravel"')
        self.assertEqual(validar(con("</body>", h + "</body>"))[0], 1)


if __name__ == "__main__":
    unittest.main()
