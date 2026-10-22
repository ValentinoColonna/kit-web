"""Documentación e instalación: una sola receta de publicación, permisos para python y python3, sin promesas sin respaldo."""
import glob
import json
import os
import re
import unittest

from util import KIT, RAIZ, leer

SCRIPTS = sorted(os.path.basename(p) for p in glob.glob(os.path.join(KIT, "scripts", "*.py")))


class Instalacion(unittest.TestCase):
    def test_permisos_para_python_y_python3(self):
        permisos = json.loads(leer(os.path.join(RAIZ, ".claude", "settings.json")))["permissions"]["allow"]
        for s in SCRIPTS:
            for interprete in ("python3", "python"):
                self.assertIn("Bash(%s rehacer-web/scripts/%s:*)" % (interprete, s), permisos)

    def test_cada_script_citado_existe(self):
        for ruta in ("CLAUDE.md", "README.md", "EMPIEZA-AQUI.md", "rehacer-web/SKILL.md"):
            for s in re.findall(r"rehacer-web/scripts/([a-z_]+\.py)", leer(os.path.join(RAIZ, ruta))):
                self.assertIn(s, SCRIPTS, "%s cita %s, que no existe" % (ruta, s))

    def test_chequeo_inicial_documentado(self):
        for ruta in ("CLAUDE.md", "rehacer-web/SKILL.md"):
            self.assertIn("chequear_entorno.py", leer(os.path.join(RAIZ, ruta)))

    def test_sips_se_avisa_como_solo_de_mac(self):
        for ruta in ("rehacer-web/SKILL.md", "rehacer-web/references/imagenes.md"):
            self.assertRegex(leer(os.path.join(RAIZ, ruta)), r"(?i)solo de Mac|solo en Mac")


class Publicacion(unittest.TestCase):
    def test_una_sola_receta(self):
        claude, skill = leer(os.path.join(RAIZ, "CLAUDE.md")), leer(os.path.join(KIT, "SKILL.md"))
        self.assertNotIn("Esa carpeta es la que se publica", claude)
        self.assertIn("-publicar", claude)
        self.assertIn("-publicar", skill)
        self.assertIn("Una sola receta", skill)

    def test_cuotas_de_netlify_mencionadas(self):
        for ruta in ("README.md", "rehacer-web/references/publicar-netlify.md", "rehacer-web/SKILL.md"):
            self.assertRegex(leer(os.path.join(RAIZ, ruta)), r"(?i)cuota")


class Promesas(unittest.TestCase):
    def test_no_promete_que_cualquier_modelo_rinde_igual(self):
        for ruta in ("README.md", "EMPIEZA-AQUI.md", "rehacer-web/SKILL.md", "CLAUDE.md"):
            self.assertIsNone(re.search(r"(?i)rind[ae]n? igual", leer(os.path.join(RAIZ, ruta))), ruta)

    def test_gate_sin_no_sandbox_y_con_lo_que_no_prueba(self):
        gate = leer(os.path.join(KIT, "references", "gate-visual.md"))
        self.assertEqual([l for l in gate.splitlines() if "--no-sandbox" in l and not l.lstrip().startswith(("No se usa", "-"))], [])
        self.assertIn("No prueba", gate)

    def test_contenido_de_webs_es_dato_no_instruccion(self):
        for ruta in ("CLAUDE.md", "rehacer-web/SKILL.md"):
            self.assertRegex(leer(os.path.join(RAIZ, ruta)), r"(?i)dato, no instrucci")

    def test_el_validador_ya_no_dice_lista_para_publicar(self):
        for ruta in ("README.md", "CLAUDE.md", "rehacer-web/SKILL.md"):
            self.assertIsNone(re.search(r"validador tiene que decir PASA|hasta que diga PASA", leer(os.path.join(RAIZ, ruta))), ruta)

    def test_el_comando_de_pruebas_esta_documentado(self):
        self.assertIn("python3 -m unittest discover -s tests", leer(os.path.join(RAIZ, "README.md")))


if __name__ == "__main__":
    unittest.main()
