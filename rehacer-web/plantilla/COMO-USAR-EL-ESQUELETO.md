# Cómo usar los esqueletos (para que cualquier modelo rinda igual)

En esta carpeta hay **cinco esqueletos**. Los cinco traen la mecánica del scroll hecha y probada con el gate visual: GSAP y ScrollTrigger, una sección fija, contadores, botones magnéticos, la web completa sin JavaScript y sin animaciones si la persona las tiene desactivadas. También comparten la estructura: los mismos nombres de fotos, el catálogo, los colores en variables y las fuentes en dos variables. Lo que cambia es el lenguaje visual: cómo se arma el hero, el orden de las secciones, la tipografía, el ritmo y el tipo de animación. Así, dos webs hechas con el kit no salen iguales.

Un modelo chico no tiene que inventar GSAP: tiene que **completar slots** (`{{…}}`) y **adaptar secciones al rubro**.

## Los cinco

| Esqueleto | Archivo | Cómo se ve | Rubros recomendados | Lo que lo hace propio |
|---|---|---|---|---|
| **Noche** | `esqueleto-espectaculo.html` | Oscuro y técnico; sans geométrica pesada | Concesionaria, taller, gomería, servicio técnico, transporte, oficios | Titular con máscara; un faro que recorre la ruta; servicios en una sección horizontal fija; una garantía que se firma sola; una galería que desfila y se inclina con el mouse |
| **Mantel** | `esqueleto-mantel.html` | Papel cálido y serif editorial | Restaurante, bodegón, café, panadería, heladería, catering | Una foto en arco que se abre a pantalla completa (sección fija); un manifiesto que se enciende palabra por palabra; la carta con una foto que sigue al mouse; un ticket que se imprime; un telón que se abre; polaroids sobre un mantel a cuadros; el mapa en un plato |
| **Aire** | `esqueleto-aire.html` | Blanco frío, sans liviana, mucho espacio | Consultorio, odontología, kinesiología, veterinaria, estudio contable o jurídico, inmobiliaria | Una tarjeta de turno que se confirma sola; especialidades con una columna fija, un índice y una barra de avance; pasos que se trazan; un mosaico que se destapa; el recorrido hasta el pin; el horario de hoy resaltado |
| **Pulso** | `esqueleto-pulso.html` | Negro y un acento eléctrico; tipografía condensada gigante; fotos en duotono | Gimnasio, crossfit, barbería, peluquería, estética, tatuajes, danza | Letras que caen; cintas cruzadas que se tuercen con la velocidad del scroll; planes que se apilan (sección fija); un bloque que cambia de color; números que se llenan; antes y después deslizable; los horarios en un tablero de aeropuerto |
| **Vidriera** | `esqueleto-vidriera.html` | Claro teñido, bordes gruesos, sombras duras, stickers | Tienda, vivero, florería, ferretería, librería, bazar, dietética, ropa | Un mosaico que se arma solo; un cartel que dice ABIERTO o CERRADO según el horario real; filtros por categoría; «sumar a la consulta», que arma un solo WhatsApp con varios productos; una vidriera giratoria en 3D (sección fija); un toldo que se despliega |

Orden de las secciones de cada uno:
- **Noche:** hero · marquee · qué hacemos (horizontal) · catálogo · garantías · salón · galería · dónde · contacto.
- **Mantel:** hero con la ventana · la casa · la carta · por qué venir (ticket) · el salón (telón) · la mesa (polaroids) · dónde (plato) · contacto.
- **Aire:** hero partido · barra de datos · especialidades · quién atiende (opcional) · cómo pedir turno · por qué elegirnos · el lugar · galería · dónde · preguntas frecuentes (opcional) · contacto.
- **Pulso:** hero tipográfico · cintas · planes · por qué (bloque de color) · antes y después (opcional) · horarios (tablero) · galería · dónde · contacto final.
- **Vidriera:** aviso y hero en mosaico · productos con filtros · la vidriera en 3D · el local (toldo) · motivos en stickers · dónde · contacto.

## Cuál usar
1. **El recomendado del rubro** (la tabla de arriba y la de `SKILL.md`, paso 4). Si el rubro no está, el más parecido: un bar nocturno va con Noche o Pulso, una óptica con Aire o Vidriera.
2. **Se ofrece, no se impone:** en la ronda 2 del brief va la pregunta «¿Qué estilo de página?», con el recomendado primero y dos alternativas que también le queden bien.
3. **Que no se repita:** si en `webs/` ya hay una web del mismo rubro hecha con el recomendado (lo dice su `brief.md`), recomendá otro. Dentro del mismo esqueleto también cambian la paleta (la del negocio) y el par de fuentes.
4. **Cualquier esqueleto sirve para cualquier rubro:** el rubro decide el recomendado, no prohíbe los demás. Una cafetería de especialidad puede ir con Vidriera y un estudio de tatuajes con Noche.

