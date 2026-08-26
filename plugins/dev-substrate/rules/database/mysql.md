---
paths:
  - "**/*.sql"
  - "**/migrations/**/*"
  - "**/repositories/**/*"
---

# MySQL

- Verify the actual schema before writing queries.
- Never assume a table, column, index, or constraint exists.
- Use parameterized queries/ORM bindings.
- Avoid `SELECT *` in application paths unless intentionally required.
- Avoid N+1 and repeated queries inside loops.
- Bound large result sets with pagination, batching, or explicit limits.
- Evaluate indexes against actual filter/join/order patterns; do not add speculative indexes.
- Keep transactions as short as correctness allows.
- Consider concurrency, unique constraints, locking, and idempotency for state changes.
- Schema changes require migrations.
- Prefer backwards-compatible migrations for rolling deployments.
- Never delete or rewrite production data as part of an ordinary code task.
