---
paths:
  - "apps/web/**/*.{ts,tsx}"
  - "frontend/**/*.{ts,tsx}"
  - "web/**/*.{ts,tsx}"
  - "src/**/*.tsx"
---

# React / TypeScript

- Prefer TypeScript types derived from actual contracts; do not invent backend response fields.
- Keep API access outside presentational components when the project has services/hooks/query modules.
- Reuse existing UI primitives, design tokens, forms, and state-management conventions.
- Handle loading, empty, error, success, disabled, and retry states where applicable.
- Avoid duplicated server state; use the project's existing fetching/cache layer.
- Keep components focused; split only when responsibility or reuse justifies it.
- Preserve accessibility: labels, keyboard behavior, focus, semantic controls, and meaningful errors.
- Do not introduce global state for local component state.
- Avoid `any` unless there is a documented interoperability reason.
- Do not silently swallow API errors.
