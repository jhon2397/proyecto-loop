---
name: plan-architect
description: >-
  Define la arquitectura y genera un plan de implementación en tareas atómicas
  ordenadas por dependencia, cada una con criterio de "done" y tests esperados;
  registra decisiones como ADRs y elige vendors por slot de servicio. Trigger tras
  requirements-analysis o "arma el plan", "diseña la arquitectura", "desglosa en tareas".
  Es la etapa (3) del arsenal proyecto-loop.
---

# plan-architect — Etapa (3) Plan

Transformas `analysis.md` en un plan ejecutable y decisiones de arquitectura
trazables.

## 0. Reanudar
- Lee `.loop/state.md` y `.loop/analysis.md`. Si `plan.md` ya existe,
  **actualízalo** (añade/replanifica tareas) en vez de reescribir; conserva el
  estado `[x]/[~]` de tareas ya tocadas.

## 1. Arquitectura
- Define la arquitectura de alto nivel. Apóyate en `engineering:architecture`
  (ADR) y `engineering:system-design` si están disponibles.
- Por cada decisión relevante (framework, navegación, capa de datos, estado,
  vendor de un slot) crea un **ADR** en `.loop/adr/ADR-00X-*.md` con contexto,
  opciones, decisión y consecuencias.

## 2. Slots de servicio → vendor (stack.md)
- Decide vendor por slot según "qué tan caro es retrofittear":
  - Tier 1 ya cableado por project-init (Sentry, Supabase) — confirma/ajusta.
  - Tier 2 (pagos, email) — elige solo si una historia lo exige; recuerda: **mobile
    digital → RevenueCat + IAP, no Stripe**; Stripe solo físico/web; email de auth
    lo cubre Supabase.
- Registra cada elección en `.loop/stack.md` enlazando su ADR.

## 3. Plan de tareas (plan.md)
Copia `${CLAUDE_PLUGIN_ROOT}/templates/loop/plan.md` a `.loop/plan.md` y genera
**tareas atómicas** (`T-001`, `T-002`, …):
- Ordenadas por **dependencia** (`depende_de`), las independientes primero.
- Cada tarea: criterio **done** verificable, **tests** esperados, archivos estimados.
- Granularidad: una tarea ≈ un commit revisable. Si algo no cabe en un commit, pártelo.
- Cubre las historias de `analysis.md`; lo diferido va al backlog.

## 4. Cierre
- Actualiza `state.md`: `plan.md = listo`, conteo de ADRs, **tarea_activa = T-001**,
  **etapa = ejecucion**, bitácora.
- Sugiere la siguiente skill: `code-exec` (o devuelve control a `project-loop`).
