---
name: loop-doctor
description: >-
  Verifica que esta máquina tenga todo lo que el loop necesita —plugins, skills de apoyo,
  herramientas, entorno y Figma— e instala lo que falta. También trae la última versión
  del plugin. Trigger con "prepará esta máquina", "qué le falta al loop", "instalá lo que
  falta", "actualizá el loop". Manual: cambia la instalación de la máquina.
argument-hint: "[instalar | actualizar]"
model: sonnet
effort: low
disable-model-invocation: true
---

# loop-doctor — La máquina, lista para el loop

El plugin trae las skills del loop y nada más. Lo que el loop **usa** vive afuera: otros
plugins, skills sueltas, herramientas de línea de comandos, variables de entorno, la
conexión de Figma. En una máquina nueva falta casi todo, y el loop no se rompe por eso:
anota `NO VERIFICADO` y sigue, con lo cual el resultado es peor sin que nadie lo note.
Esta skill lo hace visible y lo arregla.

## Preguntas al usuario: siempre con `AskUserQuestion`
Toda pregunta de esta skill (confirmar, elegir, reinicializar) va con la herramienta
`AskUserQuestion`, **nunca en texto**. Una pregunta en texto cierra el turno, y la
respuesta llega en un turno nuevo que ya no corre con el `model:` de esta skill sino
con el de la sesión: el resto del trabajo se hace con otro modelo y otro costo.
Si `AskUserQuestion` no está disponible, hacé
la pregunta en texto como **último** mensaje y no sigas trabajando en ese turno.

## 1. Verificar (no cambia nada)
Corré el verificador y mostrá su salida tal cual:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/herramientas/preparar-maquina.sh"
```

Cada línea dice `OK`, `FALTA`, `AVISO` o `NO VERIFICADO`. No resumas un `NO VERIFICADO`
como si fuera un `OK`: significa que no se pudo comprobar.

## 2. Lo que solo se ve desde una sesión
El script corre en la terminal y hay dos cosas que desde ahí no se ven. Comprobalas vos:

- **Skills de la cuenta.** Mirá tu lista de skills disponibles y decí cuáles de estas
  están: `engineering:code-review`, `engineering:architecture`, `design:design-critique`,
  `anthropic-skills:frontend-design`, `anthropic-skills:ui-ux-pro-max`, `figma:figma-use`.
  No se instalan desde acá: las habilita la cuenta o la organización en la app. Qué
  etapa usa cada una y qué deja sin revisar si falta está en
  `${CLAUDE_PLUGIN_ROOT}/references/dependencias-externas.md`.
- **Figma.** Llamá a una herramienta de solo lectura del conector de Figma. Si responde,
  está conectado; si pide autorización, decí que se conecta desde la configuración de
  conectores de la app. Sin Figma no hay propuesta estética, pantallas ni storyboard.

## 3. Instalar lo que falta
Si el verificador dejó algún `FALTA`, mostrá la lista y preguntá con `AskUserQuestion`:
**Instalar todo lo que se pueda** · **Solo mostrarme los comandos** · **No instalar**.

Con el sí:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/herramientas/preparar-maquina.sh" --instalar
```

Instala plugins y marketplaces (con la CLI `claude`), skills sueltas (con `npx skills`),
herramientas (con Homebrew, solo en macOS) y agrega a `~/.zshenv` las variables que
falten, con respaldo del archivo.

**No instala**, y hay que decirlo: Xcode, Docker Desktop, las imágenes y los emuladores
de Android, la conexión de Figma y las skills de la cuenta. Para cada una que falte,
decí dónde se resuelve.

Después volvé a correr el paso 1 y mostrá qué cambió.

## 4. Actualizar el loop
Si el argumento es `actualizar`, o el usuario lo pide:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/herramientas/preparar-maquina.sh" --actualizar
```

Trae la última versión de `proyecto-loop` y `dev-substrate`. Mostrá la versión que quedó.

## 5. Cierre
- Decí en una lista corta qué quedó `OK`, qué se instaló y qué sigue faltando, con el
  motivo de cada faltante.
- **Si se instaló o actualizó algo, hay que abrir una sesión nueva**: los plugins y las
  skills cargan al iniciar. Y no conviene actualizar con una corrida del loop abierta en
  otra sesión: esa sesión mezcla la versión vieja con la nueva.
- Esta skill no toca ningún proyecto ni mueve la `etapa` del loop.
