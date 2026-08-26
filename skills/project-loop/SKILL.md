---
name: project-loop
description: >-
  Meta-orquestador del arsenal. Lee .loop/state.md y dispara la skill de la etapa
  actual, encadenando Ejecución → Revisión → Test → (Corrección) → siguiente tarea
  hasta agotar el plan. Full-auto: para solo al fallar o al terminar. Trigger con
  "corre el loop", "automatiza el ciclo", "sigue con el proyecto", "avanza solo".
argument-hint: [ruta-del-proyecto]
version: 0.3.0
disable-model-invocation: true
disallowed-tools: AskUserQuestion
---

# project-loop — Meta-orquestador

Eres el driver del arsenal **proyecto-loop**. No implementas tú: **orquestas** las
skills de cada etapa leyendo y actualizando `.loop/state.md`.

## Modo
- **Autonomía: full-auto** (default, ver `state.md`). Avanza sin pedir permiso entre
  etapas. **Te detienes solo en dos casos:** (a) un fallo que el sub-bucle de
  corrección no logra resolver tras reintentos razonables, o (b) se agota el plan.
- Si `state.md` dice `autonomía = checkpoint-tras-review`, párate tras cada revisión
  a esperar el OK del usuario antes de testear/seguir.

## 0. Arranque
- Lee `.loop/state.md`. Si no existe, no hay proyecto inicializado → sugiere `project-init`.
- Determina la `etapa` actual y la `tarea_activa`.

## 1. Máquina de estados (encadena según la etapa)
Dispara la skill correspondiente y, al volver, relee `state.md` y continúa:

| etapa actual | skill que disparas | al terminar pasas a |
|--------------|--------------------|---------------------|
| inicio | `project-init` | analisis |
| analisis | `requirements-analysis` | plan |
| plan | `plan-architect` | reglas |
| reglas | `loop-rules` (saltear si `.claude/rules/` ya tiene contenido) | ejecucion |
| ejecucion | `code-exec` (siguiente tarea) | revision |
| revision | `engineering:code-review`; **si la tarea es de UI** también `design:design-critique` + `accesslint` + `web-design-guidelines` (web) / `react-native-best-practices` (mobile) → hallazgos a `review-log.md` | test |
| test | correr la suite de la tarea (`engineering:testing-strategy` / runner) | correccion si rojo, si verde → cerrar tarea |
| correccion | `fix-loop` | test (reverificar) |

### Reglas del bucle interno (la clave del loop)
- **Ejecución → Revisión → Test.** Si Revisión deja hallazgos o Test queda en rojo
  → entra `fix-loop` → vuelve a Test. Repite hasta verde.
- Cuando una tarea queda **verde y sin hallazgos abiertos**: márcala `[x]` en
  `plan.md`, limpia `tarea_activa`, y toma la **siguiente** tarea pendiente
  (deps satisfechas) → vuelve a `ejecucion`.
- **Revisión secuencial, no simultánea:** corre cada revisor como paso separado con
  output a `review-log.md`. En web: `web-design-guidelines` + `accesslint`. En mobile:
  `react-native-best-practices` + auditoría a11y. Las tareas de UI suman `design:design-critique`.

## 2. Estética y diseño (de primera clase, no incidental)
- El **design system** se construye temprano (primera tarea de UI) y se documenta en
  `.loop/design-system.md`. Toda pantalla lo reusa; **nada de estilos ad-hoc**.
- La **dirección estética** se fija UNA vez en `state.md` (`aesthetic`): `frontend-design`
  manda, `design-taste-frontend` ajusta parámetros, `ui-ux-pro-max` es consulta. No compiten por tarea.
- En `code-exec`, las tareas de UI **invocan explícitamente** las skills de diseño y su
  "done" exige **calidad visual**; en Revisión pasan `design:design-critique`.
- Si te salteás esto, el loop produce UI funcional pero **plana**: el diseño es parte del "done".

## 3. Guardas anti-bucle infinito
- Lleva la cuenta `iteracion` por tarea en `state.md`. Si una tarea no pasa a verde
  tras varios ciclos de corrección, **detente** y reporta al usuario el bloqueo
  (hallazgos abiertos, último error de test, hipótesis), marcando la tarea `[!]`.

## 4. Cierre
- Cuando no quedan tareas `[ ]` en `plan.md`: pon **etapa = entrega**, resume lo
  hecho (tareas cerradas, ADRs, hallazgos resueltos) y **sugiere `deploy-checklist`**,
  más `documentation` y `standup`/retro según corresponda.
- Mantén la bitácora de `state.md` actualizada en cada transición para que el loop
  sea siempre reanudable.
