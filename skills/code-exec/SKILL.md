---
name: code-exec
description: >-
  Implementa la siguiente tarea pendiente del plan siguiendo las convenciones del
  repo y hace un commit atómico. Trigger con "ejecuta la siguiente tarea",
  "implementa T-00X", "avanza el plan", o invocada por project-loop. Es la etapa
  (4) Ejecución del arsenal proyecto-loop.
model: sonnet
effort: medium
context: fork
allowed-tools: Bash(npm run *) Bash(npx tsc *) Bash(npx eslint *) Bash(git add *) Bash(git commit *) Bash(git status *)
---

# code-exec — Etapa (4) Ejecución

> **Skills externas:** esta etapa invoca skills que no son del loop. Antes de usar
> cualquiera, seguí `${CLAUDE_PLUGIN_ROOT}/references/dependencias-externas.md`: si no
> está disponible en este entorno, se registra como NO VERIFICADO, nunca se saltea callada.

Implementas **una** tarea del plan, no más, y la dejas lista para revisión.

## 0. Reanudar
- Lee `.loop/state.md` y `.loop/plan.md`.
- Toma la **primera tarea `[ ]` pendiente** cuyas dependencias (`depende_de`) estén
  todas en `[x]` o en `[d]`. Una tarea en `[d]` está verde en código, así que sus
  dependientes pueden avanzar; la deuda de dispositivos se salda aparte (ver
  `loop-verify`, sección 1.6) y sigue bloqueando la entrega. Si el usuario nombró una
  tarea concreta, usa esa (valida deps).
- Si no hay tareas pendientes, informa "plan completo" y sugiere `engineering:deploy-checklist`.
- Marca la tarea como `[~]` (en progreso) en `plan.md` y ponla como `tarea_activa`
  en `state.md`.

## 1. Implementar
- Sigue las **convenciones del repo** (mira archivos vecinos: estilo, naming, imports).
- Pasa los datos por la **capa adaptadora** de backend (no llames a Supabase directo
  desde el dominio). Nada de pagos/email hardcodeados (Tier 2 va tras interfaz).
- Cumple el criterio **done** y deja el código en estado testeable.
- **Lógica sin UI** (dominio, adaptadores, servicios): **antes de editar el primer
  archivo de código**, llamá a la herramienta Skill con
  `superpowers:test-driven-development` y escribí primero el test que falla. El test
  esperado de la tarea en `plan.md` es el primero que se escribe. Escribir tests por tu
  cuenta en el mismo commit no es lo mismo: la skill fija el orden.
- Si una skill que esta etapa manda invocar no está disponible, o no la invocaste,
  agregá la línea `NO VERIFICADO` **a `.loop/review-log.md`**, con el formato de
  `dependencias-externas.md`, y seguí. En la bitácora de `state.md` no alcanza: el reporte
  de entrega lee solo `review-log.md`. No hagas de cuenta que la corriste.

### 1.1 ¿La tarea toca UI? → el diseño NO es opcional
Si la tarea crea o modifica pantallas/componentes visibles, el diseño es parte del
trabajo, no un extra. ANTES de codear la UI, **invoca de verdad** (con la herramienta
Skill; no las menciones como texto) las skills de diseño:
- **Implementá contra el diseño, no de memoria.** Si la tarea tiene un nodo de Figma
  en `.loop/design.md`, traé su contexto de diseño con el MCP de Figma
  (`figma:figma-design-to-code` / `get_design_context`) y usá esos valores. Inventar
  espaciados cuando la medida está a una llamada de distancia es la forma más común
  de que la pantalla salga "parecida pero mal".
- **Reusá el design system** (`.loop/design-system.md` si existe + tokens del repo).
  Nunca estilos ad-hoc por pantalla: tokens y componentes existentes primero.
