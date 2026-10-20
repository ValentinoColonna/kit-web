#!/usr/bin/env python3
# Kit rehacer-web · Valentino Colonna (@valentino.ia) · Licencia MIT · https://github.com/ValentinoColonna/kit-web
"""Mide una URL con PageSpeed Insights (celular) y guarda los cuatro puntajes.

Uso:
    python3 medir_pagespeed.py https://la-web.com [--clave TU_CLAVE] [--etiqueta antes]

Sin clave, la API pública compartida suele responder «429 quota exceeded»: en ese caso imprime la URL de
https://pagespeed.web.dev para medir a mano y sacar captura. La clave es gratis: Google Cloud → APIs y servicios →
habilitar «PageSpeed Insights API» → Credenciales → Clave de API. También se puede pasar por la variable PSI_KEY.
Escribe medicion-<etiqueta>.json y una línea en mediciones.md. Solo Python 3.
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--clave", default=os.environ.get("PSI_KEY", ""))
    ap.add_argument("--etiqueta", default="medicion")
    a = ap.parse_args()
    q = {"url": a.url, "strategy": "mobile"}
    if a.clave:
        q["key"] = a.clave
    api = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + urllib.parse.urlencode(q) + "&category=performance&category=seo&category=accessibility&category=best-practices"
    manual = "https://pagespeed.web.dev/analysis?url=" + urllib.parse.quote(a.url, safe="")
    try:
        with urllib.request.urlopen(api, timeout=90) as r:
            d = json.load(r)
    except Exception as e:
        print(f"No se pudo medir por API ({e}).")
        print(f"Medí a mano acá y sacá captura: {manual}")
        sys.exit(1)
    if "error" in d:
        print("API:", d["error"].get("message"))
        print(f"Medí a mano acá y sacá captura: {manual}")
        sys.exit(1)
    lr = d["lighthouseResult"]
    cats = {k: round((v.get("score") or 0) * 100) for k, v in lr["categories"].items()}
    au = lr["audits"]
    fila = {
        "etiqueta": a.etiqueta, "url": a.url, "fecha": time.strftime("%Y-%m-%d %H:%M"),
        "rendimiento": cats.get("performance"), "accesibilidad": cats.get("accessibility"),
        "buenas_practicas": cats.get("best-practices"), "seo": cats.get("seo"),
        "LCP": au.get("largest-contentful-paint", {}).get("displayValue"),
        "CLS": au.get("cumulative-layout-shift", {}).get("displayValue"),
        "TBT": au.get("total-blocking-time", {}).get("displayValue"),
        "lighthouse": lr.get("lighthouseVersion"),
    }
    with open(f"medicion-{a.etiqueta}.json", "w", encoding="utf-8") as f:
        json.dump(fila, f, ensure_ascii=False, indent=2)
    nuevo = not os.path.exists("mediciones.md")
    with open("mediciones.md", "a", encoding="utf-8") as f:
        if nuevo:
            f.write("| Etiqueta | URL | Fecha | Rendimiento | Accesibilidad | Buenas prácticas | SEO | LCP | CLS |\n|---|---|---|---|---|---|---|---|---|\n")
        f.write(f"| {fila['etiqueta']} | {fila['url']} | {fila['fecha']} | {fila['rendimiento']} | {fila['accesibilidad']} | {fila['buenas_practicas']} | {fila['seo']} | {fila['LCP']} | {fila['CLS']} |\n")
    print(json.dumps(fila, ensure_ascii=False, indent=2))
    print(f"\nLISTO  medicion-{a.etiqueta}.json y una fila en mediciones.md · captura para el video: {manual}")


if __name__ == "__main__":
    main()
