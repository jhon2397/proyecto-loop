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
version: 0.11.0
disable-model-invocation: true
---

# project-loop — Meta-orquestador

> **Skills externas:** esta etapa invoca skills que no son del loop. Antes de usar
> cualquiera, seguí `${CLAUDE_PLUGIN_ROOT}/references/dependencias-externas.md`: si no
> está disponible en este entorno, se registra como NO VERIFICADO, nunca se saltea callada.

Eres el driver del arsenal **proyecto-loop**. No implementas tú: **orquestas** las
skills de cada etapa leyendo y actualizando `.loop/state.md`.

## Modo
- **Autonomía: full-auto** (default, ver `state.md`). Avanza sin pedir permiso entre
  etapas. **Te detienes solo en tres casos:** (a) un fallo que el sub-bucle de
  corrección no logra resolver tras reintentos razonables, (b) se agota el plan, o
  (c) `etapa = diseno-revision`: el diseño está listo y espera que una persona lo
  revise. Ese alto **no es una falla**: reportá el link de Figma y qué se armó, y
  retomá en `presentacion` cuando el usuario apruebe.
- Si `state.md` dice `autonomía = checkpoint-tras-review`, párate tras cada revisión
  a esperar el OK del usuario antes de testear/seguir.

## Preguntas: pocas, y siempre con `AskUserQuestion`
Full-auto no significa preguntar en texto: significa preguntar poco. Solo hay tres
momentos en que le hablás al usuario esperando respuesta, y en los tres usás
`AskUserQuestion` (opciones concretas; el usuario siempre puede escribir otra):
1. **El checkpoint `diseno-revision`** — "Aprobar el diseño" / "Pedir cambios".
2. **`autonomía = checkpoint-tras-review`** — "Seguir" / "Corregir antes".
3. **Bloqueantes críticos** que deja una etapa (por ejemplo, preguntas abiertas de
   `requirements-analysis` marcadas como bloqueantes).

Por qué: el `model:` de esta skill dura un turno. Una pregunta en texto cierra el turno
y la respuesta corre con el modelo de la sesión — medido: 129 llamadas del orquestador
en opus contra 14 en sonnet, porque cada aprobación se pidió en texto. `AskUserQuestion`
no cierra el turno y el loop sigue en sonnet.

Fuera de esos tres casos no preguntes nada: decidí con el plan y `state.md`, y anotá la
decisión en la bitácora. El reporte final (plan agotado o tarea `[!]`) no es una
pregunta: es el último mensaje de la corrida.

## 0. Arranque
- Lee `.loop/state.md`. Si no existe, no hay proyecto inicializado → sugiere `project-init`.
- Determina la `etapa` actual y la `tarea_activa`.
- **Comprobación de dispositivos (una sola vez por corrida).** Si `state.md` dice
  `mobile: si`, primero mirá si el entorno **está completo** (criterio de
  `loop-verify`, sección 1.6). Son dos casos distintos y se tratan distinto:
  - **Entorno incompleto** (no puede correr los cuatro, criterio de `loop-verify`
    1.6) —por ejemplo, una sesión cloud, o una máquina con solo Android—: no es una
    falla. Registrá `matriz_dispositivos: entorno incompleto (<qué falta>)` y seguí.
    Las tareas de UI van a quedar en `[d]`.
  - **Entorno completo**: verificá que los cuatro **puedan** arrancar, de a pares
    y nunca los cuatro juntos, y apagalos al terminar. Cuatro emuladores simultáneos
    agotan la memoria. Si alguno no arranca, **la corrida no empieza**: es preferible
    fallar acá que descubrirlo en el gate de dispositivos de `loop-verify`.

## 1. Máquina de estados (encadena según la etapa)
Dispara la skill correspondiente y, al volver, relee `state.md` y continúa:

| etapa actual | skill que disparas | al terminar pasas a |
|--------------|--------------------|---------------------|
| inicio | `project-init` | analisis |
| analisis | `requirements-analysis` | diseno |
| diseno | `loop-design` (saltear si el proyecto no tiene UI) | diseno-revision |
| diseno-revision | — **alto de checkpoint**: entregá el link de Figma y esperá | presentacion |
| presentacion | `loop-presentacion` (saltear si el proyecto no tiene UI) | plan |
| plan | `plan-architect` | reglas |
| reglas | `loop-rules` (saltear si `.claude/rules/` ya tiene contenido) | ejecucion |
| ejecucion | `code-exec` (siguiente tarea) | revision |
| revision | `loop-review` (subagente: `engineering:code-review` y, si la tarea es de UI, los revisores de diseño/a11y) → hallazgos a `review-log.md` | test |
| test | `loop-verify` | correccion si rojo · si verde y la tarea toca auth/tenant/dinero/secretos → seguridad · si no, cerrar tarea |
| seguridad | `loop-security` | correccion si hay hallazgos, si no cerrar tarea |
| correccion | `fix-loop` | test (reverificar) |
| entrega-bloqueada | — **alto**: no queda tarea ejecutable, pero hay `[d]`, `[!]` o decisiones abiertas. Listá qué bloquea y qué hace falta para destrabarlo | ejecucion o test cuando algo se destrabe · entrega cuando no quede nada |

### Reglas del bucle interno (la clave del loop)
- **Ejecución → Revisión → Test.** Si Revisión deja hallazgos o Test queda en rojo
  → entra `fix-loop` → vuelve a Test. Repite hasta verde.
- Cuando una tarea queda **verde y sin hallazgos abiertos**: márcala `[x]` en
  `plan.md` —o `[d]` si `loop-verify` la dejó en deuda por entorno incompleto (sección
  1.6)—, limpia `tarea_activa`, y toma la **siguiente** tarea pendiente (deps
  satisfechas) → vuelve a `ejecucion`. Con `[d]` la corrida sigue igual: la deuda se
  salda aparte.
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
`loop-ship`, `loop-status`, `loop-pitch`, `loop-doctor`), no para etapas.

