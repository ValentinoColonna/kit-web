---
name: rehacer-web
description: Rehace la web vieja de un negocio chico con IA y la deja lista para publicar y medir. Audita la web actual (celular, velocidad, contacto, Google) con un informe visual, arma el brief con lo que ya dice la web y lo confirma con la persona en dos o tres mensajes, genera una página nueva de una sola pantalla con scroll animado, WhatsApp y los datos del negocio, la valida, la revisa en celular y escritorio, deja la carpeta lista para Netlify Drop y mide el antes y el después. Usala cuando alguien pase el link o el HTML de una web vieja, o el nombre de un negocio sin web, y quiera una nueva simple hoy, o para abrir una conversación con un negocio mostrándole lo que le falta a su web. No la uses para tiendas online, reservas, webs de varias páginas con login ni para prometer posiciones en Google.
license: MIT
metadata:
  author: Valentino Colonna (@valentino.ia)
  source: https://github.com/ValentinoColonna/kit-web
  version: "1.1"
---

# Rehacer la web de un negocio con IA

Objetivo: de una web vieja (o de ninguna) a una página nueva, validada y lista para publicar, en una sesión. Herramientas públicas: Python 3, Claude, Google Chrome, Netlify Drop y PageSpeed Insights.

Las rutas son relativas a la raíz del kit. `<negocio>` es el nombre del negocio en minúsculas y con guiones (por ejemplo, `autos-perez`). Todo el trabajo va en `webs/<negocio>/`.

## Cuándo empieza
La persona pasa una de tres cosas: **el link** de la web actual, **un archivo `.html`** en `entrada/`, o **el nombre y el rubro** de un negocio sin web. Con el link o el archivo, corrés el auditor antes de preguntar nada más. Si no hay nada de eso, pedí solo el link.

## Cuándo usarla
- Un negocio chico (local, servicio, profesional) con una web que no se ve bien en el celular, carga lento, no tiene WhatsApp a un toque o no dice dónde está ni qué vende.
- Un negocio sin web que necesita una página seria para que lo encuentren y lo contacten.
- Para **abrir una conversación** con un negocio: la auditoría en modo teaser (tres hallazgos) es el mensaje de apertura.

## Cuándo no
- Tienda online con carrito, reservas, pagos, login o varias páginas con contenido propio: es otro proyecto.
- Prometer «primero en Google»: una página nueva mejora la base técnica, no garantiza posiciones.

## Pasos (en este orden)

### 1 · Auditar el «antes»
- `mkdir -p webs/<negocio>` y después `python3 rehacer-web/scripts/auditar_web.py <link o entrada/archivo.html> --html --salida webs/<negocio>/auditoria.md`. Deja `auditoria.md` (para trabajar) y `auditoria.html` (semáforo para mostrarle al dueño). En Windows, `python` en vez de `python3`.
- Contale a la persona, en tres líneas y sin jerga, los **tres hallazgos** que más contactos le cuestan al negocio (en general: no se adapta al celular, sin WhatsApp a un toque, sin datos para Google). Es el teaser: sirve tal cual como mensaje de apertura para el dueño.
- PageSpeed del antes: `python3 rehacer-web/scripts/medir_pagespeed.py <link> --etiqueta antes` si hay clave de API; si no, dale el enlace de https://pagespeed.web.dev para que lo mida a mano y anote los cuatro números. Con un archivo local, el antes se mide solo si existe el link publicado.

### 2 · Brief (dos o tres mensajes, no un interrogatorio)
Armá `webs/<negocio>/brief.md` con la plantilla `rehacer-web/references/brief-plantilla.md`. **Proponé vos lo que ya sacaste de la web vieja** y pedí que corrija. El auditor deja en `auditoria.md` la sección «Datos del negocio que dice la web vieja» (teléfonos, WhatsApp, emails, dirección, horarios, redes; si la web tiene página de contacto, también la lee) y el texto completo en `auditoria-texto-web-vieja.txt`: usalos para completar el bloque 1 antes de preguntar.
- **Bloque 1, lo básico:** qué vende, a quién, dónde, horarios, WhatsApp con código de país, teléfono, email.
- **Bloque 2, identidad:** colores que ya usa (cartel, Instagram), logo, fotos reales. Si no tiene colores, proponé dos o tres paletas acordes al rubro y que elija. **La paleta es la del negocio.**
- **Bloque 3, opcional:** tres motivos por los que lo eligen, redes, datos legales.
Lo que no se sabe queda como `[PLACEHOLDER]` visible. Nunca inventes ni omitas en silencio.

### 3 · Fotos
- Pedí que deje en `entrada/` el logo y las fotos que tenga (local, equipo, productos o platos). Si no tiene, seguí: los marcos muestran un panel y la página igual se ve diseñada.
- Mirá cada foto en grande antes de usarla: nada de carteles o logos de otro negocio, patentes, caras de clientes sin permiso ni escenas que no son del rubro.
- Copialas a `webs/<negocio>/assets/` con los nombres fijos de `rehacer-web/references/imagenes.md` (`hero-salon.jpg`, `salon.jpg`, `galeria-01.jpg`…, `catalogo-01.jpg`…). En Mac, achicalas al copiarlas: `sips -Z 1600 -s formatOptions 80 entrada/foto.jpg --out webs/<negocio>/assets/salon.jpg`.

