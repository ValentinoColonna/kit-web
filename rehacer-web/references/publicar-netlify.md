# Publicar la página nueva (gratis, en minutos)

## Con Netlify Drop (sin instalar nada)
1. Poné en una carpeta el `index.html` y las imágenes que usa.
2. Entrá a https://app.netlify.com/drop y arrastrá la carpeta.
3. Netlify te da una dirección del tipo `nombre-raro.netlify.app`. Ya está en línea, con HTTPS.
4. Para que no venza y poder cambiarle el nombre, creá una cuenta gratuita (la misma página te lo ofrece) y, en Site settings → Change site name, poné algo como `nombre-del-negocio.netlify.app`.

Cada vez que corrijas la página, entrá al sitio en Netlify, pestaña **Deploys**, y arrastrá la carpeta ahí: reemplaza la versión anterior y el link queda igual. Si la arrastrás de nuevo en `/drop`, Netlify crea **otro sitio** con otro link.

**Muestra para ofrecer:** mientras el dueño no la pidió, la copia publicada lleva `<meta name="robots" content="noindex">` (comprobalo con `validar_sitio.py index.html --muestra`). Si dice que no: Site configuration → Delete this site.

## Dominio propio (si el dueño ya tiene uno)
1. En Netlify: Domain management → Add a domain → escribir el dominio del negocio.
2. En el proveedor del dominio del dueño (donde lo compró): apuntar el dominio a Netlify como Netlify indica en esa pantalla (un registro A o un CNAME; Netlify muestra los valores exactos). Esto lo tiene que hacer quien tenga la clave del dominio.
3. Esperar la propagación (de minutos a 24 horas). Netlify activa el HTTPS solo.

**Antes de cambiar el dominio:** guardar una copia de la web vieja (capturas y, si se puede, los archivos). Si el dueño se arrepiente, se vuelve a apuntar el dominio a donde estaba.

## Alternativas igual de válidas
- GitHub Pages, Cloudflare Pages o Vercel: también gratis para una página estática. El flujo es el mismo: subir la carpeta.
- El hosting que ya paga el negocio: subir `index.html` por el panel o por FTP, reemplazando el anterior (con copia previa).
