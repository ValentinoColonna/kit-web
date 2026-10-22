# Ofrecerle la web al dueño

La web nueva abre la conversación; lo que se vende después es dejarla publicada con sus fotos, sus datos y su dominio. Este paso arma los mensajes con los datos reales de la auditoría. **Los manda la persona, nunca Claude.**

## Antes de escribir
- **La web de muestra se publica sin aparecer en Google:** mientras el dueño no diga que sí, el `index.html` lleva `<meta name="robots" content="noindex">` en el `<head>`. Se saca cuando acepta.
- **Es una propuesta, y se dice así.** No va en su dominio, no reemplaza su web y no se comparte con nadie más.
- **Si dice que no, se borra de Netlify** (Site configuration → Delete this site).
- **A quién:** al WhatsApp o al email que el negocio publica para atender. No a números personales que no publicó.
- **Mirá vos la web vieja en tu celular** antes del primer mensaje: lo que decís tiene que ser lo que viste.
- **Cómo firmás y qué incluye tu servicio:** Claude te lo pregunta para completar `[TU NOMBRE]` y `[LO QUE INCLUYE]`; el precio lo podés dejar en blanco.

## Los mensajes
Cortos, uno por vez y en la voz de quien los manda. Los `[ ]` se completan con los datos de `auditoria.md`, del brief y de la publicación. Claude los deja en `webs/<negocio>/mensajes.md`.

**1 · Primer contacto (sin link):**
> Hola, [nombre o «buenas»]. Soy [TU NOMBRE]. Estuve mirando la web de [negocio] desde el celular y encontré tres cosas que les pueden estar costando consultas: [hallazgo 1], [hallazgo 2] y [hallazgo 3]. Les armé una versión nueva para que vean cómo quedaría. ¿Se la paso?

**2 · Con el link (cuando responde, o si conviene mandarlo de una):**
> Es esta: [link de la muestra]. Abrila en el celular: [lo que resuelve, por ejemplo «WhatsApp a un toque, horarios y la dirección con el mapa»]. Es una propuesta: no está en su dominio ni reemplaza nada hasta que ustedes digan.

**3 · Seguimiento (a los 3 o 4 días, sin respuesta):**
> Hola, [nombre]. ¿Pudieron mirar la web que les armé? Si les sirve, la dejamos andando esta semana con sus fotos.

**4 · Último mensaje (a la semana del anterior, sin respuesta):**
> Les escribo por última vez por la web. Si ahora no es el momento, ningún problema; si más adelante les sirve, me avisan.

Después del cuarto no se insiste.

## Respuestas a las preguntas de siempre
- **«¿Cuánto sale?»** → «Dejarla publicada en su dominio, con sus fotos y sus datos, sale [TU PRECIO]. Incluye [LO QUE INCLUYE: por ejemplo, los ajustes que pidan, la publicación y la medición del antes y el después].» El precio lo pone cada uno: el kit no lo sugiere.
- **«¿Qué tengo que hacer yo?»** → «Mandarme fotos del local y de [productos, platos, unidades] y confirmar los datos. El resto lo hago yo.»
- **«¿Y mi web de ahora / mi dominio?»** → «La web actual sigue igual hasta que ustedes digan. Antes de cambiar nada guardo una copia.»
- **«¿Esto me va a traer clientes?»** → «Les saca obstáculos: que se lea bien en el celular, que puedan escribirles a un toque y que Google entienda dónde están. Ventas no le puedo prometer a nadie.»
- **«No me interesa»** → «Gracias por mirarla. La borro.» Y se borra.

## Reglas
- Antes de nombrar un hallazgo, comprobalo a mano en la web del negocio: el auditor es heurístico (solo lee el HTML) y puede equivocarse. Un «no tienen WhatsApp» que es falso quema la conversación.
- Solo hallazgos reales de la auditoría. Nada inventado: ni cifras, ni casos, ni «otros negocios de la zona ya lo hicieron».
- Sin urgencia ni escasez inventadas («solo esta semana», «quedan dos lugares»).
- Sin promesas de ventas ni de posiciones en Google.
- Un canal por vez y como mucho cuatro mensajes. Un «no» se respeta.
