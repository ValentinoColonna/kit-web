"""chequear_entorno.py: qué dice cuando falta Python 3.8+, Chrome o sips."""
import unittest

from util import cargar, correr

ce = cargar("chequear_entorno")


class Entorno(unittest.TestCase):
    def test_todo_presente_en_mac(self):
        r = ce.chequear("Darwin", existe=lambda p: True, que=lambda n: "/usr/bin/" + n, version=(3, 9, 6), entorno={})
        self.assertEqual([e for e, _ in r], ["OK", "OK", "OK"])

    def test_sin_chrome_dice_donde_instalarlo(self):
        r = ce.chequear("Darwin", existe=lambda p: False, que=lambda n: None, version=(3, 9, 6), entorno={})
        falta = [m for e, m in r if e == "FALTA"]
        self.assertEqual(len(falta), 1)
        self.assertIn("google.com/chrome", falta[0])

    def test_python_viejo(self):
        r = ce.chequear("Windows", existe=lambda p: True, que=lambda n: None, version=(3, 6, 0), entorno={})
        self.assertIn("python.org", [m for e, m in r if e == "FALTA"][0])

    def test_sips_solo_en_mac(self):
        r = ce.chequear("Windows", existe=lambda p: True, que=lambda n: None, version=(3, 11, 0), entorno={})
        aviso = [m for e, m in r if e == "AVISO"][0]
        self.assertIn("solo de Mac", aviso)
        self.assertIn("magick", aviso)

    def test_chrome_por_variable_de_entorno(self):
        r = ce.chequear("Linux", existe=lambda p: p == "/opt/chrome", que=lambda n: None, version=(3, 11, 0), entorno={"CHROME_BIN": "/opt/chrome"})
        self.assertIn("/opt/chrome", [m for e, m in r if e == "OK"][1])

    def test_por_linea_de_comandos(self):
        cod, out = correr("chequear_entorno.py")
        self.assertIn("Python", out)
        self.assertIn(cod, (0, 1))


if __name__ == "__main__":
    unittest.main()
