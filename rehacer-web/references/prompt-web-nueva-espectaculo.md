# Prompt abierto · la web nueva con scrolling deslumbrante (el principal)

Pegalo entero en Claude (Claude Code es lo ideal: genera el archivo y lo abre), y debajo el `brief.md` y la `auditoria.md`. Con Claude Code el kit no parte de cero: usa uno de los cinco esqueletos de `plantilla/`, y este prompt es la especificación que manda en todo lo demás. Receta: HTML único + GSAP 3 con ScrollTrigger por CDN + Google Fonts. Es el mismo stack que usan las webs premium con scroll «tipo Apple».

```
Vas a crear la página web nueva de un negocio chico: una sola página (index.html) que deslumbre al hacer scroll y que, aun así, cargue rápido, se lea en el celular y le diga a Google dónde está el negocio.

Stack, obligatorio:
- Un único archivo index.html con el CSS adentro (<style>) y el JavaScript adentro (<script>).
- Permitido cargar de afuera, solo esto: GSAP 3.12 y ScrollTrigger desde cdnjs (https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js y .../ScrollTrigger.min.js) y una o dos familias de Google Fonts (una display para titulares, una de texto). Nada más.
- Pensada primero para celular: <meta name="viewport" content="width=device-width, initial-scale=1">, legible sin zoom, botones de 44 px o más.
- <html lang="es-AR">, <title> de 10 a 70 caracteres, <meta name="description"> de 50 a 170, exactamente un <h1>, alt en todas las imágenes, JSON-LD LocalBusiness (o subtipo) con name, address, telephone, openingHours y url.
- Botón de WhatsApp fijo (https://wa.me/<número del brief>?text=...), teléfono con tel:, dirección con enlace a Google Maps, horarios visibles.

Diseño (sistema cerrado):
- Paleta del negocio, nunca la de quien hace la página. Base oscura cálida u off-white cálido (sin #000 ni #fff puros), UN acento, un secundario con cuentagotas, un color de estado. Sombras tintadas con el acento, no negras. Bordes y fondos de tarjeta en opacidades bajas (.04 a .10): el detalle susurra.
- Tipografía: display con carácter para titulares (peso alto), sans limpia para texto. Degradado de texto solo en la palabra clave del titular.
- Jerarquía: en cada pantalla gritan como mucho tres cosas: el remate del titular, un dato grande y el CTA.
- Mostrar, no contar: el hero demuestra lo que el negocio da (una garantía que se firma sola, un turno que se confirma, un plato que aparece), no lo describe.
- Un «momento firma» propio del negocio, que no se repita en otra web.
- Adaptá tono, sección estrella y botón principal al rubro: taller o concesionaria (directo; servicios y garantías; WhatsApp), restaurante (cálido; la carta con precios; reservar o pedir), clínica o profesional (serio y claro; especialidades y quién atiende; pedir turno), estética o gimnasio (personal; servicios o planes; pedir turno), tienda (práctico; productos; visitanos).

El scrolling (elegí por rubro, no metas todo):
- Hero con reveal de máscara: cada línea del titular en un contenedor overflow:hidden y entra con yPercent de 110 a 0, escalonado. Blobs de luz de fondo con parallax (scrub) y una grilla enmascarada.
- Barra de progreso de lectura arriba. Nav que se compacta al bajar, con fondo sólido (rgba .96), NUNCA backdrop-filter: blur en la nav fija (mata el scroll).
- Marquee de palabras del negocio.
- Una sección horizontal pineada en escritorio (las tarjetas desfilan con scrub); en celular, carril con scroll nativo y snap.
- Contadores que suben al entrar en pantalla, SOLO con números reales del brief; en el HTML va el número final (sin JS se ve el dato, no un 0).
- Reveals con stagger por sección, parallax sutil, tarjetas que se levantan al pasar el mouse.
- Botones magnéticos en los CTA con gsap.quickTo en mousemove (nunca gsap.to dentro de mousemove) y vuelta elástica al salir. Solo si hay hover (no en celular).
- Todo respeta prefers-reduced-motion (si está activo, no hay animaciones) y se degrada sin JS: los estados iniciales ocultos los fija GSAP con gsap.set (no el CSS), para que sin JS o si el CDN falla la web se vea completa. Agregá gsap.ticker.lagSmoothing(0).
- Animá solo transform y opacity; will-change con moderación. El archivo entero, sin imágenes, por debajo de 40 KB.

Imágenes (integradas, nunca «un cuadradito» suelto):
- Las fotos del negocio forman parte del sistema: mismos radios, bordes en baja opacidad, un velo (gradiente) del color base por encima para que convivan con la paleta, pie de foto discreto adentro del marco. Nada de grillas de cuadrados iguales.
- Componentes, elegí dos o tres: (a) foto de fondo del hero enmascarada con parallax y zoom lento; (b) una foto grande que se revela con clip-path al entrar y cuya imagen se desplaza adentro al hacer scroll, con texto al lado; (c) banda de galería que desfila con el scroll en escritorio (scrub) y se desliza con el dedo en celular, con fotos de tamaños distintos y tilt 3D con el mouse (quickTo); (d) antes/después deslizable si el rubro lo pide (reformas, estética).
- (e) Catálogo / carta / servicios con foto: tarjetas con foto (velo de la paleta, radio del sistema), título, una línea y botón de WhatsApp con mensaje prearmado que nombra el ítem; los ítems son SOLO los del brief o los que la web vieja ya publica; sin precios inventados («Consultar»). En escritorio, grilla de 3; en celular, carril con snap. Hover: la foto hace un zoom lento y la tarjeta se levanta.
- Incluí SIEMPRE al menos dos de estos componentes (y el catálogo si el negocio vende cosas enumerables), aunque hoy el negocio no tenga fotos: los marcos quedan listos y, sin archivo, muestran el panel del sistema con el nombre que falta. Una página sin ningún lugar para fotos no está terminada.
- Swap-ready: cada foto apunta a un archivo con nombre fijo en assets/ (hero-salon.jpg, salon.jpg, galeria-01.jpg...). Si el archivo no existe, onerror agrega la clase .sin y el marco muestra un panel del sistema con el nombre del archivo que falta: la página se ve diseñada igual, y el dueño reemplaza las fotos 1 a 1 sin tocar el código. Nunca uses fotos de bancos ni de otros negocios.
- Todas con alt descriptivo (las decorativas, alt="").

Contenido:
- Usá SOLO la información del brief. No inventes reseñas, cifras, años, premios, clientes ni «somos líderes». Sin reseñas, no hay sección de reseñas.
- Castellano rioplatense, con voseo, directo. Sin rayas largas en los textos.
- Donde el brief tenga un dato en blanco, dejá un placeholder visible entre corchetes ([TELÉFONO]); no inventes ni omitas en silencio. Mientras haya placeholders, la página se valida con `validar_sitio.py index.html --borrador`; sin el flag, el validador los bloquea porque no se publica con placeholders.

Entregá:
1. El index.html completo.
2. La lista de lo que quedó en blanco porque el brief no lo tenía.
3. Los nombres de archivo de las imágenes que la página espera encontrar en la misma carpeta.
4. Qué tres cosas de la página son el «momento firma» y por qué le pertenecen a este negocio.

Si algo del brief es ambiguo, preguntame antes de escribir.
```
