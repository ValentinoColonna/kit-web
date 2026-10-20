---
name: rehacer-web
description: Rehace la web vieja de un negocio chico con IA y la deja publicada y medida. Audita la web actual (celular, velocidad, contacto, Google) y genera un informe visual, arma el brief con el dueño en dos o tres mensajes, genera una página nueva de una sola pantalla con WhatsApp y datos del negocio, la valida, la revisa en celular, la publica gratis y mide el antes y el después. Usala cuando alguien tenga una web vieja o sin web y quiera una nueva simple hoy, o cuando quieras abrir una conversación con un negocio mostrándole lo que le falta a su web. No la uses para tiendas online, sistemas de reservas, webs de varias páginas con login ni para prometer posiciones en Google.
license: MIT
metadata:
  author: Valentino Colonna (@valentino.ia)
  source: https://github.com/ValentinoColonna/kit-web
  version: "1.0"
---

# Rehacer la web de un negocio con IA

Objetivo: pasar de una web vieja (o de ninguna) a una página nueva, publicada y medida, en una sesión de trabajo. Todo con herramientas públicas y gratis: Python 3, Claude o ChatGPT, Netlify Drop y PageSpeed Insights.

## Cuándo empieza
Al arrancar, saludá en una línea y pedí una sola cosa: **la dirección de la web actual del negocio** (o que te digan que no tiene). Con eso corrés el auditor antes de preguntar nada más.

## Cuándo usarla
- Un negocio chico (local, servicio, profesional) con una web que no se ve bien en el celular, carga lento, no tiene WhatsApp a un toque o no dice dónde está ni qué vende.
- Un negocio sin web que necesita una página seria para que lo encuentren y lo contacten.
- Para **abrir una conversación** con un negocio: la auditoría en modo teaser (tres hallazgos) es el mensaje de apertura.

## Cuándo no
- Tienda online con carrito, reservas, pagos, login o varias páginas con contenido propio: eso es otro proyecto.
- Prometer «primero en Google»: una página nueva mejora la base técnica, no garantiza posiciones.

## Pasos (en este orden)

### 1 · Medir y auditar el «antes»
- `python3 scripts/auditar_web.py https://la-web-vieja.com --html` → `auditoria.md` (para trabajar) y `auditoria.html` (para mostrar: semáforo legible por un dueño de negocio). Mira lo que un cliente mira desde el celular y lo que mira Google: título, descripción, viewport, HTTPS, teléfono y WhatsApp a un toque, dirección, horarios, redes, imágenes sin texto alternativo, peso, tecnología visible.
- Medir en https://pagespeed.web.dev con la URL vieja (celular). Guardar captura de los cuatro puntajes. `scripts/medir_pagespeed.py` lo hace solo si tenés una clave de API gratuita de Google; sin clave, imprime la URL para hacerlo a mano.
- Guardar capturas de la web vieja en celular y en escritorio.
- **Modo teaser (para abrir la conversación):** de la auditoría, elegí los **tres** hallazgos que más contactos le cuestan al negocio (en general: no se adapta al celular, sin WhatsApp a un toque, sin datos para Google) y escribilos en un mensaje de tres líneas, sin jerga. Es lo que se le manda al dueño antes de pedirle nada. La salida es una llamada o un «te la hago», no un grupo ni una descarga.

### 2 · Brief con el dueño (10 minutos, en dos o tres mensajes)
No hagas un interrogatorio de veinte preguntas; agrupá en bloques y proponé vos lo que ya sacaste de la web vieja para que el dueño corrija:
- **Bloque 1, lo básico:** qué vende, a quién, dónde, horarios, WhatsApp con código de país, teléfono, email.
- **Bloque 2, identidad:** colores que ya usa (cartel, Instagram), logo, fotos reales. Si no tiene colores, proponé dos o tres paletas acordes al rubro y que elija. **La paleta es la del negocio, nunca la de tu marca.**
- **Bloque 3, opcional:** tres motivos por los que lo eligen, redes, textos legales (CUIT, matrícula).
Plantilla completa en `references/brief-plantilla.md`. **No inventar nada:** lo que el dueño no sabe queda como placeholder visible (`[TELÉFONO]`, `[HORARIOS]`) para que se vea qué falta, nunca inventado ni omitido en silencio.

### 3 · Adaptar al rubro y generar la página
Antes de generar, decidí tono, «sección estrella» y CTA según el rubro:

