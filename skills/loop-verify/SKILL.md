---
name: loop-verify
description: >-
  Etapa de test del loop. Corre la verificación real de la tarea activa, guarda la
  salida como evidencia y decide verde o rojo. No marca nada verde sin haber
  ejecutado el comando. Trigger con "verificá la tarea", "corré los tests", o vía
  project-loop.
context: fork
model: sonnet
effort: low
---

# loop-verify — Etapa (7) Test

## 0. Reanudar
Lee `.loop/state.md`, `.loop/plan.md` (la `tarea_activa` y sus **tests esperados**)
y la tabla de comandos de `.loop/stack.md`.

Si `stack.md` no tiene comandos cargados, dedúcelos del repo (`package.json`,
`Makefile`, `pyproject.toml`, la CI), **escríbelos en `stack.md`** y sigue. Que el
contrato quede escrito es parte del trabajo: la próxima vuelta no debe volver a adivinar.

## 1. Ejecutar
Corre, en este orden, parando en el primer rojo:
1. los tests de la tarea (patrón acotado, no la suite entera si se puede);
2. typecheck;
3. lint.

Guarda la salida completa en `.loop/test-<TAREA>.log`.

## 1.5 Gate de dispositivo

Si `state.md` dice `mobile: si`, la tarea **no cierra** hasta que su flow pase en los
cuatro dispositivos de la matriz (los ids están en `.loop/stack.md`). No hay dispositivo
primario, y la única verificación diferida es la de la sección 1.6 (entorno que no puede
correr los cuatro dispositivos, con la deuda registrada); en un entorno completo, un
layout que rompe solo en tablet, descubierto al final, ya tiene cinco pantallas
construidas encima.

**Los dispositivos se corren por pares, nunca los cuatro juntos.** Medido: cuatro
emuladores vivos a la vez dejan la máquina sin memoria para los builds que la propia
verificación necesita. El orden es:

1. Bootear el par Android (teléfono + tablet), build/instalar, correr los flows, **apagarlos**.
2. Bootear el par iOS (iPhone + iPad), build/instalar, correr los flows, **apagarlos**.

La cobertura es la misma; lo que cambia es que nunca hay más de dos dispositivos vivos.
Dentro de cada par sí vale bootear una vez y reusar: el costo que se evita es el boot por
dispositivo, no el boot por par.

**Rebuild nativo solo si cambió lo nativo.** Si la tarea tocó únicamente JS/TS, reusá el
binario ya instalado y recargá el bundle. El build nativo completo se paga solo cuando
cambian dependencias nativas o la configuración de Expo.

La app instalada sobrevive al apagado y reencendido del dispositivo: apagar un par no
obliga a reinstalar en la vuelta siguiente, siempre que no borres los datos del emulador.

Corré un `maestro` por dispositivo — cuatro invocaciones en total, dos por par — que es
además lo que deja un log por dispositivo:

```bash
maestro --device <id> test e2e/<flow>.yaml
```

Guardá cada salida en `.loop/device-<dispositivo>-<TAREA>.log`.

### Requisitos para que el flow corra (verificados el 2026-09-21, a los golpes)

1. **`JAVA_HOME` tiene que estar exportado.** Maestro es una herramienta JVM y sin eso
   falla con `Unable to locate a Java Runtime`, que no dice nada sobre la causa real.
2. **Un build debug NO trae la JS adentro**: la sirve Metro en runtime. Si el flow corre
   sin Metro levantado, la app abre en pantalla de error y la aserción falla por el motivo
   equivocado. Levantá Metro y conectá el emulador con `adb reverse tcp:8081 tcp:8081`.
3. **`launchApp` seguido de `assertVisible` es inestable.** La primera carga arma el bundle
   (~12 s medidos, 1131 módulos) y la aserción corre antes de que haya pantalla. Usá una
   espera explícita —`extendedWaitUntil` con su `timeout`— en vez de asumir que la app ya
   renderizó. Verificado: una corrida falló con la pantalla en `Bundling 99%`.
4. **El emulador puede morir por presión de memoria** en medio del flow. Si el dispositivo
   desaparece a mitad de una corrida, el estado es **bloqueado**, no rojo: no es un fallo
   de la app, y reportarlo como tal manda a `fix-loop` a buscar un bug que no existe.

