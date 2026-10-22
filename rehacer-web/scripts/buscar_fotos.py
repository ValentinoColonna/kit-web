#!/usr/bin/env python3
# Kit rehacer-web · Valentino Colonna (@valentino.ia) · Licencia MIT · https://github.com/ValentinoColonna/kit-web
"""Busca las fotos que el negocio ya publicó en su propia web y las deja para elegir.

Uso:
    python3 buscar_fotos.py https://la-web-vieja.com --salida webs/<negocio>/fotos-candidatas [--max-paginas 15] [--max-fotos 80]

Recorre la portada y las páginas del mismo sitio que suelen tener fotos (galería, productos, unidades,
carta, servicios, nosotros) y sus fichas. Toma las imágenes de las etiquetas <img>, de los srcset, de og:image
y de las rutas que aparecen en el código de la página (muchas galerías cargan las fotos por JavaScript).
Descarta íconos, flechas, miniaturas chicas y repetidas; separa el logo. Deja en la carpeta de salida:
  - las fotos numeradas (NN-<página>.jpg),
  - candidatas.json (de qué página sale cada una, su tamaño y su texto alternativo),
  - index.html (hoja de contactos para mirarlas todas juntas).
No elige ninguna: elegir es mirar cada foto (ver SKILL.md, paso 3).

Baja las fotos que las páginas del negocio muestran. Las que están en el propio sitio (o sus subdominios) van
marcadas «propio»; las que vienen de otro host (un CDN, un servicio de fotos) van marcadas «externo» y hay que
confirmar que sean del negocio antes de usarlas. No toca Google Maps, Instagram ni buscadores: Google no permite
descargar y volver a publicar las fotos de Maps (y muchas las suben clientes, no el negocio), e Instagram
bloquea las descargas automáticas. Esas fotos las pasa el dueño.
Límites de seguridad: solo http y https; nunca direcciones internas (localhost, 127.x, 10.x, 192.168.x, 169.254.x, etc.),
tampoco después de una redirección; un presupuesto global de solicitudes y de tiempo (--max-solicitudes, --max-segundos).
No protege contra un DNS que cambie de respuesta entre la comprobación y la descarga.
Solo Python 3, sin dependencias. Una página o una foto por vez, con pausa, y con tope de páginas y fotos.
"""
import argparse
import hashlib
import html
import ipaddress
import json
import os
import re
import socket
import ssl
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
CLAVES = r"galer|imagen|foto|nosotros|quienes|local|sucursal|equipo|instalacion|auto|camion|moto|vehicul|unidad|producto|catalog|stock|tienda|carta|menu|plato|servicio|trabajo|obra|proyecto|portfolio|tratamiento|especialidad"
SALTAR = r"login|ingres|registr|carrito|cart|checkout|politica|privacidad|terminos|wp-admin|feed|\.pdf$|\.zip$"
UI = r"icon|arrow|flecha|loading|spinner|sprite|favicon|btn|boton|button|blank|pixel|spacer|placeholder|whatsapp|facebook|instagram|twitter|tiktok|youtube|linkedin|mercadopago|visa|master|payment|badge|sello-afip|data-fiscal|flag"
EXT = r"\.(?:jpe?g|png|webp)(?:\?[^\"'()\s<>]*)?"


def resolver(host):
    """Direcciones IP de un nombre (se reemplaza en las pruebas)."""
    try:
        return [i[4][0] for i in socket.getaddrinfo(host, None)]
    except OSError:
        return []


def _publica(ip):
    a = ipaddress.ip_address(str(ip).split("%")[0])
    if getattr(a, "ipv4_mapped", None):
        a = a.ipv4_mapped
    return a.is_global


def destino_permitido(url):
    """Solo http(s) hacia direcciones públicas. Localhost, redes privadas, link-local y reservadas se rechazan."""
    p = urllib.parse.urlparse(url.strip())
    host = (p.hostname or "").lower()
    if p.scheme not in ("http", "https") or not host:
        return False
    try:
        ips = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            ips = [ipaddress.ip_address(socket.inet_ntoa(socket.inet_aton(host)))]  # 127.1, 2130706433…
        except OSError:
            ips = [ipaddress.ip_address(i.split("%")[0]) for i in resolver(host)]
    if not ips:
        return False
    if os.environ.get("REHACER_PERMITIR_LOCAL") == "1" and all(i.is_loopback for i in ips):
        return True  # solo para las pruebas del kit con un servidor ficticio en localhost
    return all(_publica(i) for i in ips)


