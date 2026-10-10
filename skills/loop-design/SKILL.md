---
name: loop-design
description: >-
  Etapa de diseño del loop. Fija la dirección estética, define el design system y
  arma en Figma las pantallas clave que salen del análisis, dejando el mapa
  pantalla ↔ nodo ↔ historia que después consume la implementación. Trigger tras
  requirements-analysis, o "diseñá las pantallas", "armá el design system".
model: opus
effort: high
---

# loop-design — Etapa (3) Diseño

> **Skills externas:** esta etapa invoca skills que no son del loop. Antes de usar
> cualquiera, seguí `${CLAUDE_PLUGIN_ROOT}/references/dependencias-externas.md`: si no
> está disponible en este entorno, se registra como NO VERIFICADO, nunca se saltea callada.

Antes del plan, no después. Si las pantallas existen primero, `plan-architect` puede
desglosar las tareas **por pantalla**; si el diseño llega después, el plan queda
abstracto y hay que mapearlo de vuelta a mano.

## Preguntas al usuario: siempre con `AskUserQuestion`
Toda pregunta de esta skill (confirmar, elegir, reinicializar) va con la herramienta
`AskUserQuestion`, **nunca en texto**. Una pregunta en texto cierra el turno, y la
respuesta llega en un turno nuevo que ya no corre con el `model:` de esta skill sino
con el de la sesión: el resto del trabajo se hace con otro modelo y otro costo.
Si `AskUserQuestion` no está disponible, hacé
la pregunta en texto como **último** mensaje y no sigas trabajando en ese turno.

## 0. Reanudar
- Lee `.loop/state.md` y `.loop/analysis.md`.
- Si `.loop/design.md` ya existe, **completá el delta** (pantallas nuevas), no rehagas.
- Si te invocaron con el argumento **`propuesta`**, seguí la sección 0.5 y nada más.

## 0.5 Modo propuesta (lo invoca `project-init`, antes del análisis)
El proyecto recién nace y todavía no hay historias. El objetivo es que la persona **vea**
la dirección estética en Figma el primer día, no que la lea en un párrafo.

1. Sección 1 (Figma conectado). Si no lo está, **no frenes el arranque del proyecto**:
   anotá en la bitácora de `state.md` que la propuesta quedó pendiente y devolvé control.
   La vas a hacer vos misma al entrar en la etapa `diseno`.
2. Sección 2: tomá la `aesthetic` que dejó `project-init` como punto de partida.
3. Sección 4.1: creá el archivo del proyecto con sus páginas.
4. Elegí **2 pantallas representativas** a partir de la descripción y los requerimientos
   iniciales de `state.md`: la que el usuario va a ver más (un inicio o un listado) y la
   que más pesa en la tarea principal (un detalle o un alta). Con datos del dominio real,
   no "Lorem ipsum" ni "Producto 1".
5. Armá las **3 variantes** de la sección 4.4 sobre esas 2 pantallas, en `05 · Opciones`,
   lado a lado. En mobile las tres respetan la base de
   `${CLAUDE_PLUGIN_ROOT}/references/mobile-style.md` y se diferencian en lo que la base
   deja libre: paleta, tipografía y elemento firma. Solo teléfono: la tablet se diseña
   en la etapa `diseno`.
6. Pedí la elección con `AskUserQuestion`: una opción por variante, con su nombre y en
   una línea qué la distingue, y el link de Figma en la pregunta.
7. Promové la elegida: sus variables a `00 · Foundations`, las descartadas a
   `99 · Archive`. Escribí en `state.md` la `aesthetic` definitiva y el campo `figma`
   (link y fileKey del archivo).

No armes más pantallas ni escribas `design.md`: eso es de la etapa `diseno`, cuando
existan las historias. Devolvé un resumen corto con el link y la variante elegida.

## 1. Precondición: Figma conectado
Comprobá que las herramientas del MCP de Figma respondan. Si piden autorización,
**pará y decilo**: hay que conectarlo desde la configuración de conectores.

No improvises el diseño en markdown y sigas como si estuviera hecho. Una descripción
en prosa de una pantalla no es una pantalla, y el resto del loop la va a tratar como si
lo fuera.

## 2. Dirección estética (una vez, y no se discute más)
Si `state.md` todavía no tiene `aesthetic`, definila ahora y escribila **completa**:
tono, densidad, tipografía y principios — no un color.

