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

Revisás **la tarea activa**, no el repo. Corrés en un subagente para que la salida de
cada revisor no se acumule en el contexto del orquestador.

## 0. Reanudar
- Lee `.loop/state.md` (`tarea_activa`) y la entrada de esa tarea en `.loop/plan.md`.
- El alcance es el diff de la tarea: `git diff` contra el commit anterior al de la tarea.
  No leas archivos que el diff no toca salvo para entender una llamada concreta.

## 1. Revisores (secuenciales, nunca en paralelo)
1. **Siempre:** `engineering:code-review` sobre el diff.
2. **Si la tarea toca UI:**
   - **Web:** `web-design-guidelines` + `accesslint`.
   - **Mobile:** `react-native-best-practices` + auditoría a11y.
   - **`design:design-critique` solo si la tarea crea una pantalla nueva** o cambia su
     layout. Un ajuste de una pantalla ya criticada no la repite.
   - Las reglas `[chequeable]` de `${CLAUDE_PLUGIN_ROOT}/references/ui-patterns.md` se
     chequean contra el diff; no hace falta releer el catálogo entero si ya lo cita la tarea.

Invocá cada revisor de verdad (herramienta Skill). Si uno no está instalado, anotalo en
la bitácora y seguí con los demás: no lo reemplaces con tu opinión.

## 2. Registrar
- Cada hallazgo va a `.loop/review-log.md` → **Abiertos**, con id `H-00X`, severidad,
  fuente, `file:line` y fix sugerido.
- Unificá duplicados entre revisores: un mismo problema reportado por dos fuentes es
  **un** hallazgo.
- Descartá lo que sea estilo puro que el linter ya cubre.

## 3. Cierre
- Actualiza `state.md`: `ultima_skill = loop-review`, **etapa = test**, bitácora.
- **Devolvé solo el resumen** (máx. ~10 líneas): cantidad de hallazgos por severidad,
  los ids, y qué revisores corrieron. El detalle vive en `review-log.md`; no lo repitas.
