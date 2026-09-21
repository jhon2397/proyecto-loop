# Estructura estándar de proyecto

> Fuente única. Ninguna skill describe la estructura por su cuenta: la leen de acá.
> **Lo que el proyecto no usa, no se crea.** Estructura fija significa *mismo lugar
> cuando existe*, no *todas las carpetas siempre*.

Monorepo con npm workspaces.

```
<proyecto>/
├── .loop/                   estado del loop (state, analysis, design, plan, adr/, stack…)
├── .claude/                 reglas, permisos, hooks (los instala loop-rules)
├── apps/
│   ├── mobile/              Expo + React Native + TS   ← siempre Expo, sin excepción
│   └── web/                 Next.js + TS
├── packages/
│   ├── core/                dominio, tipos, validadores + ADAPTADOR de datos (Tier 1)
│   └── ui/                  design system en código ← materializa .loop/design-system.md
├── supabase/                migrations/ · functions/ · seed.sql · config.toml
├── infra/                   docker-compose de self-host (solo si el hosting es self-hosted)
├── e2e/                     flows de Maestro para la matriz de dispositivos
├── docs/
│   └── pitch/               presentación HyperFrames (loop-pitch)
└── .github/workflows/
```

## Por qué cada pieza está donde está

**`packages/core`** es la dirección fija del adaptador de datos que `project-init` cablea
en Tier 1. El dominio importa de `core`; **nunca** llama a Supabase directo. Tener una
única dirección es lo que hace que la regla se pueda verificar en vez de recordar.

**`packages/ui`** es la contraparte en código de `.loop/design-system.md`: tokens y
componentes base. Toda pantalla los reusa; nada de estilos ad-hoc por pantalla.

**`supabase/`** existe siempre que el proyecto tenga backend, con las migraciones
versionadas. **`infra/`** solo aparece si el hosting elegido es self-hosted en el servidor
interno; con Supabase Cloud no hay nada que levantar.

**`e2e/`** guarda los flows de Maestro. Vive en la raíz y no dentro de `apps/mobile`
porque los mismos flows corren contra las dos plataformas.

## Reglas de decisión

- **¿Hay mobile?** Lo pregunta `project-init` siempre, no lo infiere. Si la respuesta es
  sí, `apps/mobile` nace con Expo — no se ofrecen alternativas.
- **¿Web?** Solo si el proyecto la pide. Next.js + TypeScript.
- **Proyecto sin UI (data):** tendría `packages/core`, `supabase/` y nada más.
