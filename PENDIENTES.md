# Pendientes conocidos (kit 1.5.3)

Lo que una auditoría externa señaló (22/10/2026) y **no se resolvió** en 1.5.3, para no seguir desarrollando el kit indefinidamente. Nada de esto impide usarlo; son límites que hay que conocer.

## Estructural
- **La skill no está en `.claude/skills/`.** El kit funciona porque `CLAUDE.md` le pide a Claude Code leer `rehacer-web/SKILL.md`; no se instala como skill invocable por sí sola. Mover la skill implicaría repensar las rutas (todas son relativas a la raíz del kit).
- **El gate visual es un bloque de shell Unix** (Mac y Linux). En Windows hay que adaptarlo (Git Bash, WSL o pedirle a Claude que lo traduzca). Tampoco hay un script de gate multiplataforma.
- **Sin SRI en los CDN:** los `<script>` de GSAP y las fuentes de Google no llevan `integrity`. El validador solo acepta cdnjs, jsdelivr y unpkg (comparando el host real), pero el contenido de esos CDN no se verifica.
- **El peso de las plantillas:** Aire y Mantel pasan los 42 KB aun sin comentarios, antes de completar contenidos. La meta documental de «menos de 40 KB» no está garantizada.

## Cobertura de pruebas
- **Las animaciones con GSAP real** (pines, reveals, el anillo 3D, parallax) no tienen prueba automática: las pruebas de `tests/` corren sin GSAP o con movimiento reducido. Se comprueban a mano en el navegador.
- **Aire** (`esqueleto-aire.html`) también resalta «hoy» en los horarios con la hora del visitante, no la del negocio, y una sola vez al cargar. Solo Vidriera tiene el cartel ABIERTO/CERRADO con zona horaria, tramos nocturnos y recálculo cada minuto.
- **El buscador de fotos no protege contra DNS rebinding** (un nombre que cambia de dirección entre la comprobación y la descarga). Valida el destino de cada solicitud y de cada redirección, pero resuelve el nombre dos veces.
- **Contraste:** se garantiza 4,5:1 en los roles de texto que generan las paletas (`variar.py --chequear`). No se audita el texto sobre fotos ni el contraste con los colores propios del negocio.
- **Sin evaluación comparativa entre modelos.** El kit está pensado para que alcance con Sonnet; no hay una evaluación guardada que lo respalde. Otras herramientas (ChatGPT, Codex) no se probaron.
- **No hay integración continua.** Las pruebas se corren a mano (`python3 -m unittest discover -s tests -v`).

## Licencias de lo externo
La licencia MIT cubre el kit, no las fotos de cada negocio, las fuentes de Google ni GSAP (que tiene su propia licencia).
