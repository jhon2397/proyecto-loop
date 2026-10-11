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
| 3b | `proyecto-loop:loop-presentacion` | Presentación | Con las pantallas aprobadas: guion, storyboard en Figma y pieza animada con HyperFrames |
| 4 | `proyecto-loop:plan-architect` | Plan | Arquitectura + ADRs + tareas atómicas, desglosadas por pantalla |
| 5 | `proyecto-loop:loop-rules` | Reglas | Instala las convenciones del stack desde `dev-substrate`, ancladas al repo |
| 6 | `proyecto-loop:code-exec` | Ejecución | Implementa la siguiente tarea + commit atómico |
| 7 | `proyecto-loop:loop-review` | Revisión | Corre los revisores de la tarea en subagente y deja los hallazgos en `review-log.md` |
| 8 | `proyecto-loop:loop-verify` | Test | Corre la verificación real, guarda evidencia en `.loop/test-*.log` |
| 9 | `proyecto-loop:loop-security` | Seguridad | Revisa el diff si toca auth, tenant, dinero o secretos |
| 10 | `proyecto-loop:fix-loop` | Corrección | Prioriza hallazgos, corrige, re-testea |
| 11 | `proyecto-loop:project-loop` | Orquestador | Driver full-auto del ciclo completo |
| 12 | `proyecto-loop:loop-ship` | Entrega | Despliegue al servidor. **Manual: toca producción** |
| 13 | `proyecto-loop:loop-adopt` | Entrada brownfield | Reconstruye `.loop/` en un repo que ya existe |
| 14 | `proyecto-loop:loop-status` | — | Lectura barata del estado (haiku, solo lectura) |
| 15 | `proyecto-loop:loop-pitch` | — | Presentación del producto con HyperFrames, usando el design system real. **Manual** |
| 17 | `proyecto-loop:loop-doctor` | — | Verifica que la máquina tenga todo lo que el loop usa e instala lo que falta; actualiza el plugin. **Manual** |
| 16 | `proyecto-loop:loop-actualizar` | — | Trae una versión nueva del loop a un proyecto con el loop vendoreado |

Reusa del plugin `engineering`: `code-review` (dentro de `loop-review`), `debug` (fix-loop),
y `deploy-checklist`/`documentation`/`standup` al cierre. La etapa de test dejó de
delegarse: la cubre `loop-verify`, que exige evidencia ejecutada.
Backbone de metodología opcional: **Superpowers** (TDD, debug 4-fases, brainstorm).

**Skills de apoyo por etapa (v0.8.1).** Cada etapa las invoca con la herramienta Skill y
por su nombre completo; si una falta, lo anota en `state.md` y sigue.

| Etapa | Skills |
|-------|--------|
| `project-init` | `superpowers:brainstorming` (idea vaga), `anthropic-skills:frontend-design`, `design-taste-frontend`, `anthropic-skills:ui-ux-pro-max`, `animate`, `react-native-best-practices:react-native-best-practices` (mobile) |
| `requirements-analysis` | `superpowers:brainstorming` (dudas de producto) |
| `loop-design` | las tres de diseño (si no hay `aesthetic`) + `animate` para los tokens de motion |
| `code-exec` | UI: diseño + `animate`; lógica: `superpowers:test-driven-development` |

`scripts/verificar-arsenal.py` falla si una skill cita otra por un nombre corto que la
herramienta Skill no resuelve.

## Novedades de v0.11.1

- **Las etapas responden con una plantilla fija** de campos de una línea, no con un
  resumen libre. Con "máximo 10 líneas" devolvían de 18 a 43; `loop-security`, de 56 a 74.
- **El código de una tarea del plan lo escribe `code-exec`, siempre.** La herramienta
  Agent queda para tareas operativas.
- **`loop-security` es de solo lectura:** devuelve una línea por hallazgo y el
  orquestador la registra en `review-log.md`.

## Novedades de v0.11.0

- **`loop-doctor`** y `herramientas/preparar-maquina.sh`: una máquina nueva queda lista
  con un comando. Cada cosa sale como `OK`, `FALTA`, `AVISO` o `NO VERIFICADO`, e instala
  plugins, skills sueltas, herramientas y variables de entorno.

## Novedades de v0.10.0

- **La propuesta estética se ve en Figma el primer día.** `project-init` invoca
  `loop-design` en modo `propuesta`: 3 variantes de la dirección sobre 2 pantallas
  representativas, a elegir antes del análisis.
- **La presentación del producto, antes de construirlo.** Etapa nueva `loop-presentacion`,
  entre la aprobación del diseño y el plan: guion, storyboard en el mismo archivo de Figma
  (con las pantallas reales como instancias) y pieza animada con HyperFrames. Pregunta
  antes de renderizar. `loop-pitch` la retoma al entregar, con el producto real.
