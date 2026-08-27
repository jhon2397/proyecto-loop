---
name: loop-security
description: >-
  Revisión de seguridad de la tarea activa, para tareas que tocan autenticación,
  autorización, aislamiento de tenant, dinero, secretos o entrada externa. Trigger
  vía project-loop cuando la tarea toca esas áreas, o "revisá la seguridad de esto".
context: fork
agent: dev-substrate:security-reviewer
---

# loop-security — Revisión de seguridad de la tarea

Aplica SOLO si la tarea activa toca alguna de estas áreas. Si no toca ninguna,
saltea la etapa y decilo explícitamente:

autenticación · autorización · `tenant_id` / RLS · dinero · secretos y configuración ·
entrada externa · webhooks · subida de archivos · operaciones privilegiadas.

## 1. Alcance
Lee el diff de la tarea activa (`git diff` del último commit) y el código
directamente afectado. No audites el repo entero: esto es revisión de un cambio.

## 2. Revisión
Separa siempre:
- **vulnerabilidades verificadas**, con evidencia y precondiciones de explotación;
- **riesgos probables**;
- **endurecimiento opcional**.

Para multi-tenant no alcanza con que exista la política RLS: verificá que la consulta
no la esquive (service_role, consultas administrativas, jobs).

Para dinero: idempotencia, doble gasto, redondeo y unidad monetaria.

## 3. Salida
Registra los hallazgos materiales en `.loop/review-log.md` con el mismo formato
`H-00X` y severidad que consume `fix-loop`. Si no hay nada material, decilo
claramente en vez de llenar la revisión con observaciones cosméticas.

## 4. Cierre
- Con hallazgos abiertos → `etapa = correccion`.
- Sin hallazgos → la tarea puede cerrarse.

## Nota de implementación
Esta skill forkea al subagente `dev-substrate:security-reviewer` (opus, solo lectura).
El namespace del plugin es obligatorio: el nombre pelado `security-reviewer` no resuelve.
Si el plugin `dev-substrate` no está instalado, la skill no puede correr: decilo en vez
de improvisar la revisión inline.