`loop-ship` es la excepción deliberada: la **sugerís** al llegar a entrega, nunca la
disparás. Toca producción.

`loop-pitch` es la otra excepción: renderizar video es caro en tiempo y es un entregable
para humanos, no un paso del ciclo. La **sugerís** al llegar a entrega, nunca la disparás.
No la confundas con `loop-presentacion`, que sí es una etapa: corre una vez, con las
pantallas aprobadas, y pregunta antes de renderizar.

Si una etapa te devuelve "cannot be invoked via the Skill tool", **no repliques su
trabajo a mano**: es un error de empaquetado del arsenal. Pará y reportalo.

## 2.c Higiene de contexto (el loop corre muchas vueltas: cada token se paga N veces)
- `code-exec`, `loop-review`, `loop-verify`, `fix-loop` y `loop-security` corren en
  subagente y te devuelven **un resumen**. Trabajá con ese resumen.
- **No leas** logs de test, `review-log.md` completo ni diffs en este hilo. Si necesitás
  un dato puntual (un id de hallazgo, la etapa), leé `state.md` o hacé un `grep` dirigido.
- No re-narres lo que hizo cada etapa: una línea en la bitácora de `state.md` alcanza.

## 2.d Lo que una etapa dice que corrió, se comprueba
`code-exec` y `loop-review` cierran su resumen con la línea
`Skills invocadas: <lista | ninguna>`. Leela al volver de cada una, **antes de disparar
la etapa siguiente**. Las dos escriben sus `NO VERIFICADO` en `.loop/review-log.md`; si
el resumen dice que lo anotó en otro lado (la bitácora de `state.md`, por ejemplo), no
cuenta: el reporte de entrega lee solo `review-log.md`, así que la línea la agregás vos.

- **`loop-review` sin `engineering:code-review` en la lista** (o sin la línea): la revisión
  de código no corrió. Agregá vos a `.loop/review-log.md` la línea
  `NO VERIFICADO — engineering:code-review no se invocó. Quedó sin evaluar: el diff de <tarea>.`
  y seguí. No la relances: una segunda vuelta cuesta lo mismo y no garantiza nada.
- **`code-exec` con "ninguna"** en una tarea de UI, o de lógica sin UI: misma línea, con la
  skill que la tarea pedía (diseño, motion o `superpowers:test-driven-development`).
- **Nunca copies a la bitácora el nombre de una skill que no esté en esa línea.** Un
  resumen que dice "revisó code-review (inline)" describe una revisión propia del agente.

Estas líneas no frenan la corrida. Salen en el reporte de entrega, que es donde una
persona decide si alcanza.

## 2.e Vos no implementás, tampoco para destrabar
Cuando el plan se traba, lo natural es resolverlo en este hilo: escribir el flow que
falta, entrar al servidor, correr la matriz. No lo hagas. Medido: una corrida trabada
gastó 33 llamadas del orquestador sin lanzar una sola etapa. Cada caso tiene su dueño:

- **Una tarea en `[d]` y el entorno ya puede correr los cuatro dispositivos** → la salda
  `loop-verify`, invocada con el argumento `saldar deuda <tarea>`.
- **Falta un artefacto que el gate necesita** (el flow e2e de una pantalla, un seed) → es
  una tarea: agregala a `plan.md` con su "done" y su test, y despachala con `code-exec`.
- **Una tarea operativa contra un servidor o un ambiente** (alta de un cliente, migración
  en DEV o PROD, deploy) → una persona, o `loop-ship`. No es del ciclo: reportala en el alto.
- **Una decisión de producto o un `[!]`** → el usuario, con `AskUserQuestion`.

Si el usuario te autoriza explícitamente una tarea operativa, **delegala a un subagente**
(herramienta Agent) con el encargo exacto y pedile un resumen corto. En este hilo quedan
el encargo y el resultado, no los comandos.

Si después de eso no queda nada ejecutable, poné **etapa = `entrega-bloqueada`** y hacé
el alto de la tabla. No inventes otro nombre de etapa: lo que no está en la enumeración
de `state.md` no lo entiende la próxima corrida.

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
- Cuando no quedan tareas `[ ]` en `plan.md`, antes de nada verificá que **no quede
  ninguna tarea `[d]`**. Si queda alguna, **no entres en `entrega`**: poné
  `entrega-bloqueada` (sección 2.e), pará y reportá cuántas y cuáles —están en `.loop/deuda-dispositivos.md`— y que se saldan corriendo
  `loop-verify` en un entorno con los cuatro dispositivos. Después verificá que **el gate
  de arranque esté verde** —la matriz de cuatro si hay mobile, la web levantada si no—.
  Recién ahí pon **etapa = entrega**, resume lo hecho (tareas cerradas, ADRs, hallazgos
  resueltos) y **sugiere `engineering:deploy-checklist`**, después `loop-ship`, y
  **`loop-pitch`** si querés la presentación del producto. Sumá `documentation` y
  `standup`/retro según corresponda.
- **En el reporte de entrega, listá todas las líneas `NO VERIFICADO` de
  `.loop/review-log.md`**: qué revisiones no corrieron por falta de una skill externa y qué
  quedó sin evaluar. No bloquean la entrega, pero no se esconden.
- **`loop-ship` no la disparás vos.** Toca producción: la invoca una persona. El loop
  llega hasta sugerirla.
- Mantén la bitácora de `state.md` actualizada en cada transición para que el loop
  sea siempre reanudable.
