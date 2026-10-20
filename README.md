# Recurso abierto · «Rehice la web de un negocio con IA»

Lo que te llevás del video de Valentino IA, sin pedir nada a cambio. Es una **skill** (una carpeta con instrucciones que entienden Claude, ChatGPT, Codex y otras IAs) más tres scripts que corren con Python 3, sin instalar nada.

| Qué | Dónde | Para qué |
|---|---|---|
| La skill `rehacer-web` | `rehacer-web/SKILL.md` | Los seis pasos: auditar, brief, generar, validar, publicar, medir |
| Auditor de la web vieja | `rehacer-web/scripts/auditar_web.py` | Te dice qué tiene y qué le falta a la web actual (celular, WhatsApp, Google, peso). Con `--html` genera un informe visual para mostrarle al dueño y el «teaser»: los 3 hallazgos para abrir la conversación |
| Validador de la web nueva | `rehacer-web/scripts/validar_sitio.py` | Chequea el `index.html` antes de publicarlo |
| Medidor de PageSpeed | `rehacer-web/scripts/medir_pagespeed.py` | El antes y el después, con clave gratuita de Google o a mano |
| Brief | `rehacer-web/references/brief-plantilla.md` | Las diez preguntas para el dueño |
| Prompt de espectáculo (el principal) | `rehacer-web/references/prompt-web-nueva-espectaculo.md` | Scrolling deslumbrante con GSAP: hero con máscara, sección pineada, contadores, fotos integradas con parallax y banda con tilt, magnéticos |
| Esqueleto con la mecánica hecha | `rehacer-web/plantilla/esqueleto-espectaculo.html` + `COMO-USAR-EL-ESQUELETO.md` | Para que cualquier modelo (Sonnet, ChatGPT, Codex) rinda igual: solo completa los slots {{...}} (unos 80, con catálogo, servicios e imágenes) y adapta al rubro |
| Gate visual | `rehacer-web/references/gate-visual.md` | Cuatro renders con Chrome headless (escritorio y celular, con y sin JS) y checklist de cierre |
| Prompt sobrio | `rehacer-web/references/prompt-web-nueva.md` | Versión mínima sin librerías, por si el negocio la pide |
| Cómo publicar | `rehacer-web/references/publicar-netlify.md` | Netlify Drop, gratis, y dominio propio |
| Checklist | `rehacer-web/references/checklist.md` | Para tildar |

## En tres comandos

```
python3 rehacer-web/scripts/auditar_web.py https://la-web-vieja.com --html
python3 rehacer-web/scripts/validar_sitio.py index.html
python3 rehacer-web/scripts/medir_pagespeed.py https://la-web-nueva.netlify.app --etiqueta despues
```

## Para usarla como skill
- **Claude.ai:** Customize → Skills → subir la carpeta `rehacer-web` como ZIP.
- **Claude Code o Codex:** copiar `rehacer-web/` en `.claude/skills/` o `.agents/skills/` del proyecto.
- **ChatGPT:** pegar el `SKILL.md` como instrucciones de un proyecto, o usar el prompt abierto directo.

## Qué no hace
- No inventa datos del negocio: lo que el dueño no dijo, no va.
- No garantiza posiciones en Google ni ventas: mejora la base técnica y el contacto.
- No sirve para tiendas con carrito, reservas ni sistemas con login.

## Quién lo hizo y con qué licencia
Hecho por **Valentino Colonna** (@valentino.ia en Instagram · YouTube «Valentino Colonna | IA»), publicado junto con el video «Creá páginas web con IA en 10 minutos y vendelas a negocios». Licencia **MIT** (ver `LICENSE`): podés usarlo, cambiarlo y venderlo con lo que hagas; solo dejá el aviso de copyright. Si lo mejorás, mandá un pull request o contame por Instagram.
