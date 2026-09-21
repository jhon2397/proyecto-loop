---
name: loop-verify
description: >-
  Etapa de test del loop. Corre la verificación real de la tarea activa, guarda la
  salida como evidencia y decide verde o rojo. No marca nada verde sin haber
  ejecutado el comando. Trigger con "verificá la tarea", "corré los tests", o vía
  project-loop.
effort: medium
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
primario ni verificación diferida: un layout que rompe solo en tablet, descubierto al
final, ya tiene cinco pantallas construidas encima.

**Rebuild nativo solo si cambió lo nativo.** Si la tarea tocó únicamente JS/TS, reusá el
binario ya instalado y recargá el bundle. El build nativo completo se paga solo cuando
cambian dependencias nativas o la configuración de Expo. Sin esta distinción, la matriz
por tarea es impagable.

Corré un `maestro` por dispositivo — cuatro invocaciones, no una — que es además lo que
deja un log por dispositivo:

```bash
maestro --device <id> test e2e/<flow>.yaml
```

Guardá cada salida en `.loop/device-<dispositivo>-<TAREA>.log`.

**Si `mobile: no`,** el gate equivalente es que la web levante y responda en el navegador;
registralo igual, con un solo log. Un proyecto `data`, sin UI, no tiene gate de arranque:
le basta el contrato de test/typecheck/lint.

Un rojo en cualquier dispositivo manda la tarea a `fix-loop`, y al volver se reverifica en
**los cuatro**, no solo en el que falló.

Si un dispositivo no arranca, el estado es **bloqueado**, no verde: decilo y explicá qué
falta. Nunca declares verde un dispositivo en el que no corriste el flow.

## 2. Cotejar contra el plan
Los "tests esperados" de la tarea en `plan.md` tienen que existir de verdad y haber
corrido. Si la tarea declaraba un test que no existe, eso es un hallazgo de severidad
**alta**, aunque la suite esté en verde. Una suite verde que no cubre lo que la tarea
prometía no es una tarea terminada.

## 3. Decidir
- **Verde** = comando ejecutado + exit 0 + los tests esperados presentes. Nada más cuenta.
- **Rojo** → registra los hallazgos en `.loop/review-log.md`, pon `etapa = correccion`
  y devuelve control para que entre `fix-loop`.

Nunca declares verde algo que no ejecutaste. Si no pudiste correr el comando, el
estado es **bloqueado**, no verde: decilo y explicá qué falta.

## 4. Cierre
Actualiza `state.md`: `ultima_skill = loop-verify`, la etapa que corresponda y la
ruta del log en la bitácora.

Si la tarea quedó verde y toca autenticación, autorización, `tenant_id`/RLS, dinero,
secretos o entrada externa, la siguiente etapa es **seguridad** (`loop-security`),
no cerrar la tarea.
