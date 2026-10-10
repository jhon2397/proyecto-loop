---
name: loop-presentacion
description: >-
  Etapa de presentación del loop. Con las pantallas ya aprobadas en Figma, arma la
  presentación del producto: guion, storyboard en el mismo archivo de Figma y la pieza
  animada con HyperFrames. Trigger vía project-loop tras aprobar el diseño, o "armá la
  presentación del diseño", "presentá el producto con las pantallas de Figma".
model: opus
effort: high
---

# loop-presentacion — La presentación del producto, desde el diseño

> **Skills externas:** esta etapa invoca skills que no son del loop. Antes de usar
> cualquiera, seguí `${CLAUDE_PLUGIN_ROOT}/references/dependencias-externas.md`: si no
> está disponible en este entorno, se registra como NO VERIFICADO, nunca se saltea callada.

El producto todavía no existe en código, pero ya se puede mostrar: las pantallas están
diseñadas y aprobadas. Esta etapa produce la pieza con la que se cuenta qué es el
producto, para quién y cómo se ve, **antes de construirlo**. Sirve para conseguir el sí
de quien decide con algo concreto delante, y deja el guion que `loop-pitch` va a
actualizar con el producto real al llegar a entrega.

## Preguntas al usuario: siempre con `AskUserQuestion`
Toda pregunta de esta skill (confirmar, elegir, reinicializar) va con la herramienta
`AskUserQuestion`, **nunca en texto**. Una pregunta en texto cierra el turno, y la
respuesta llega en un turno nuevo que ya no corre con el `model:` de esta skill sino
con el de la sesión: el resto del trabajo se hace con otro modelo y otro costo.
Si `AskUserQuestion` no está disponible, hacé
la pregunta en texto como **último** mensaje y no sigas trabajando en ese turno.

## 0. Reanudar y precondiciones
- Leé `.loop/state.md`, `.loop/analysis.md`, `.loop/design.md` y `.loop/design-system.md`.
- Si `docs/pitch/` ya tiene una presentación, **actualizala** con lo que cambió; no la
  rehagas.
- **Hacen falta las pantallas.** Si `design.md` no existe o no tiene nodos, esta etapa no
  tiene de qué hablar: decilo y devolvé control sin inventar pantallas.
- **Figma conectado**, igual que en `loop-design`. Si no lo está, pará y decilo.
- **HyperFrames necesita FFmpeg y Node 22 o más.** Si `ffmpeg -version` no responde, hacé
  el guion y el storyboard en Figma, dejá la pieza animada como `NO VERIFICADO` con el
  motivo, y seguí: el storyboard solo ya sirve para presentar.

## 1. De dónde sale el contenido (no lo inventes)

| Qué | De dónde |
|-----|----------|
| Qué problema resuelve y para quién | `.loop/analysis.md` |
| Tono, tipografía, paleta, densidad, motion | `state.md` (`aesthetic`) + `.loop/design-system.md` |
| Las pantallas y sus nodos | `.loop/design.md` y el archivo de `state.md` (`figma`) |

**La presentación se tiene que ver como el producto.** Mismas variables, misma
tipografía, mismos componentes. Un deck con una plantilla genérica al lado de pantallas
con identidad propia le quita credibilidad a las dos cosas.

## 2. Guion
Apoyate en `hyperframes-creative` (herramienta Skill) para el guion y los beats. La
estructura base, en este orden:

1. **El problema**, dicho como lo diría quien lo sufre. Una escena.
2. **Para quién es.** Una escena.
3. **El producto en una frase.**
4. **El recorrido:** de 3 a 5 pantallas clave, en el orden en que una persona las usa.
   Cada escena muestra una pantalla y dice qué resuelve, no qué botones tiene.
5. **Qué lo hace distinto:** el elemento firma del diseño, o la decisión de producto que
   más pesa.
6. **Cierre:** qué sigue.

Entre 45 y 90 segundos. Si no entra, sobran pantallas, no falta tiempo. Guardá el guion
en `docs/pitch/guion.md`.

## 3. Storyboard en Figma
**Invocá `figma:figma-use` antes de cualquier escritura en Figma.**

En el archivo del proyecto, en la página **`06 · Presentación`**: un frame por escena,
en el orden del guion, con el nombre `P-01 · <título de la escena>`.

- Formato **16:9 (1920×1080)** por defecto. Si la pieza es para redes o para verse en el
  teléfono, 9:16; preguntalo solo si la descripción del proyecto no lo deja claro.
- Las pantallas entran como **instancias de los frames reales** de `02 · Mobile` o
  `03 · Web`, dentro del marco del dispositivo. No las redibujes: si la pantalla cambia,
  la escena tiene que cambiar con ella.
- Texto y color con las **variables de `00 · Foundations`**. Ningún valor suelto.
- Una idea por escena. Si una escena necesita dos títulos, son dos escenas.

El storyboard es un entregable por sí mismo: se puede presentar desde Figma.

## 4. Pieza animada con HyperFrames
Empezá **siempre** por la skill router `hyperframes`, que elige el workflow e instala lo
que falte. No saltes directo a una skill de workflow.

- Trabajá en `docs/pitch/` del proyecto.
- **Las imágenes de las pantallas salen de Figma**, exportadas de los frames reales a
  `docs/pitch/assets/`. No capturas de otra cosa ni maquetas hechas en HTML.
- Tokens del design system, no los de una plantilla.
- Para el movimiento, `hyperframes-animation`, con las duraciones y curvas de los tokens
  de motion del design system: la presentación se mueve como se va a mover el producto.
- Antes de construir a mano un visual con nombre propio (un gráfico, un mapa, una ventana
  de dispositivo), pasá por `hyperframes-registry`.

## 5. Checkpoint antes de renderizar
El render es la parte cara. Con el storyboard y la composición armados, mostrá el link de
Figma y la vista previa, y preguntá con `AskUserQuestion`: **Renderizar** · **Ajustar
antes** · **Dejar sin renderizar por ahora**.

No renderices sin esa respuesta. "Dejar sin renderizar" es una salida válida: el
storyboard y la composición quedan listos.

## 6. Cierre
- Dejá todo en `docs/pitch/` (guion, assets, composición y, si se renderizó, el video).
- En `state.md`: `ultima_skill = loop-presentacion`, **etapa = plan**, y una línea en la
  bitácora con qué se generó y el link del storyboard.
- Commit: `docs(pitch): presentación del producto desde el diseño`.
- Devolvé un resumen corto: link del storyboard, ruta de la pieza y si quedó renderizada.

Esta etapa **no frena el loop si algo falta**: sin FFmpeg queda el storyboard; sin
decisión de render queda la composición. Lo único que la saltea entera es no tener
pantallas.