- **Base de estilo mobile** (`references/mobile-style.md`): toda app mobile parte del
  mismo lenguaje visual —superficies blandas, navegación flotante, mucho aire— y del
  mismo rigor de sistema —tokens de una fuente, preset por superficie, estado con texto,
  iconos vectoriales—. Cada producto decide paleta, tipografía y su elemento firma.

## Novedades de v0.9.2

- **El orquestador no implementa, tampoco para destrabar.** Deuda `[d]` → `loop-verify`
  con `saldar deuda`; artefacto que falta (un flow e2e) → tarea nueva para `code-exec`;
  tarea operativa contra un servidor → una persona o `loop-ship`, o un subagente si el
  usuario la autoriza.
- **Etapa `entrega-bloqueada`:** el alto cuando no queda tarea ejecutable pero hay `[d]`,
  `[!]` o decisiones abiertas.
- **Los `NO VERIFICADO` van siempre a `review-log.md`**, que es lo que lee el reporte de
  entrega. Resúmenes de etapa de 10 líneas como máximo.

## Novedades de v0.9.1

- **Lo que una etapa dice que corrió, se comprueba.** `code-exec` y `loop-review` cierran
  su resumen con `Skills invocadas: …`, con los nombres que de verdad pasaron a la
  herramienta Skill. Si falta la que la tarea pedía, `project-loop` deja una línea
  `NO VERIFICADO` que sale en la entrega. No existe el revisor "inline".
- **UI-010 · Nada de formularios inline:** alta y edición van en pantalla, panel o diálogo
  propio, nunca dentro de una fila, lista o tarjeta.

## Novedades de v0.9.0: el loop en la nube

- **Vendoreo:** `scripts/vendorear.py` copia el loop al `.claude/` de un proyecto, para que
  corra en una sesión cloud sin los plugins de la máquina. Las skills de terceros viajan
  fijadas por commit y con su licencia (`terceros.json`); sus citas pasan a nombre corto.
- **Degradación explícita:** si una skill externa no está, la etapa deja una línea
  `NO VERIFICADO` en `review-log.md` y `project-loop` la lista en la entrega
  (`references/dependencias-externas.md`).
- **Deuda de dispositivos `[d]`:** una tarea verde en código pero sin la matriz de cuatro
  dispositivos avanza, y la deuda bloquea la entrega.
- **`loop-actualizar`** y la plantilla que se regenera con cada tag.

## Consumo de tokens (v0.8.0)

Opus se reserva para lo que corre **una vez** o es de alto impacto; lo que corre **por
tarea** va en sonnet y en subagente, para que el contexto del orquestador no crezca.

| Perfil | Skills / agentes |
|--------|------------------|
| opus · high | `requirements-analysis`, `plan-architect`, `loop-design`, `loop-presentacion`, `loop-adopt`, `security-reviewer`, `architect` |
| opus · xhigh (solo al escalar) | `deep-debugger`, en la 2.ª vuelta roja de una tarea |
| sonnet · subagente | `code-exec`, `loop-review`, `loop-verify`, `fix-loop` |
| sonnet | `project-loop` (orquestador), `project-init`, `loop-rules`, `loop-ship`, `loop-pitch` |
| haiku | `loop-status` |

- Cada etapa forkeada devuelve **un resumen**; el detalle queda en `.loop/`.
- Tope por tarea: escalado a `deep-debugger` en `iteracion = 2`, alto en `iteracion = 3`.
- `design:design-critique` corre solo en pantallas nuevas o con cambio de layout.
- **El `model:` de una skill dura un turno.** Si la conversación sigue después (una
  respuesta tuya, una pregunta en texto), vuelve el modelo de la sesión. Por eso las
  skills preguntan con `AskUserQuestion`, que no cierra el turno. Para que el loop corra
  barato de punta a punta, abrí la sesión en sonnet.

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

## Instalación en una máquina nueva

1. Agregar el marketplace e instalar el plugin. Desde la app de escritorio: **+ → Add
   marketplace from GitHub** → `jhon2397/proyecto-loop`, e instalar `proyecto-loop` y
   `dev-substrate`. O desde la terminal:

   ```bash
   claude plugin marketplace add https://github.com/jhon2397/proyecto-loop.git
   claude plugin install proyecto-loop@proyecto-loop-local
   claude plugin install dev-substrate@proyecto-loop-local
   ```

2. Abrir una sesión nueva y correr **`/proyecto-loop:loop-doctor`**. Verifica plugins,
   skills de apoyo, herramientas, entorno y Figma, y ofrece instalar lo que falta.

El verificador también corre solo, sin sesión:

```bash
bash herramientas/preparar-maquina.sh              # verifica
bash herramientas/preparar-maquina.sh --instalar   # instala lo que se puede
bash herramientas/preparar-maquina.sh --actualizar # trae la última versión del loop
```

No instala Xcode, Docker Desktop, los emuladores de Android, la conexión de Figma ni las
skills que provee la cuenta: las informa y dice dónde se resuelven.
