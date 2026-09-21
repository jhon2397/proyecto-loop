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

## Lo que NO se midió

Se declara explícitamente en vez de estimarse:

- **Si la app instalada sobrevive al apagado y reencendido del emulador.** `loop-verify`
  lo **afirma** y de eso depende la regla de "rebuild nativo solo si cambió lo nativo". Dos
  intentos fallaron por errores de comando —el lock del AVD todavía tomado en el primero,
  y `setsid`, que no existe en macOS, en el segundo—, no por comportamiento del sistema.
  **Sigue sin verificar.**
- **Build nativo vs recarga de bundle.** Sin ese número, no se sabe cuánto ahorra la
  optimización.
- **El par iOS.** Ni boot, ni build, ni flows.
- **El ciclo completo de una tarea** (par Android + par iOS, de punta a punta).

## Conclusión

**La matriz por tarea es viable en pares, pero cara en esta máquina y por una razón
distinta a la que el diseño suponía.**

El par de emuladores entra en memoria y el build completa. Lo que no entra es la
expectativa de que verificar sea barato: 17 minutos de build nativo, sobre una máquina que
ya arranca con 302 MB libres, multiplicado por las tareas de un plan.

El diseño ya contempla que el build nativo se paga **solo cuando cambia algo nativo**, y en
las tareas que tocan únicamente JS/TS se recarga el bundle. Esa es la optimización que
sostiene todo — y es justamente la que quedó sin medir.

**Recomendación:** antes de correr el loop con la matriz en cada tarea, medir las dos cosas
que faltan (supervivencia de la app al reencendido, y recarga de bundle vs build nativo).
Si la app no sobreviviera al apagado, la optimización no existe y habría que bajar la
matriz a las tareas de UI. La palanca de escape sigue escrita en el spec.
