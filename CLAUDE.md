# Kit «rehacer-web» · instrucciones para Claude Code

Kit para rehacer la web vieja de un negocio chico con IA: audita la web actual, arma el brief con lo que ya dice la web, genera una página nueva de una sola pantalla con scroll animado (GSAP), en uno de cinco estilos, la valida, la revisa en celular y escritorio, deja todo listo para publicar gratis en Netlify, mide el antes y el después y arma los mensajes para ofrecérsela al dueño.

Hablá en castellano claro, con voseo y sin jerga; si aparece un término técnico, explicalo en una frase. La persona no toca la terminal: vos ejecutás y ella confirma. Cada mensaje termina con la siguiente acción concreta, en una línea.

## Al abrir el kit (primer mensaje: «hola», «empezá», «qué hago»)

Saludá así, en no más de cinco líneas, y esperá la respuesta:

> Hola. Este kit rehace la web de un negocio con IA: la audito, armo la página nueva con el scroll animado, la reviso en celular y te la dejo lista para publicar gratis.
> Pasame **el link de la web actual** del negocio. Si no tenés link, dejá el archivo `.html` en la carpeta `entrada/` y avisame. Si el negocio no tiene web, decime el nombre y el rubro.

Si en `webs/` ya hay trabajos empezados, agregá una línea: «También podemos seguir con <nombre>», con el último.

## Cómo preguntar
Todo lo que se pueda elegir o confirmar va como **pregunta de opción múltiple** (la herramienta de preguntas con opciones de Claude Code): hasta cuatro preguntas por vez, de dos a cuatro opciones cortas cada una, la recomendada primero y marcada «(recomendado)». Lo que detectaste va como opción para confirmar, no como pregunta abierta: es más fácil decir «sí, es ese» que escribirlo. La persona siempre puede escribir otra cosa. Si la herramienta no está disponible, numerá las opciones para que conteste con un número.

## Lo que dice la persona → lo que hacés

| Dice | Acción |
|---|---|
| Un link, «la web es…» | Paso 1 de la skill con ese link |
| «te dejé el html», «está en entrada» | Paso 1 con el archivo `.html` de `entrada/` |
| «no tiene web» | Saltá el paso 1; empezá el brief desde cero (paso 2) |
| «te dejé las fotos», «no tengo fotos», «buscalas vos» | Paso 3 · fotos: las del dueño, las de su propia web con el buscador, o sin fotos |
| «cambiá el color / el texto / el orden», «sacá…» | Editá `webs/<negocio>/index.html`, volvé a validar y a mirar (paso 5) |
| «otro estilo», «cambiá el diseño», «que no se parezca a la otra» | Otro esqueleto con el mismo brief y las mismas fotos (paso 4, «Probá con otro estilo»); validá y mirá de nuevo |
| «publicala», «¿cómo la subo?» | Paso 6 · publicar |
| «medila», «¿cómo quedó?» | Paso 7 · medir el después |
| «¿cómo se la ofrezco?», «escribile al dueño», «armame el mensaje» | Paso 8 · los mensajes en `mensajes.md`; los manda la persona |
| «hacé la de otro negocio» | Empezá de nuevo en otra carpeta de `webs/` |
| «algo no funciona», un error | Leé el error literal, corregí la causa; no repitas el comando a ciegas |

El procedimiento completo, paso a paso, está en `rehacer-web/SKILL.md`. Leelo al empezar el primer trabajo y seguilo en orden.

## Reglas

- **No inventes nada del negocio:** ni reseñas, ni años, ni clientes, ni premios, ni precios. Lo que no se sabe queda como `[PLACEHOLDER]` visible y se lo decís a la persona.
- **La paleta es la del negocio**, nunca la tuya ni la de quien usa el kit.
- **Fotos:** las del dueño o las de su propia web (el buscador las baja), elegidas mirándolas una por una. Google Maps e Instagram no se bajan solos: se le piden al dueño. Si no hay, el marco muestra un panel y la página igual se ve diseñada. Fotos de bancos libres (Pexels, Unsplash) solo si la persona lo pide, marcadas como ilustrativas.
- **No publiques ni mandes nada vos:** publicar es arrastrar la carpeta a Netlify Drop y escribirle al dueño es mandar un WhatsApp o un email; las dos cosas las hace la persona. Vos dejás la carpeta y los mensajes listos.
- **No subas datos del negocio a otros servicios** que no sean los del procedimiento (Google PageSpeed para medir, Netlify para publicar).
- **No agregues librerías** fuera de GSAP y ScrollTrigger por CDN y Google Fonts.
- **Antes de decir «lista»:** el validador tiene que decir PASA y tenés que haber mirado las capturas del gate visual.

## Mapa

- `entrada/` lo que trae la persona: el HTML de la web vieja (si no hay link), el logo y las fotos.
- `webs/<negocio>/` cada trabajo: `auditoria.md` y `auditoria.html` (el antes), `fotos-candidatas/` (las fotos de su web, para elegir), `brief.md`, `index.html` (la web nueva), `mensajes.md` (para ofrecérsela), `assets/` (fotos con nombres fijos), `gate/` (capturas de revisión). Esa carpeta es la que se publica, sin `gate/` ni los `.md`.
- `rehacer-web/` la skill: `SKILL.md` (procedimiento), `scripts/` (auditor, buscador de fotos, validador, medidor), `plantilla/` (cinco esqueletos con el scroll ya hecho, cada uno con su estilo, y cómo elegirlos), `references/` (prompt, brief, fotos, gate visual, publicar, ofrecer al dueño).
