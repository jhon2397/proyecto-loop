---
name: project-loop
description: >-
  Meta-orquestador del arsenal. Lee .loop/state.md y dispara la skill de la etapa
  actual, encadenando Ejecución → Revisión → Test → (Corrección) → siguiente tarea
  hasta agotar el plan. Full-auto: para solo al fallar o al terminar. Trigger con
  "corre el loop", "automatiza el ciclo", "sigue con el proyecto", "avanza solo".
effort: medium
model: sonnet
argument-hint: [ruta-del-proyecto]
version: 0.8.1
disable-model-invocation: true
disallowed-tools: AskUserQuestion
---

# project-loop — Meta-orquestador

Eres el driver del arsenal **proyecto-loop**. No implementas tú: **orquestas** las
skills de cada etapa leyendo y actualizando `.loop/state.md`.

## Modo
- **Autonomía: full-auto** (default, ver `state.md`). Avanza sin pedir permiso entre
  etapas. **Te detienes solo en tres casos:** (a) un fallo que el sub-bucle de
  corrección no logra resolver tras reintentos razonables, (b) se agota el plan, o
  (c) `etapa = diseno-revision`: el diseño está listo y espera que una persona lo
  revise. Ese alto **no es una falla**: reportá el link de Figma y qué se armó, y
  retomá en `plan` cuando el usuario apruebe.
- Si `state.md` dice `autonomía = checkpoint-tras-review`, párate tras cada revisión
  a esperar el OK del usuario antes de testear/seguir.

## 0. Arranque
- Lee `.loop/state.md`. Si no existe, no hay proyecto inicializado → sugiere `project-init`.
- Determina la `etapa` actual y la `tarea_activa`.
- **Comprobación de dispositivos (una sola vez por corrida).** Si `state.md` dice
  `mobile: si`, verificá que los cuatro dispositivos de la matriz **puedan** arrancar —
  de a pares, no los cuatro juntos — y **apagalos al terminar la comprobación**. No los
  dejes vivos: cuatro emuladores simultáneos agotan la memoria de la máquina y los builds
  que la verificación necesita no entran.
- Registrá el resultado en `state.md` como `matriz_dispositivos`. **Si alguno no arranca,
  la corrida no empieza**: es preferible fallar acá que descubrirlo en la tarea 12.

## 1. Máquina de estados (encadena según la etapa)
Dispara la skill correspondiente y, al volver, relee `state.md` y continúa:

| etapa actual | skill que disparas | al terminar pasas a |
|--------------|--------------------|---------------------|
| inicio | `project-init` | analisis |
| analisis | `requirements-analysis` | diseno |
| diseno | `loop-design` (saltear si el proyecto no tiene UI) | diseno-revision |
| diseno-revision | — **alto de checkpoint**: entregá el link de Figma y esperá | plan |
| plan | `plan-architect` | reglas |
| reglas | `loop-rules` (saltear si `.claude/rules/` ya tiene contenido) | ejecucion |
| ejecucion | `code-exec` (siguiente tarea) | revision |
| revision | `loop-review` (subagente: `engineering:code-review` y, si la tarea es de UI, los revisores de diseño/a11y) → hallazgos a `review-log.md` | test |
| test | `loop-verify` | correccion si rojo · si verde y la tarea toca auth/tenant/dinero/secretos → seguridad · si no, cerrar tarea |
| seguridad | `loop-security` | correccion si hay hallazgos, si no cerrar tarea |
| correccion | `fix-loop` | test (reverificar) |

### Reglas del bucle interno (la clave del loop)
- **Ejecución → Revisión → Test.** Si Revisión deja hallazgos o Test queda en rojo
  → entra `fix-loop` → vuelve a Test. Repite hasta verde.
- Cuando una tarea queda **verde y sin hallazgos abiertos**: márcala `[x]` en
  `plan.md`, limpia `tarea_activa`, y toma la **siguiente** tarea pendiente
  (deps satisfechas) → vuelve a `ejecucion`.
- **Revisión secuencial, no simultánea:** la hace `loop-review` dentro de su subagente,
  un revisor por vez, con output a `review-log.md`. Vos recibís solo el resumen.

