"""buscar_fotos.py: alcance de las descargas (esquemas, IP privadas, redirecciones, presupuesto, sitio propio vs CDN)."""
import http.server
import json
import os
import struct
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from util import cargar, correr, leer

bf = cargar("buscar_fotos")
PUBLICA = "93.184.216.34"  # IP pública de documentación


def resolver_falso(host):
    return {"publico.test": [PUBLICA], "interno.test": ["10.0.0.7"], "loop.test": ["127.0.0.1"], "mixto.test": [PUBLICA, "192.168.1.5"]}.get(host, [])


class Destinos(unittest.TestCase):
    def setUp(self):
        self._r = getattr(bf, "resolver", None)
        bf.resolver = resolver_falso

    def tearDown(self):
        bf.resolver = self._r

    def ok(self, url):
        return bf.destino_permitido(url)

    def test_esquemas_distintos_de_http_se_rechazan(self):
        for u in ("file:///etc/passwd", "ftp://publico.test/a.jpg", "gopher://publico.test/", "data:image/png;base64,AAAA", "javascript:alert(1)"):
            self.assertFalse(self.ok(u), u)

    def test_ip_privadas_y_loopback_se_rechazan(self):
        for u in ("http://127.0.0.1/a.jpg", "http://127.1/a.jpg", "http://[::1]/a.jpg", "http://10.0.0.5/a.jpg", "http://192.168.1.1/a.jpg",
                  "http://172.16.0.9/a.jpg", "http://169.254.169.254/latest/meta-data", "http://0.0.0.0/a.jpg", "http://2130706433/a.jpg",
                  "http://interno.test/a.jpg", "http://loop.test/a.jpg", "http://mixto.test/a.jpg"):
            self.assertFalse(self.ok(u), u)

    def test_nombre_que_no_resuelve_se_rechaza(self):
        self.assertFalse(self.ok("http://no-existe.test/a.jpg"))

    def test_destinos_publicos_pasan(self):
        for u in ("http://publico.test/a.jpg", "https://publico.test:8443/a.jpg", "http://%s/a.jpg" % PUBLICA):
            self.assertTrue(self.ok(u), u)

    def test_la_extraccion_acepta_cualquier_host_y_el_filtro_lo_corrige(self):
        html = '<img src="http://127.0.0.1/secreto.jpg"><img src="https://cdn.otro.test/a.jpg"><img src="/fotos/b.jpg">'
        vistas = bf.imagenes(html, "https://negocio.test/")
        self.assertIn("http://127.0.0.1/secreto.jpg", vistas)  # la extracción no filtra: lo hace destino_permitido
        permitidas = [u for u in vistas if self.ok(u)]
        self.assertNotIn("http://127.0.0.1/secreto.jpg", permitidas)

    def test_redireccion_a_un_destino_interno_se_corta(self):
        h = bf.ManejadorRedirecciones()
        req = urllib.request.Request("http://publico.test/a.jpg")
        with self.assertRaises(urllib.error.URLError):
            h.redirect_request(req, None, 302, "Found", {}, "http://interno.test/admin")
        with self.assertRaises(urllib.error.URLError):
            h.redirect_request(req, None, 302, "Found", {}, "file:///etc/passwd")

    def test_redireccion_a_un_destino_publico_sigue(self):
        h = bf.ManejadorRedirecciones()
        req = urllib.request.Request("http://publico.test/a.jpg")
        nuevo = h.redirect_request(req, None, 302, "Found", {}, "http://publico.test/b.jpg")
        self.assertIsNotNone(nuevo)


class Presupuesto(unittest.TestCase):
    def test_tope_de_solicitudes(self):
        p = bf.Presupuesto(max_solicitudes=3, max_segundos=100)
        self.assertEqual([p.permitir() for _ in range(5)], [True, True, True, False, False])

    def test_tope_de_tiempo(self):
        t = [0.0]
        p = bf.Presupuesto(max_solicitudes=100, max_segundos=60, reloj=lambda: t[0])
        self.assertTrue(p.permitir())
        t[0] = 61
        self.assertFalse(p.permitir())


class Origen(unittest.TestCase):
    def test_sitio_propio_subdominio_y_cdn(self):
        self.assertEqual(bf.origen("https://www.negocio.com.ar/a.jpg", "negocio.com.ar"), "propio")
        self.assertEqual(bf.origen("https://negocio.com.ar/a.jpg", "negocio.com.ar"), "propio")
        self.assertEqual(bf.origen("https://static.negocio.com.ar/a.jpg", "negocio.com.ar"), "propio")
        self.assertEqual(bf.origen("https://cdn.otro.com/a.jpg", "negocio.com.ar"), "externo")
        self.assertEqual(bf.origen("https://negocio.com.ar.malo.com/a.jpg", "negocio.com.ar"), "externo")


PNG = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 600, 600) + b"\x00" * 40


class Manejador(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith(".png"):
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(PNG + self.path.encode())
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b'<html><title>Negocio Ficticio</title><img src="/a.png"><img src="/b.png"><img src="/c.png"></html>')

    def log_message(self, *a):
        pass


class DeExtremoAExtremo(unittest.TestCase):
    """Con un servidor ficticio en localhost: sin el permiso de pruebas se bloquea; con él funciona y respeta el presupuesto."""

    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Manejador)
        cls.url = "http://127.0.0.1:%d/" % cls.srv.server_port
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def test_localhost_se_bloquea_por_defecto(self):
        cod, out = correr("buscar_fotos.py", self.url, "--salida", tempfile.mkdtemp(), env={"REHACER_PERMITIR_LOCAL": ""})
        self.assertEqual(cod, 1, out)
        self.assertIn("no permitida", out)

    def test_con_el_permiso_de_pruebas_baja_y_marca_el_origen(self):
        d = tempfile.mkdtemp()
        cod, out = correr("buscar_fotos.py", self.url, "--salida", d, env={"REHACER_PERMITIR_LOCAL": "1"})
        self.assertEqual(cod, 0, out)
        datos = json.loads(leer(os.path.join(d, "candidatas.json")))
        self.assertEqual(len(datos["fotos"]), 3)
        self.assertTrue(all(f["origen"] == "propio" for f in datos["fotos"]))

    def test_el_presupuesto_corta_la_corrida(self):
        d = tempfile.mkdtemp()
        cod, out = correr("buscar_fotos.py", self.url, "--salida", d, "--max-solicitudes", "2", env={"REHACER_PERMITIR_LOCAL": "1"})
        datos = json.loads(leer(os.path.join(d, "candidatas.json")))
        self.assertLessEqual(datos["solicitudes"], 2)
        self.assertTrue(datos["presupuesto_agotado"])
        self.assertIn("presupuesto", out)


if __name__ == "__main__":
    unittest.main()
