---
paths:
  - "**/Dockerfile"
  - "**/Dockerfile.*"
  - "**/docker-compose*.yml"
  - "**/docker-compose*.yaml"
  - "**/compose*.yml"
  - "**/compose*.yaml"
  - "infra/**/*"
  - "deploy/**/*"
---

# Docker / Deployment

- Keep images reproducible and minimal.
- Pin versions where reproducibility matters.
- Do not bake secrets into images or committed compose files.
- Prefer non-root runtime users where practical.
- Use healthchecks when services have a meaningful readiness/liveness condition.
- Persist state only through explicit volumes/external services.
- Preserve graceful shutdown and restart behavior.
- Avoid installing build/debug tooling in the final production stage unless required.
- Consider resource limits and log growth for long-running services.
- Do not run destructive Docker cleanup against shared/production hosts without explicit approval.
