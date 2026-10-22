#!/usr/bin/env python3
# Kit rehacer-web · Valentino Colonna (@valentino.ia) · Licencia MIT · https://github.com/ValentinoColonna/kit-web
"""Valida el index.html nuevo antes de publicarlo.

Uso:
    python3 validar_sitio.py index.html [--borrador]

--borrador: los placeholders [ASÍ] son avisos, no errores (para validar antes de tener todos los datos). Sin el flag, bloquean: no se publica con placeholders.
--muestra: es una muestra para ofrecer al dueño: exige <meta name="robots" content="noindex">. Sin el flag, si la página tiene noindex, avisa (la versión definitiva no lo lleva).

Errores (hay que corregir): sin viewport, sin título o fuera de medida, sin descripción o fuera de medida,
H1 distinto de uno, sin enlace de WhatsApp real (el host tiene que ser wa.me o api.whatsapp.com, con número),
sin enlace tel: con número, imágenes sin alt, JSON-LD de LocalBusiness sin name, address, telephone u horarios,
scripts o hojas de estilo externas fuera de la lista (se compara el host real, no un trozo de texto de la URL;
«//host» también es externa), sin lang, slots {{...}} del esqueleto sin completar, placeholders ([TELÉFONO],
[telefono pendiente], PENDIENTE, COMPLETAR, XXXX, lorem ipsum…) en el texto, atributos o JSON-LD, y horarios
dinámicos (data-abre) sin zona horaria del negocio (data-tz="America/Argentina/Buenos_Aires").
Los slots se buscan fuera de los comentarios HTML.
Avisos: textos que suenan a inventados («líderes», «premiados», «+N clientes», «N años de experiencia» sin dato
del brief), enlaces vacíos (#), imágenes que no existen en la carpeta.
Sale con 0 si pasa y 1 si hay errores. PASAR NO ES ESTAR LISTA: son comprobaciones automáticas sobre el HTML.
Al final imprime lo que hay que revisar a mano. Solo Python 3.
"""
import json
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser

try:
    import zoneinfo
except ImportError:  # Python < 3.9
    zoneinfo = None

# Subtipos de LocalBusiness de schema.org que usan los negocios chicos (además de cualquier «…Store»)
SUBTIPOS = {
    "Restaurant", "FoodEstablishment", "CafeOrCoffeeShop", "Bakery", "BarOrPub", "IceCreamShop", "FastFoodRestaurant", "Brewery", "Winery",
    "Dentist", "MedicalBusiness", "MedicalClinic", "Physician", "Optician", "Pharmacy", "Physiotherapy", "VeterinaryCare",
    "HealthAndBeautyBusiness", "HairSalon", "BeautySalon", "DaySpa", "NailSalon", "TattooParlor", "ExerciseGym", "HealthClub",
    "SportsActivityLocation", "SportsClub", "AutoDealer", "AutoRepair", "AutomotiveBusiness", "AutoBodyShop", "AutoPartsStore",
    "ProfessionalService", "AccountingService", "LegalService", "Attorney", "Notary", "RealEstateAgent", "InsuranceAgency",
    "HomeAndConstructionBusiness", "Electrician", "Plumber", "HVACBusiness", "GeneralContractor", "HousePainter", "Locksmith",
    "Store", "Florist", "ChildCare", "Library", "TravelAgency", "LodgingBusiness", "Hotel", "BedAndBreakfast", "Campground",
}

# Lo único externo que se acepta, comparado por HOST REAL (y prefijo de ruta), nunca por un trozo de texto de la URL.
SCRIPTS_OK = {"cdnjs.cloudflare.com": "/ajax/libs/gsap/", "cdn.jsdelivr.net": "/npm/gsap", "unpkg.com": "/gsap"}
CSS_OK = {"fonts.googleapis.com": "/"}
PLACEHOLDERS = [
    r"\[[^\[\]\n]{2,60}\]",                      # [TELÉFONO], [Teléfono], [telefono pendiente], [ completar acá ]
    r"\b(?:PENDIENTE|COMPLETAR|XXX+|TBD)\b",       # PENDIENTE-A-CONFIRMAR, COMPLETAR, XXXX
    r"\bA CONFIRMAR\b",
    r"\bTODO\b(?=\s*(?:[:\-–|]|$))",
    r"(?i:lorem ipsum|dolor sit amet)",
]


