# Base de estilo mobile

> Toda app mobile que nace del loop parte de acá. `project-init` y `loop-design` la usan
> al proponer la dirección estética; `code-exec`, al implementar.

Tiene dos mitades, y hacen falta las dos:

- **El lenguaje visual** — cómo se ve y se siente. Sale de las capturas de referencia que
  pasó Gabriel (2026-10-10): apps de consumo con mucho aire, superficies blandas y
  navegación flotante.
- **El rigor del sistema** — qué tan completo y consistente es. Sale del design system
  más completo que tiene el equipo, el de su ERP: tokens de una sola fuente, un preset
  por tipo de superficie, estados que nunca dependen solo del color.

Una sin la otra falla de formas conocidas. Lenguaje sin rigor es una maqueta linda que se
desarma en la tercera pantalla. Rigor sin lenguaje es un sistema impecable que nadie
quiere usar en el teléfono.

## Qué fija la base y qué decide cada producto

| Lo fija esta base | Lo decide cada producto |
|---|---|
| Forma: radios, superficies, elevación, espaciado | Paleta y su color de acento |
| Patrones: navegación, encabezado, tarjetas, hojas | Tipografía |
| Disciplina: tokens, estados, iconos, objetivos táctiles | El elemento firma: lo que hace reconocible a este producto |
| | Tono del copy, imágenes, ilustración |

La base no es un tema para copiar. Dos productos hechos con ella tienen que poder
distinguirse a tres metros. Si la propuesta estética sale igual a las capturas de
referencia cambiando el logo, no se usó la base: se la calcó.

## Lenguaje visual

Los valores numéricos son **puntos de partida**. Cada producto los fija como decisión en
`.loop/design-system.md`, con su porqué.

1. **Fondo neutro claro, superficies blancas.** La pantalla es un gris muy claro y el
   contenido vive en tarjetas blancas encima. La separación la da el contraste entre
   fondo y superficie, no líneas ni sombras marcadas.
2. **Radios grandes y una sola escala.** Tarjetas entre 20 y 28; controles y campos entre
   14 y 18; etiquetas y botones de icono, píldora o círculo completo. Tres pasos, no más.
3. **Elevación casi nula.** Sombra suave y amplia solo en lo que flota de verdad: la
   barra de navegación, una hoja, un menú. Una tarjeta de listado no flota.
4. **Navegación flotante.** La barra inferior es una píldora separada de los bordes, en
   un tono oscuro, con iconos y el destino activo marcado con el color de acento. De 3 a
   5 destinos. No ocupa el ancho completo ni se pega al borde.
5. **Encabezado con jerarquía de una sola mirada.** Un título grande y pesado, con parte
   de la frase en un tono más bajo para dar ritmo. Arriba, una fila chica de contexto
   (quién sos, dónde estás) y las acciones globales como botones de icono redondos.
6. **Categorías como selector circular.** Las opciones de primer nivel van en círculos
   con imagen o icono y su etiqueta debajo, en una fila que se desplaza. La activa se
   distingue por tamaño o por un subrayado, además del color.
7. **Tarjetas con la imagen como protagonista.** En un listado de cosas que se ven
   —productos, lugares, personas— la imagen manda, el nombre va debajo, el dato clave
   (precio, estado) abajo a la izquierda y la acción principal abajo a la derecha, como
   botón de icono.
8. **Etiquetas en píldora.** Descuentos, estados y conteos van en píldoras chicas de alto
   contraste, apoyadas sobre la imagen o el borde de la tarjeta.
9. **Mapa con hoja inferior.** Cuando la pantalla es un recorrido o una ubicación, el
   mapa ocupa el fondo y el detalle sube en una hoja con las esquinas superiores
   redondeadas. La hoja muestra primero lo esencial y se expande.
10. **Progreso por puntos.** Un proceso con etapas se dibuja como puntos unidos por una
    línea, con las etapas cumplidas en el color de acento. No una barra de porcentaje.
11. **Aire.** Márgenes laterales de 20 a 24, separación entre bloques de 24 a 32. Si una
    pantalla se siente apretada, sobra contenido: se parte en dos, no se achica.
12. **Motion corto y con motivo.** Entrada de tarjetas escalonada, la hoja que sube con
    resorte, respuesta al toque en todo lo pulsable. Los valores salen de `animate`; nada
    se mueve en bucle ni para decorar.

## Rigor del sistema

1. **Tokens de una sola fuente.** Un paquete de tokens que emite los valores para cada
   plataforma. En el código de una pantalla no hay colores, radios ni espaciados
   literales.
2. **Un preset por tipo de superficie, sobre la misma escala.** No todas las pantallas
   mobile son de consumo:
   - **App de cliente** — el lenguaje visual completo de arriba.
   - **App de operación** (personal, tablet de mostrador, tareas repetidas en hora pico)
     — misma forma y mismos tokens, con más densidad, objetivos táctiles más grandes,
     menos imagen y flujos de tres toques o menos.

   El preset se elige por pantalla según quién la usa, y se anota en el design system.
3. **Objetivos táctiles de 44 pt o más** en todo lo pulsable; 48 o más en operación.
4. **El estado nunca es solo color.** Toda etiqueta de estado lleva texto. Un punto de
   estado es una forma dibujada, no un carácter tipográfico.
5. **Cifras tabulares.** Dinero, cantidades, códigos y números de documento usan cifras
   de ancho fijo y se alinean entre filas.
6. **Iconos vectoriales de un solo set, nunca emojis.** Mismo trazo y misma grilla en
   Figma y en código. Un emoji cambia de forma en cada sistema operativo y un frame con
   emojis no es implementable.
7. **Los tres estados, siempre.** Toda pantalla con datos tiene `vacio`, `carga` y
   `error` diseñados e implementados, además de `default`.
8. **Claro y oscuro desde el primer día**, y áreas seguras respetadas en todos los
   bordes. La barra flotante se apoya sobre el área segura inferior, no la tapa.
9. **Teléfono y tablet.** En tablet las tarjetas pasan a más columnas y la hoja inferior
   puede volverse un panel lateral. No es la pantalla de teléfono estirada.
10. **Diseño primero, con un nodo por pantalla.** Cada pantalla existe en Figma antes
    que en código, y el archivo de código de la pantalla abre con el enlace a su nodo.

## Cómo se verifica

**[chequeable]** — el loop lo comprueba solo, sobre el diff o el frame:

- Ningún color, radio ni espaciado literal en el código de una pantalla.
- Ningún emoji usado como icono, ni un carácter usado como punto de estado.
- Todo lo pulsable mide 44 pt o más.
- Toda etiqueta de estado tiene texto.
- Toda pantalla con datos tiene sus cuatro frames y sus cuatro estados en código.
- La barra de navegación es flotante y respeta el área segura inferior.
- El archivo de la pantalla abre con el enlace a su nodo de Figma.

**[principio]** — lo evalúa una persona o `design:design-critique`:

- El producto se distingue de las referencias y de otro producto hecho con esta base.
- La pantalla tiene aire: nada compite con la acción principal.
- El preset elegido corresponde a quién usa la pantalla.

## Lo que la base no es

- **No es para web de escritorio.** Un back-office denso, de teclado y sesiones largas,
  se rige por otra lógica: ahí la tabla es la superficie y la densidad es la virtud.
- **No autoriza a copiar** la marca, la paleta ni las imágenes de las referencias. Se
  toma el lenguaje, no el contenido.