def origen(url, host_negocio):
    """«propio» si la foto está en el sitio del negocio (o un subdominio suyo); «externo» si viene de otro host (un CDN, por ejemplo)."""
    h = (urllib.parse.urlparse(url).hostname or "").lower()
    n = host_negocio.lower()
    h, n = (h[4:] if h.startswith("www.") else h), (n[4:] if n.startswith("www.") else n)
    return "propio" if h == n or h.endswith("." + n) else "externo"


class Presupuesto:
    """Tope global de solicitudes y de tiempo para toda la corrida."""
    def __init__(self, max_solicitudes=150, max_segundos=120, reloj=time.monotonic):
        self.max_solicitudes, self.max_segundos, self.reloj = max_solicitudes, max_segundos, reloj
        self.inicio, self.usadas, self.agotado = reloj(), 0, False

    def permitir(self):
        if self.usadas >= self.max_solicitudes or self.reloj() - self.inicio > self.max_segundos:
            self.agotado = True
            return False
        self.usadas += 1
        return True

    def segundos_restantes(self):
        return max(1.0, self.max_segundos - (self.reloj() - self.inicio))


class ManejadorRedirecciones(urllib.request.HTTPRedirectHandler):
    """Cada salto de una redirección tiene que pasar la misma comprobación que la URL original."""
    max_redirections = 5

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        destino = urllib.parse.urljoin(req.full_url, newurl)
        if not destino_permitido(destino):
            raise urllib.error.URLError("redirección a un destino no permitido: " + destino)
        return super().redirect_request(req, fp, code, msg, headers, destino)


PRESUPUESTO = Presupuesto()
_OPENER = urllib.request.build_opener(ManejadorRedirecciones(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))


def bajar(url, binario=False):
    if not destino_permitido(url) or not PRESUPUESTO.permitir():
        return url, None, b""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-AR,es;q=0.9"})
    try:
        with _OPENER.open(req, timeout=min(20, PRESUPUESTO.segundos_restantes())) as r:
            if not destino_permitido(r.geturl()):
                return url, None, b""
            cuerpo = r.read(8_000_000 if binario else 3_000_000)
            return r.geturl(), r.status, cuerpo
    except Exception:
        return url, None, b""


