---
name: dev-db-review
description: >-
  Revisa cambios de esquema, consultas o migraciones. Correctitud, índices,
  transacciones, concurrencia, integridad, aislamiento de tenant y riesgo operativo.
  Trigger con "revisá esta migración", "revisá esta query", "esto escala".
argument-hint: [migración|query|módulo]
model: opus
effort: high
disallowed-tools: Edit Write NotebookEdit
---

# dev-db-review — revisión de base de datos

Objetivo de la revisión:

$ARGUMENTS

Inspeccioná el esquema real y las consultas relevantes antes de concluir nada.
Nunca asumas que un objeto de esquema existe: verificalo.

Revisá:
- tablas y columnas exactas;
- claves y constraints;
- índices, y si la consulta los usa de verdad;
- plan de ejecución cuando sea practicable;
- N+1 y consultas repetidas;
- alcance de la transacción;
- aislamiento y concurrencia;
- locking;
- paginación y batching;
- seguridad de la migración y su rollback;
- compatibilidad hacia atrás durante el despliegue;
- aislamiento de tenant: en Postgres, que la política RLS exista y que la consulta
  no la esquive con service_role, consultas administrativas o jobs.

Reportá por severidad, con ubicación y corrección concreta. Si no hay nada material,
decilo claramente en vez de llenar la revisión con observaciones cosméticas.

No edites código: esta skill revisa. El arreglo lo aplica quien corresponda.