- **Pasá la pantalla por el catálogo**
  `${CLAUDE_PLUGIN_ROOT}/references/ui-patterns.md`. Las reglas `[chequeable]` son
  condiciones del "done", no sugerencias. Las que más se olvidan al implementar:
  **UI-005** (validación por campo, no un banner global al enviar), **UI-006** (los
  requisitos visibles antes del error), **UI-010** (nada de formularios inline: alta y
  edición van en pantalla, panel o diálogo propio), **UI-011** (estados `parcial` y
  `sin-conexion` cuando aplican), **UI-012** (confirmación proporcional al peor error),
  **UI-013** (tablas como lista y montos completos por debajo de 640 px) y **UI-009** (toda acción asincrónica muestra
  estado de carga en su control y termina en éxito o error accionable).
- **UI-009 es la contraparte de los estados del diseño.** Si la pantalla tiene los tres
  estados en Figma (default, vacio, carga, error) pero el código solo implementa el camino
  feliz, la tarea **no** está terminada.
- **Web:** `anthropic-skills:frontend-design` (dirección) + `design-taste-frontend` (anti-template);
  `anthropic-skills:ui-ux-pro-max` solo para paletas/tipografía; motion con `animate`.
- **Mobile (RN/Expo):** `react-native-best-practices:react-native-best-practices`
  (FlashList/perf) + `animate` (motion).
- **Mobile:** la pantalla cumple las reglas `[chequeable]` de
  `${CLAUDE_PLUGIN_ROOT}/references/mobile-style.md` (tokens sin literales, iconos
  vectoriales y nunca emojis, objetivos de 44 pt o más, estado con texto, barra flotante
  sobre el área segura) y el archivo abre con el enlace a su nodo de Figma.
- **Motion en toda tarea de UI**, web o mobile: `animate` siempre que la pantalla tenga
  transiciones, apariciones o feedback de interacción. Usá los tokens de motion de
  `.loop/design-system.md`; no inventes duraciones por pantalla.
- Respetá la `aesthetic` fijada en `state.md`: **una sola dirección**, sin mezclar 3 opiniones.
- El criterio **done** de una tarea de UI incluye **calidad visual y consistencia con el
  design system**, no solo compilar/pasar tests. Pantalla fea con tests verdes = **NO** está "done".

## 2. Sanity local

- Corre lint + typecheck rápidos. Si fallan por algo que introdujiste, arréglalo antes del
  commit (esto es trivial; los fallos de lógica los caza la etapa de test).
- **La app tiene que levantar.** Typecheck en verde con la app rota no es una tarea
  terminada. Si el proyecto tiene mobile, confirmá que arranca en al menos un dispositivo
  antes de cerrar; la matriz completa la corre `loop-verify`, pero no le pases una tarea
  que ni siquiera abre.

## 3. Commit atómico
- Un commit por tarea: `feat(T-00X): <título>` (o `fix:`/`chore:` según corresponda).
- No mezcles tareas en un commit.

## 4. Cierre
- Deja la tarea en `[~]` (NO en `[x]` todavía: se cierra al pasar test/revisión).
- Actualiza `state.md`: `ultima_skill = code-exec`, **etapa = revision**, bitácora.
- Sugiere la siguiente etapa: `loop-review` (revisión) → luego test.
  Si corre `project-loop`, devuelve control para que encadene revisión y test.
- **Formato de la respuesta: esta plantilla y nada más.** Medido: con "máximo 10 líneas"
  los resúmenes llegaban de 18 a 43 líneas, y cada una se paga en cada vuelta del
  orquestador.

  ```
  Tarea: <id> — <título>
  Commit: <sha corto>
  Sanity: <verde | rojo> — <qué corrió, en una línea>
  Pendiente: <una línea, o "nada">
  NO VERIFICADO: <skills que no corrieron, o "nada">
  Skills invocadas: <lista separada por comas, o "ninguna">
  ```

  Sin encabezados, sin listas anidadas, sin negritas, sin frases de apertura ni de
  cierre. Cada campo ocupa **una línea**. Lo que no entra en su línea ya está escrito en
  otro lado (el commit, `state.md`, `review-log.md`, los logs): no lo repitas.
- **La última línea es obligatoria y literal**, con los nombres exactos que pasaste a la
  herramienta Skill en esta corrida:

  `Skills invocadas: <lista separada por comas, o "ninguna">`
