"""Auditor (P1): contacto en otra página, fallo de carga e inferencias moderadas. Servidor local con una web ficticia."""
import http.server
import os
import re
import tempfile
import threading
import unittest

from util import correr, leer

PORTADA = """<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><title>Panadería Ficticia · pan casero</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Panadería ficticia de barrio con pan casero, facturas y tortas por encargo, para las pruebas del kit.">
</head><body><h1>Panadería Ficticia</h1><p>Pan casero todos los días. Mirá nuestra carta y pedí por encargo.</p>
<nav><a href="/contacto">Contacto</a></nav></body></html>"""
CONTACTO = """<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><title>Contacto · Panadería Ficticia</title></head><body>
<h1>Contacto</h1><p>Av. Siempreviva 742, Ciudad Ficticia.</p><p>Horario: lunes a sábado de 8 a 20 hs.</p>
<a href="tel:+541155555555">+54 11 5555-5555</a> <a href="https://wa.me/5491155555555">Escribinos por WhatsApp</a></body></html>"""


class Manejador(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        cuerpo = {"/": PORTADA, "/contacto": CONTACTO}.get(self.path.split("?")[0])
        self.send_response(200 if cuerpo else 404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write((cuerpo or "no existe").encode())

    def log_message(self, *a):
        pass


class ServidorFicticio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Manejador)
        cls.url = "http://127.0.0.1:%d/" % cls.srv.server_port
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def auditar(self, url, *extra):
        d = tempfile.mkdtemp(prefix="kitweb-aud-")
        cod, out = correr("auditar_web.py", url, "--salida", os.path.join(d, "auditoria.md"), "--html", *extra)
        md = leer(os.path.join(d, "auditoria.md"))
        html = leer(os.path.join(d, "auditoria.html"))
        return cod, out, md, html


class ContactoEnOtraPagina(ServidorFicticio):
    def test_no_marca_como_faltante_lo_que_esta_en_contacto(self):
        cod, out, md, html = self.auditar(self.url)
        self.assertIn("Se leyó también la página de contacto", out)
        faltas = [l for l in out.splitlines() if l.startswith("FALTA")]
        for tema in ("WhatsApp", "tel", "dirección", "horarios"):
            self.assertFalse([l for l in faltas if tema.lower() in l.lower()], f"marca como faltante «{tema}»: {faltas}")
        self.assertNotRegex(html, r"(?i)No hay botón de WhatsApp|No dice los horarios|No hay teléfono")

    def test_el_resumen_cuenta_bien(self):
        _, out, md, _ = self.auditar(self.url)
        faltas = len([l for l in out.splitlines() if l.startswith("FALTA")])
        self.assertIn(f"**{faltas} cosas que faltan**", md)


class FalloDeCarga(unittest.TestCase):
    URL = "http://127.0.0.1:9/"  # puerto cerrado: conexión rechazada

    def test_el_informe_no_dice_que_la_web_esta_bien(self):
        cod, out, md, html = self._aud()
        self.assertNotEqual(cod, 0)
        self.assertNotIn("la web está bien", html)
        self.assertNotIn("Nada grave", html)
        self.assertRegex(html, r"(?i)no se pudo cargar")
        self.assertRegex(md, r"(?i)no se pudo cargar")
        self.assertNotRegex(md, r"\*\*0 cosas que faltan\*\*")

    def _aud(self):
        d = tempfile.mkdtemp(prefix="kitweb-aud-")
        cod, out = correr("auditar_web.py", self.URL, "--salida", os.path.join(d, "auditoria.md"), "--html")
        return cod, out, leer(os.path.join(d, "auditoria.md")), leer(os.path.join(d, "auditoria.html"))


class InferenciasModeradas(ServidorFicticio):
    def test_viewport_no_se_presenta_como_prueba_de_buen_celular(self):
        _, out, _, _ = self.auditar(self.url)
        lineas = [l for l in out.splitlines() if "viewport" in l.lower()]
        self.assertTrue(lineas)
        for l in lineas:
            self.assertRegex(l, r"(?i)no prueba|no garantiza|mirar|probar")

    def test_sin_json_ld_no_se_afirma_que_google_no_entiende(self):
        _, out, _, _ = self.auditar(self.url)
        lineas = [l for l in out.splitlines() if "json-ld" in l.lower() or "datos estructurados" in l.lower()]
        self.assertTrue(lineas)
        for l in lineas:
            self.assertNotIn("Google no recibe", l)
            self.assertRegex(l, r"(?i)en el HTML")

    def test_el_informe_html_aclara_que_es_heuristico(self):
        _, _, _, html = self.auditar(self.url)
        self.assertRegex(html, r"(?i)heur[ií]stic|no (es|reemplaza) una evaluaci")


if __name__ == "__main__":
    unittest.main()
