---
paths:
  - "**/*.py"
---

# Python / Flask

> Alternativa a `backend/python-fastapi.md`. **Nunca instales las dos**: matchean
> los mismos archivos y se contradicen.

- Follow the project's existing Python version, formatting, typing, and dependency conventions.
- Keep HTTP concerns in routes/controllers and business rules in services/use cases when those layers exist.
- Keep persistence logic in repositories/data-access modules when that pattern exists.
- Validate request input using the project's existing validation mechanism.
- Return consistent API errors; do not leak stack traces or internal credentials.
- Do not use broad `except Exception` unless re-raising, translating at a boundary, or adding meaningful context.
- Keep transactions at a deliberate application boundary.
- Avoid database calls inside loops when batching/joining is reasonable.
- Use dependency injection or explicit dependencies where the project already follows that approach.
- Add type hints to new public/service code when consistent with the codebase.
- Prefer focused tests for service/business logic over trivial route-only tests.