def destino(url):
    """('host', 'ruta') si la URL sale de la carpeta; None si es relativa y local. Entiende «//host» y «/\\host» como externas."""
    u = re.sub(r"[\t\r\n]", "", url.strip()).replace("\\", "/")
    if u.startswith("//"):
        u = "https:" + u
    p = urllib.parse.urlparse(u)
    if p.scheme in ("http", "https"):
        return (p.hostname or "").lower(), p.path or "/"
    if p.scheme or p.netloc:
        return "?" + p.scheme, u  # data:, javascript:, blob:… no se aceptan como recurso
    return None


def permitido(url, lista):
    d = destino(url)
    return d is not None and d[0] in lista and d[1].startswith(lista[d[0]])


def es_whatsapp(url):
    """Enlace de WhatsApp real: host wa.me (número en la ruta) o api.whatsapp.com/send (phone=número)."""
    d = destino(url)
    if not d or url.strip().lower().startswith(("//", "/")):
        return False
    p = urllib.parse.urlparse(re.sub(r"[\t\r\n]", "", url.strip()))
    if p.scheme not in ("http", "https") or p.username or p.password:
        return False
    host = (p.hostname or "").lower()
    if host == "wa.me":
        return bool(re.fullmatch(r"/\d{8,15}/?", p.path))
    if host == "api.whatsapp.com":
        tel = urllib.parse.parse_qs(p.query).get("phone", [""])[0]
        return p.path.rstrip("/") == "/send" and bool(re.fullmatch(r"\d{8,15}", tel))
    return False


def es_tel(url):
    n = urllib.parse.unquote(url.strip()[4:])
    return url.lower().startswith("tel:") and bool(re.fullmatch(r"\+?[\d\s().\-]+", n)) and len(re.sub(r"\D", "", n)) >= 6


def falta_de_ld(o):
    """Campos que faltan en el mejor nodo LocalBusiness del JSON-LD; None si no hay ninguno."""
    nodos = []
    for item in (o if isinstance(o, list) else [o]):
        if isinstance(item, dict):
            nodos.append(item)
            g = item.get("@graph")
            nodos += [n for n in (g if isinstance(g, list) else []) if isinstance(n, dict)]
    mejor = None
    for n in nodos:
        tipos = n.get("@type", "")
        tipos = tipos if isinstance(tipos, list) else [tipos]
        if not any("LocalBusiness" in str(x) or x in SUBTIPOS or str(x).endswith("Store") for x in tipos):
            continue
        def lleno(v):
            if isinstance(v, str):
                return bool(v.strip())
            if isinstance(v, dict):
                return any(lleno(x) for k, x in v.items() if not str(k).startswith("@"))
            if isinstance(v, list):
                return any(lleno(x) for x in v)
            return False
        faltan = [k for k in ("name", "address") if not lleno(n.get(k))]
        if len(re.sub(r"\D", "", str(n.get("telephone", "")))) < 6:
            faltan.append("telephone")
        if not (lleno(n.get("openingHours")) or lleno(n.get("openingHoursSpecification"))):
            faltan.append("openingHours (u openingHoursSpecification)")
        if mejor is None or len(faltan) < len(mejor):
            mejor = faltan
    return mejor


def zona_valida(tz):
    if not re.fullmatch(r"UTC|[A-Za-z_]+(?:/[A-Za-z0-9_+\-]+){1,2}", tz.strip()):
        return False
    if zoneinfo is not None:
        try:
            if zoneinfo.available_timezones():
                return tz.strip() in zoneinfo.available_timezones()
        except Exception:
            pass
    return True


