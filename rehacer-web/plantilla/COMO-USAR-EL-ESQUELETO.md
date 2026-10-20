# Cómo usar el esqueleto (para que cualquier modelo rinda igual)

`esqueleto-espectaculo.html` trae toda la mecánica del scrolling deslumbrante ya hecha y probada con el gate visual. Un modelo chico no tiene que inventar GSAP: tiene que **completar slots** y **adaptar secciones al rubro**.

Prompt corto para Claude (cualquier modelo), ChatGPT o Codex:

```
Tomá el archivo esqueleto-espectaculo.html. Completá todos los slots {{...}} con los datos del brief que te paso abajo. Lo que el brief no tenga, dejalo como [PLACEHOLDER] visible. Adaptá al rubro: renombrá secciones, sacá las que no apliquen y reemplazá el «momento firma» (la tarjeta que se firma sola) por uno propio de este negocio, hecho con los mismos recursos (CSS y GSAP que ya están en el archivo). No agregues librerías, no toques la nav ni los scripts salvo para adaptar nombres de clases que renombres. Elegí paleta del negocio (nunca la de quien hace la página), sin #000 ni #fff puros, y dos fuentes de Google. Devolveme el index.html completo y la lista de slots que quedaron como placeholder.
```

Después: `python3 scripts/validar_sitio.py index.html` y el gate visual (`references/gate-visual.md`). Si querés ir más lejos que el esqueleto, usá `references/prompt-web-nueva-espectaculo.md`, que describe la receta completa para que el modelo la construya desde cero.
