# Gate visual · el método exacto (no «abrí el navegador y miré»)

Antes de publicar, la página se renderiza en cuatro estados y se mira cada uno. Sirve cualquier Chrome; si no tenés, un Chrome headless (el que trae el editor de YouTube con IA, por ejemplo, en `motor/node_modules/.remotion/chrome-headless-shell/.../chrome-headless-shell`).

```
CH="/ruta/a/chrome"          # o: CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
F="file://$PWD/index.html"
mkdir -p gate

# 1 · Escritorio con JS (hero asentado después de las animaciones)
"$CH" --headless=new --disable-gpu --hide-scrollbars --no-sandbox --user-data-dir=/tmp/g1 \
  --window-size=1280,900 --virtual-time-budget=8000 --screenshot=gate/desktop-js.png "$F"

# 2 · Celular con JS
"$CH" --headless=new --disable-gpu --hide-scrollbars --no-sandbox --user-data-dir=/tmp/g2 \
  --window-size=375,812 --force-device-scale-factor=2 --virtual-time-budget=8000 --screenshot=gate/movil-js.png "$F"

# 3 · Sin JS (estructura y SEO): una copia sin <script> (menos el JSON-LD) y sin el hero a pantalla completa, alta
python3 - <<'EOF'
import re;t=open('index.html',encoding='utf-8').read()
t=re.sub(r'<script(?! type="application/ld\+json")[^>]*>.*?</script>','',t,flags=re.S)
t=t.replace('</style>','.hero{min-height:auto!important}.hz{height:auto!important}</style>')
open('/tmp/sinjs.html','w',encoding='utf-8').write(t)
EOF
"$CH" --headless=new --disable-gpu --hide-scrollbars --no-sandbox --user-data-dir=/tmp/g3 \
  --window-size=1280,3000 --screenshot=gate/secciones-sinjs.png file:///tmp/sinjs.html
"$CH" --headless=new --disable-gpu --hide-scrollbars --no-sandbox --user-data-dir=/tmp/g4 \
  --window-size=375,3600 --screenshot=gate/secciones-movil-sinjs.png file:///tmp/sinjs.html
```

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
- [ ] Scroll con rueda fluido en cualquier punto de la página (abrirla en Chrome y probar): si pesa, hay backdrop-filter en la nav o gsap.to dentro de mousemove.
- [ ] Capturas guardadas en `gate/`: son el «después» del video.