## Prompt corto (para Claude con cualquier modelo, ChatGPT o Codex)

```
Tomá el archivo esqueleto-<nombre>.html. Completá todos los slots {{...}} con los datos del brief que te paso abajo. Lo que el brief no tenga, dejalo como [PLACEHOLDER] visible. Repetí el bloque del catálogo por cada ítem real. Adaptá al rubro: renombrá secciones, sacá las que no apliquen y, si el negocio tiene un momento firma más propio que el del esqueleto, reemplazalo con los mismos recursos (CSS y GSAP que ya están en el archivo). No agregues librerías y no toques los scripts, salvo para adaptar nombres de clases que renombres. Elegí la paleta del negocio (nunca la de quien hace la página), sin #000 ni #fff puros, y uno de los pares de fuentes de COMO-USAR-EL-ESQUELETO.md. Al terminar, borrá los comentarios de ayuda (<!-- … -->). Devolveme el index.html completo y la lista de slots que quedaron como placeholder.
```

Después: `python3 rehacer-web/scripts/validar_sitio.py webs/<negocio>/index.html`, que marca si quedó algún `{{…}}`, y el gate visual (`rehacer-web/references/gate-visual.md`). Con Claude Code no hace falta pegar este prompt: el kit lo hace solo cuando escribís «hola». La receta completa, para construir desde cero, está en `rehacer-web/references/prompt-web-nueva-espectaculo.md`.

## Factores variables y paletas (1.5.1)

Para que dos webs del mismo esqueleto no se vean iguales, los cinco traen al final del `<style>` el mismo bloque `variar:inicio … variar:fin`. Lo activan dos slots, y los llena `scripts/variar.py --esqueleto <nombre> --rubro "<rubro>"`:
- `{{VARIACION}}` en `<body>`: los atributos `data-btn` (pildora, recto, corte, subrayado, grueso), `data-cta` (izq, centro, fijo: la barra de WhatsApp a lo ancho abajo en el celular), `data-esq` (0, chica, grande), `data-marco` de las fotos (recto, arco, circulo, diagonal, organico), `data-sep` entre secciones (recto, ola, diagonal, zigzag) y `data-hero`.
- `{{PALETA_ROOT}}` en el bloque: texto, texto secundario, el color «apagado» (`--muted`), los acentos usados como texto (`--acc-t`, `--acc2-t`) y el texto sobre el secundario (`--sobre-acc2`), todos ya ajustados a 4,5:1 de contraste sobre los fondos donde se apoyan, más la superficie de la paleta sorteada. Los slots de color de siempre (`FONDO`, `ACENTO`…) se llenan con los valores que imprime el mismo script.

Hero que aplica a cada uno sin romper su animación: **Aire** izq, centro, partido · **Noche** izq, centro, fondo · **Mantel** izq, centro · **Vidriera** izq, centro · **Pulso** solo izq (las letras gigantes ya ocupan el ancho). Las paletas (60, en `references/paletas.json`) se filtran por esqueleto: claras para Aire, Mantel y Vidriera; oscuras para Noche y Pulso. Con los colores del negocio, se borra `{{PALETA_ROOT}}` y se usan los suyos: los factores se mantienen. Si se borra `{{VARIACION}}`, el esqueleto se ve como en la 1.5.

## Lo que tienen en común los cinco

**Las fotos tienen nombres fijos** (`references/imagenes.md`): `hero-salon.jpg`, `salon.jpg`, `galeria-01.jpg` a `galeria-05.jpg` y `catalogo-01.jpg` en adelante. Pulso suma `antes.jpg` y `despues.jpg` para el antes y después. Si un archivo falta, el marco muestra un panel con su `data-nombre`. Para publicar, ese texto se cambia por uno para el público.

