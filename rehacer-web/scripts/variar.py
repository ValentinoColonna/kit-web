#!/usr/bin/env python3
# Kit rehacer-web · Valentino Colonna (@valentino.ia) · Licencia MIT · https://github.com/ValentinoColonna/kit-web
"""Sortea una variación (paleta + factores) para que dos webs del mismo esqueleto no salgan iguales.

Uso:
    python3 variar.py --esqueleto aire --rubro "veterinaria"
    python3 variar.py --esqueleto pulso --rubro gimnasio --semilla 7
    python3 variar.py --chequear          # contraste de todas las paletas (4,5:1)

Lee la última web de webs/ (su brief.md, la línea «variar: …») y no repite su combinación.
Imprime: las líneas para el brief, los atributos de <body> (slot {{VARIACION}}),
la línea :root (slot {{PALETA_ROOT}}) y los valores de los slots de color del esqueleto.
Solo Python 3.
"""
import argparse
import glob
import json
import os
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PALETAS = os.path.join(AQUI, '..', 'references', 'paletas.json')
WEBS = os.path.join(AQUI, '..', '..', 'webs')

ALIAS = {'noche': 'espectaculo', 'espectáculo': 'espectaculo'}
OSCUROS = {'espectaculo', 'pulso'}
# Variantes de hero que no rompen la animación de cada esqueleto
HERO = {'aire': ['izq', 'centro', 'partido'], 'espectaculo': ['izq', 'centro', 'fondo'],
        'mantel': ['izq', 'centro'], 'pulso': ['izq'], 'vidriera': ['izq', 'centro']}
FACTORES = {'btn': ['pildora', 'recto', 'corte', 'subrayado', 'grueso'],
            'esq': ['0', 'chica', 'grande'],
            'marco': ['recto', 'arco', 'circulo', 'diagonal', 'organico'],
            'sep': ['recto', 'ola', 'diagonal', 'zigzag']}
NOMBRES = {'pildora': 'píldora', 'corte': 'esquina cortada', 'grueso': 'borde grueso', 'circulo': 'círculo',
           'organico': 'orgánico', 'izq': 'a la izquierda', 'fijo': 'fijo abajo en el celular',
           'partido': 'pantalla partida', 'fondo': 'foto de fondo', '0': 'sin curva'}


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def mezclar(a, b, t):
    a, b = hex_rgb(a), hex_rgb(b)
    return rgb_hex([x + (y - x) * t for x, y in zip(a, b)])


