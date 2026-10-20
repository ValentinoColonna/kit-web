# Checklist · rehacer la web de un negocio con IA

```
[ ] Permiso del dueño, por escrito (un mensaje alcanza): para rehacer, publicar y mostrar el antes y el después.
[ ] Antes: auditoría de la web vieja (auditar_web.py --html), medición en PageSpeed (celular) y capturas en celular y escritorio.
[ ] Teaser: los 3 hallazgos que más contactos le cuestan, en un mensaje de 3 líneas para el dueño.
[ ] Brief completado con el dueño en 2 o 3 mensajes: qué vende, a quién, dónde, WhatsApp con código de país, horarios, 3 motivos, colores del negocio, fotos reales. Lo que falta, en placeholder visible.
[ ] Página nueva generada con el prompt abierto, a partir del brief y la auditoría, adaptada al rubro.
[ ] Corrección humana: leer todo, sacar lo que el dueño no dijo, revisar colores y orden.
[ ] Validación (validar_sitio.py): PASA, sin placeholders.
[ ] Gate visual: vista en escritorio y en celular (375 px); se lee sin zoom, WhatsApp se toca, el teléfono llama, el mapa abre. Capturas guardadas.
[ ] Publicada en Netlify Drop (o similar) con HTTPS. Nombre del sitio legible.
[ ] Después: misma medición de PageSpeed y mismas capturas. Antes y después lado a lado.
[ ] Dominio propio apuntado, solo si el dueño quiere y con copia de la web vieja guardada.
[ ] Entregarle al dueño: la dirección nueva, el index.html, el brief y cómo cambiar un texto o una foto.
```
