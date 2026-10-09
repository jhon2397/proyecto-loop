---
name: fix-loop
description: >-
  Lee los hallazgos de revisión y la salida de tests, los prioriza por severidad,
  aplica las correcciones (apoyándose en engineering:debug para fallos no obvios) y
  re-dispara el test. Trigger cuando una revisión deja hallazgos o los tests están
  en rojo, o "corrige los hallazgos", "arregla el test". Es la etapa (6) Corrección
  del arsenal proyecto-loop.
context: fork
model: sonnet
effort: medium
---

# fix-loop — Etapa (6) Corrección

Cierras el sub-bucle Test/Revisión → Corrección → Test hasta que la tarea queda verde.

## 0. Reanudar
- Lee `.loop/state.md`, `.loop/review-log.md` y la última salida de tests.
- Identifica la `tarea_activa` y sus hallazgos abiertos (`H-00X`).
- Si existe `.loop/diagnostico-<TAREA>.md`, léelo primero: es el diagnóstico de
  `dev-substrate:deep-debugger` que el orquestador pidió al escalar. Partí de su causa
  raíz en vez de volver a investigar desde cero.
- De los logs de test leé solo la parte que falla (`tail`, `grep` del error), no el
  archivo entero.

## 1. Priorizar
- Ordena los hallazgos por severidad: **crítica → alta → media → baja**.
- Agrupa los que comparten causa raíz para no parchear el mismo bug dos veces.

## 2. Corregir
- Para cada hallazgo, aplica el fix mínimo y correcto (no refactors oportunistas
  salvo que el hallazgo lo pida).
- Para **fallos no obvios** (intermitentes, "funciona en local pero no en CI",
  causa poco clara) usa el método de 4 fases de Superpowers o `engineering:debug`:
  reproducir → aislar → diagnosticar → corregir. No adivines.
- Registra cada fix en `review-log.md` (mueve `H-00X` a **Cerrados** con commit y
  cómo se verificó).

## 3. Re-test
- Vuelve a correr los tests afectados (idealmente la suite relacionada a la tarea).
- **Si vuelve a fallar:** incrementa `iteracion` en `state.md`, dejá etapa `correccion`
  y devolvé control. **No iteres dentro de esta corrida**: el escalado y el tope de
  vueltas los decide `project-loop`. No avances hasta verde.
- **Si pasa:** continúa al cierre.

## 4. Commit
- `fix(T-00X): <qué se corrigió>`. Atómico por causa raíz cuando sea posible.

## 5. Cierre
- Actualiza `state.md`: `ultima_skill = fix-loop`, **etapa = test** (para reverificar)
  o, si ya reverificaste y está verde, deja listo para cerrar la tarea, bitácora.
- Si todos los hallazgos de la tarea están cerrados y los tests pasan, indica que la
  tarea puede marcarse `[x]` y devolver control a `project-loop`.
- **Devolvé solo un resumen** (máx. ~10 líneas): hallazgos cerrados y abiertos, commits,
  y si el re-test quedó verde o rojo (con el error principal en una línea).
