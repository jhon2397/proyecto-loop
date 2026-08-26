---
paths:
  - "**/wms/**/*"
  - "**/inventory/**/*"
  - "**/warehouse/**/*"
  - "**/picking/**/*"
  - "**/receiving/**/*"
  - "**/shipping/**/*"
---

# WMS Domain

Protect inventory correctness above convenience.

For stock-affecting operations consider:
- warehouse;
- bin/location;
- item;
- quantity/UoM;
- lot/batch;
- serial;
- expiration;
- inventory status;
- owner/tenant;
- source document;
- operation identity/idempotency;
- user/device;
- timestamp.

Do not treat an inventory balance as the only source of truth when the architecture uses movements/reservations.

Explicitly reason about:
- available vs on-hand vs reserved;
- concurrent picking/receiving/replenishment;
- duplicate mobile submissions;
- partial execution;
- cancellation/reversal;
- offline retry;
- ERP/WMS reconciliation.

Never silently overwrite conflicting inventory state.
Prefer auditable movements and explicit state transitions.