**Si el proyecto tiene mobile, la dirección parte de
`${CLAUDE_PLUGIN_ROOT}/references/mobile-style.md`.** Leelo antes de proponer nada. Fija
la forma, los patrones y la disciplina; vos decidís paleta, tipografía y el elemento
firma del producto. Una propuesta que calca las referencias no cumple la base.

**Invocá de verdad** (herramienta Skill, no como texto) y en este orden:
`anthropic-skills:frontend-design` manda la dirección; `design-taste-frontend` ajusta
parámetros; `anthropic-skills:ui-ux-pro-max` es consulta para paletas y tipografía, no
decide. Si `state.md` ya trae `aesthetic` de `project-init`, no las vuelvas a correr para
redefinirla. Si una no está disponible, registralo como `NO VERIFICADO` según `dependencias-externas.md` y seguí.
Tres skills compitiendo en cada pantalla es cómo se llega a un diseño sin carácter.

## 3. Design system → `.loop/design-system.md`
Tokens como **decisiones**, no como vibras: escala tipográfica, paleta con sus roles,
espaciado, radios, elevación, motion. Cada uno con una línea de por qué.

Los tokens de **motion** (duraciones, curvas, qué transiciones existen) salen de invocar
`animate` (herramienta Skill), no de valores inventados. Para mobile, sumá
`react-native-best-practices:react-native-best-practices`: el motion corre en Reanimated
y no puede bloquear el hilo de JS.

Para mobile, contemplá modo claro y oscuro y las áreas seguras desde acá: retrofitearlo
después toca todas las pantallas. Fijá como decisión cada valor que la base mobile da
como punto de partida (radios, márgenes, objetivos táctiles) y anotá qué **preset** usa
cada pantalla: app de cliente o app de operación.

## 4. Figma

**Obligatorio: invocá `figma:figma-use` antes de cualquier escritura en Figma.** No
llames a las herramientas de escritura sin haber cargado esa skill; es la causa de los
fallos difíciles de depurar. Para traducir una pantalla concreta a Figma, apoyate en
`figma:figma-generate-design`.

### 4.1 Un archivo por proyecto, páginas fijas

```
<Proyecto> — Design
├── 00 · Foundations     variables reales de color, tipografía, espaciado, radios, motion
├── 01 · Components      componentes base con sus variantes y estados
├── 02 · Mobile          pantallas mobile (secciones Teléfono y Tablet)
├── 03 · Web             pantallas web
├── 04 · Flows           cómo se encadenan las pantallas
├── 05 · Opciones        variantes a elegir (ver 4.4)
└── 99 · Archive         descartes: no se borran, pero no se implementan
```

El número fija el orden y hace el nombre estable para búsqueda. Las páginas que el
proyecto no usa no se crean. Foundations y Components viven **dentro del archivo del
producto**, no en una librería aparte: cada producto tiene su propia dirección estética.

### 4.2 El nombre del frame es la clave del mapa

Un frame por pantalla **y por estado**:

```
H-03 · Checkout · default
H-03 · Checkout · vacio
H-03 · Checkout · carga
H-03 · Checkout · error
```

El patrón es `<id de historia> · <Pantalla> · <estado>`, con ` · ` (espacio,
punto medio, espacio) como separador.

Los estados tienen **nombres canónicos y sin acentos**, porque son claves de
búsqueda y no texto de interfaz: `default`, `vacio`, `carga`, `error`. Escribilos
así aunque en prosa lleven tilde — un acento de más rompe la búsqueda de la etapa
que viene, y el fallo es silencioso.

`H-03` es el id de historia de `.loop/analysis.md`. Con eso la cadena queda cerrada:
historia → frame → fila en `design.md` → tarea en `plan.md` → componente en `packages/ui`.

**Los ids de historia son inmutables una vez emitidos.** Si una replanificación los
renumera, los frames quedan desalineados con `design.md` y el mapa se rompe en silencio.
Si necesitás historias nuevas, seguí numerando; no reordenes.

### 4.3 Teléfono y tablet, las dos

El gate de verificación corre en tablet Android e iPad en **cada** tarea. Si solo diseñás
teléfono, el layout de tablet lo improvisa la implementación y la matriz lo reporta como
rojo sin una referencia contra la cual arreglarlo: pagás el costo de testear en tablet sin
el beneficio de haber diseñado para tablet.

