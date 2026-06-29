# proyecto-loop

Arsenal de skills encadenadas estilo **loop** para arrancar y avanzar proyectos
nuevos de forma iterativa, reanudable y auditable. **Mobile-first** (Expo/React
Native por defecto), con capa web.

## El loop (7 etapas)

```
(1) inicio → (2) análisis → (3) plan → (4) ejecución → (5) revisión → (7) test
                                            ▲                              │
                                            └──── (6) corrección ◀── falla ─┘
                                  (pasa) → ¿más tareas? → sí ↑ · no → entrega
```

## Skills

| # | Skill | Etapa | Qué hace |
|---|-------|-------|----------|
| 1 | `proyecto-loop:project-init` | Inicio | Scaffold + tooling + CI + Tier 1 (Sentry/Supabase) + arranca `.loop/` |
| 2 | `proyecto-loop:requirements-analysis` | Análisis | Épicas/historias, criterios, riesgos, preguntas abiertas |
| 3 | `proyecto-loop:plan-architect` | Plan | Arquitectura + ADRs + tareas atómicas por dependencia |
| 4 | `proyecto-loop:code-exec` | Ejecución | Implementa la siguiente tarea + commit atómico |
| 5 | `proyecto-loop:fix-loop` | Corrección | Prioriza hallazgos, corrige, re-testea |
| 6 | `proyecto-loop:project-loop` | Orquestador | Driver full-auto del ciclo completo |

Reusa del plugin `engineering`: `code-review` (revisión), `debug` (fix-loop),
`testing-strategy` (test), y `deploy-checklist`/`documentation`/`standup` al cierre.
Backbone de metodología opcional: **Superpowers** (TDD, debug 4-fases, brainstorm).

## Mecanismo de estado

Cada proyecto lleva una carpeta `.loop/` (plantillas en `templates/loop/`):
`state.md` (control), `analysis.md`, `plan.md`, `adr/`, `review-log.md`, `stack.md`.
Toda skill **lee** el estado y **escribe** su salida → el loop es reanudable.

## Uso

1. `proyecto-loop:project-init` para arrancar el repo.
2. `proyecto-loop:project-loop` para que el ciclo corra full-auto hasta agotar el plan
   (se detiene solo al fallar o terminar).

O corre las skills una a una siguiendo la columna "Etapa".

## Instalación (local)

Registrado como marketplace local en `~/.claude/settings.json`
(`extraKnownMarketplaces` + `enabledPlugins`). Verifica con `/plugin` en una sesión
interactiva de Claude Code.
