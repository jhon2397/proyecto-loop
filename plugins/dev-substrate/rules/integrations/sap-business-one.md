---
paths:
  - "**/sap/**/*"
  - "**/service_layer/**/*"
  - "**/service-layer/**/*"
  - "**/integrations/**/*sap*"
  - "**/integrations/**/*b1*"
---

# SAP Business One / Service Layer

- Never invent SAP Business One Service Layer entities, properties, actions, or enum values.
- Verify against existing working code, `$metadata`, or authoritative SAP documentation.
- Treat Service Layer as OData and preserve correct URL encoding/query semantics.
- Handle authentication/session expiration deliberately.
- Handle pagination for collections.
- Avoid repeated Service Layer requests inside loops when batching/caching/data reshaping can reduce calls.
- Preserve SAP document lifecycle and approval semantics.
- Do not update SAP Business One business documents by direct database DML.
- Verify company database context before issuing company-specific requests.
- Treat SAP numeric IDs, document entries, document numbers, drafts, approval-request IDs, users, series, warehouses, batches, and serials as distinct concepts.
- Log enough correlation information to diagnose an integration without logging credentials or full sensitive payloads.
- For retryable operations, analyze idempotency before automatic retries.
