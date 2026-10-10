---
name: loop-review
description: >-
  Etapa de revisión del loop. Corre en un subagente los revisores que correspondan a
  la tarea activa (código, y diseño/a11y si es de UI), vuelca los hallazgos en
  .loop/review-log.md y devuelve solo un resumen. Trigger vía project-loop tras
  code-exec, o "revisá la tarea".
model: sonnet
effort: medium
context: fork
---

# loop-review — Etapa (7) Revisión

> **Skills externas:** esta etapa invoca skills que no son del loop. Antes de usar
> cualquiera, seguí `${CLAUDE_PLUGIN_ROOT}/references/dependencias-externas.md`: si no
> está disponible en este entorno, se registra como NO VERIFICADO, nunca se saltea callada.

Revisás **la tarea activa**, no el repo. Corrés en un subagente para que la salida de
cada revisor no se acumule en el contexto del orquestador.

## 0. Reanudar
- Lee `.loop/state.md` (`tarea_activa`) y la entrada de esa tarea en `.loop/plan.md`.
- El alcance es el diff de la tarea: `git diff` contra el commit anterior al de la tarea.
  No leas archivos que el diff no toca salvo para entender una llamada concreta.

## 1. Revisores (secuenciales, nunca en paralelo)

**Tu primera acción de esta sección es una llamada a la herramienta Skill con
`engineering:code-review`.** No leas el diff a fondo antes: el revisor lo lee. Si
empezás por analizarlo vos, ya estás haciendo la revisión que no te toca.

1. **Siempre:** `engineering:code-review` sobre el diff.
2. **Si la tarea toca UI:**
   - **Web:** `web-design-guidelines` + `accesslint:audit`.
   - **Mobile:** `react-native-best-practices:react-native-best-practices` + auditoría a11y.
   - **`design:design-critique` solo si la tarea crea una pantalla nueva** o cambia su
     layout. Un ajuste de una pantalla ya criticada no la repite.
   - Las reglas `[chequeable]` de `${CLAUDE_PLUGIN_ROOT}/references/ui-patterns.md` se
     chequean contra el diff; no hace falta releer el catálogo entero si ya lo cita la tarea.

### Qué cuenta como "corrió"
Un revisor **corrió** solo si en esta corrida hiciste una llamada a la herramienta Skill
con su nombre. Nada más cuenta.

- Leer el diff vos y opinar no es `engineering:code-review`: es una **revisión propia**.
  No existe el revisor "inline". Si `review-log.md` tiene entradas anteriores que dicen
  `(inline)`, son el error que esta regla corrige: no las imites.
- Si un revisor no está disponible, o no lo invocaste, va una línea `NO VERIFICADO` en
  `review-log.md` con lo concreto que quedó sin evaluar
  (`${CLAUDE_PLUGIN_ROOT}/references/dependencias-externas.md`).
- Lo que encuentres por tu cuenta se registra igual, con fuente **`revisión propia`**.
  Nunca con el nombre de una skill que no invocaste.

## 2. Registrar
- Cada hallazgo va a `.loop/review-log.md` → **Abiertos**, con id `H-00X`, severidad,
  fuente, `file:line` y fix sugerido.
- Unificá duplicados entre revisores: un mismo problema reportado por dos fuentes es
  **un** hallazgo.
- Descartá lo que sea estilo puro que el linter ya cubre.

## 3. Cierre
- Actualiza `state.md`: `ultima_skill = loop-review`, **etapa = test**, bitácora.
- **Devolvé solo un resumen de 10 líneas como máximo**, contando la de las skills:
  cantidad de hallazgos por severidad, los ids, una línea por cada hallazgo alto o medio,
  y qué quedó `NO VERIFICADO`. Los bajos van solo por id. El detalle vive en
  `review-log.md`; no lo repitas.
- **La última línea del resumen es obligatoria y literal**, con los nombres exactos que
  pasaste a la herramienta Skill:

  `Skills invocadas: <lista separada por comas, o "ninguna">`

  `project-loop` la lee. Sin esa línea, o con una skill que no invocaste, la revisión
  cuenta como no verificada.