A_MANO = [
    "Mirarla en un celular de verdad (o a 375 px) y en escritorio: textos cortados, fotos, botones.",
    "Tocar cada botón: WhatsApp abre el chat con el número del dueño, «Llamar» marca el teléfono correcto, el mapa abre la dirección.",
    "Confirmar con el dueño cada dato: nombre, dirección, teléfono, horarios, precios, textos y fotos.",
    "Fotos: que sean del negocio o con permiso del dueño (no las de Google Maps ni las de Instagram de terceros).",
    "Si tiene el cartel ABIERTO/CERRADO: probarlo a una hora en que esté abierto y a otra en que esté cerrado.",
    "Después de publicar, repetir los dos primeros pasos con el link público.",
]


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
        self.visible = []   # texto que se ve (sin scripts ni estilos)
        self.attrs_txt = []  # alt, title, aria-label, content, placeholder
        self.css_inline = []
        self._cod = 0
        self._estilo = False
        self.hrefs_css = []
        self.abre = 0
        self.tz = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        if tag in ("script", "style"):
            self._cod += 1
        if tag == "style":
            self._estilo = True
        for k in ("alt", "title", "aria-label", "content", "placeholder"):
            if a.get(k):
                self.attrs_txt.append(a[k])
        if "data-abre" in a:
            self.abre += 1
        if "data-tz" in a:
            self.tz.append(a["data-tz"])
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
        if tag == "link" and a.get("href"):
            rel = set((a.get("rel") or "").lower().split())
            if "stylesheet" in rel or ("preload" in rel and (a.get("as") or "").lower() in ("style", "script")):
                self.hrefs_css.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False
        if tag == "script":
            self._j = False
        if tag in ("script", "style"):
            self._cod = max(0, self._cod - 1)
        if tag == "style":
            self._estilo = False

    def handle_data(self, d):
        if self._estilo:
            self.css_inline.append(d)
        if d.strip() and not self._cod:
            self.visible.append(d.strip())
        if self._t:
            self.title += d
        if self._j:
            self.jsonld.append(d)
        if d.strip():
            self.texto.append(d.strip())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    borrador = "--borrador" in sys.argv
    muestra = "--muestra" in sys.argv
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
    if not any(es_whatsapp(l) for l in p.links):
        errores.append("no hay un enlace de WhatsApp que funcione: tiene que ser https://wa.me/549… (solo dígitos) o https://api.whatsapp.com/send?phone=549…")
    if not any(es_tel(l) for l in p.links):
        errores.append("no hay un teléfono con enlace tel: que tenga número (tel:+54…)")
    sin_alt = [i.get("src", "?") for i in p.imgs if i.get("alt") is None]  # alt="" es válido para imágenes decorativas
    if sin_alt:
        errores.append(f"{len(sin_alt)} imágenes sin alt: {', '.join(sin_alt[:5])}")
    ld_ok, ld_faltan = False, None
    for j in p.jsonld:
        try:
            faltan = falta_de_ld(json.loads(j))
        except Exception:
            avisos.append("hay un JSON-LD que no es JSON válido")
            continue
        if faltan is not None:
            ld_faltan = faltan if ld_faltan is None or len(faltan) < len(ld_faltan) else ld_faltan
            ld_ok = ld_ok or not faltan
    if not ld_ok:
        errores.append("JSON-LD de LocalBusiness " + ("con campos que faltan o están vacíos: " + ", ".join(ld_faltan) if ld_faltan else "ausente (name, address, telephone y openingHours)"))
    elif "url" not in " ".join(p.jsonld):
        avisos.append("el JSON-LD no tiene url: sumala cuando ya conozcas la dirección pública")
    # Lo externo se compara por el host real. Permitido: GSAP/ScrollTrigger (cdnjs, jsdelivr, unpkg) y Google Fonts. Lo demás, error.
    raros = [s_ for s_ in p.scripts_ext if not permitido(s_, SCRIPTS_OK)]
    if raros:
        errores.append(f"scripts no permitidos: {', '.join(raros[:3])} (solo GSAP/ScrollTrigger desde cdnjs.cloudflare.com, cdn.jsdelivr.net o unpkg.com; el host tiene que ser ese)")
    elif p.scripts_ext:
        avisos.append(f"usa {len(p.scripts_ext)} scripts de GSAP por CDN: sin internet las animaciones no corren; la página tiene que verse completa igual")
    css_ext = p.hrefs_css + [m for c in p.css_inline for m in re.findall(r"@import\s+(?:url\()?\s*[\"']?([^\"')\s;]+)", c)]
    css_raros = [c for c in css_ext if destino(c) is not None and not permitido(c, CSS_OK)]
    if css_raros:
        errores.append(f"hojas de estilo externas no permitidas: {', '.join(css_raros[:3])} (solo fonts.googleapis.com)")
    if p.abre and not p.tz:
        errores.append('los horarios con data-abre necesitan la zona horaria del negocio: data-tz="America/Argentina/Buenos_Aires" en el contenedor .horas')
    for tz in p.tz:
        if not zona_valida(tz):
            errores.append(f'zona horaria inválida en data-tz: «{tz}» (formato Continente/Ciudad, p. ej. America/Argentina/Buenos_Aires)')
    robots = p.metas.get("robots", "").lower()
    if muestra and "noindex" not in robots:
        errores.append('es una muestra y no tiene <meta name="robots" content="noindex">: Google podría mostrarla antes de que el dueño diga que sí')
    elif not muestra and "noindex" in robots:
        avisos.append("tiene noindex: Google no la va a mostrar. Si ya es la versión definitiva, sacalo")
    if not p.lang:
        errores.append("falta lang en <html> (por ejemplo lang=\"es-AR\")")
    texto = " ".join(p.texto)
    for patron, msg in [(r"\b(líderes|lideres|el mejor|los mejores|n[úu]mero 1|premiad[oa]s?)\b", "superlativos sin respaldo"), (r"\+\s?\d{2,}\s*(clientes|proyectos|casos)", "cifras de clientes o proyectos"), (r"\d{1,2}\s*años de (experiencia|trayectoria)", "años de experiencia")]:
        m = re.search(patron, texto, re.I)
        if m:
            avisos.append(f"{msg}: «{m.group(0)}» (confirmar que lo dijo el dueño)")
    visible = re.sub(r"<!--.*?-->", "", src, flags=re.S)  # los comentarios no se ven en la página
    slots = re.findall(r"\{\{[^{}]{1,60}", visible)
    if slots:
        errores.append(f"quedan {len(slots)} slots del esqueleto sin completar: {', '.join(sorted(set(s[2:].split(':')[0].strip() for s in slots))[:5])} (completalos o dejalos como [PLACEHOLDER])")
    def textos_json(o):
        if isinstance(o, str):
            return [o]
        if isinstance(o, dict):
            return [t for v in o.values() for t in textos_json(v)]
        if isinstance(o, list):
            return [t for v in o for t in textos_json(v)]
        return []
    en_ld = []
    for j in p.jsonld:
        try:
            en_ld += textos_json(json.loads(j))  # solo los valores de texto: una lista JSON con corchetes no es un placeholder
        except Exception:
            pass
    superficie = " | ".join(p.visible + p.attrs_txt + en_ld)  # lo que se ve, los atributos con texto y los textos del JSON-LD
    placeholders = []
    for patron in PLACEHOLDERS:
        placeholders += [m.group(0) for m in re.finditer(patron, superficie) if patron != PLACEHOLDERS[0] or re.search(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", m.group(0))]
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
    print("PASA: superó las comprobaciones automáticas. Eso no es lo mismo que estar lista: falta revisar a mano")
    for n, paso in enumerate(A_MANO, 1):
        print(f"  {n}. {paso}")


if __name__ == "__main__":
    main()