def medidas(b):
    """Ancho y alto de un JPEG, PNG o WebP leyendo solo la cabecera."""
    try:
        if b[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", b[16:24])
        if b[:2] == b"\xff\xd8":
            i = 2
            while i < len(b) - 9:
                if b[i] != 0xFF:
                    i += 1
                    continue
                marca = b[i + 1]
                if marca in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    alto, ancho = struct.unpack(">HH", b[i + 5:i + 9])
                    return ancho, alto
                largo = struct.unpack(">H", b[i + 2:i + 4])[0]
                i += 2 + largo
        if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
            tipo = b[12:16]
            if tipo == b"VP8 ":
                return struct.unpack("<H", b[26:28])[0] & 0x3FFF, struct.unpack("<H", b[28:30])[0] & 0x3FFF
            if tipo == b"VP8L":
                x = struct.unpack("<I", b[21:25])[0]
                return (x & 0x3FFF) + 1, ((x >> 14) & 0x3FFF) + 1
            if tipo == b"VP8X":
                return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    except Exception:
        pass
    return 0, 0


def titulo_de(texto):
    m = re.search(r"<title[^>]*>(.*?)</title>", texto, re.I | re.S)
    t = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else ""
    return re.split(r"\s[-|–]\s", t)[0].strip() if t else ""


def enlaces(texto, base, host):
    out = []
    for m in re.finditer(r"<a\b[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", texto, re.I | re.S):
        href, ancla = m.group(1).strip(), re.sub(r"<[^>]+>", " ", m.group(2))
        url = urllib.parse.urljoin(base, href)
        p = urllib.parse.urlparse(url)
        if p.scheme not in ("http", "https") or p.netloc.replace("www.", "") != host or re.search(SALTAR, url, re.I):
            continue
        puntos = 0
        if re.search(CLAVES, url + " " + ancla, re.I):
            puntos += 2
        if re.search(r"m[aá]s|ver|detalle|ficha", ancla, re.I) or re.search(r"/[^/]*-[^/]*/\d+|\d{3,}", p.path):
            puntos += 1
        out.append((puntos, url.split("#")[0]))
    return out


def imagenes(texto, base):
    """Rutas de imágenes en atributos, srcset, og:image, estilos y código."""
    vistas = {}
    for m in re.finditer(r"<img\b[^>]*>", texto, re.I):
        tag = m.group(0)
        alt = re.search(r"\balt=[\"']([^\"']*)[\"']", tag, re.I)
        for attr in ("src", "data-src", "data-lazy-src", "data-original"):
            s = re.search(rf"\b{attr}=[\"']([^\"']+)[\"']", tag, re.I)
            if s:
                vistas.setdefault(urllib.parse.urljoin(base, html.unescape(s.group(1))), html.unescape(alt.group(1)) if alt else "")
        ss = re.search(r"\b(?:data-)?srcset=[\"']([^\"']+)[\"']", tag, re.I)
        if ss:
            for parte in ss.group(1).split(","):
                u = parte.strip().split(" ")[0]
                if u:
                    vistas.setdefault(urllib.parse.urljoin(base, html.unescape(u)), html.unescape(alt.group(1)) if alt else "")
    for m in re.finditer(r"<meta[^>]+(?:property|name)=[\"']og:image[\"'][^>]*content=[\"']([^\"']+)", texto, re.I):
        vistas.setdefault(urllib.parse.urljoin(base, m.group(1)), "og:image")
    for m in re.finditer(rf"[\"'(]([^\"'()\s<>]+?{EXT})", texto, re.I):
        vistas.setdefault(urllib.parse.urljoin(base, html.unescape(m.group(1)).replace("\\/", "/")), "")
    return vistas


def slug(t, n=30):
    t = re.sub(r"[^a-z0-9]+", "-", t.lower().encode("ascii", "ignore").decode())
    return t.strip("-")[:n] or "pagina"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", help="link de la web del negocio")
    ap.add_argument("--salida", required=True, help="carpeta donde dejar las candidatas, por ejemplo webs/<negocio>/fotos-candidatas")
    ap.add_argument("--max-paginas", type=int, default=15)
    ap.add_argument("--max-fotos", type=int, default=80)
    ap.add_argument("--max-solicitudes", type=int, default=150, help="tope global de solicitudes HTTP de toda la corrida")
    ap.add_argument("--max-segundos", type=int, default=120, help="tope global de segundos de toda la corrida")
    ap.add_argument("--min-ancho", type=int, default=400, help="lado mayor mínimo para candidata; las de 300 a este valor van a chicas/ (píxeles)")
    a = ap.parse_args()

    global PRESUPUESTO
    PRESUPUESTO = Presupuesto(a.max_solicitudes, a.max_segundos)
    inicio = a.url if re.match(r"^https?://", a.url) else "https://" + a.url
    final, status, cuerpo = bajar(inicio)
    if not cuerpo:
        print(f"ERROR  No se pudo abrir {inicio} (o es una dirección no permitida: solo sitios públicos por http/https)")
        sys.exit(1)
    host = urllib.parse.urlparse(final).netloc.replace("www.", "")
    host_negocio = (urllib.parse.urlparse(final).hostname or host)
    cola, visitadas, paginas = [(9, final)], set(), []
    while cola and len(paginas) < a.max_paginas:
        cola.sort(key=lambda x: -x[0])
        _, url = cola.pop(0)
        if url in visitadas:
            continue
        visitadas.add(url)
        if url == final:
            texto = cuerpo.decode("utf-8", "ignore")
        else:
            time.sleep(0.4)
            u2, st, c = bajar(url)
            if not c:
                continue
            texto = c.decode("utf-8", "ignore")
        paginas.append((url, titulo_de(texto), texto))
        for puntos, u in enlaces(texto, url, host):
            if u not in visitadas and puntos > 0:
                cola.append((puntos, u))

    candidatas, vistas = [], set()
    for url, titulo, texto in paginas:
        for img, alt in imagenes(texto, url).items():
            if img in vistas:
                continue
            vistas.add(img)
            nombre = urllib.parse.urlparse(img).path.rsplit("/", 1)[-1].lower()
            if re.search(UI, nombre):
                continue
            candidatas.append({"url": img, "pagina": url, "titulo_pagina": titulo, "alt": alt, "logo": "logo" in nombre})

    os.makedirs(a.salida, exist_ok=True)
    guardadas, hashes, descartes = [], {}, {"chicas": 0, "repetidas": 0, "fallidas": 0, "bloqueadas": 0}
    for c in candidatas:
        if len(guardadas) >= a.max_fotos or PRESUPUESTO.agotado:
            break
        c["origen"] = origen(c["url"], host_negocio)
        if not destino_permitido(c["url"]):
            descartes["bloqueadas"] += 1
            continue
        time.sleep(0.2)
        _, st, b = bajar(c["url"], binario=True)
        if not b:
            descartes["fallidas"] += 1
            continue
        ancho, alto = medidas(b)
        mayor, menor = max(ancho, alto), min(ancho, alto)
        chica = not c["logo"] and (mayor < a.min_ancho or menor < 200)
        if chica and (mayor < 300 or menor < 180):
            descartes["chicas"] += 1
            continue
        h = hashlib.sha1(b).hexdigest()
        if h in hashes:
            descartes["repetidas"] += 1
            continue
        hashes[h] = True
        ext = ".png" if b[:4] == b"\x89PNG" else ".webp" if b[:4] == b"RIFF" else ".jpg"
        n = len(guardadas) + 1
        archivo = ("logo" if c["logo"] else f"{n:02d}-{slug(c['titulo_pagina'])}") + ext
        if c["logo"] and os.path.exists(os.path.join(a.salida, archivo)):
            archivo = f"logo-{n:02d}{ext}"
        if chica:
            os.makedirs(os.path.join(a.salida, "chicas"), exist_ok=True)
            archivo = "chicas/" + archivo
        with open(os.path.join(a.salida, archivo), "wb") as f:
            f.write(b)
        guardadas.append({**c, "archivo": archivo, "ancho": ancho, "alto": alto, "kb": round(len(b) / 1024), "chica": chica})

    with open(os.path.join(a.salida, "candidatas.json"), "w", encoding="utf-8") as f:
        json.dump({"web": final, "paginas_leidas": [p[0] for p in paginas], "fotos": guardadas, "descartes": descartes,
                   "solicitudes": PRESUPUESTO.usadas, "presupuesto_agotado": PRESUPUESTO.agotado}, f, ensure_ascii=False, indent=1)
    def celdas_de(fotos):
        return "".join(
        f'<figure><img src="{html.escape(g["archivo"])}" loading="lazy"><figcaption><b>{html.escape(g["archivo"])}</b> · {g["ancho"]}×{g["alto"]} · {g["kb"]} KB · {"propio" if g["origen"] == "propio" else "EXTERNO: " + html.escape(urllib.parse.urlparse(g["url"]).hostname or "?")}<br>{html.escape(g["titulo_pagina"][:60])}{(" · alt: " + html.escape(g["alt"][:50])) if g["alt"] else ""}</figcaption></figure>'
            for g in fotos)
    celdas = celdas_de([g for g in guardadas if not g["chica"]])
    chicas = [g for g in guardadas if g["chica"]]
    if chicas:
        celdas += f'</main><h2>Chicas (menos de {a.min_ancho} px): solo para una tarjeta, si no hay otra</h2><main>' + celdas_de(chicas)
    with open(os.path.join(a.salida, "index.html"), "w", encoding="utf-8") as f:
        f.write(f'<!doctype html><meta charset="utf-8"><title>Fotos candidatas</title><style>body{{margin:0;padding:16px;background:#111;color:#eee;font:13px/1.4 system-ui}}main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}}figure{{margin:0;background:#1c1c1c;border-radius:8px;overflow:hidden}}img{{width:100%;height:170px;object-fit:cover;display:block}}figcaption{{padding:8px}}</style><h1>Fotos de {html.escape(final)}</h1><p>{len(guardadas)} candidatas de {len(paginas)} páginas. Elegir es mirar cada una.</p><main>{celdas}</main>')

    n_chicas = sum(1 for g in guardadas if g["chica"])
    print(f"LISTO  {len(guardadas) - n_chicas} fotos candidatas y {n_chicas} chicas (en chicas/) de {len(paginas)} páginas en {a.salida}/")
    print(f"       Descartadas: {descartes['chicas']} miniaturas, {descartes['repetidas']} repetidas, {descartes['fallidas']} que no bajaron, {descartes['bloqueadas']} bloqueadas (dirección no permitida)")
    externas = [g for g in guardadas if g["origen"] == "externo"]
    print(f"       Origen: {len(guardadas) - len(externas)} del sitio del negocio, {len(externas)} de otros hosts" + (" (" + ", ".join(sorted({urllib.parse.urlparse(g['url']).hostname for g in externas})[:4]) + "): confirmar que sean del negocio" if externas else ""))
    print(f"       Solicitudes: {PRESUPUESTO.usadas} de {a.max_solicitudes} permitidas")
    if PRESUPUESTO.agotado:
        print("AVISO  Se agotó el presupuesto de solicitudes o de tiempo: el resultado es parcial. Si hace falta más, volvé a correrlo con --max-solicitudes o --max-segundos más altos.")
    for g in guardadas:
        print(f"  {g['archivo']:34s} {g['ancho']:>5}×{g['alto']:<5} {g['titulo_pagina'][:50]}")
    print("Hoja de contactos: index.html. Ahora hay que mirarlas una por una antes de usar ninguna.")


if __name__ == "__main__":
    main()