| Rubro | Tono | Sección estrella | CTA |
|---|---|---|---|
| Taller, concesionaria, servicio técnico | directo, confiable | qué hacemos + garantías | «Escribir por WhatsApp» |
| Restaurante, bar, cafetería | cálido, sensorial | la carta o los platos con precio | «Reservar» / «Pedir por WhatsApp» |
| Clínica, consultorio, profesional | serio, cercano, fondo claro | especialidades y quién atiende | «Pedir turno» |
| Peluquería, estética, gimnasio | personal, enérgico | servicios con precios o planes | «Pedir turno» / «Empezar» |
| Tienda, negocio local | práctico | productos destacados | «Visitanos» / «Consultar» |

- Pegar `references/prompt-web-nueva-espectaculo.md` (el principal: scrolling deslumbrante con GSAP + ScrollTrigger por CDN, hero con máscara, sección pineada, contadores reales, magnéticos) en Claude Code o Claude, con el brief y la auditoría, y pedir el `index.html`. `prompt-web-nueva.md` es la versión sobria, sin librerías, para cuando el negocio pide algo mínimo.
- Reglas que el prompt impone y vos controlás: una sola página, HTML con CSS y JS adentro; de afuera solo GSAP/ScrollTrigger por CDN y Google Fonts, pensada primero para celular, botón de WhatsApp fijo, teléfono con `tel:`, dirección con enlace a Google Maps, horarios, datos estructurados `LocalBusiness`, título y descripción para Google, textos del brief (sin inventar premios, años ni clientes), sin blanco ni negro puros.
- La **corrección humana** va acá: leer los textos, sacar lo que el dueño no dijo, ajustar colores y orden.

### 4 · Validar y mirar
- `python3 scripts/validar_sitio.py index.html` → lista de errores y avisos (viewport, título, descripción, un solo H1, alt en imágenes, WhatsApp, `tel:`, JSON-LD LocalBusiness, sin scripts externos, placeholders que quedaron). Corregir hasta que diga PASA.
- **Gate visual (no se publica sin esto):** el método exacto está en `references/gate-visual.md`: cuatro renders (escritorio con JS, celular con JS, secciones sin JS en escritorio y en celular) con Chrome headless, y una checklist de cierre. Sin JS la página tiene que verse completa. Las capturas van a `gate/` y son el «después» del video y la prueba para el dueño.

### 5 · Publicar
`references/publicar-netlify.md`: arrastrar la carpeta a Netlify Drop (gratis, sin cuenta para probar; con cuenta para que no venza). Después, si el dueño quiere, apuntar su dominio (sección «Dominio propio»), con copia de la web vieja guardada.

### 6 · Medir el «después» y entregar
- La misma medición de PageSpeed con la URL nueva, y la misma captura en celular y escritorio. Antes y después lado a lado. Si algo dio peor, decirlo.
- **Resumen final, siempre:** qué quedó publicado (URL), qué cambió respecto de la web vieja (los hallazgos de la auditoría que se resolvieron), qué quedó pendiente del dueño (fotos, dominio, datos en placeholder) y cómo cambia un texto o una foto él mismo.

## Qué entrega esta skill
- `auditoria.md` y `auditoria.html` del sitio viejo, más el mensaje teaser de tres hallazgos.
- `brief.md` completado.
- `index.html` nuevo, validado, mirado en celular y publicado.
- Comparativa antes/después (puntajes y capturas) y el resumen final para el dueño.

## Qué no hacer
- No inventar datos del negocio: ni reseñas, ni años, ni clientes, ni premios, ni «somos líderes».
- No usar fotos ajenas: fotos del dueño; si no hay, de un banco con licencia libre (Pexels, Unsplash) marcadas como ilustrativas y miradas en grande (ver references/imagenes.md), o ninguna.
- No usar la paleta de tu propia marca en la web del negocio.
- No prometer resultados de ventas ni de Google.
- No subir a otra plataforma datos de clientes del negocio.
- No meter librerías que no sean GSAP/ScrollTrigger (CDN) y Google Fonts: cada dependencia más cuesta velocidad. El espectáculo es obligatorio y se hace con esa receta, degradando sin JS y respetando `prefers-reduced-motion`. Por defecto, el prompt de espectáculo: una web que deslumbra es la que el dueño muestra y la que abre conversaciones.

---
Hecho por Valentino Colonna (@valentino.ia · YouTube «Valentino Colonna | IA»). Licencia MIT: usala, cambiala y compartila; dejá el crédito.
