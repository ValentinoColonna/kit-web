#!/usr/bin/env python3
# Kit rehacer-web · Valentino Colonna (@valentino.ia) · Licencia MIT · https://github.com/ValentinoColonna/kit-web
"""Valida el index.html nuevo antes de publicarlo.

Uso:
    python3 validar_sitio.py index.html [--borrador]

--borrador: los placeholders [ASÍ] son avisos, no errores (para validar antes de tener todos los datos). Sin el flag, bloquean: no se publica con placeholders.

Errores (hay que corregir): sin viewport, sin título o fuera de medida, sin descripción o fuera de medida,
H1 distinto de uno, sin botón de WhatsApp (wa.me), sin teléfono tel:, imágenes sin alt, sin JSON-LD LocalBusiness,
scripts o hojas de estilo externas (la página tiene que ser autónoma), sin lang.
Avisos: textos que suenan a inventados («líderes», «premiados», «+N clientes», «N años de experiencia» sin dato
del brief), enlaces vacíos (#), imágenes que no existen en la carpeta.
Sale con 0 si pasa y 1 si hay errores. Solo Python 3.
"""
import json
import os
import re
import sys
from html.parser import HTMLParser


class Lector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._t = False
        self.metas = {}
        self.h1 = 0
        self.imgs = []
        self.links = []
        self.scripts_ext = []
        self.css_ext = []
        self.jsonld = []
        self._j = False
        self.lang = None
        self.texto = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self._t = True
        if tag == "meta":
            n = (a.get("name") or a.get("property") or "").lower()
            if n:
                self.metas[n] = a.get("content", "")
        if tag == "h1":
            self.h1 += 1
        if tag == "img":
            self.imgs.append(a)
        if tag == "a":
            self.links.append(a.get("href", ""))
        if tag == "script":
            if a.get("src"):
                self.scripts_ext.append(a["src"])
            elif (a.get("type") or "").lower() == "application/ld+json":
                self._j = True
        if tag == "link" and (a.get("rel") or "").lower() == "stylesheet" and a.get("href", "").startswith("http"):
            self.css_ext.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False
        if tag == "script":
            self._j = False

    def handle_data(self, d):
        if self._t:
            self.title += d
        if self._j:
            self.jsonld.append(d)
        if d.strip():
            self.texto.append(d.strip())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    borrador = "--borrador" in sys.argv
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    ruta = args[0]
    carpeta = os.path.dirname(os.path.abspath(ruta))
    with open(ruta, encoding="utf-8") as f:
        src = f.read()
    p = Lector()
    p.feed(src)
    errores, avisos = [], []
    t = p.title.strip()
    d = p.metas.get("description", "").strip()
    if "viewport" not in p.metas:
        errores.append("falta <meta name=\"viewport\">: no se adapta al celular")
    if not (10 <= len(t) <= 70):
        errores.append(f"título de {len(t)} caracteres (ideal 10 a 70): «{t}»")
    if not (50 <= len(d) <= 170):
        errores.append(f"meta description de {len(d)} caracteres (ideal 50 a 170)")
    if p.h1 != 1:
        errores.append(f"{p.h1} H1; tiene que haber exactamente uno")
    if not any("wa.me" in l or "api.whatsapp.com" in l for l in p.links):
        errores.append("no hay enlace de WhatsApp (https://wa.me/549...)")
    if not any(l.lower().startswith("tel:") for l in p.links):
        errores.append("no hay teléfono con enlace tel:")
    sin_alt = [i.get("src", "?") for i in p.imgs if i.get("alt") is None]  # alt="" es válido para imágenes decorativas
    if sin_alt:
        errores.append(f"{len(sin_alt)} imágenes sin alt: {', '.join(sin_alt[:5])}")
    ld_ok = False
    for j in p.jsonld:
        try:
            o = json.loads(j)
            tipos = []
            for item in (o if isinstance(o, list) else [o]):
                tipos.append(item.get("@type", ""))
            if any("LocalBusiness" in str(x) or x in ("Store", "Restaurant", "Dentist", "AutoDealer", "AutoRepair", "HairSalon", "MedicalBusiness", "ProfessionalService") for x in tipos):
                ld_ok = True
        except Exception:
            avisos.append("hay un JSON-LD que no es JSON válido")
    if not ld_ok:
        errores.append("falta JSON-LD de tipo LocalBusiness (o un subtipo) con name, address, telephone y openingHours")
    # Librerías permitidas (públicas, gratis, con CDN estable): GSAP y ScrollTrigger; fuentes de Google. Cualquier otra, error.
    permitidos = ("cdnjs.cloudflare.com/ajax/libs/gsap/", "cdn.jsdelivr.net/npm/gsap", "unpkg.com/gsap")
    raros = [s for s in p.scripts_ext if not any(k in s for k in permitidos)]
    if raros:
        errores.append(f"scripts externos no permitidos: {', '.join(raros[:3])} (solo GSAP/ScrollTrigger desde cdnjs, jsdelivr o unpkg)")
    elif p.scripts_ext:
        avisos.append(f"usa {len(p.scripts_ext)} scripts de GSAP por CDN: sin internet las animaciones no corren; la página tiene que verse completa igual")
    css_raros = [c for c in p.css_ext if "fonts.googleapis.com" not in c]
    if css_raros:
        errores.append(f"hojas de estilo externas no permitidas: {', '.join(css_raros[:3])} (solo Google Fonts)")
    if not p.lang:
        errores.append("falta lang en <html> (por ejemplo lang=\"es-AR\")")
    texto = " ".join(p.texto)
    for patron, msg in [(r"\b(líderes|lideres|el mejor|los mejores|n[úu]mero 1|premiad[oa]s?)\b", "superlativos sin respaldo"), (r"\+\s?\d{2,}\s*(clientes|proyectos|casos)", "cifras de clientes o proyectos"), (r"\d{1,2}\s*años de (experiencia|trayectoria)", "años de experiencia")]:
        m = re.search(patron, texto, re.I)
        if m:
            avisos.append(f"{msg}: «{m.group(0)}» (confirmar que lo dijo el dueño)")
    placeholders = re.findall(r"\[[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ \-/]{2,}\]|PENDIENTE-A-CONFIRMAR", src)
    if placeholders:
        msg = f"quedan {len(placeholders)} placeholders sin completar: {', '.join(sorted(set(placeholders))[:5])}"
        (avisos if borrador else errores).append(msg + ("" if borrador else " (mientras falten datos, validá con --borrador)"))
    vacios = [l for l in p.links if l in ("#", "", "javascript:void(0)")]
    if vacios:
        avisos.append(f"{len(vacios)} enlaces vacíos (#)")
    for i in p.imgs:
        s = i.get("src", "")
        if s and not s.startswith(("http", "data:")) and not os.path.exists(os.path.join(carpeta, s)):
            avisos.append(f"la imagen {s} no está en la carpeta")
    for a in avisos:
        print(f"AVISO  {a}")
    for e in errores:
        print(f"ERROR  {e}")
    if errores:
        print(f"NO PASA: {len(errores)} error(es)")
        sys.exit(1)
    print("PASA: la página está lista para publicar")


if __name__ == "__main__":
    main()
