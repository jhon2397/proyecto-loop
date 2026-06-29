---
name: project-init
description: >-
  Inicia y hace scaffold de un proyecto nuevo, mobile-first (Expo/React Native
  por defecto). Trigger cuando el usuario dice "nuevo proyecto", "inicializa",
  "scaffold", "arranca repo", "crea la app". Crea estructura, tooling, CI base,
  cablea Tier 1 (Sentry + adaptador de backend Supabase) y arranca el mecanismo
  .loop/. Es la etapa (1) del arsenal proyecto-loop.
---

# project-init — Etapa (1) Inicio

Eres el bootstrap del arsenal **proyecto-loop**. Tu trabajo es dejar un repo
listo para entrar al loop, **sin** implementar features todavía.

## 0. Idempotencia (siempre primero)
- Si ya existe `.loop/state.md`, **no re-scaffoldees**: lee el estado, informa en
  qué etapa está y sugiere la skill correspondiente. Solo continúa si el usuario
  pide reinicializar explícitamente.
- Si el directorio ya tiene un repo, detéctalo y trabaja sobre lo existente
  (completa lo que falte) en vez de sobrescribir.

## 1. Recoger contexto (pregunta solo lo que no puedas inferir)
- **platform:** mobile | web | full-stack | data. Default **mobile** (~95% de casos).
- **nombre** del proyecto y **descripción** en una frase.
- **stack:** propón el default según platform y confirma con trade-offs breves:
  - mobile → **Expo + React Native + TypeScript** (default). Reanimated + FlashList listos.
  - web → **Next.js + TypeScript**.
  - full-stack → monorepo (Expo app + Next + paquete compartido).
  - data → scripts/MCP en Python o TS.

## 2. Scaffold (según platform)
Crea, de forma idempotente:
- Estructura de carpetas idiomática del stack.
- `.editorconfig`, linter + formatter (ESLint + Prettier para TS; ruff/black para Python).
- `.gitignore` apropiado, y `git init` si no es repo.
- **CI base** (GitHub Actions): lint + typecheck + test en push/PR.
- `README.md` esqueleto (qué es, cómo correr, cómo testear).
- Para **mobile/Expo**: `app.json`/`app.config.ts`, navegación base, una pantalla de
  ejemplo. Usa las convenciones de React Native Skills si está disponible.

## 3. Tier 1 de servicios (cablear desde el día 1 — barato y caro de retrofittear)
- **Observabilidad → Sentry:** instala e inicializa (crash + performance) desde el
  primer commit. En Expo cuida source maps / symbolication de Hermes.
- **Backend/Auth/DB → adaptador Supabase:** crea una **capa adaptadora** (interfaz
  de dominio) con binding a Supabase, NO llamadas directas dispersas. Diseña pensando
  en RLS desde el inicio.
- **NO** hardcodees pagos ni email (Tier 2). Quedan diferidos tras su interfaz.

## 4. Arrancar el loop
- Crea la carpeta `.loop/` copiando las plantillas desde
  `${CLAUDE_PLUGIN_ROOT}/templates/loop/` (`state.md`, `stack.md`; las demás se crean
  en su etapa). Si no puedes leer esa ruta, genera los archivos con el contenido
  equivalente.
- Rellena `state.md`: meta (proyecto, platform, stack, autonomía=full-auto por
  defecto, aesthetic si ya se definió) y pon **etapa = analisis**.
- Rellena `stack.md` Tier 1 con Sentry/Supabase = activo; Tier 2 = diferido.
- Commit atómico: `chore: scaffold inicial + tooling + tier1 + loop state`.

## 5. Cierre
Confirma qué se creó (lista breve), el commit, y **sugiere la siguiente skill**:
`requirements-analysis`. Si el usuario corre el arsenal en automático, indícalo a
`project-loop`.
