# Catálogo de reglas de UI

> **En construcción.** Gabriel las está pasando por tandas. Cuando esté completo, este
> archivo se convierte en la referencia que consultan `loop-design` (al armar las
> pantallas) y `code-exec` (al implementarlas), y contra la que revisa la etapa de
> revisión de UI.

Cada regla tiene tres partes: **qué hacer**, **por qué** y **cómo se verifica**. La
tercera es la que las hace útiles para el loop — sin ella vuelven a ser una opinión.

Cada regla se marca como **[chequeable]** —el loop puede verificarla sin criterio
humano— o **[principio]** —orienta el diseño pero la evalúa una persona o
`design:design-critique`—. La distinción importa: un principio disfrazado de regla hace
que la revisión automática dé falsos verdes.

Fuentes: tanda 1, cards de `@munoz.graphic`. Tanda 2, cards de `@northlav.studio`.

---

## UI-001 · Cajas, no líneas, en los campos de formulario  ·  [chequeable]

**Qué.** Los campos de entrada llevan **borde cerrado** (caja), con la etiqueta arriba y
el placeholder adentro. No usar líneas sueltas debajo del texto.

**Por qué.** Un campo con borde cerrado se lee como zona editable. La línea suelta se
confunde con un separador y obliga al usuario a adivinar dónde escribe cada dato.

**Cómo se verifica.** Ningún input del design system usa `border-bottom` como único
borde. Los campos tienen etiqueta visible propia, no etiqueta-como-placeholder.

---

## UI-002 · El placeholder del buscador da pistas reales  ·  [chequeable]

**Qué.** El placeholder del buscador muestra **ejemplos concretos del catálogo**
("Hamburguesas, Pizzas, Tacos"), no la palabra "Buscar".

**Por qué.** Un buscador vacío no dice qué se puede buscar. Los ejemplos reales orientan
la consulta y bajan la cantidad de búsquedas sin resultados.

**Cómo se verifica.** El placeholder del buscador nombra al menos dos ejemplos tomados
del dominio real del producto, no texto genérico.

---

## UI-003 · El botón dice la acción, no "Sí"/"No"  ·  [chequeable]

**Qué.** El texto del botón contiene el **verbo de la acción** ("Enviar", "Cancelar",
"Eliminar"). Nunca "Sí"/"No" ni "Aceptar"/"Aceptar" genéricos.

**Por qué.** "Sí" y "No" obligan a releer la pregunta para saber qué hace cada botón. Con
el verbo adentro, el botón se entiende sin contexto — que es también como lo lee un
lector de pantalla, fuera del flujo del diálogo.

**Cómo se verifica.** Ningún botón de confirmación tiene como label "Sí", "No", "OK" o
"Aceptar" a secas.

---

## UI-004 · "Leer más" para textos largos  ·  [chequeable]

**Qué.** Los bloques de texto largo se recortan a unas pocas líneas y se acompañan de un
control para expandir ("Leer más").

**Por qué.** Un párrafo largo se salta completo. Recortarlo mantiene la pantalla ligera y
le devuelve al usuario la decisión de profundizar.

**Cómo se verifica.** Ningún bloque de texto corrido supera el límite de líneas fijado en
el design system sin control de expandir.

**Matiz.** No aplica a contenido que el usuario necesita para decidir en esa misma
pantalla —precios, condiciones, advertencias—: ahí esconder es peor que scrollear.

**Precedencia sobre UI-008.** En una tarjeta de resultado, `UI-008` gana: los datos de
decisión (nombre, precio, acción) se muestran siempre completos. `UI-004` aplica al texto
descriptivo que acompaña, no a esos datos. Cuando dos reglas chocan, la que preserva
información para decidir tiene prioridad sobre la que ahorra espacio.

---

## UI-005 · Validación por campo y en el momento  ·  [chequeable]

**Qué.** Cada campo se valida al completarlo y muestra su propio estado —correcto o con
error— con el mensaje debajo del campo. No dejar toda la validación para el envío ni
resolverla con un banner global del tipo "Hay errores en el formulario".

**Por qué.** El error al final obliga a volver a recorrer el formulario buscando cuál
falló. La validación por campo señala el problema donde está y mientras el usuario
todavía tiene el contexto de lo que escribía.

**Cómo se verifica.** Ningún formulario tiene como único feedback un mensaje global al
enviar. Cada campo validable tiene estado visual propio y un mensaje asociado.

---

## UI-006 · Las reglas se muestran antes del error  ·  [chequeable]

**Qué.** Los requisitos de un campo con restricciones —una contraseña, típicamente— se
muestran **desde el principio**, como lista que se va marcando a medida que se cumplen.
El campo de contraseña lleva además control para ver lo escrito.

**Por qué.** Si las reglas se descubren recién al fallar, el usuario adivina y reintenta.
Mostrarlas antes convierte el error en algo que no llega a ocurrir.

**Cómo se verifica.** Todo campo con reglas de formato las expone antes del primer envío.
Los campos de contraseña tienen toggle de visibilidad.

---

## UI-007 · Una sola jerarquía por pantalla  ·  [principio]

**Qué.** Cada pantalla tiene **un foco principal** y el resto se subordina: un bloque
protagonista con su acción, secciones nombradas con su "ver todo", y densidad que
distingue lo importante de lo secundario. Evitar la grilla donde todo pesa igual.

**Por qué.** Cuando todos los bloques tienen el mismo peso visual, el usuario no sabe
dónde mirar primero y la pantalla se lee como un depósito de opciones.

**Cómo se verifica.** No mecánicamente. Lo evalúa `design:design-critique` en la etapa de
revisión y la persona en el checkpoint de diseño.

---

## UI-008 · Los filtros se ven sin buscarlos  ·  [chequeable]

**Qué.** En pantallas de resultados, los filtros están **a la vista** junto al buscador
(chips o similar), no escondidos detrás de un ícono. Cada resultado muestra la
información necesaria para decidir —imagen, nombre, precio— y su acción directa.

**Por qué.** Si encontrar los filtros es en sí una búsqueda, el usuario recorre listas
largas a mano. Y un resultado sin precio ni acción obliga a entrar para volver a salir.

**Cómo se verifica.** La pantalla de resultados expone al menos un control de filtro sin
abrir un menú. Cada tarjeta de resultado incluye los datos de decisión del dominio.

---

## UI-009 · El sistema siempre dice en qué estado está  ·  [chequeable]

**Qué.** Toda acción asincrónica muestra **estado de carga en el control que la disparó**
("Creando…") y termina en un desenlace explícito: confirmación de éxito, o error que
dice qué pasó y qué hacer.

**Por qué.** Sin eso el usuario no sabe si se envió, si está guardando o si funcionó, y
la respuesta natural es volver a apretar el botón.

**Cómo se verifica.** Ningún handler asincrónico deja su control sin estado de carga.
Toda operación que puede fallar tiene su caso de error con mensaje accionable, no solo
el camino feliz.

**Relación con el loop.** Esta regla es la contraparte en código de los estados que
`.loop/design.md` ya exige diseñar por pantalla (vacío, carga, error). Si la pantalla
tiene los tres estados en Figma pero el código solo implementa el feliz, la tarea no
está terminada.
