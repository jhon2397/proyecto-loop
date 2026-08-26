---
name: loop-adopt
description: >-
  Incorpora al loop un repositorio que YA existe: reconstruye .loop/ leyendo el
  código y la historia en vez de hacer scaffold. Trigger con "meté este repo en el
  loop", "adoptá este proyecto", "armá el .loop de acá".
argument-hint: [qué querés hacer a continuación en este repo]
disable-model-invocation: true
model: opus
effort: high
---

# loop-adopt — Entrada al loop para un repo existente

Equivalente de `project-init` para brownfield. **No hacés scaffold ni tocás el
código**: reconstruís el estado del loop a partir de lo que ya hay.

Objetivo del usuario para este repo (puede venir vacío): $ARGUMENTS

## 0. Idempotencia
Si ya existe `.loop/state.md`, no reconstruyas: leelo, informá la etapa y sugerí la
skill que corresponde. Solo seguí si el usuario pide re-adoptar explícitamente.

## 1. Leer el repo, no inventarlo
Sacá del código, de la CI y de la historia de git: propósito, stack, arquitectura,
comandos reales de test/build/lint, integraciones y restricciones. La historia dice
mucho: qué se toca seguido, dónde se concentran los arreglos, qué está muerto.

Lo que no puedas verificar, preguntalo o marcalo como supuesto explícito.

## 2. Reconstruir `.loop/`
Copiá lo que falte desde `${CLAUDE_PLUGIN_ROOT}/templates/loop/` y completá:

- **`state.md`** — meta del proyecto y **`etapa = plan`**: el repo ya existe, así que
  no arranca en inicio ni en análisis.
- **`stack.md`** — Tier 1 según lo que el repo ya use de verdad (no lo que debería
  usar), y la tabla de comandos que consume `loop-verify`, sacada del `Makefile`,
  el `package.json` o el `pyproject.toml`.
- **`analysis.md`** — solo si el usuario dijo qué quiere hacer a continuación. Un
  análisis de lo ya construido no le sirve a nadie; lo que sirve es el alcance de lo
  que viene.
- **`plan.md`** — las tareas de ese trabajo nuevo, no una reconstrucción arqueológica
  de lo ya hecho.

## 3. El sustrato va aparte
Las convenciones (`CLAUDE.md`, reglas, permisos, hooks) las instala
`dev-substrate:substrate-init`. Si el repo no las tiene, sugerila; no dupliques
ese trabajo acá.

## 4. Cierre
Informá qué se reconstruyó y con qué evidencia, qué quedó como supuesto, y sugerí
la siguiente skill: `plan-architect` si hay trabajo nuevo que planificar, o
`loop-status` si solo querías dejarlo enganchado al loop.
