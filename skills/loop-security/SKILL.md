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
El revisor es de **solo lectura**: no puede escribir en `.loop/review-log.md`. Por eso tu
respuesta es el registro, y `project-loop` la copia tal cual al archivo. Tiene que servir
para eso sin edición y sin ocupar más de lo necesario (medido: de 56 a 74 líneas por
revisión, que quedaban en el contexto del orquestador el resto de la corrida).

**Formato de la respuesta: esta plantilla y nada más.**

```
Seguridad: <id de la tarea> — <sin hallazgos | N hallazgos materiales>
- <alta|media|baja> · <archivo:línea> · <qué se puede hacer y con qué precondición> · <fix>
Endurecimiento opcional: <hasta dos ideas en una línea, o "nada">
```

Una línea por hallazgo material, verificado o probable; decí cuál es. Sin encabezados, sin
tablas, sin el razonamiento que te llevó ahí, sin listar lo que revisaste y estaba bien.
Si no hay nada material, la respuesta son dos líneas.

## 4. Cierre
- Con hallazgos → `project-loop` los registra en `review-log.md` con id `H-00X` y pasa a
  `etapa = correccion`.
- Sin hallazgos → la tarea puede cerrarse.

## Nota de implementación
Esta skill forkea al subagente `dev-substrate:security-reviewer` (opus, solo lectura).
El namespace del plugin es obligatorio: el nombre pelado `security-reviewer` no resuelve.
Si el plugin `dev-substrate` no está instalado, la skill no puede correr: decilo en vez
de improvisar la revisión inline.
