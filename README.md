# kit-web · Rehacé la web de un negocio con IA

Lo que te llevás del video de Valentino IA, sin pedir nada a cambio. Abrís la carpeta con Claude Code, escribís «hola» y te pide el link de la web vieja del negocio. Con eso audita la web, arma la página nueva con scroll animado en uno de cinco estilos, la valida, la revisa en celular y te la deja lista para publicar gratis.

## Cómo se usa

1. **Code → Download ZIP**, descomprimilo y abrí la carpeta con Claude Code (la app de Claude, pestaña Code, o VS Code con la extensión).
2. Escribí **«hola»** y pasale el link de la web actual. Si no tenés link, dejá el `.html` en `entrada/`; si el negocio no tiene web, decile el nombre y el rubro.
3. Contestá lo que te pregunte y dejá el logo y las fotos en `entrada/` si las tenés. Al final te dice qué carpeta arrastrar a Netlify Drop.

Funciona con Sonnet. Necesitás Python 3 (en Mac ya viene) y Google Chrome para las capturas de revisión. La guía corta está en `EMPIEZA-AQUI.md`.

## Qué hay adentro

| Qué | Dónde | Para qué |
|---|---|---|
| Instrucciones de arranque | `CLAUDE.md` | Lo que hace Claude Code cuando escribís «hola» |
| La skill `rehacer-web` | `rehacer-web/SKILL.md` | Los ocho pasos: auditar, brief, fotos, generar, validar, publicar, medir y ofrecérsela al dueño |
| Carpetas de trabajo | `entrada/` y `webs/` | Lo que traés (HTML, logo, fotos) y cada web nueva, en su carpeta |
| Auditor de la web vieja | `rehacer-web/scripts/auditar_web.py` | Te dice qué tiene y qué le falta a la web actual (celular, WhatsApp, Google, peso). Con `--html` genera un informe visual para mostrarle al dueño y el «teaser»: los 3 hallazgos para abrir la conversación |
| Buscador de fotos | `rehacer-web/scripts/buscar_fotos.py` | Baja las fotos que el negocio ya publicó en su propia web (galería, productos, fichas) y arma una hoja de contactos para elegir. No toca Google Maps ni Instagram |
| Validador de la web nueva | `rehacer-web/scripts/validar_sitio.py` | Chequea el `index.html` antes de publicarlo |
| Medidor de PageSpeed | `rehacer-web/scripts/medir_pagespeed.py` | El antes y el después, con clave gratuita de Google o a mano |
| Brief | `rehacer-web/references/brief-plantilla.md` | Las diez preguntas para el dueño |
| Prompt de espectáculo (el principal) | `rehacer-web/references/prompt-web-nueva-espectaculo.md` | Scrolling deslumbrante con GSAP: hero con máscara, sección pineada, contadores, fotos integradas con parallax y banda con tilt, magnéticos |
| Cinco esqueletos con la mecánica hecha | `rehacer-web/plantilla/` + `COMO-USAR-EL-ESQUELETO.md` | Para que cualquier modelo (Sonnet, ChatGPT, Codex) rinda igual y las webs no salgan iguales: **Noche** (autos y oficios), **Mantel** (gastronomía), **Aire** (salud y profesionales), **Pulso** (gimnasio, barbería, estética) y **Vidriera** (tiendas). Cada uno con su hero, su orden, su tipografía y sus animaciones; el modelo completa los slots {{...}} y adapta al rubro. Claude te propone el del rubro y te deja elegir |
| Gate visual | `rehacer-web/references/gate-visual.md` | Cuatro renders con Chrome headless (escritorio y celular, con y sin JS) y checklist de cierre |
| Prompt sobrio | `rehacer-web/references/prompt-web-nueva.md` | Versión mínima sin librerías, por si el negocio la pide |
| Cómo publicar | `rehacer-web/references/publicar-netlify.md` | Netlify Drop, gratis, y dominio propio |
| Ofrecérsela al dueño | `rehacer-web/references/ofrecer-al-dueno.md` | Los mensajes de WhatsApp con los hallazgos reales, el seguimiento y las respuestas a «¿cuánto sale?». El precio lo pone cada uno |
| Checklist | `rehacer-web/references/checklist.md` | Para tildar |

## Sin Claude Code (los scripts solos)

```
python3 rehacer-web/scripts/auditar_web.py https://la-web-vieja.com --html
python3 rehacer-web/scripts/validar_sitio.py webs/<negocio>/index.html
python3 rehacer-web/scripts/medir_pagespeed.py https://la-web-nueva.netlify.app --etiqueta despues
```

## En otras herramientas (todavía sin probar)
Lo probado es Claude Code. La skill sigue el formato estándar de skills, así que debería servir en otros lados, pero no lo comprobamos:
- **Claude.ai:** Customize → Skills → subir la carpeta `rehacer-web` como ZIP.
- **Codex u otro agente:** copiar `rehacer-web/` en la carpeta de skills del proyecto.
- **ChatGPT:** pegar `rehacer-web/SKILL.md` como instrucciones de un proyecto, junto con el esqueleto y el brief.

## Qué no hace
- No inventa datos del negocio: lo que el dueño no dijo, no va.
- No garantiza posiciones en Google ni ventas: mejora la base técnica y el contacto.
- No sirve para tiendas con carrito, reservas ni sistemas con login.

## Quién lo hizo y con qué licencia
Hecho por **Valentino Colonna** (@valentino.ia en Instagram · YouTube «Valentino Colonna | IA»), publicado junto con el video «Creá páginas web con IA en 10 minutos y vendelas a negocios». Licencia **MIT** (ver `LICENSE`): podés usarlo, cambiarlo y venderlo con lo que hagas; solo dejá el aviso de copyright. Si lo mejorás, mandá un pull request o contame por Instagram.
