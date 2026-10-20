# Prompt abierto · la web nueva (pegar en Claude o ChatGPT)

Pegalo entero, y debajo el `brief.md` completado y la `auditoria.md` de la web vieja.

```
Vas a crear la página web nueva de un negocio chico. Una sola página (index.html), lista para publicar tal cual.

Reglas técnicas, todas obligatorias:
- Un único archivo index.html con el CSS adentro (<style>) y, si hace falta, JavaScript mínimo adentro (<script>). Sin frameworks, sin fuentes externas, sin scripts ni hojas de estilo de otros sitios. La página tiene que funcionar sin internet salvo las imágenes del negocio.
- Pensada primero para celular (mobile first), legible sin hacer zoom, con <meta name="viewport" content="width=device-width, initial-scale=1">.
- <html lang="es-AR">, <title> de 10 a 70 caracteres con el nombre del negocio y qué hace, y <meta name="description"> de 50 a 170 caracteres.
- Exactamente un <h1> que diga qué es el negocio y para quién.
- Botón de WhatsApp fijo, visible siempre, con el enlace https://wa.me/<número del brief> y un texto prearmado (?text=...).
- Teléfono con enlace tel:, dirección con enlace a Google Maps, horarios visibles.
- Datos estructurados JSON-LD de tipo LocalBusiness (o el subtipo que corresponda) con name, address, telephone, openingHours y url.
- Todas las imágenes con alt descriptivo. Usá solo las fotos que el brief dice que existen, con esos nombres de archivo; si no hay fotos, no inventes imágenes: usá color y tipografía.
- Colores: los del brief (los del negocio, nunca los de quien hace la página); si no hay, una paleta sobria de dos colores. Sin blanco puro (#FFFFFF) ni negro puro (#000000) como fondo o texto: usá tonos cercanos.
- Adaptá tono, «sección estrella» y botón principal al rubro: taller o concesionaria (directo; qué hacemos y garantías; WhatsApp), restaurante (cálido; la carta con precios; reservar o pedir), clínica o profesional (serio y claro; especialidades y quién atiende; pedir turno), estética o gimnasio (personal; servicios o planes con precio; pedir turno), tienda o negocio local (práctico; productos destacados; visitanos o consultar).
- Donde el brief tenga un dato en blanco, dejá un placeholder visible entre corchetes ([TELÉFONO], [HORARIOS]); no inventes ni omitas en silencio.
- Secciones, en este orden: encabezado con nombre y botón de contacto; qué hace y para quién (H1 y un párrafo); servicios o productos (los del brief, nada más); por qué elegirlo (los tres motivos del brief, en sus palabras); dónde y cuándo (dirección, mapa, horarios); contacto (WhatsApp, teléfono, email, redes); pie con nombre y datos legales si los hay.

Reglas de contenido, todas obligatorias:
- Usá SOLO la información del brief. No inventes reseñas, cifras, años de experiencia, premios, clientes ni «somos líderes».
- Castellano rioplatense, con voseo, directo, sin exagerar.
- Cada sección corta: títulos claros, párrafos de dos o tres líneas, listas donde haya varias cosas.

Entregá:
1. El index.html completo.
2. Una lista de lo que quedó en blanco porque el brief no lo tenía, para preguntárselo al dueño.
3. Los nombres de archivo de las imágenes que la página espera encontrar en la misma carpeta.

Si algo del brief es ambiguo, preguntame antes de escribir.
```