### 4 · Generar la página
Antes de generar, decidí tono, «sección estrella» y CTA según el rubro:

| Rubro | Tono | Sección estrella | CTA |
|---|---|---|---|
| Taller, concesionaria, servicio técnico | directo, confiable | qué hacemos + garantías | «Escribir por WhatsApp» |
| Restaurante, bar, cafetería | cálido, sensorial | la carta o los platos con precio | «Reservar» / «Pedir por WhatsApp» |
| Clínica, consultorio, profesional | serio, cercano, fondo claro | especialidades y quién atiende | «Pedir turno» |
| Peluquería, estética, gimnasio | personal, enérgico | servicios con precios o planes | «Pedir turno» / «Empezar» |
| Tienda, negocio local | práctico | productos destacados | «Visitanos» / «Consultar» |

- **Camino principal, el esqueleto:** copiá `rehacer-web/plantilla/esqueleto-espectaculo.html` a `webs/<negocio>/index.html` y completá todos los `{{…}}` con el brief, siguiendo `rehacer-web/plantilla/COMO-USAR-EL-ESQUELETO.md`. La mecánica del scroll ya está hecha y probada: tu trabajo es el contenido, la paleta y adaptar las secciones al rubro (renombrar, sacar lo que no aplique, repetir el ítem del catálogo por cada ítem real y reemplazar el «momento firma» por uno propio del negocio).
- **La especificación** que manda en todo lo demás es `rehacer-web/references/prompt-web-nueva-espectaculo.md`: leela entera antes de completar el esqueleto. Si la persona pide algo mínimo, sin animaciones, usá `rehacer-web/references/prompt-web-nueva.md`.
- **Corrección humana a la vista:** mostrale los textos clave (titular, subtítulo, servicios) y preguntá si algo sobra o falta. Lo que el dueño no dijo, sale.

### 5 · Validar y mirar
- `python3 rehacer-web/scripts/validar_sitio.py webs/<negocio>/index.html` hasta que diga PASA. Mientras haya placeholders, `--borrador`, y avisá cuáles quedan.
- **Gate visual (no se dice «lista» sin esto):** el método está en `rehacer-web/references/gate-visual.md`: cuatro capturas con Chrome sin ventana (escritorio y celular, con y sin JavaScript), corridas desde `webs/<negocio>/`. Mirá cada captura con atención y corregí lo que esté mal: titular invisible, textos cortados, tarjetas que se salen en el celular, fotos rotas. Sin JavaScript la página tiene que verse completa.
- Abrila en Chrome para que la persona pruebe el scroll con la rueda y en el celular.

### 6 · Publicar (lo hace la persona)
- Prepará `webs/<negocio>-publicar/` con `index.html` y `assets/`, sin los `.md` ni `gate/`.
- Si quedan marcos sin foto, cambiá su `data-nombre` por un texto para el público: el nombre del producto, del plato, del lugar o del negocio. El nombre del archivo (`assets/…`) solo sirve mientras se trabaja.
- Decile que abra https://app.netlify.com/drop y arrastre esa carpeta. Netlify le da una dirección con candado al instante. Para que no venza, que cree la cuenta gratis. Dominio propio: `rehacer-web/references/publicar-netlify.md`.
- Vos no publicás nada.

### 7 · Medir el «después» y entregar
- La misma medición de PageSpeed con la URL nueva. Antes y después lado a lado. Si algo dio peor, decilo y explicá por qué.
- **Resumen final, siempre:** la URL publicada, qué hallazgos de la auditoría se resolvieron, qué queda pendiente del dueño (fotos, dominio, datos en placeholder) y cómo cambia él mismo un texto o una foto.

## Qué entrega esta skill
- `webs/<negocio>/auditoria.md` y `auditoria.html`, y el teaser de tres hallazgos.
- `webs/<negocio>/brief.md`.
- `webs/<negocio>/index.html` con `assets/`, validado y revisado en `gate/`.
- `webs/<negocio>-publicar/`, lista para Netlify Drop.
- El antes y el después, y el resumen final para el dueño.

## Qué no hacer
- No inventar datos del negocio: ni reseñas, ni años, ni clientes, ni premios, ni «somos líderes».
- No usar fotos ajenas. Fotos del dueño; si no hay, ninguna, o de un banco libre (Pexels, Unsplash) solo si la persona lo pide, marcadas como ilustrativas.
- No usar la paleta de quien usa el kit en la web del negocio.
- No prometer resultados de ventas ni de Google.
- No publicar ni subir datos del negocio a otros servicios.
- No meter librerías que no sean GSAP y ScrollTrigger (CDN) y Google Fonts. El espectáculo se hace con esa receta, degradando sin JavaScript y respetando `prefers-reduced-motion`.

---
Hecho por Valentino Colonna (@valentino.ia · YouTube «Valentino Colonna | IA»). Licencia MIT: usala, cambiala y compartila; dejá el crédito.
