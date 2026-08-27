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

Antes del plan, no después. Si las pantallas existen primero, `plan-architect` puede
desglosar las tareas **por pantalla**; si el diseño llega después, el plan queda
abstracto y hay que mapearlo de vuelta a mano.

## 0. Reanudar
- Lee `.loop/state.md` y `.loop/analysis.md`.
- Si `.loop/design.md` ya existe, **completá el delta** (pantallas nuevas), no rehagas.

## 1. Precondición: Figma conectado
Comprobá que las herramientas del MCP de Figma respondan. Si piden autorización,
**pará y decilo**: hay que conectarlo desde la configuración de conectores.

No improvises el diseño en markdown y sigas como si estuviera hecho. Una descripción
en prosa de una pantalla no es una pantalla, y el resto del loop la va a tratar como si
lo fuera.

## 2. Dirección estética (una vez, y no se discute más)
Si `state.md` todavía no tiene `aesthetic`, definila ahora y escribila **completa**:
tono, densidad, tipografía y principios — no un color.

Manda `frontend-design` para la dirección; `design-taste-frontend` ajusta parámetros;
UI-UX-PRO-MAX es consulta para paletas y tipografía, no decide. Tres skills compitiendo
en cada pantalla es cómo se llega a un diseño sin carácter.

## 3. Design system → `.loop/design-system.md`
Tokens como **decisiones**, no como vibras: escala tipográfica, paleta con sus roles,
espaciado, radios, elevación, motion. Cada uno con una línea de por qué.

Para mobile, contemplá modo claro y oscuro y las áreas seguras desde acá: retrofitearlo
después toca todas las pantallas.

## 4. Figma
**Obligatorio: invocá `figma:figma-use` antes de cualquier escritura en Figma.** No
llames a las herramientas de escritura sin haber cargado esa skill; es la causa de los
fallos difíciles de depurar. Para traducir una pantalla concreta a Figma, apoyate en
`figma:figma-generate-design`.

Armá el archivo con dos partes:
1. **Design system** — los tokens del punto 3, como estilos y variables reales.
2. **Pantallas clave** — las que salen de las épicas de `analysis.md`. No todas: las
   que definen el producto y las que tienen estados no obvios (vacío, error, carga).

Nombrá las capas y los nodos de forma que un humano los reconozca. Ese nombre es la
clave con la que la implementación va a buscar cada pantalla.

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
| <nombre> | <url del nodo> | <id>     | vacío / carga / error |
```

Sin este mapa el resto del loop no sabe qué implementar contra qué, y vuelve a improvisar.

## 7. Cierre
Actualizá `state.md`: `design-system.md` y `design.md` listos, **etapa = plan**,
bitácora. Sugerí `plan-architect`.
