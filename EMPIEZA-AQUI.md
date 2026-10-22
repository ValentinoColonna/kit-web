# Empezá acá · kit «rehacer-web»

Rehacé la web de un negocio con IA: la auditás, la IA arma la página nueva con scroll animado, la revisa en celular y te la deja lista para publicar gratis.

## 3 pasos

1. **Bajá el kit y abrilo con Claude Code.** En GitHub: botón **Code → Download ZIP**, descomprimilo y abrí la carpeta con Claude Code (la app de Claude, pestaña Code, o VS Code con la extensión de Claude Code).
2. **Escribí «hola».** La primera vez, Claude Code te pregunta si confiás en la carpeta: decí que sí, así puede correr los scripts del kit. Después te pide el link de la web actual del negocio. Si no tenés link, dejá el archivo `.html` en `entrada/`; si el negocio no tiene web, decile el nombre y el rubro.
3. **Contestá lo que te pregunte y dejá las fotos en `entrada/`** si las tenés. Claude audita, te propone un estilo de página según el rubro (hay cinco), la arma, la valida y la revisa. Al final te dice qué carpeta arrastrar a Netlify Drop para publicarla y te arma los mensajes para ofrecérsela al dueño, que mandás vos.

## Qué necesitás

- Claude Code con tu cuenta de Claude. Está pensado para que alcance con Sonnet; igual, revisá siempre lo que genera.
- Python 3 (en Mac ya viene; en Windows, desde python.org, marcando «Add python.exe to PATH»). No hay que instalar nada más.
- Google Chrome, para las capturas de revisión.
- Para publicar: una cuenta gratis de Netlify (el plan gratis tiene cuotas mensuales; si se agotan, pausa el sitio).

**Si falta algo:** lo primero que hace el kit es chequear Python y Chrome, y te dice qué instalar. Sin Chrome igual podés seguir, pero la revisión de la página la hacés vos abriendo `index.html`.

## Cómo se publica
Claude te deja una carpeta `webs/<negocio>-publicar/` con solo `index.html` y las fotos. Entrá a https://app.netlify.com/drop y arrastrala. Antes de publicar, tocá vos cada botón (WhatsApp, llamar, mapa) y confirmá los datos con el dueño.

Todo lo demás está en `README.md`. No hace falta leerlo: preguntale a Claude.