## 2. Estética y diseño (de primera clase, no incidental)
- El **design system** se construye temprano (primera tarea de UI) y se documenta en
  `.loop/design-system.md`. Toda pantalla lo reusa; **nada de estilos ad-hoc**.
- La **dirección estética** se fija UNA vez en `state.md` (`aesthetic`): `anthropic-skills:frontend-design`
  manda, `design-taste-frontend` ajusta parámetros, `anthropic-skills:ui-ux-pro-max` es consulta. No compiten por tarea.
- En `code-exec`, las tareas de UI **invocan explícitamente** las skills de diseño y su
  "done" exige **calidad visual**; en Revisión pasan `design:design-critique`.
- Si te salteás esto, el loop produce UI funcional pero **plana**: el diseño es parte del "done".

## 2.b Qué puede disparar el orquestador
Una skill que **vos encadenás** no puede llevar `disable-model-invocation: true`: ese
flag la reserva para invocación humana y el harness te la va a rechazar en medio del
ciclo. El flag es para **puntos de entrada** (`project-loop`, `loop-adopt`,
`loop-ship`, `loop-status`, `loop-pitch`), no para etapas.

`loop-ship` es la excepción deliberada: la **sugerís** al llegar a entrega, nunca la
disparás. Toca producción.

`loop-pitch` es la otra excepción: renderizar video es caro en tiempo y es un entregable
para humanos, no un paso del ciclo. La **sugerís** al llegar a entrega, nunca la disparás.

Si una etapa te devuelve "cannot be invoked via the Skill tool", **no repliques su
trabajo a mano**: es un error de empaquetado del arsenal. Pará y reportalo.

## 2.c Higiene de contexto (el loop corre muchas vueltas: cada token se paga N veces)
- `code-exec`, `loop-review`, `loop-verify`, `fix-loop` y `loop-security` corren en
  subagente y te devuelven **un resumen**. Trabajá con ese resumen.
- **No leas** logs de test, `review-log.md` completo ni diffs en este hilo. Si necesitás
  un dato puntual (un id de hallazgo, la etapa), leé `state.md` o hacé un `grep` dirigido.
- No re-narres lo que hizo cada etapa: una línea en la bitácora de `state.md` alcanza.

## 3. Guardas anti-bucle infinito (escalado y tope)
- `iteracion` vive en `state.md`: la incrementa `fix-loop` en cada vuelta y vos la
  ponés en 0 al tomar una tarea nueva. Leela al volver de cada `loop-verify` en rojo.
- **`iteracion = 2` y sigue en rojo → escalá.** Antes del siguiente `fix-loop`, lanzá el
  agente `dev-substrate:deep-debugger` (herramienta Agent) con la tarea, el error
  principal y las rutas de los logs. Pedile solo causa raíz, evidencia (`file:line`) y
  fix propuesto, en pocas líneas. El agente es de solo lectura: **vos** guardás esa
  respuesta en `.loop/diagnostico-<TAREA>.md`, que `fix-loop` lee al arrancar. Es la única vuelta que paga opus: las anteriores ya
  descartaron lo obvio.
- **`iteracion = 3` y sigue en rojo → detente.** Marcá la tarea `[!]` y reportá al
  usuario el bloqueo (hallazgos abiertos, último error de test, diagnóstico de
  `deep-debugger`). No hay cuarta vuelta automática.

## 4. Cierre
- Cuando no quedan tareas `[ ]` en `plan.md`: verificá primero que **el gate de arranque
  esté verde** — la matriz de cuatro si hay mobile, la web levantada si no. Recién ahí
  pon **etapa = entrega**, resume lo hecho (tareas cerradas, ADRs, hallazgos resueltos) y
  **sugiere `engineering:deploy-checklist`**, después `loop-ship`, y **`loop-pitch`** si querés la
  presentación del producto. Sumá `documentation` y `standup`/retro según corresponda.
- **`loop-ship` no la disparás vos.** Toca producción: la invoca una persona. El loop
  llega hasta sugerirla.
- Mantén la bitácora de `state.md` actualizada en cada transición para que el loop
  sea siempre reanudable.
