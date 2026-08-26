---
paths:
  - "mobile/**/*.{ts,tsx,js,jsx}"
  - "apps/mobile/**/*.{ts,tsx,js,jsx}"
---

# React Native

- Optimize for touch, small screens, intermittent connectivity, and mobile lifecycle.
- Do not copy desktop layouts literally.
- Use the project's navigation, state, storage, and networking conventions.
- Make retries safe and idempotent when operations can be repeated.
- Handle offline/slow-network states when business flow requires them.
- Avoid large synchronous work on the UI thread.
- Request platform permissions only when necessary and explain denial/retry states.
- Protect locally stored tokens and sensitive data using the project's secure-storage mechanism.
