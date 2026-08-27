---
name: project-init
description: >-
  Inicia y hace scaffold de un proyecto nuevo, mobile-first (Expo/React Native
  por defecto). Trigger cuando el usuario dice "nuevo proyecto", "inicializa",
  "scaffold", "arranca repo", "crea la app". Crea estructura, tooling, CI base,
  cablea Tier 1 (Sentry + adaptador de backend Supabase) y arranca el mecanismo
  .loop/. Es la etapa (1) del arsenal proyecto-loop.
argument-hint: [nombre-del-proyecto]
allowed-tools: Bash(git init) Bash(git add *) Bash(git commit *) Bash(npx create-expo-app *) Bash(npm install *) Bash(npm run *)
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

## 2.5 Dirección estética (si el proyecto tiene UI)
- Define la **dirección estética** invocando `frontend-design` (propósito, audiencia, tono)
  y `design-taste-frontend` (anti-template); usa `ui-ux-pro-max` para paletas/tipografía.
- No es "un color": tono, densidad, tipografía y principios. Guárdala **completa** en
  `state.md` (`aesthetic`) para que no se reinvente en cada pantalla.
- El **design system** en sí (tokens/componentes) NO se construye aquí: `plan-architect`
  lo agenda como **primera tarea de UI** y se documenta en `.loop/design-system.md`.

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
  defecto, y la **dirección estética completa** en `aesthetic` si el proyecto tiene UI)
  y pon **etapa = analisis**.
- Rellena `stack.md` Tier 1 con Sentry/Supabase = **cableado**, NO activo: instalaste
  el código, pero sin credenciales los dos son inertes. `activo` lo pone quien verifica
  que un evento real llegó.
- Commit atómico: `chore: scaffold inicial + tooling + tier1 + loop state`.

## 5. Cierre
Confirma qué se creó (lista breve), el commit, y **decí explícitamente qué queda
inerte hasta que el usuario pegue credenciales**: sin DSN, Sentry no reporta; sin
claves, el adaptador de Supabase no habla con nada. Listá las variables exactas que
hacen falta (están en `stack.md`) en vez de dejarlo implícito — es el paso que se
olvida y se descubre meses después, cuando hace falta un error de producción que
nunca se registró.

Después **sugiere la siguiente skill**:
`requirements-analysis`. Si el usuario corre el arsenal en automático, indícalo a
`project-loop`.
