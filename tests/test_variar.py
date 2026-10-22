"""Contraste (P2): las 60 paletas, para cada rol de texto que generan los esqueletos."""
import contextlib
import io
import json
import os
import re
import unittest

from util import KIT, cargar, correr

v = cargar("variar")
PALETAS = json.load(open(os.path.join(KIT, "references", "paletas.json"), encoding="utf-8"))["paletas"]
MINIMO = 4.5


def valores(p, esqueleto):
    """Lo que imprime variar.py para esa paleta: el :root y los slots de color."""
    c = {"pal": p["id"], "btn": "recto", "cta": "izq", "esq": "0", "marco": "recto", "sep": "recto", "hero": "izq"}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        v.salida(esqueleto, c, p)
    out = buf.getvalue()
    raiz = dict(re.findall(r"--([a-z0-9-]+):(#[0-9a-fA-F]{6})", re.search(r":root \(slot \{\{PALETA_ROOT\}\}\) ==\n(.*)", out).group(1)))
    slots = dict(re.findall(r"^([A-Z0-9_]+): (#[0-9a-fA-F]{6})$", out, re.M))
    return raiz, slots


class Paletas(unittest.TestCase):
    def test_todos_los_roles_de_texto_llegan_a_4_5(self):
        malos = []
        for p in PALETAS:
            esq = "pulso" if v.oscura(p) else "aire"
            raiz, s = valores(p, esq)
            bg, f2 = s["FONDO"], s["FONDO2"]
            sup = raiz.get("papel", p["superficie"])
            acc = s["ACENTO"]
            roles = [("ink/fondo", raiz["ink"], bg), ("ink/fondo2", raiz["ink"], f2), ("ink/superficie", raiz["ink"], sup),
                     ("ink2/fondo", raiz["ink2"], bg), ("ink2/fondo2", raiz["ink2"], f2), ("ink2/superficie", raiz["ink2"], sup),
                     ("muted/fondo", raiz["muted"], bg), ("muted/fondo2", raiz["muted"], f2), ("muted/superficie", raiz["muted"], sup),
                     ("sobre-acc/acc", s["TEXTO_SOBRE_ACENTO"], acc),
                     ("sobre-acc2/acc2", raiz.get("sobre-acc2", s["TEXTO_SOBRE_ACENTO"]), s["SECUNDARIO"]),
                     ("acc-texto/fondo", raiz.get("acc-t", acc), bg), ("acc-texto/fondo2", raiz.get("acc-t", acc), f2), ("acc-texto/superficie", raiz.get("acc-t", acc), sup),
                     ("acc2-texto/fondo", raiz.get("acc2-t", s["SECUNDARIO"]), bg), ("acc2-texto/superficie", raiz.get("acc2-t", s["SECUNDARIO"]), sup)]
            for nombre, fg, fd in roles:
                c = v.contraste(fg, fd)
                if c < MINIMO:
                    malos.append("%s %s %.2f" % (p["id"], nombre, c))
        self.assertEqual(malos, [], "%d combinaciones bajo 4,5:1; las primeras: %s" % (len(malos), malos[:8]))

    def test_el_chequeo_cubre_cada_rol_y_falla_si_uno_no_llega(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertTrue(v.chequear(PALETAS))
        salida = buf.getvalue()
        for rol in ("muted", "ink2", "secundario"):
            self.assertIn(rol, salida)
        mala = dict(PALETAS[0], fondo="#777777", texto="#888888", id="mala")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(v.chequear([mala]))

    def test_chequear_por_linea_de_comandos(self):
        cod, out = correr("variar.py", "--chequear")
        self.assertEqual(cod, 0, out[-300:])
        self.assertIn("60 paletas, 0 no llegan", out)


if __name__ == "__main__":
    unittest.main()
