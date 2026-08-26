---
paths:
  - "**/api/**/*"
  - "**/routes/**/*"
  - "**/controllers/**/*"
  - "**/*route*.{py,ts,js}"
  - "**/*controller*.{py,ts,js}"
---

# REST API

- Preserve established resource naming and response conventions.
- Validate input at the boundary.
- Enforce authentication and authorization independently.
- Use appropriate HTTP status codes.
- Keep error responses stable and safe.
- Add pagination for potentially large collections.
- Make create/update operations idempotent when retries are expected and business semantics permit it.
- Do not expose internal exceptions, SQL, stack traces, or secrets.
- Version or coordinate breaking contract changes deliberately.
