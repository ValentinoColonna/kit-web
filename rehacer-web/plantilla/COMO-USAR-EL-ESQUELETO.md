# Cómo usar el esqueleto (para que cualquier modelo rinda igual)

`esqueleto-espectaculo.html` trae toda la mecánica del scrolling deslumbrante ya hecha y probada con el gate visual. Un modelo chico no tiene que inventar GSAP: tiene que **completar slots** y **adaptar secciones al rubro**.

Prompt corto para Claude (cualquier modelo), ChatGPT o Codex:

```
Tomá el archivo esqueleto-espectaculo.html. Completá todos los slots {{...}} con los datos del brief que te paso abajo. Lo que el brief no tenga, dejalo como [PLACEHOLDER] visible. Adaptá al rubro: renombrá secciones, sacá las que no apliquen y reemplazá el «momento firma» (la tarjeta que se firma sola) por uno propio de este negocio, hecho con los mismos recursos (CSS y GSAP que ya están en el archivo). No agregues librerías, no toques la nav ni los scripts salvo para adaptar nombres de clases que renombres. Elegí paleta del negocio (nunca la de quien hace la página), sin #000 ni #fff puros, y dos fuentes de Google. Devolveme el index.html completo y la lista de slots que quedaron como placeholder.
```

Después: `python3 rehacer-web/scripts/validar_sitio.py webs/<negocio>/index.html` y el gate visual (`rehacer-web/references/gate-visual.md`). Con Claude Code no hace falta pegar este prompt: el kit lo hace solo cuando escribís «hola». La receta completa, para construir desde cero, está en `rehacer-web/references/prompt-web-nueva-espectaculo.md`.

## La paleta se cambia en un solo lugar
Todos los colores salen de las variables de `:root`, al principio del `<style>`. Cada color de la marca va dos veces: en hex (`--acc: #1e5bb8`) y en r,g,b (`--acc-rgb: 30,91,184`), porque los velos y las sombras usan `rgba(var(--acc-rgb), .3)`. Completá `--bg`/`--bg-rgb`, `--bg2`, `--acc`/`--acc-rgb`, `--acc-claro`, `--sobre-acc` y `--acc2`/`--acc2-rgb`. No busques colores sueltos en el resto del archivo: no hay.

## Lo que se borra o se repite según el negocio
- **Fondo del hero:** solo con una foto de 1200 px de ancho o más. Si no hay, se borra el `<div class="fondo">` entero.
- **Contadores:** solo números reales del brief. Si hay dos, se deja dos; si no hay ninguno, se saca el bloque.
- **Catálogo:** se repite la tarjeta por cada ítem real. En el celular es un carril que se desliza con el dedo.
- **Momento firma:** el papel que se firma es un ejemplo; se reemplaza por uno propio del negocio con los mismos recursos.
