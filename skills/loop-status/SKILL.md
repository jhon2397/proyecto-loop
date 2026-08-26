---
name: loop-status
description: >-
  Muestra el estado del loop en este proyecto: etapa, tarea activa, avance del plan,
  hallazgos abiertos y última actividad. Solo lectura. Trigger con "cómo viene esto",
  "en qué quedamos", "estado del loop".
disable-model-invocation: true
model: haiku
allowed-tools: Read Glob Grep
disallowed-tools: Edit Write NotebookEdit Bash
---

# loop-status — Dónde quedó el proyecto

Skill de **solo lectura**: no modificás ni un archivo, no corrés comandos, no
avanzás el loop. Es para retomar después de días sin gastar contexto.

## 1. Leer
- `.loop/state.md` — etapa, tarea activa, iteración, última skill, bitácora.
- `.loop/plan.md` — cuántas tareas `[x]`, `[~]`, `[ ]`, `[!]`.
- `.loop/review-log.md` — hallazgos abiertos y su severidad.

Si no existe `.loop/`, decilo y sugerí `project-init` (proyecto nuevo) o
`loop-adopt` (repo que ya existe).

## 2. Reportar, corto
```
Proyecto · etapa · tarea activa (iteración N)
Plan: X de Y cerradas · Z pendientes · W bloqueadas
Hallazgos abiertos: N (la severidad más alta primero)
Última actividad: <fecha> · <qué pasó>
Siguiente paso sugerido: <skill de la etapa actual>
```

Si hay tareas `[!]` (bloqueadas) o hallazgos críticos, esos van primero: es lo
único que puede estar frenando todo.

## 3. No hagas nada más
No corrijas el estado aunque veas una inconsistencia: reportala. Quien arregla es
la skill de la etapa, con el contexto que vos no tenés.
