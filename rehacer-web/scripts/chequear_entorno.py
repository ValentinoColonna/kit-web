#!/usr/bin/env python3
# Kit rehacer-web · Valentino Colonna (@valentino.ia) · Licencia MIT · https://github.com/ValentinoColonna/kit-web
"""Chequeo inicial del entorno: Python, Google Chrome (para las capturas de revisión) y el redimensionado de fotos.

Uso:
    python3 chequear_entorno.py        (en Windows, `python chequear_entorno.py`)

Imprime una línea por cosa: OK, FALTA (con qué hacer) o AVISO. Sale con 0 si no falta nada imprescindible.
Solo Python 3.
"""
import os
import platform
import shutil
import sys

CHROME_RUTAS = {
    "Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
    "Windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
    "Linux": [],
}
CHROME_NOMBRES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]


def chequear(sistema=None, existe=os.path.exists, que=shutil.which, version=None, entorno=None):
    sistema = sistema or platform.system()
    version = version or sys.version_info
    entorno = os.environ if entorno is None else entorno
    r = []
    if version >= (3, 8):
        r.append(("OK", "Python %d.%d.%d" % tuple(version[:3])))
    else:
        r.append(("FALTA", "Python 3.8 o más nuevo. Mac: instalá las herramientas de Apple (escribí xcode-select --install en la Terminal) o bajá Python de https://www.python.org/downloads/. Windows: bajá Python de python.org y marcá «Add python.exe to PATH»."))
    chrome = entorno.get("CHROME_BIN") if entorno.get("CHROME_BIN") and existe(entorno.get("CHROME_BIN")) else None
    for ruta in CHROME_RUTAS.get(sistema, []):
        chrome = chrome or (ruta if existe(ruta) else None)
    for nombre in CHROME_NOMBRES:
        chrome = chrome or que(nombre)
    if chrome:
        r.append(("OK", "Google Chrome: " + chrome))
    else:
        r.append(("FALTA", "Google Chrome. Instalalo gratis desde https://www.google.com/chrome/ y volvé a correr este chequeo. Sin Chrome el kit funciona, pero no se pueden sacar las capturas de revisión: habría que abrir index.html a mano y mirar la página en el navegador."))
    if sistema == "Darwin":
        r.append(("OK" if que("sips") else "AVISO", "sips (achicar fotos): viene con la Mac" if que("sips") else "No se encontró sips; las fotos hay que achicarlas a mano"))
    else:
        r.append(("AVISO", "sips (achicar fotos) es solo de Mac. En Windows o Linux: abrí cada foto en Fotos/Paint/GIMP, achicala a 1600 px de ancho como máximo y guardala como JPG; o, si tenés ImageMagick: magick foto.jpg -resize 1600x -quality 80 salida.jpg"))
    return r


def main():
    r = chequear()
    for estado, msg in r:
        print(f"{estado:5s}  {msg}")
    falta = [m for e, m in r if e == "FALTA"]
    print("\n" + ("LISTO: el entorno tiene lo necesario." if not falta else "Falta instalar algo (ver arriba)."))
    sys.exit(1 if falta else 0)


if __name__ == "__main__":
    main()