def lum(h):
    def canal(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(v) for v in hex_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def oscura(p):
    return lum(p['fondo']) < 0.2


def sobre_acento(acc):
    """Texto de botón sobre el acento: casi blanco o casi negro teñido del acento; si no llega, puro."""
    claro, oscuro = mezclar(acc, '#ffffff', .92), mezclar(acc, '#000000', .85)
    mejor = max((claro, oscuro), key=lambda c: contraste(c, acc))
    if contraste(mejor, acc) >= 4.5:
        return mejor
    return max(('#ffffff', '#000000'), key=lambda c: contraste(c, acc))


def chequear(paletas):
    malas = 0
    for p in paletas:
        t = contraste(p['texto'], p['fondo'])
        s = contraste(p['texto'], p['superficie'])
        b = contraste(sobre_acento(p['acento']), p['acento'])
        ok = min(t, s, b) >= 4.5
        malas += not ok
        print('%s %-22s texto/fondo %5.2f  texto/superficie %5.2f  botón/acento %5.2f' % (
            'ok ' if ok else 'MAL', p['id'], t, s, b))
    print('\n%d paletas, %d no llegan a 4,5:1' % (len(paletas), malas))
    return malas == 0


def ultima_combinacion():
    briefs = glob.glob(os.path.join(WEBS, '*', 'brief.md'))
    if not briefs:
        return None, None
    ultimo = max(briefs, key=os.path.getmtime)
    for linea in open(ultimo, encoding='utf-8'):
        if 'variar:' in linea:
            combo = dict(par.split('=', 1) for par in linea.split('variar:', 1)[1].strip(' `\n').split('|') if '=' in par)
            return ultimo, combo
    return ultimo, None


def sortear(esqueleto, rubro, paletas, previa, rnd):
    aptas = [p for p in paletas if oscura(p) == (esqueleto in OSCUROS)]
    rubro = (rubro or '').lower()
    del_rubro = [p for p in aptas if any(r in rubro or rubro in r for r in p['rubros'])] if rubro else []
    for _ in range(200):
        # mitad de las veces una del rubro (si hay), mitad cualquiera apta: variedad sin perder sentido
        pool = del_rubro if del_rubro and rnd.random() < .5 else aptas
        c = {'pal': rnd.choice(pool)['id']}
        for k, v in FACTORES.items():
            c[k] = rnd.choice(v)
        c['hero'] = rnd.choice(HERO[esqueleto])
        c['cta'] = rnd.choice(['centro', 'fijo']) if c['hero'] == 'centro' else rnd.choice(['izq', 'fijo'])
        if not previa:
            return c
        distintos = sum(c.get(k) != previa.get(k) for k in ('btn', 'esq', 'marco', 'sep', 'hero', 'cta'))
        if c['pal'] != previa.get('pal') and distintos >= 3:
            return c
    return c


def salida(esqueleto, c, p):
    osc = esqueleto in OSCUROS
    acc, ink, bg = p['acento'], p['texto'], p['fondo']
    fondo2 = p['superficie'] if osc else mezclar(bg, ink, .06)
    raiz = '--ink:%s;--ink-rgb:%s;--ink2:%s;--muted:%s' % (
        ink, ','.join(map(str, hex_rgb(ink))), mezclar(ink, bg, .28), mezclar(ink, bg, .45))
    if not osc:
        raiz += ';--blanco:%s;--blanco-rgb:%s;--papel:%s' % (
            p['superficie'], ','.join(map(str, hex_rgb(p['superficie']))), p['superficie'])
    combo = 'esqueleto=%s|' % esqueleto + '|'.join('%s=%s' % (k, c[k]) for k in ('pal', 'btn', 'cta', 'esq', 'marco', 'sep', 'hero'))
    n = lambda v: NOMBRES.get(v, v)
    print('== Para el brief (ronda 2: esta es la opción recomendada) ==')
    print('- **Variación:** paleta «%s» (%s) · botones %s, %s · esquinas %s · fotos %s · separador %s · hero %s' % (
        p['nombre'], p['tipo'], n(c['btn']), n(c['cta']), n(c['esq']), n(c['marco']), n(c['sep']), n(c['hero'])))
    print('- `variar: %s`' % combo)
    print('\n== <body> (slot {{VARIACION}}) ==')
    print(' '.join('data-%s="%s"' % (k, c[k]) for k in ('btn', 'cta', 'esq', 'marco', 'sep', 'hero')))
    print('\n== :root (slot {{PALETA_ROOT}}) ==')
    print(raiz)
    print('\n== Slots de color del esqueleto ==')
    for k, v in (('FONDO', bg), ('FONDO_RGB', ','.join(map(str, hex_rgb(bg)))), ('FONDO2', fondo2),
                 ('ACENTO', acc), ('ACENTO_RGB', ','.join(map(str, hex_rgb(acc)))),
                 ('ACENTO_CLARO', mezclar(acc, '#ffffff', .35)), ('TEXTO_SOBRE_ACENTO', sobre_acento(acc)),
                 ('SECUNDARIO', p['acento2']), ('SECUNDARIO_RGB', ','.join(map(str, hex_rgb(p['acento2']))))):
        print('%s: %s' % (k, v))


def main():
    ap = argparse.ArgumentParser(description='Sortea paleta y factores para un esqueleto.')
    ap.add_argument('--esqueleto', help='aire, noche (espectaculo), mantel, pulso o vidriera')
    ap.add_argument('--rubro', default='')
    ap.add_argument('--semilla', type=int)
    ap.add_argument('--chequear', action='store_true', help='chequea el contraste de todas las paletas')
    a = ap.parse_args()
    paletas = json.load(open(PALETAS, encoding='utf-8'))['paletas']
    if a.chequear:
        sys.exit(0 if chequear(paletas) else 1)
    esq = ALIAS.get((a.esqueleto or '').lower(), (a.esqueleto or '').lower())
    if esq not in HERO:
        ap.error('--esqueleto tiene que ser uno de: aire, noche, mantel, pulso, vidriera')
    brief, previa = ultima_combinacion()
    if previa:
        print('(No repite la de %s)\n' % os.path.relpath(brief))
    c = sortear(esq, a.rubro, paletas, previa, random.Random(a.semilla))
    salida(esq, c, next(p for p in paletas if p['id'] == c['pal']))


if __name__ == '__main__':
    main()
