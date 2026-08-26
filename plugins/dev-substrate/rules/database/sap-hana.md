---
paths:
  - "**/*.sql"
  - "**/hana/**/*"
  - "**/queries/**/*"
---

# SAP HANA

- Use SAP HANA SQL syntax; do not assume SQL Server/MySQL syntax is valid.
- Verify schema, table, view, and column names before using them.
- Preserve exact identifier case/quoting conventions used by the project.
- Prefer parameterized execution.
- Avoid unnecessary full-table scans and unbounded application queries.
- Check joins and filters against the actual SAP/company schema.
- Distinguish SAP Business One system tables/views from project-owned tables.
- Do not perform unsupported direct DML against SAP Business One business data.
- For business document operations, prefer supported SAP APIs/mechanisms.
- Treat direct database access primarily as read/reporting/integration support unless the project explicitly documents a supported write mechanism.