Por eso **cada pantalla existe en las dos secciones** de `02 · Mobile`.

**Los tamaños de frame se derivan de los dispositivos de la matriz**, no se hardcodean.
Leé los dispositivos de `.loop/stack.md`, calculá los puntos lógicos de cada uno y
escribilos en `.loop/design-system.md`. De los AVDs de referencia salen
`Pixel 7 ≈ 412×914 dp` (1080×2400 @420dpi) y `Pixel Tablet = 1280×800 dp` (2560×1600
@320dpi). Los de iOS se obtienen del simulador correspondiente. Si mañana cambia un
dispositivo de la matriz, cambian los frames: es una sola fuente.

### 4.4 Ofrecé 3 variantes, en dos momentos y solo esos

No entregues un diseño único a aprobar: en los puntos de decisión visual ofrecé **3
variantes** y que la persona elija. Tres, porque es donde todavía se comparan de un
vistazo; con dos, si ninguna convence no hay a dónde ir.

- **La dirección estética, una sola vez.** Al arrancar, 3 propuestas de look completo
  —tipografía, paleta, densidad, radios, motion— aplicadas sobre las **mismas 2 pantallas
  representativas**, para que la comparación sea de dirección y no de contenido. La
  elegida gobierna todo el resto y no se vuelve a preguntar. **Normalmente ya se hizo
  en el arranque del proyecto** (sección 0.5): si `state.md` tiene el campo `figma` y
  una `aesthetic` elegida, este momento está cumplido y no se repite.
- **Donde haya duda real.** Proponé una sola opción por defecto y abrí variantes solo
  cuando la decisión no sea obvia: un patrón de navegación, una pantalla con estados que
  compiten. Cuando lo hagas, **decí por qué dudaste**. Si no podés justificarlo, no abras
  variantes.

**Lo que no se hace: variantes por pantalla de rutina.** Un producto de 12 pantallas con 3
variantes cada una son 12 decisiones humanas antes de escribir código, y eso destruye el
`full-auto` que el loop tiene por default.

Las variantes viven en `05 · Opciones`, lado a lado. La elegida se promueve a su página
definitiva; las descartadas van a `99 · Archive` — no se borran, queda registro de qué se
evaluó. **Registrá la elección**: la dirección estética en `state.md` (`aesthetic`), una
decisión puntual de patrón como ADR. Que no se reabra en la tarea siguiente.

### 4.5 Aplicá el catálogo de UI

Antes de dar una pantalla por armada, pasala por
`${CLAUDE_PLUGIN_ROOT}/references/ui-patterns.md`. Las reglas marcadas `[chequeable]` son
condiciones, no sugerencias: campos con caja y no línea, placeholder con ejemplos reales
del dominio, botones con el verbo de la acción, validación por campo, requisitos visibles
antes del error, filtros a la vista, estado del sistema en toda acción asincrónica, y
**nada de formularios inline** (UI-010): cada alta o edición tiene su frame propio
—pantalla, panel lateral o diálogo—, nunca campos editables dentro de una fila o tarjeta.

Las pantallas mobile pasan además por las reglas `[chequeable]` de
`${CLAUDE_PLUGIN_ROOT}/references/mobile-style.md`.

Las marcadas `[principio]` orientan pero no se verifican solas: las evalúa la persona en
el checkpoint.

## 5. Checkpoint humano (esto es lo que hace híbrido al flujo)
Cuando el archivo esté armado, **pará**. Entregá el link y pedí que lo revisen y
ajusten. No sigas al plan por tu cuenta: el punto de diseñar primero es que la persona
decida cómo se ve, con algo concreto delante.

Poné `etapa = diseno-revision` en `state.md`. `project-loop` sabe que eso es un alto
de checkpoint, no una falla.

## 6. `.loop/design.md` — el mapa
Cuando el usuario apruebe, escribí el artefacto que consume la implementación:

```markdown
| Pantalla | Nodo de Figma | Historia | Estados |
|----------|---------------|----------|---------|
| <nombre> | <url del nodo> | <id>     | vacio / carga / error |
```

Sin este mapa el resto del loop no sabe qué implementar contra qué, y vuelve a improvisar.

## 7. Cierre
Actualizá `state.md`: `design-system.md` y `design.md` listos, **etapa = plan**,
bitácora. Sugerí `plan-architect`.
