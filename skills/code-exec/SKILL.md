---
name: code-exec
description: >-
  Implementa la siguiente tarea pendiente del plan siguiendo las convenciones del
  repo y hace un commit atómico. Trigger con "ejecuta la siguiente tarea",
  "implementa T-00X", "avanza el plan", o invocada por project-loop. Es la etapa
  (4) Ejecución del arsenal proyecto-loop.
effort: high
allowed-tools: Bash(npm run *) Bash(npx tsc *) Bash(npx eslint *) Bash(git add *) Bash(git commit *) Bash(git status *)
---

# code-exec — Etapa (4) Ejecución

Implementas **una** tarea del plan, no más, y la dejas lista para revisión.

## 0. Reanudar
- Lee `.loop/state.md` y `.loop/plan.md`.
- Toma la **primera tarea `[ ]` pendiente** cuyas dependencias (`depende_de`) estén
  todas en `[x]`. Si el usuario nombró una tarea concreta, usa esa (valida deps).
- Si no hay tareas pendientes, informa "plan completo" y sugiere `deploy-checklist`.
- Marca la tarea como `[~]` (en progreso) en `plan.md` y ponla como `tarea_activa`
  en `state.md`.

## 1. Implementar
- Sigue las **convenciones del repo** (mira archivos vecinos: estilo, naming, imports).
- Pasa los datos por la **capa adaptadora** de backend (no llames a Supabase directo
  desde el dominio). Nada de pagos/email hardcodeados (Tier 2 va tras interfaz).
- Cumple el criterio **done** y deja el código en estado testeable.

### 1.1 ¿La tarea toca UI? → el diseño NO es opcional
Si la tarea crea o modifica pantallas/componentes visibles, el diseño es parte del
trabajo, no un extra. ANTES de codear la UI, **invoca de verdad** (con la herramienta
Skill; no las menciones como texto) las skills de diseño:
- **Reusá el design system** (`.loop/design-system.md` si existe + tokens del repo).
  Nunca estilos ad-hoc por pantalla: tokens y componentes existentes primero.
- **Web:** `frontend-design` (dirección) + `design-taste-frontend` (anti-template);
  `ui-ux-pro-max` solo para paletas/tipografía; motion con `animate`.
- **Mobile (RN/Expo):** `react-native-best-practices` (FlashList/perf) + `animate` (motion).
- Respetá la `aesthetic` fijada en `state.md`: **una sola dirección**, sin mezclar 3 opiniones.
- El criterio **done** de una tarea de UI incluye **calidad visual y consistencia con el
  design system**, no solo compilar/pasar tests. Pantalla fea con tests verdes = **NO** está "done".

## 2. Sanity local
- Corre lint + typecheck rápidos. Si fallan por algo que introdujiste, arréglalo
  antes del commit (esto es trivial; los fallos de lógica los caza la etapa de test).

## 3. Commit atómico
- Un commit por tarea: `feat(T-00X): <título>` (o `fix:`/`chore:` según corresponda).
- No mezcles tareas en un commit.

## 4. Cierre
- Deja la tarea en `[~]` (NO en `[x]` todavía: se cierra al pasar test/revisión).
- Actualiza `state.md`: `ultima_skill = code-exec`, **etapa = revision**, bitácora.
- Sugiere la siguiente etapa: `engineering:code-review` (revisión) → luego test.
  Si corre `project-loop`, devuelve control para que encadene revisión y test.
