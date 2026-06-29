---
name: code-exec
description: >-
  Implementa la siguiente tarea pendiente del plan siguiendo las convenciones del
  repo y hace un commit atómico. Trigger con "ejecuta la siguiente tarea",
  "implementa T-00X", "avanza el plan", o invocada por project-loop. Es la etapa
  (4) Ejecución del arsenal proyecto-loop.
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
- **Mobile (RN/Expo, default):** aplica React Native Skills (FlashList, Reanimated,
  performance) y, si la tarea es de UI con motion, Emil Kowalski (traducido a
  Reanimated). La **dirección estética** está fijada en `state.md` (`aesthetic`):
  respétala; consulta UI-UX-PRO-MAX solo para paletas/tipografía, no para decidir.
- **Web:** Frontend Design (dirección) + Taste (parámetros) + Emil (motion).
- Cumple el criterio **done** de la tarea y deja el código en estado testeable.
- Pasa los datos a través de la **capa adaptadora** de backend (no llames a Supabase
  directo desde el dominio). Nada de pagos/email hardcodeados (Tier 2 va tras interfaz).

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