**Si `mobile: no`,** el gate equivalente es que la web levante y responda en el navegador;
registralo igual, con un solo log. Un proyecto `data`, sin UI, no tiene gate de arranque:
le basta el contrato de test/typecheck/lint.

Un rojo en cualquier dispositivo manda la tarea a `fix-loop`, y al volver se reverifica en
**los cuatro**, no solo en el que falló.

Si un dispositivo no arranca en un entorno completo (ver 1.6), el estado es **bloqueado**,
no verde: decilo y explicá qué falta. Nunca declares verde un dispositivo en el que no
corriste el flow.

## 1.6 Sin entorno completo de dispositivos: la tarea queda en `[d]`

**Un entorno cuenta como completo solo si puede correr los cuatro dispositivos**:
`emulator -list-avds` (Android) **y** `xcrun simctl list devices` (iOS) tienen que
responder. En una sesión cloud, que corre en Ubuntu, no responde ninguno; en una máquina
Linux con el SDK de Android responde uno solo. **Verificar la mitad de la matriz no es
verificarla.**

Si `state.md` dice `mobile: si` y el entorno no está completo:

1. Corré igual tests, typecheck y lint (sección 1).
2. Si pasan, la tarea **no** se marca `[x]`: se marca **`[d]`** en `plan.md`, verde en
   código y sin verificar en dispositivos.
3. Agregá una fila a `.loop/deuda-dispositivos.md` (creala si no existe):

   ```markdown
   | Tarea | Pantallas | Entorno donde quedó |
   |---|---|---|
   | T-00X | H-03 · Checkout | sesión cloud |
   ```

4. Sumá uno a `deuda_dispositivos` en `state.md`.

**Saldar la deuda:** `project-loop` te invoca con `saldar deuda <tarea>`. En un entorno
completo, corré la matriz de la sección 1.5 para esa tarea de `.loop/deuda-dispositivos.md`.
Si el flow e2e de la pantalla no existe, no hay matriz que correr y la deuda no se puede
saldar todavía: **no escribas el flow acá**. Devolvé `bloqueado` nombrando el flow que
falta, para que el orquestador lo agregue al plan como tarea de `code-exec`. Si pasa, `[d]` pasa a `[x]`, se saca su fila y se
resta uno a `deuda_dispositivos`. Si falla, la tarea vuelve a `correccion` como cualquier
rojo.

`[d]` no es un verde a medias ni un rojo: es una deuda con nombre. **Nunca la conviertas
en `[x]` sin haber corrido los cuatro dispositivos.**

## 2. Cotejar contra el plan
Los "tests esperados" de la tarea en `plan.md` tienen que existir de verdad y haber
corrido. Si la tarea declaraba un test que no existe, eso es un hallazgo de severidad
**alta**, aunque la suite esté en verde. Una suite verde que no cubre lo que la tarea
prometía no es una tarea terminada.

## 3. Decidir
- **Verde** = comando ejecutado + exit 0 + los tests esperados presentes. Nada más cuenta.
- **Rojo** → registra los hallazgos en `.loop/review-log.md`, pon `etapa = correccion`
  y devuelve control para que entre `fix-loop`.
- **Deuda** (`[d]`) → solo cuando el entorno no puede correr los cuatro dispositivos y
  el resto quedó verde. Ver 1.6.

Nunca declares verde algo que no ejecutaste. Si no pudiste correr el comando, el
estado es **bloqueado**, no verde: decilo y explicá qué falta.

## 4. Cierre
Actualiza `state.md`: `ultima_skill = loop-verify`, la etapa que corresponda y la
ruta del log en la bitácora.

**Devolvé solo el veredicto** (máx. ~10 líneas): verde / rojo / bloqueado, qué comandos
y dispositivos corrieron, rutas de los logs y, si es rojo, los ids `H-00X` registrados.
Nunca pegues la salida de los tests en la respuesta: está en los logs.

Si la tarea quedó verde y toca autenticación, autorización, `tenant_id`/RLS, dinero,
secretos o entrada externa, la siguiente etapa es **seguridad** (`loop-security`),
no cerrar la tarea.
