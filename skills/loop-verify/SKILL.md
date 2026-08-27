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
