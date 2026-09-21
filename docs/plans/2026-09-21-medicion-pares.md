# Medición del ciclo por pares — 2026-09-21

Mide el costo del diseño de verificación por pares de dispositivos, contra el piloto Expo
que ya existe. Reemplaza la pregunta original ("¿funcionan los dispositivos calientes?"),
que quedó respondida antes: no, cuatro dispositivos vivos dejan la máquina sin memoria.

**Máquina:** 24 GB de RAM. **Importante: no estaba descargada.** El punto de partida, con
cero emuladores, ya era de 302 MB libres y 13,9 GB de swap en uso. Todas las cifras de
abajo hay que leerlas contra ese baseline, no contra una máquina vacía.

## Lo que se midió

### Arranque de dispositivos

| Configuración | RAM libre | Swap libre | Compresor | Boot |
|---|---|---|---|---|
| Baseline (sin emuladores) | 302 MB | 1,41 GB | 5,4 GB | — |
| 1 emulador (teléfono Android) | 268 MB | 1,00 GB | 8,7 GB | 29 s |
| **Par Android (teléfono + tablet)** | **191 MB** | **1,05 GB** | **9,2 GB** | **111 s** |

Cada emulador cuesta unos 3 GB de presión de memoria. El par deja ~1,2 GB de margen entre
RAM y swap libres.

### Build nativo de Android

**Completó: 1019 s (17 min)**, 306 tareas de Gradle, APK de 167 MB, exit 0. Los primeros
~9 minutos corrió con el par de emuladores vivo; después se apagaron.

Dos correcciones a lo que parecía estar pasando, que importan más que el número:

1. **El build no se traba, es lento.** Durante la corrida, el proceso de Gradle mostraba
   1-3 % de CPU, lo que parecía un cuelgue. No lo era: la JVM de Gradle está ociosa
   mientras sus **procesos hijos de clang** compilan. Midiendo el árbol completo, el CPU
   agregado llegó a **625 %**. Cualquier diagnóstico futuro tiene que mirar el árbol de
   procesos, no el PID de Gradle.
2. **Los emuladores no son el cuello de botella dominante.** Se los mató a mitad del build
   como experimento de control: el build **no se aceleró**. El CPU siguió igual y la RAM
   libre no subió. Lo que limita es la carga de base de la máquina, no el par.

### Instalación

El APK instala sin problema en el emulador (`adb install -r` → `Success`,
`com.gambriel97.pilotomobileloop`).

## Supervivencia de la app al reencendido — **SÍ**

`loop-verify` afirma que la app instalada sobrevive al apagado del emulador, y de eso
depende toda la regla de "rebuild nativo solo si cambió lo nativo". **Verificado:**

1. Emulador booteado (25 s), APK instalado, paquete confirmado con `pm list packages`.
2. Emulador apagado; se esperó a que muriera el proceso y se liberaran los locks del AVD.
3. Reencendido **sin** `-wipe-data` (30 s).
4. `pm list packages` → el paquete **seguía instalado**.

La optimización es real. Dos intentos anteriores habían fallado por errores de comando
—el lock del AVD todavía tomado, y `setsid`, que no existe en macOS—, no por
comportamiento del sistema; uno llegó a imprimir un "no sobrevivió" que era un falso
negativo, porque el emulador nunca había terminado de arrancar.

## Build nativo vs recarga de bundle

| Operación | Tiempo |
|---|---|
| Build nativo en frío (`assembleDebug`, incluye compilación NDK) | **1019 s** |
| Gradle incremental, sin cambios | **16 s** |
| Gradle incremental **tras tocar un `.tsx`** | **16 s** |
| Bundle JS con Metro (`expo export`, 2,6 MB Hermes) | **10 s** |

Los dos incrementales dan **idéntico**: tocar TypeScript **no dispara rebuild nativo**.
Un cambio de JS/TS cuesta entre 10 y 16 segundos, contra 1019 del build en frío —
**unas 60 a 100 veces menos**.

## Lo que sigue sin medirse

- **El par iOS**: ni boot, ni build, ni flows. Todas las cifras son de Android.
- **El ciclo completo de una tarea** de punta a punta (par Android + par iOS con sus flows).
- Los flows de Maestro en sí: se verificó que Maestro está instalado y responde, pero no
  se corrió un flow real contra la app.

## Conclusión

**La matriz por tarea es viable en pares, y la optimización que la sostiene funciona.**

Las dos condiciones de las que dependía el diseño se verificaron: el par de emuladores
entra en memoria, y la app instalada sobrevive al apagado, así que reusar el binario no es
una suposición. Con eso, el costo real de verificar una tarea que toca solo JS/TS es de
**segundos**, no de minutos.

El costo alto —17 minutos— aparece solo cuando cambian dependencias nativas o la
configuración de Expo, que es exactamente cuando el diseño dice pagarlo.

Dos advertencias para quien lea esto después:

1. **La máquina no estaba descargada** (302 MB libres y 13,9 GB de swap al empezar). En una
   máquina con menos presión, todos estos números mejoran.
2. **Los emuladores no eran el cuello de botella.** Matarlos a mitad del build no lo
   aceleró. Si algún día el ciclo se vuelve lento, mirar la carga general antes de culpar a
   la matriz.
