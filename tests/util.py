"""Utilidades comunes de las pruebas del kit. Solo biblioteca estándar. Datos 100 % ficticios."""
import importlib.util
import os
import re
import subprocess
import sys
import tempfile

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KIT = os.path.join(RAIZ, "rehacer-web")
SCRIPTS = os.path.join(KIT, "scripts")
PLANTILLA = os.path.join(KIT, "plantilla")
EJEMPLO = os.path.join(KIT, "references", "ejemplo-index.html")


def cargar(nombre):
    """Importa un script de rehacer-web/scripts/ como módulo."""
    spec = importlib.util.spec_from_file_location(nombre, os.path.join(SCRIPTS, nombre + ".py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = m
    spec.loader.exec_module(m)
    return m


def correr(script, *args, cwd=None, env=None, timeout=60):
    e = dict(os.environ)
    e.update(env or {})
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args], capture_output=True, text=True, cwd=cwd, env=e, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def escribir_temp(contenido, nombre="index.html"):
    d = tempfile.mkdtemp(prefix="kitweb-test-")
    ruta = os.path.join(d, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


def buscar_chrome():
    """Un Chrome o chrome-headless-shell para las pruebas de JavaScript; None si no hay."""
    cand = [os.environ.get("CHROME_BIN", "")]
    home = os.path.expanduser("~")
    cand += [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    ]
    base = os.path.join(home, "Movies", "editor-youtube", "motor", "node_modules", ".remotion", "chrome-headless-shell")
    if os.path.isdir(base):
        for raiz, _, archivos in os.walk(base):
            if "chrome-headless-shell" in archivos:
                cand.append(os.path.join(raiz, "chrome-headless-shell"))
    for c in cand:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None
