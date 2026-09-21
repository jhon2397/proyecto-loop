---
name: loop-pitch
description: >-
  Arma la presentación del producto terminado con HyperFrames, usando el design
  system y las pantallas reales del proyecto. Trigger con "armá la presentación",
  "hacé el video del producto", "pitch del proyecto". Manual: la sugiere el loop al
  llegar a entrega, nunca la dispara solo.
argument-hint: [ruta-del-proyecto]
model: opus
effort: high
disable-model-invocation: true
---

# loop-pitch — Presentación del producto

Producís la pieza con la que se muestra el producto terminado. **Es un entregable para
humanos, no un paso del ciclo**: por eso esta skill la invoca una persona. El loop llega
hasta sugerirla.

## 0. Precondiciones

- Leé `.loop/state.md`. Si la `etapa` no es `entrega`, avisá que el producto todavía no
  está terminado y preguntá si igual se quiere un avance. No asumas que sí.
- HyperFrames necesita **FFmpeg** y Node 22+. Si `ffmpeg -version` no responde, pará y
  decilo: sin eso no hay render.

## 1. De dónde sale el contenido (no lo inventes)

| Qué | De dónde |
|-----|----------|
| Qué problema resuelve y para quién | `.loop/analysis.md` |
| Tono, tipografía, paleta, densidad | `state.md` (`aesthetic`) + `.loop/design-system.md` |
| Las pantallas y sus nodos | `.loop/design.md` |

**El punto de esta skill es que la presentación se vea como el producto.** Usá los tokens
reales de `design-system.md` — no una plantilla genérica, no la paleta que te parezca
linda. Un deck que no se parece a la app es exactamente lo que pasa cuando se arma aparte.

Si el proyecto no tiene `design-system.md` (no tenía UI), decilo: la presentación va a ser
de contenido, sin identidad propia, y eso hay que decidirlo a conciencia.

## 2. Armado

Empezá **siempre** por la skill router `hyperframes`, que selecciona el workflow que
corresponde e instala lo que falte. No saltes directo a una skill de workflow.

Trabajá en `docs/pitch/` del proyecto. Para el guion, apoyate en `hyperframes-creative`;
para el movimiento, en `hyperframes-animation`. Antes de construir un visual con nombre
propio (un gráfico, una ventana de terminal, un efecto), pasá por `hyperframes-registry`:
hay cientos de bloques hechos y rehacerlos a mano es tiempo perdido.

## 3. Checkpoint

Cuando esté armado, **mostralo antes de renderizar**. El render es la parte cara: que la
persona vea la estructura y el guion primero.

## 4. Cierre

Dejá la salida en `docs/pitch/` y anotá en la bitácora de `state.md` qué se generó. No
cambies la `etapa`: `loop-pitch` no mueve el loop, produce un artefacto al costado.