**La paleta se cambia en un solo lugar.** Todos los colores salen de las variables de `:root`, al principio del `<style>`, y los slots se llaman igual en los cinco. Cada color de la marca va dos veces: en hex (`--acc: #1e5bb8`) y en r,g,b (`--acc-rgb: 30,91,184`), porque los velos y las sombras usan `rgba(var(--acc-rgb), .3)`. Se completan `--bg`/`--bg-rgb`, `--bg2`, `--acc`/`--acc-rgb`, `--acc-claro`, `--sobre-acc` y `--acc2`/`--acc2-rgb`. Noche y Pulso son de fondo oscuro; Mantel, Aire y Vidriera, de fondo claro. La tinta (`--ink`) ya viene pensada para cada fondo. No hay colores sueltos en el resto del archivo.

**Las fuentes se cambian en dos lugares:** el `<link>` de Google Fonts y las variables `--f-display` (titulares) y `--f-texto` (texto). Cada esqueleto trae un par por defecto. Los otros pares de la tabla también le quedan, y todos los links responden; usá el link tal cual, porque si pedís un peso que la fuente no tiene, Google devuelve error.

| Esqueleto | Por defecto | Alternativa 1 | Alternativa 2 |
|---|---|---|---|
| Noche | `family=Sora:wght@400;600;800&family=Inter:wght@400;500;600` | `family=Space+Grotesk:wght@400..700&family=IBM+Plex+Sans:wght@400;500;600` | `family=Outfit:wght@400..800&family=Inter:wght@400;500;600` |
| Mantel | `family=Fraunces:ital,opsz,wght@0,9..144,400..800;1,9..144,400..700&family=Work+Sans:wght@400;500;600` | `family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Karla:wght@400;500;600` | `family=Cormorant+Garamond:ital,wght@0,400..700;1,400..700&family=Jost:wght@400;500;600` |
| Aire | `family=Manrope:wght@400..800&family=Source+Sans+3:wght@400;500;600` | `family=Plus+Jakarta+Sans:wght@400..800&family=Inter:wght@400;500;600` | `family=Lexend:wght@300..700&family=Nunito+Sans:wght@400;600;700` |
| Pulso | `family=Anton&family=Archivo:wght@400;500;600;700` | `family=Bebas+Neue&family=Barlow:wght@400;500;600;700` | `family=Oswald:wght@500..700&family=Manrope:wght@400;500;600` |
| Vidriera | `family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Figtree:wght@400;500;600;700` | `family=Syne:wght@600..800&family=Manrope:wght@400;500;600` | `family=Unbounded:wght@500..800&family=Nunito+Sans:wght@400;600;700` |

El link completo es `https://fonts.googleapis.com/css2?` + la columna + `&display=swap`. En las variables va el nombre de la familia entre comillas: `--f-display:"Playfair Display",Georgia,serif`.

**Los slots se llaman igual en los cinco:** `NOMBRE`, `WHATSAPP`, `MENSAJE_PREARMADO_URLENCODED`, `TELEFONO_TEL`, `DIRECCION_CORTA`, `HORARIOS` (en Vidriera, además, `ZONA_HORARIA`: la del negocio, p. ej. `America/Argentina/Buenos_Aires`; el cartel ABIERTO/CERRADO la usa y entiende los horarios que cruzan la medianoche), `CONTADOR_1_NUMERO`, `ITEM_1_NOMBRE`, `ALT_GALERIA_1` y el resto. Lo que cambia es dónde aparecen.

**Los horarios llevan siempre el mismo formato:** una fila `<div><span>Lunes a viernes</span><b>9 a 19</b></div>` por línea. Aire y Vidriera además leen `data-dias` (0 domingo … 6 sábado) para resaltar «hoy». Vidriera lee también `data-abre` y `data-cierra` en 24 h, y con eso el cartel dice ABIERTO o CERRADO.

**Lo que se repite por cada ítem real:**
- el ítem del catálogo, en los cinco (en Aire y Pulso el número sale solo);
- la tarjeta de servicio, en Noche (el número, 01, 02…, va a mano);
- la categoría de la carta, en Mantel;
- el profesional y la pregunta, en Aire;
- el botón de filtro, en Vidriera.

**Lo que se borra si no aplica:**
- el fondo del hero sin una foto de 1200 px o más (Noche);
- los contadores sin números reales (en los cinco);
- quién atiende y las preguntas frecuentes, si el dueño no dio esos datos (Aire);
- el antes y después sin fotos reales de un trabajo y sin permiso de quien aparece (Pulso);
- los filtros, si no hay categorías (Vidriera).

**Al terminar** se borran los comentarios de ayuda `<!-- … -->`: son para quien completa el esqueleto, y la página publicada no los necesita. Así queda por debajo de 40 KB sin imágenes. Después se valida y se pasa el gate.
