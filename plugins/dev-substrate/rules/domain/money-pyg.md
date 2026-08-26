---
paths:
  - "**/*money*"
  - "**/*monto*"
  - "**/*importe*"
  - "**/*amount*"
  - "**/ledger/**/*"
  - "**/contabilidad/**/*"
  - "**/prestamos/**/*"
---

# Dinero (Paraguay)

- El guaraní **no tiene centavos**: los montos son enteros. Nunca uses `float`,
  `double` ni `number` de punto flotante para dinero, en ningún lenguaje ni en la base.
- Postgres: `bigint` (unidades enteras de PYG). TypeScript: `bigint` o entero con
  el tipo de dominio del proyecto, nunca `number` crudo.
- El redondeo se decide y se documenta una sola vez, en el dominio, no en cada cálculo.
- Toda operación de dinero pasa por el backend: nunca se calcula ni se confirma en el cliente.
- Contabilidad por partida doble: todo asiento cuadra; el ledger es inmutable
  (se corrige con un contra-asiento, jamás con un UPDATE).
- Toda operación que mueve plata es idempotente y lleva clave de idempotencia.
