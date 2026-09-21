# proyecto-loop

Arsenal de skills encadenadas estilo **loop** para arrancar y avanzar proyectos
nuevos de forma iterativa, reanudable y auditable. **Mobile-first** (Expo/React
Native por defecto), con capa web.

## El loop (7 etapas)

```
(1) inicio → (2) análisis → (3) diseño → ⏸ revisión humana → (4) plan → (5) reglas
                                                                            │
        ┌───────────────────────────────────────────────────────────────────┘
        └→ (6) ejecución → (7) revisión → (8) test → (9) seguridad
                  ▲                          │            │
                  └──────── (10) corrección ◀┴────────────┘
        (pasa) → ¿más tareas? → sí ↑ · no → entrega → loop-ship (manual)
```

## Skills

| # | Skill | Etapa | Qué hace |
|---|-------|-------|----------|
| 1 | `proyecto-loop:project-init` | Inicio | Scaffold + tooling + CI + Tier 1 (Sentry/Supabase) + arranca `.loop/` |
| 2 | `proyecto-loop:requirements-analysis` | Análisis | Épicas/historias, criterios, riesgos, preguntas abiertas |
| 3 | `proyecto-loop:loop-design` | Diseño | Dirección estética, design system y pantallas en Figma; deja el mapa pantalla ↔ nodo |
| 4 | `proyecto-loop:plan-architect` | Plan | Arquitectura + ADRs + tareas atómicas, desglosadas por pantalla |
| 5 | `proyecto-loop:loop-rules` | Reglas | Instala las convenciones del stack desde `dev-substrate`, ancladas al repo |
| 6 | `proyecto-loop:code-exec` | Ejecución | Implementa la siguiente tarea + commit atómico |
| 7 | `proyecto-loop:loop-verify` | Test | Corre la verificación real, guarda evidencia en `.loop/test-*.log` |
| 8 | `proyecto-loop:loop-security` | Seguridad | Revisa el diff si toca auth, tenant, dinero o secretos |
| 9 | `proyecto-loop:fix-loop` | Corrección | Prioriza hallazgos, corrige, re-testea |
| 10 | `proyecto-loop:project-loop` | Orquestador | Driver full-auto del ciclo completo |
| 11 | `proyecto-loop:loop-ship` | Entrega | Despliegue al servidor. **Manual: toca producción** |
| 12 | `proyecto-loop:loop-adopt` | Entrada brownfield | Reconstruye `.loop/` en un repo que ya existe |
| 13 | `proyecto-loop:loop-status` | — | Lectura barata del estado (haiku, solo lectura) |
| 14 | `proyecto-loop:loop-pitch` | — | Presentación del producto con HyperFrames, usando el design system real. **Manual** |

Reusa del plugin `engineering`: `code-review` (revisión), `debug` (fix-loop),
y `deploy-checklist`/`documentation`/`standup` al cierre. La etapa de test dejó de
delegarse: la cubre `loop-verify`, que exige evidencia ejecutada.
Backbone de metodología opcional: **Superpowers** (TDD, debug 4-fases, brainstorm).

## Convenciones de v0.7.0

- **Estructura estándar de proyecto** — monorepo con workspaces, definido en
  `templates/estructura/monorepo.md`. Fuente única: ninguna skill la describe por su
  cuenta. Lo que el proyecto no usa, no se crea.
- **Matriz de dispositivos** — cada tarea se verifica con Maestro en teléfono y tablet de
  Android e iOS. Se corren **por pares** (primero Android, después iOS), nunca los cuatro
  vivos a la vez, y el rebuild nativo solo ocurre si cambió algo nativo.
- **Catálogo de reglas de UI** — `references/ui-patterns.md`, con cada regla marcada
  `[chequeable]` o `[principio]`. Lo consultan `loop-design` y `code-exec`.
- **Estructura del archivo de Figma** — páginas fijas numeradas y frames nombrados
  `<id de historia> · <Pantalla> · <estado>`, que es la clave del mapa que consume la
  implementación.

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
