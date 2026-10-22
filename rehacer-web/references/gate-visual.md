# Gate visual · el método exacto (no «abrí el navegador y miré»)

## Qué prueba y qué no
**Prueba:** que la primera pantalla con JavaScript se arme (escritorio y celular), y que sin JavaScript el contenido esté completo y legible en toda la página (en capturas largas de una copia sin scripts).
**No prueba:** las animaciones de las secciones de abajo (pines, desplazamientos, elementos que podrían quedar ocultos), los filtros y la selección de productos, la navegación con teclado, el movimiento reducido ni el comportamiento táctil real. El «celular» es un marco de 375 px, no un teléfono. Eso se prueba a mano con la lista del final y, para Vidriera, con las pruebas automáticas de `tests/`.

Antes de publicar, la página se renderiza en cuatro estados y se mira cada uno. Se usa Google Chrome en modo sin ventana («headless»). El bloque de abajo es de shell Unix (Mac y Linux); en Windows, hay que adaptarlo (Git Bash o WSL, o pedirle a Claude que lo haga: es una limitación conocida, ver `PENDIENTES.md`). `chequear_entorno.py` te dice la ruta de Chrome. Rutas habituales: Mac `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`; Windows `C:\Program Files\Google\Chrome\Application\chrome.exe`; Linux `google-chrome`.

```
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # en Windows o Linux, la ruta de arriba
# Correr desde la carpeta de la página (webs/<negocio>/).
F="file://$PWD/index.html"
mkdir -p gate

# 1 · Escritorio con JS (hero asentado después de las animaciones)
"$CH" --headless=new --disable-gpu --hide-scrollbars --user-data-dir=/tmp/g1 \
  --window-size=1280,900 --virtual-time-budget=8000 --screenshot=gate/desktop-js.png "$F"

# 2 · Celular con JS. Chrome sin ventana no arma la página a menos de ~500 px de ancho:
#     la captura saldría cortada a la derecha. Por eso el celular se mira dentro de un marco de 375 px.
printf '<!doctype html><meta charset=utf-8><style>html,body{margin:0}iframe{border:0;width:375px;height:812px;display:block}</style><iframe src="index.html"></iframe>' > _movil.html
"$CH" --headless=new --disable-gpu --hide-scrollbars --user-data-dir=/tmp/g2 \
  --window-size=375,812 --force-device-scale-factor=2 --virtual-time-budget=8000 --screenshot=gate/movil-js.png "file://$PWD/_movil.html"

# 3 · Sin JS (estructura y SEO): una copia sin <script> (menos el JSON-LD) y sin el hero a pantalla completa, alta.
#     Altos de 7000 y 9000 px: si la página es más larga (un catálogo grande o los esqueletos Aire y Pulso), subilos (9000 y 12000) hasta que se vea el pie.
python3 - <<'EOF'
import re;t=open('index.html',encoding='utf-8').read()
t=re.sub(r'<script(?! type="application/ld\+json")[^>]*>.*?</script>','',t,flags=re.S)
t=t.replace('</style>','.hero{min-height:auto!important}.hz{height:auto!important}</style>')
open('_sinjs.html','w',encoding='utf-8').write(t)   # al lado de index.html, para que carguen las fotos
EOF
"$CH" --headless=new --disable-gpu --hide-scrollbars --user-data-dir=/tmp/g3 \
  --window-size=1280,7000 --screenshot=gate/secciones-sinjs.png "file://$PWD/_sinjs.html"
printf '<!doctype html><meta charset=utf-8><style>html,body{margin:0}iframe{border:0;width:375px;height:9000px;display:block}</style><iframe src="_sinjs.html"></iframe>' > _movil-sinjs.html
"$CH" --headless=new --disable-gpu --hide-scrollbars --user-data-dir=/tmp/g4 \
  --window-size=375,9000 --screenshot=gate/secciones-movil-sinjs.png "file://$PWD/_movil-sinjs.html"
rm _sinjs.html _movil.html _movil-sinjs.html
```

No se usa `--no-sandbox`: es una protección de Chrome y solo se saca, bajo tu responsabilidad, si Chrome no arranca como administrador (root) o dentro de un contenedor, y solo con páginas propias del kit, nunca con la web de un tercero.

Trampas conocidas:
- Un hero de 100vh llena ventanas altas: por eso el render de secciones usa la copia sin esa altura.
- GSAP no avanza bajo `--virtual-time-budget` si tiene lag smoothing: la página lleva `gsap.ticker.lagSmoothing(0)`.
- `--disable-javascript` no siempre se respeta en headless nuevo: por eso el estado sin JS se hace con la copia sin scripts.
- Fuentes de Google: sin `--virtual-time-budget` pueden no llegar a cargar en el render; con JS cargan.

Checklist de cierre (mirá las capturas, no las supongas):
- [ ] Titular, subtítulo y botones visibles en escritorio y en celular con JS.
- [ ] Sin JS: la página se ve COMPLETA (nada queda oculto por un estado inicial), los contadores muestran el número real, no un 0.
- [ ] Celular: nada se sale del ancho; si hay carril horizontal, se desliza con el dedo.
- [ ] El botón de WhatsApp no tapa el contacto al final (padding del pie).
- [ ] Links, teléfono y WhatsApp reales, verificados a mano.
- [ ] Movimiento reducido: activar «reducir movimiento» en el sistema (o en las herramientas de Chrome → Rendering → Emulate prefers-reduced-motion) y comprobar que la página se ve completa y que filtros y botones siguen andando.
- [ ] Teclado: con Tab se llega a los botones y enlaces y se ve cuál está seleccionado.
- [ ] Si hay cartel ABIERTO/CERRADO, filtros o «sumar a la consulta» (Vidriera): probarlos a mano.
- [ ] Scroll con rueda fluido en cualquier punto de la página (abrirla en Chrome y probar): si pesa, hay backdrop-filter en la nav o gsap.to dentro de mousemove.
- [ ] Capturas guardadas en `gate/`: son el «después» del video.
