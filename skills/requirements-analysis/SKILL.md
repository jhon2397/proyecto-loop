---
name: requirements-analysis
description: >-
  Descompone requerimientos en épicas, historias y criterios de aceptación; lista
  restricciones, supuestos, riesgos y preguntas abiertas. Trigger tras
  project-init o cuando el usuario dice "analiza estos requerimientos",
  "qué necesitamos", "desglosa el alcance". Es la etapa (2) del arsenal proyecto-loop.
model: opus
effort: high
---

# requirements-analysis — Etapa (2) Análisis

Conviertes una idea o lista de requerimientos en un análisis estructurado que
`plan-architect` pueda transformar en tareas.

## 0. Reanudar
- Lee `.loop/state.md`. Si la etapa no es `analisis`, avisa e igual procede solo si
  el usuario lo pide (idempotente: si `analysis.md` ya existe, **complétalo/actualízalo**,
  no lo reescribas desde cero).

## 1. Entrada
- Toma los requerimientos del usuario (texto, doc, o lo que dejó `project-init`).
- Si es mobile y hay dudas de producto, puedes apoyarte en un brainstorm tipo
  Superpowers (`/brainstorm`) si está disponible, pero **no** inventes requisitos.

## 2. Producir `analysis.md`
Copia la plantilla `${CLAUDE_PLUGIN_ROOT}/templates/loop/analysis.md` a `.loop/analysis.md`
y rellénala:
- **Épicas → historias** en formato "Como <rol> quiero <objetivo> para <beneficio>".
- **Criterios de aceptación** verificables por historia (Given/When/Then o bullets).
- **Restricciones** (técnicas, plataforma, legales, tiempo/presupuesto).
- **Supuestos** explícitos.
- **Riesgos** con impacto/probabilidad/mitigación.
- **Preguntas abiertas**: marca lo bloqueante. Si hay bloqueantes críticos,
  **pregúntalos al usuario ahora**; no los arrastres al plan.

## 3. Calidad
- Cada historia debe ser independientemente verificable.
- Nada de soluciones técnicas aquí (eso es plan-architect): enfócate en el "qué" y el "por qué".

## 4. Cierre
- Actualiza `state.md`: artefacto `analysis.md = listo`, **etapa = plan**, añade
  línea a la bitácora.
- Sugiere la siguiente skill: `loop-design` si el proyecto tiene UI (el diseño va
  antes del plan, para que las tareas se desglosen por pantalla); si no tiene UI,
  `plan-architect` directo.
