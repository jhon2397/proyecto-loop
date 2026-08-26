# Arsenal unificado — Plan de implementación

> **Para ejecución agéntica:** usar `superpowers:executing-plans` (inline, con checkpoints) para recorrer este plan tarea por tarea. Los pasos usan checkbox (`- [ ]`).

**Goal:** fusionar el `claude-code-dev-system` con `proyecto-loop` en un solo sistema de dos capas, distribuido por el marketplace que ya funciona, descartando todo lo que ya está cubierto por skills instaladas.

**Arquitectura:** dos plugins en un marketplace. `proyecto-loop` = motor de proceso para proyectos nuevos (máquina de estados `.loop/`). `dev-substrate` = sustrato para repos que ya existen (reglas con `paths`, subagentes, permisos, hooks). El pegamento son dos skills nuevas: `substrate-init` (entrada brownfield) y `loop-rules` (el loop instala reglas del sustrato).

**Tech stack:** Claude Code 2.1.241 (runtime de la app de escritorio), plugins/marketplace por GitHub, YAML frontmatter, hooks de `settings.json`.

## Global Constraints

- **No hay CLI de `claude` en esta máquina.** Todo se valida en la app de escritorio. `/doctor`, `/permissions`, `/status`, `/memory` NO están disponibles: la verificación se hace con hooks y con lectura de archivos.
- **Las skills cargan al inicio de la sesión.** Todo cambio en un plugin exige: resync del marketplace en la app → **sesión nueva**.
- **Nunca correr `install-global.sh --force`**: pisaría `~/.claude/settings.json` con los 17 plugins y 4 marketplaces registrados.
- El repo `github.com/jhon2397/proyecto-loop` **debe seguir público**: la app clona por HTTPS sin auth.
- Idioma de todos los prompts de skills: **español**.
- Cada tarea termina en un commit atómico en `~/Documents/Desarrollos/proyecto-loop`.
- Los archivos bajo `~/.claude/` no están versionados: se editan con cuidado y se anota el cambio en el commit correspondiente del repo.

---

## Criterio: qué del kit se instala y qué se descarta

La regla es una sola: **si algo que ya está instalado lo cubre igual o mejor, el kit no lo aporta.** Resultado del cruce contra el arsenal actual (17 plugins + 4 skills sueltas + skills bundled de Claude Code):

| Pieza del kit | Ya cubierto por | Decisión |
|---|---|---|
| `dev-review` | `/code-review` bundled (corre forkeado, tiene verify pass, `--fix`, `--comment`, niveles de esfuerzo) + `engineering:code-review` | **Descartar** |
| `dev-security` | `/security-review` bundled | **Descartar como entrada**; su contenido se recicla en el agente `security-reviewer` |
| `dev-debug` | `superpowers:systematic-debugging` + `engineering:debug` | **Descartar** |
| `dev-implement` | `superpowers:test-driven-development` + `proyecto-loop:code-exec` | **Descartar** |
| `dev-analyze` | `superpowers:brainstorming` + `superpowers:writing-plans` + agente `Plan` | **Descartar** |
| `project-bootstrap` | `/init` bundled (con `CLAUDE_CODE_NEW_INIT=1` propone además skills y hooks) | **Reorientar** → `substrate-init`, que hace lo que `/init` no hace: elegir reglas de la librería y escribir permisos + hooks |
| `dev-db-review` | nada | **Conservar** |
| agente `code-explorer` (haiku) | agente `Explore` built-in | **Descartar** |
| agente `debugger` (sonnet) | `engineering:debug` | **Descartar** |
| agente `code-reviewer` (sonnet) | `/code-review` bundled | **Descartar** |
| agentes `architect`, `deep-debugger`, `security-reviewer` | nada (no tenés ni un subagente propio instalado) | **Conservar** |
| `rule-library/` (9 reglas con `paths`) | nada — en especial SAP B1, HANA y WMS | **Conservar. Es el activo real del kit.** |
| `presets/` | nada | **Conservar** |
| `project-template/settings.json` | nada | **Conservar y endurecer** |
| `global/.claude/CLAUDE.md` (128 líneas) | comportamiento de fábrica del modelo, en buena parte | **Recortar a ~35 líneas** y moverlo a `~/.claude/rules/` con `paths` |
| `scripts/*.ps1`, `scripts/*.sh` | el marketplace de plugins | **Descartar** |

**De 7 skills del kit sobrevive 1. De 6 agentes sobreviven 3. La rule-library sobrevive entera.**

Un agente propio se gana el lugar solo si cumple las dos condiciones: tiene un perfil de modelo/herramientas que ningún agente bundled da, **y** alguna de nuestras skills lo usa como destino de `context: fork`.

---

## Mapa de archivos

```text
~/Documents/Desarrollos/proyecto-loop/          # repo canónico = marketplace
├── .claude-plugin/
│   └── marketplace.json                        # MODIFICAR: agregar 2º plugin
├── .claude-plugin/plugin.json                  # MODIFICAR: 0.2.0 → 0.3.0
├── skills/                                     # plugin proyecto-loop (6 skills)
│   ├── project-init/SKILL.md                   # MODIFICAR: frontmatter + hooks
│   ├── requirements-analysis/SKILL.md          # MODIFICAR: frontmatter
│   ├── plan-architect/SKILL.md                 # MODIFICAR: frontmatter + paso loop-rules
│   ├── code-exec/SKILL.md                      # MODIFICAR: frontmatter
│   ├── fix-loop/SKILL.md                       # MODIFICAR: frontmatter
│   ├── project-loop/SKILL.md                   # MODIFICAR: frontmatter + etapas nuevas
│   ├── loop-rules/SKILL.md                     # CREAR
│   ├── loop-verify/SKILL.md                    # CREAR
│   ├── loop-security/SKILL.md                  # CREAR
│   └── loop-status/SKILL.md                    # CREAR
├── templates/loop/stack.md                     # MODIFICAR: bloque de comandos
└── plugins/
    └── dev-substrate/                          # CREAR: plugin nuevo
        ├── .claude-plugin/plugin.json
        ├── agents/
        │   ├── architect.md
        │   ├── deep-debugger.md
        │   └── security-reviewer.md
        ├── skills/
        │   ├── substrate-init/SKILL.md
        │   ├── dev-db-review/SKILL.md
        │   └── sap-service-layer/SKILL.md
        ├── rules/                              # librería (datos, no se cargan solas)
        │   ├── api/rest.md
        │   ├── backend/python-flask.md
        │   ├── database/mysql.md
        │   ├── database/sap-hana.md
        │   ├── devops/docker.md
        │   ├── domain/wms.md
        │   ├── domain/money-pyg.md              # CREAR
        │   ├── frontend/react-typescript.md
        │   ├── integrations/sap-business-one.md
        │   └── mobile/react-native.md
        ├── presets/{base,web-saas,sap-integration,wms-sap,mobile-expo}.txt
        └── templates/
            ├── CLAUDE.md
            └── settings.json                   # permisos + hooks

~/.claude/rules/ingenieria.md                   # CREAR (fuera del repo)
```

---

### Tarea 0: Base de ingeniería personal como regla con `paths`

Lo más barato del plan y lo primero que se nota. Hoy no tenés `~/.claude/rules/` — el mecanismo está sin usar. En vez de sumar 128 líneas a todas las sesiones, entran ~35 y solo cuando tocás código.

**Files:**
- Crear: `~/.claude/rules/ingenieria.md`

**Interfaces:**
- Produce: comportamiento base de ingeniería, activo solo en archivos de código. Ninguna otra tarea depende de esto.

- [ ] **Paso 1: Crear el directorio**

```bash
mkdir -p ~/.claude/rules
```

- [ ] **Paso 2: Escribir la regla**

Contenido exacto de `~/.claude/rules/ingenieria.md`:

```markdown
---
paths:
  - "**/*.{ts,tsx,js,jsx,mjs,cjs}"
  - "**/*.{py,sql,sh,rb,php}"
  - "**/*.{java,kt,swift,go,rs}"
---

# Ingeniería

## Prioridades
Correctitud > simplicidad > mantenibilidad > seguridad > rendimiento.
La solución más chica que sea correcta gana.

## Antes de editar
- Leé la implementación existente y buscá un patrón similar ya presente en el repo.
- Identificá dependencias e impacto antes de escribir código.

## Alcance
Cambios quirúrgicos. No refactorices código no relacionado, no renombres símbolos ajenos
a la tarea, no reformatees archivos que no tocás, no agregues ni subas dependencias sin
un motivo concreto. Los problemas que encuentres de paso se reportan aparte, no se
arreglan de prepo.

## Grounding
Nunca inventes APIs, métodos de librería, opciones de configuración, tablas, columnas,
campos de servicios externos ni esquemas de respuesta. Verificá contra el repo o la
documentación. Si no lo podés verificar, decilo en vez de adivinar.

## Contexto
No leas el repo entero. Búsqueda dirigida, lookup de símbolos, trazado de imports.

## Verificación
Corré primero el chequeo más chico que sea relevante: test enfocado → lint → typecheck → build.
Nunca declares verificado algo que no ejecutaste.

## Cierre
Terminá con: qué cambió · archivos importantes · verificaciones ejecutadas y su resultado ·
riesgos o pendientes. Sin relleno.
```

- [ ] **Paso 3: Verificar que carga**

Abrí una sesión nueva de la app en cualquier repo con código y pedí: *"leé `package.json` y decime qué instrucciones de ingeniería tenés cargadas"*. La regla debe aparecer recién después de que lea un archivo que matchee (las reglas con `paths` cargan por demanda, no al inicio).

Contra-prueba: en una sesión donde solo abrís archivos `.md`, la regla **no** debe estar cargada.

- [ ] **Paso 4: Sin commit (fuera del repo)**

Anotarlo: el contenido queda espejado en `plugins/dev-substrate/templates/` en la Tarea 5 para no perderlo.

---

### Tarea 1: Endurecer las 6 skills del loop (v0.3.0)

Hoy las 6 skills declaran solo `name` y `description`. `project-loop` es un driver full-auto que commitea y Claude lo puede lanzar por su cuenta.

**Files:**
- Modificar: `skills/project-loop/SKILL.md` (frontmatter)
- Modificar: `skills/project-init/SKILL.md` (frontmatter)
- Modificar: `skills/requirements-analysis/SKILL.md` (frontmatter)
- Modificar: `skills/plan-architect/SKILL.md` (frontmatter)
- Modificar: `skills/code-exec/SKILL.md` (frontmatter)
- Modificar: `skills/fix-loop/SKILL.md` (frontmatter)
- Modificar: `.claude-plugin/plugin.json` (version)

**Interfaces:**
- Produce: contrato de invocación estable para todas las skills del loop. Las tareas 2, 6, 7 y 8 asumen estos campos.

- [ ] **Paso 1: `project-loop` — cerrarlo a invocación manual**

Reemplazar el frontmatter completo por:

```yaml
---
name: project-loop
description: >-
  Meta-orquestador del arsenal. Lee .loop/state.md y dispara la skill de la etapa
  actual, encadenando Ejecución → Revisión → Test → (Corrección) → siguiente tarea
  hasta agotar el plan. Full-auto: para solo al fallar o al terminar. Trigger con
  "corre el loop", "automatiza el ciclo", "sigue con el proyecto", "avanza solo".
argument-hint: [ruta-del-proyecto]
version: 0.3.0
disable-model-invocation: true
disallowed-tools: AskUserQuestion
---
```

Motivo de cada campo: `disable-model-invocation` porque commitea y no querés que arranque solo; `disallowed-tools: AskUserQuestion` porque la skill declara "full-auto" y hoy nada se lo impide — es el caso que la documentación cita textualmente para bucles en background.

- [ ] **Paso 2: `plan-architect` y `requirements-analysis` — razonamiento arriba**

En ambos archivos, agregar debajo de `description`:

```yaml
model: opus
effort: high
```

- [ ] **Paso 3: `code-exec` — esfuerzo alto y permisos pre-aprobados**

Agregar debajo de `description`:

```yaml
effort: high
allowed-tools: Bash(npm run *) Bash(npx tsc *) Bash(npx eslint *) Bash(git add *) Bash(git commit *) Bash(git status *)
```

`allowed-tools` recorta los prompts de permiso durante el turno que invoca la skill; el permiso se limpia con tu siguiente mensaje.

- [ ] **Paso 4: `fix-loop` — esfuerzo alto**

Agregar debajo de `description`:

```yaml
effort: high
```

- [ ] **Paso 5: `project-init` — permisos de scaffold**

Agregar debajo de `description`:

```yaml
argument-hint: [nombre-del-proyecto]
allowed-tools: Bash(git init) Bash(git add *) Bash(git commit *) Bash(npx create-expo-app *) Bash(npm install *) Bash(npm run *)
```

- [ ] **Paso 6: Subir versión**

En `.claude-plugin/plugin.json`, cambiar `"version": "0.2.0"` por `"version": "0.3.0"`.

- [ ] **Paso 7: Verificar sintaxis del frontmatter**

```bash
cd ~/Documents/Desarrollos/proyecto-loop && python3 -c "
import sys,glob
try: import yaml
except ImportError: sys.exit('instalá pyyaml o revisá a mano')
for f in glob.glob('skills/*/SKILL.md'):
    t=open(f).read().split('---')
    d=yaml.safe_load(t[1])
    print(f, '->', sorted(d.keys()))
"
```

Esperado: cada archivo lista sus campos sin lanzar excepción de YAML.

- [ ] **Paso 8: Commit**

```bash
cd ~/Documents/Desarrollos/proyecto-loop
git add skills .claude-plugin/plugin.json
git commit -m "feat: frontmatter explícito en las 6 skills del loop (modelo, esfuerzo, permisos, invocación) [v0.3.0]"
```

---

### Tarea 2: Aislar las etapas pesadas con `context: fork`

El riesgo estructural del full-auto: el contenido de cada skill invocada queda en el contexto por el resto de la sesión. Después de N tareas el orquestador se ahoga. Esta tarea va **sola y con verificación empírica**, porque el comportamiento de forkear una skill invocada desde otra skill hay que comprobarlo, no asumirlo.

**Files:**
- Modificar: `skills/code-exec/SKILL.md` (frontmatter)

**Interfaces:**
- Consume: frontmatter de la Tarea 1.
- Produce: `code-exec` devuelve al orquestador solo su resumen final, no su transcripción.

- [ ] **Paso 1: Agregar el fork a `code-exec`**

Agregar al frontmatter:

```yaml
context: fork
```

- [ ] **Paso 2: Prueba empírica en el piloto**

En `~/Documents/Desarrollos/piloto-mobile-loop` (que ya tiene `.loop/` y plan), sesión nueva:

```text
proyecto-loop:project-loop
```

Observar: `code-exec` debe aparecer como tarea en background/subagente y volver con un resumen, no con toda su ejecución inline.

- [ ] **Paso 3: Decidir con evidencia**

- Si forkea y el loop sigue encadenando: se queda.
- Si el orquestador pierde el hilo del estado, o la skill no forkea al ser invocada desde `project-loop`: **revertir este campo** y anotar el resultado en el commit. El fallback vale igual: el loop funciona hoy sin fork.

- [ ] **Paso 4: Commit (según resultado)**

```bash
cd ~/Documents/Desarrollos/proyecto-loop
git add skills/code-exec/SKILL.md
git commit -m "perf: code-exec corre forkeado para no inflar el contexto del orquestador"
```

o, si se revierte:

```bash
git checkout skills/code-exec/SKILL.md
```

---

### Tarea 3: Esqueleto del plugin `dev-substrate` + los 3 subagentes

No tenés ni un subagente propio instalado (`~/.claude/agents/` no existe). Estos tres son aporte neto del kit.

**Files:**
- Crear: `plugins/dev-substrate/.claude-plugin/plugin.json`
- Crear: `plugins/dev-substrate/agents/architect.md`
- Crear: `plugins/dev-substrate/agents/deep-debugger.md`
- Crear: `plugins/dev-substrate/agents/security-reviewer.md`

**Interfaces:**
- Produce: los agent types `architect`, `deep-debugger`, `security-reviewer`, usados como destino de `context: fork` en las tareas 6 y 9.

- [ ] **Paso 1: Crear estructura y manifiesto**

```bash
mkdir -p ~/Documents/Desarrollos/proyecto-loop/plugins/dev-substrate/{.claude-plugin,agents,skills,rules,presets,templates}
```

Contenido de `plugins/dev-substrate/.claude-plugin/plugin.json`:

```json
{
  "name": "dev-substrate",
  "description": "Sustrato de convenciones para repos existentes: librería de reglas con paths (SAP B1, HANA, WMS, Docker, REST, React, RN, Python), subagentes de alto razonamiento, permisos endurecidos y hooks de calidad. Complementa a proyecto-loop, que cubre proyectos nuevos.",
  "version": "0.1.0",
  "author": { "name": "Gabriel" },
  "license": "MIT"
}
```

- [ ] **Paso 2: `architect.md`**

Copiar el archivo del kit (`global/.claude/agents/architect.md`) tal cual y agregar dos campos al frontmatter:

```yaml
---
name: architect
description: Especialista en arquitectura para decisiones de alto impacto, límites de sistema, escalabilidad, consistencia de datos, migraciones y cambios que cruzan servicios. Usar cuando la decisión tiene trade-offs reales.
tools: Read, Glob, Grep
model: opus
effort: high
color: purple
---
```

El cuerpo en inglés del kit se traduce a español (el resto del arsenal está en español; mezclar idiomas degrada la adherencia).

- [ ] **Paso 3: `deep-debugger.md`**

Mismo procedimiento, frontmatter:

```yaml
---
name: deep-debugger
description: Especialista en fallas difíciles: intermitentes, de concurrencia, distribuidas, multi-servicio, de consistencia de base de datos o de integración, donde la causa raíz no es obvia.
tools: Read, Glob, Grep, Bash
model: opus
effort: xhigh
color: red
---
```

- [ ] **Paso 4: `security-reviewer.md`**

Frontmatter, con el foco puesto en lo que realmente te importa (multi-tenant, plata, SAP):

```yaml
---
name: security-reviewer
description: Revisor de seguridad de aplicación: autenticación, autorización a nivel de objeto, aislamiento de tenant (RLS), manejo de secretos, inyección, SSRF, webhooks, replay/idempotencia y operaciones privilegiadas. Usar en cambios sensibles de alto impacto.
tools: Read, Glob, Grep
model: opus
effort: high
color: orange
---
```

En el cuerpo, agregar al listado de foco dos líneas que el kit no tiene y tu dominio sí exige:

```markdown
- aislamiento de tenant vía RLS de Postgres: que la política exista Y que la consulta no la esquive con service_role;
- operaciones de dinero: idempotencia, doble gasto, redondeo y unidad monetaria.
```

- [ ] **Paso 5: Commit**

```bash
cd ~/Documents/Desarrollos/proyecto-loop
git add plugins/dev-substrate
git commit -m "feat(dev-substrate): esqueleto del plugin + 3 subagentes de alto razonamiento"
```

---

### Tarea 4: Librería de reglas, con las colisiones corregidas

**Files:**
- Crear: `plugins/dev-substrate/rules/**` (10 archivos)
- Crear: `plugins/dev-substrate/presets/*.txt` (5 archivos)

**Interfaces:**
- Produce: catálogo de reglas que `substrate-init` (Tarea 5) y `loop-rules` (Tarea 8) copian al repo destino. Los nombres de archivo son la interfaz: los presets los referencian por ruta relativa.

- [ ] **Paso 1: Copiar las 9 reglas del kit**

```bash
KIT=<ruta-donde-descomprimiste>/claude-code-dev-system
DST=~/Documents/Desarrollos/proyecto-loop/plugins/dev-substrate/rules
cp -R "$KIT/rule-library/." "$DST/"
ls -R "$DST"
```

- [ ] **Paso 2: Corregir la colisión React / React Native**

En `rules/frontend/react-typescript.md`, reemplazar el bloque `paths` por:

```yaml
---
paths:
  - "apps/web/**/*.{ts,tsx}"
  - "frontend/**/*.{ts,tsx}"
  - "web/**/*.{ts,tsx}"
  - "src/**/*.tsx"
---
```

Motivo: hoy declara `**/*.{ts,tsx,js,jsx}` y en el preset `wms-sap` se instala junto a `mobile/react-native.md`. Al tocar un archivo de la app móvil cargan las dos reglas y se contradicen; la documentación dice explícitamente que ante instrucciones contradictorias Claude puede elegir cualquiera.

- [ ] **Paso 3: Corregir el sobre-alcance de la regla de MySQL**

En `rules/database/mysql.md`, reemplazar el bloque `paths` por:

```yaml
---
paths:
  - "**/*.sql"
  - "**/migrations/**/*"
  - "**/repositories/**/*"
---
```

Motivo: `**/models/**` atrapaba archivos `.ts` y `.py` que no tienen nada que ver con SQL.

- [ ] **Paso 4: Crear la regla de dinero (Paraguay)**

Contenido exacto de `rules/domain/money-pyg.md`:

```markdown
---
paths:
  - "**/*money*"
  - "**/*monto*"
  - "**/*importe*"
  - "**/*amount*"
  - "**/ledger/**/*"
  - "**/contabilidad/**/*"
  - "**/prestamos/**/*"
---

# Dinero (Paraguay)

- El guaraní **no tiene centavos**: los montos son enteros. Nunca uses `float`,
  `double` ni `number` de punto flotante para dinero, en ningún lenguaje ni en la base.
- Postgres: `bigint` (unidades enteras de PYG). TypeScript: `bigint` o entero con
  el tipo de dominio del proyecto, nunca `number` crudo.
- El redondeo se decide y se documenta una sola vez, en el dominio, no en cada cálculo.
- Toda operación de dinero pasa por el backend: nunca se calcula ni se confirma en el cliente.
- Contabilidad por partida doble: todo asiento cuadra; el ledger es inmutable
  (se corrige con un contra-asiento, jamás con un UPDATE).
- Toda operación que mueve plata es idempotente y lleva clave de idempotencia.
```

- [ ] **Paso 5: Presets**

Copiar los 3 presets del kit y agregar dos. Contenido exacto:

`presets/web-saas.txt`:
```text
api/rest.md
backend/python-flask.md
frontend/react-typescript.md
database/mysql.md
devops/docker.md
```

`presets/sap-integration.txt`:
```text
api/rest.md
backend/python-flask.md
database/sap-hana.md
devops/docker.md
integrations/sap-business-one.md
```

`presets/wms-sap.txt`:
```text
api/rest.md
backend/python-flask.md
frontend/react-typescript.md
mobile/react-native.md
database/mysql.md
devops/docker.md
integrations/sap-business-one.md
domain/wms.md
```

`presets/mobile-expo.txt`:
```text
mobile/react-native.md
api/rest.md
```

`presets/financiera.txt`:
```text
api/rest.md
frontend/react-typescript.md
mobile/react-native.md
domain/money-pyg.md
devops/docker.md
```

- [ ] **Paso 6: Verificar que todo preset apunta a un archivo que existe**

```bash
cd ~/Documents/Desarrollos/proyecto-loop/plugins/dev-substrate
for p in presets/*.txt; do
  while read -r r; do
    [ -z "$r" ] && continue
    [ -f "rules/$r" ] || echo "FALTA: $p -> $r"
  done < "$p"
done; echo "chequeo terminado"
```

Esperado: ninguna línea `FALTA:`.

- [ ] **Paso 7: Commit**

```bash
cd ~/Documents/Desarrollos/proyecto-loop
git add plugins/dev-substrate/rules plugins/dev-substrate/presets
git commit -m "feat(dev-substrate): librería de reglas con paths corregidos + presets (incluye money-pyg)"
```

---

### Tarea 5: Plantillas de proyecto — permisos endurecidos y hooks

Acá está el aporte que ninguna skill instalada cubre: **enforcement**. CLAUDE.md y las reglas son contexto; los hooks se ejecutan pase lo que pase.

**Files:**
- Crear: `plugins/dev-substrate/templates/settings.json`
- Crear: `plugins/dev-substrate/templates/CLAUDE.md`

**Interfaces:**
- Produce: los dos archivos que `substrate-init` (Tarea 6) copia al repo destino.

- [ ] **Paso 1: `templates/settings.json`**

Contenido exacto:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "defaultMode": "default",
    "deny": [
      "Read(**/.env)",
      "Read(**/.env.local)",
      "Read(**/.env.production)",
      "Read(**/secrets/**)",
      "Read(**/credentials/**)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Read(**/*.p8)",
      "Read(**/*.jks)",
      "Read(**/*.keystore)",
      "Read(**/google-services.json)",
      "Read(**/GoogleService-Info.plist)",
      "Read(//**/.ssh/**)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(git reset --hard *)",
      "Bash(git clean -fd *)",
      "Bash(rm -rf *)",
      "Bash(docker system prune *)",
      "Bash(docker volume rm *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(ssh *)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "f=$(jq -r '.tool_input.file_path // empty'); [ -z \"$f\" ] && exit 0; case \"$f\" in *.ts|*.tsx|*.js|*.jsx) npx --no-install prettier --write \"$f\" >/dev/null 2>&1; npx --no-install eslint --fix \"$f\" >/dev/null 2>&1;; *.py) ruff format \"$f\" >/dev/null 2>&1 && ruff check --fix \"$f\" >/dev/null 2>&1;; esac; exit 0"
          }
        ]
      }
    ]
  }
}
```

Notas de diseño, para no repetir errores del kit:
- `Read(./.env)` del kit ancla al directorio actual; `Read(**/.env)` matchea a cualquier profundidad.
- Una deny de `Read()` **también** cubre Edit/Write en esa ruta y los comandos de archivo que Claude Code reconoce en Bash (`cat`, `head`, `tail`, `sed`). **No** cubre un script de Python o Node que abra el archivo por su cuenta: para eso hace falta `sandbox`, que queda fuera de alcance de este plan.
- Las deny **no admiten excepciones**: por eso las variantes de `.env` van enumeradas y no como `**/.env*`, que bloquearía también `.env.example`.
- `curl`/`wget` en `ask` cierran la vía de exfiltración que las deny de lectura no tapan.
- El hook de formato termina siempre en `exit 0`: nunca debe bloquear la edición por un formatter ausente.

- [ ] **Paso 2: `templates/CLAUDE.md`**

Copiar `project-template/CLAUDE.md` del kit, con dos cambios:
1. Traducir los encabezados al español.
2. Borrar la sección `## Definition of Done` completa: ya está cubierta por `~/.claude/rules/ingenieria.md` (Tarea 0) y duplicarla en cada proyecto es contexto pagado dos veces.

- [ ] **Paso 3: Verificar que el JSON parsea**

```bash
python3 -m json.tool ~/Documents/Desarrollos/proyecto-loop/plugins/dev-substrate/templates/settings.json > /dev/null && echo "JSON válido"
```

- [ ] **Paso 4: Commit**

```bash
cd ~/Documents/Desarrollos/proyecto-loop
git add plugins/dev-substrate/templates
git commit -m "feat(dev-substrate): plantillas de proyecto con permisos endurecidos y hook de formato"
```

---

### Tarea 6: Skills del sustrato — `substrate-init`, `dev-db-review`, `sap-service-layer`

**Files:**
- Crear: `plugins/dev-substrate/skills/substrate-init/SKILL.md`
- Crear: `plugins/dev-substrate/skills/dev-db-review/SKILL.md`
- Crear: `plugins/dev-substrate/skills/sap-service-layer/SKILL.md`

**Interfaces:**
- Consume: `rules/` y `templates/` (Tareas 4 y 5), agentes de la Tarea 3.
- Produce: `/substrate-init` como puerta de entrada brownfield; la Tarea 7 la usa en el piloto.

- [ ] **Paso 1: `substrate-init/SKILL.md`**

Contenido exacto:

```markdown
---
name: substrate-init
description: >-
  Configura Claude Code en un repositorio que YA existe: analiza el stack, propone
  un CLAUDE.md corto, instala solo las reglas de la librería que aplican, y escribe
  permisos y hooks. Trigger con "configurá este repo", "instalá el sustrato",
  "preparar proyecto para Claude". Para proyectos nuevos usar proyecto-loop:project-init.
argument-hint: [preset opcional: web-saas|sap-integration|wms-sap|mobile-expo|financiera]
disable-model-invocation: true
model: opus
effort: high
---

Configurá el sustrato de Claude Code para este repositorio.

Preset sugerido por el usuario (puede estar vacío): $ARGUMENTS

## 0. Idempotencia
Si ya existe `.claude/rules/` o `.claude/settings.json`, NO sobrescribas: leé lo que
hay, informá qué falta y proponé solo el delta.

## 1. Analizar el repo antes de proponer nada
Identificá, con evidencia del repositorio: propósito, lenguajes y frameworks,
arquitectura, estructura de directorios, comandos reales de test/build/lint/typecheck
(leelos de `package.json`, `Makefile`, `pyproject.toml`, CI), motores de base de datos,
integraciones externas, runtime de despliegue y restricciones no obvias.

No inventes comandos: si no encontrás el de test, decilo y preguntá.

## 2. CLAUDE.md
Escribí o proponé `CLAUDE.md` usando `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md`
como esqueleto. Reglas: menos de 100 líneas, solo lo que hace falta en
prácticamente toda sesión. Nada que Claude pueda descubrir leyendo el repo
(estructura de directorios, listas de dependencias, resúmenes de arquitectura).
Lo que sí va: comandos, límites del proyecto, convenciones no obvias, reglas de negocio.

## 3. Reglas
Elegí del catálogo `${CLAUDE_PLUGIN_ROOT}/rules/` SOLO lo que el repo usa.
Si el usuario pasó un preset, arrancá de `${CLAUDE_PLUGIN_ROOT}/presets/<preset>.txt`
y ajustá según lo que encontraste.

Copiá cada regla elegida a `.claude/rules/<categoría>/<archivo>.md` y **ajustá su
frontmatter `paths` a los directorios reales de este repo** (si el Python vive solo
en `backend/`, la regla dice `backend/**/*.py`, no `**/*.py`).

Antes de terminar, verificá que dos reglas instaladas no matcheen los mismos archivos
con instrucciones que se contradigan.

## 4. Permisos y hooks
Copiá `${CLAUDE_PLUGIN_ROOT}/templates/settings.json` a `.claude/settings.json` y
adaptalo: agregá al `deny` cualquier ruta de secretos propia del repo, y ajustá el
hook de formato al formateador que el repo realmente usa (no impongas prettier a un
repo que usa biome, ni ruff a uno que usa black).

Si el repo tiene typecheck, agregá el hook `Stop`:
`{ "type": "command", "command": "<comando real> || exit 2" }`

## 5. Cierre
Informá en una lista breve: qué se creó, qué reglas se instalaron y por qué,
qué reglas del catálogo se descartaron y por qué, y qué queda por completar a mano
en el CLAUDE.md. Recordá que los hooks de un settings de proyecto exigen confiar
la carpeta la primera vez.
```

- [ ] **Paso 2: `dev-db-review/SKILL.md`**

Única skill del kit que sobrevive; se le agrega lo que le faltaba: modelo, esfuerzo y prohibición de escribir.

A diferencia del kit, **no** lleva `disable-model-invocation`: no tiene efectos secundarios (no puede editar) y conviene que Claude la cargue solo cuando la conversación toca una migración o una query. El flag se reserva para lo que commitea o escribe.

```markdown
---
name: dev-db-review
description: >-
  Revisa cambios de esquema, consultas o migraciones: correctitud, índices,
  transacciones, concurrencia, integridad, aislamiento de tenant y riesgo operativo.
  Trigger con "revisá esta migración", "revisá esta query", "esto escala?".
argument-hint: [migración|query|módulo]
model: opus
effort: high
disallowed-tools: Edit Write NotebookEdit
---

Revisión de base de datos:

$ARGUMENTS

Inspeccioná el esquema real y las consultas relevantes antes de concluir nada.
Nunca asumas que un objeto de esquema existe: verificalo.

Revisá:
- tablas y columnas exactas;
- claves y constraints;
- índices (y si la query los usa de verdad);
- plan de ejecución cuando sea practicable;
- N+1 y consultas repetidas;
- alcance de la transacción;
- aislamiento y concurrencia;
- locking;
- paginación y batching;
- seguridad de la migración y su rollback;
- compatibilidad hacia atrás durante el despliegue;
- aislamiento de tenant (en Postgres: que la política RLS exista y que la consulta
  no la esquive con service_role).

Reportá por severidad, con ubicación y corrección concreta.
```

- [ ] **Paso 3: `sap-service-layer/SKILL.md`**

Ejemplo del criterio "regla vs skill": las convenciones de SAP son regla; el **procedimiento** es skill con `paths`, y no paga contexto hasta que abrís un archivo de SAP.

```markdown
---
name: sap-service-layer
description: >-
  Procedimiento de trabajo con SAP Business One Service Layer: sesiones y login,
  paginación, batch, manejo de errores, campos de usuario y los límites de qué se
  hace por Service Layer y qué por SQL.
paths:
  - "**/sap/**"
  - "**/service_layer/**"
  - "**/service-layer/**"
  - "**/integrations/**/*sap*"
user-invocable: true
---

# SAP Business One — Service Layer

> El cuerpo de esta skill se completa en la **Tarea 10**, extrayéndolo del código de
> integración real del repo piloto. No inventar el procedimiento:
> lo que no se pueda verificar contra el código o la documentación de SAP, no entra.

Estructura a completar:

## Sesión
- Login, vigencia de la cookie de sesión, renovación, un solo login por proceso.

## Operaciones
- Service Layer es la interfaz soportada para operaciones de negocio (crear/modificar documentos).
- SQL directo sobre HANA es para consulta y reportes, dentro de los límites funcionales
  de SAP y de las políticas del proyecto. Nunca para escribir documentos.

## Paginación y volumen
- `$top`/`$skip`, `Prefer: odata.maxpagesize`, y qué hacer cuando el set es grande.

## Batch
- Cuándo conviene `$batch`, y cómo se manejan los errores parciales.

## Errores
- Códigos que hay que reintentar vs los que no. Idempotencia al reintentar creación de documentos.
```

- [ ] **Paso 4: Dejar `sap-service-layer` como esqueleto, no como invento**

El archivo se commitea con la estructura vacía y la nota de origen. Su contenido real
se escribe en la Tarea 10, leyendo el módulo de integración del repo piloto. Una skill
con procedimiento inventado es peor que no tener skill.

- [ ] **Paso 5: Commit**

```bash
cd ~/Documents/Desarrollos/proyecto-loop
git add plugins/dev-substrate/skills
git commit -m "feat(dev-substrate): substrate-init (entrada brownfield), dev-db-review y esqueleto sap-service-layer"
```

---

### Tarea 7: Publicar el segundo plugin en el marketplace

Punto de mayor riesgo del plan: el marketplace actual declara el plugin con `"source": "./"`. Se agrega un segundo con source relativo, **sin mover el primero**, para no romper la instalación que ya funciona.

**Files:**
- Modificar: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consume: todo lo creado en las tareas 3–6.
- Produce: `dev-substrate` instalable desde la app.

- [ ] **Paso 1: Editar `marketplace.json`**

Contenido exacto:

```json
{
  "name": "proyecto-loop-local",
  "owner": { "name": "Gabriel" },
  "metadata": {
    "description": "Marketplace del arsenal: proyecto-loop (proyectos nuevos) + dev-substrate (repos existentes)."
  },
  "plugins": [
    {
      "name": "proyecto-loop",
      "source": "./",
      "description": "Arsenal de skills estilo loop, mobile-first, para arrancar y avanzar proyectos nuevos de forma iterativa y reanudable."
    },
    {
      "name": "dev-substrate",
      "source": "./plugins/dev-substrate",
      "description": "Sustrato para repos existentes: reglas con paths (SAP B1, HANA, WMS, Docker, REST, React, RN, Python), subagentes de alto razonamiento, permisos endurecidos y hooks."
    }
  ]
}
```

- [ ] **Paso 2: Push**

```bash
cd ~/Documents/Desarrollos/proyecto-loop
git add .claude-plugin/marketplace.json
git commit -m "feat: marketplace con dos plugins (proyecto-loop + dev-substrate)"
git push
```

- [ ] **Paso 3: Resync e instalación en la app**

En la app: panel de plugins → resync del marketplace `proyecto-loop-local` → instalar `dev-substrate` → **abrir sesión nueva**.

- [ ] **Paso 4: Verificar**

En la sesión nueva, comprobar que aparecen `dev-substrate:substrate-init` y `dev-substrate:dev-db-review` en la lista de skills, y que `proyecto-loop` figura en v0.3.0.

```bash
python3 -c "
import json,os
d=json.load(open(os.path.expanduser('~/.claude/plugins/installed_plugins.json')))
for k,v in d['plugins'].items():
    if 'loop' in k or 'substrate' in k: print(k, v[0]['version'], v[0]['installPath'])
"
```

- [ ] **Paso 5: Fallback si el marketplace rechaza el segundo plugin**

Si la app no lo toma con source relativo: mover `proyecto-loop` a `plugins/proyecto-loop/` y poner ambos con source de subdirectorio. Eso obliga a desinstalar y reinstalar el plugin en la app (el `installPath` cambia). Hacerlo solo si el camino de menor riesgo falla.

---

### Tarea 8: `loop-rules` — el pegamento entre los dos plugins

Es el punto de fusión de mayor valor: el loop deja de arrancar proyectos sin convenciones.

**Files:**
- Crear: `skills/loop-rules/SKILL.md`
- Modificar: `skills/plan-architect/SKILL.md` (paso de cierre)
- Modificar: `skills/project-loop/SKILL.md` (tabla de la máquina de estados)

**Interfaces:**
- Consume: `.loop/stack.md`, catálogo `dev-substrate/rules/`.
- Produce: `.claude/rules/**` en el proyecto; a partir de ahí toda tarea del loop trabaja con las convenciones cargadas.

- [ ] **Paso 1: Crear `skills/loop-rules/SKILL.md`**

```markdown
---
name: loop-rules
description: >-
  Instala en el proyecto las reglas con paths que corresponden a su stack, tomándolas
  del catálogo de dev-substrate, y las ancla a los directorios reales del repo.
  Se ejecuta una vez, después de plan-architect. Trigger con "instalá las reglas",
  "configurá las convenciones del stack".
disable-model-invocation: true
effort: medium
---

# loop-rules — convenciones del stack

## 0. Reanudar
- Leé `.loop/state.md` y `.loop/stack.md`.
- Si `.claude/rules/` ya tiene contenido, **completá el delta**, no reescribas.

## 1. Elegir
Del catálogo del plugin `dev-substrate` (`rules/`), elegí SOLO lo que el stack de
`stack.md` realmente usa. Si el plugin no está instalado, decilo y seguí sin reglas
en vez de inventar el contenido.

## 2. Anclar
Copiá cada regla a `.claude/rules/<categoría>/<archivo>.md` y ajustá su `paths` a la
estructura real de este repo. Un glob preciso consume menos contexto que uno amplio.

## 3. Verificar que no se pisen
Dos reglas no deben matchear el mismo archivo con instrucciones contradictorias.
Si pasa, angostá el `paths` de la más general.

## 4. Cierre
Anotá en `state.md` (bitácora) qué reglas se instalaron. Devolvé control a `project-loop`.
```

- [ ] **Paso 2: Encadenarla desde `plan-architect`**

En `skills/plan-architect/SKILL.md`, sección `## 4. Cierre`, reemplazar la última línea por:

```markdown
- Sugerí la siguiente skill: `loop-rules` (una sola vez, para instalar las convenciones
  del stack) y después `code-exec`. Si corre `project-loop`, devolvé control.
```

- [ ] **Paso 3: Agregarla a la máquina de estados**

En `skills/project-loop/SKILL.md`, en la tabla de la sección `## 1`, insertar una fila entre `plan` y `ejecucion`:

```markdown
| reglas | `loop-rules` (solo si `.claude/rules/` está vacío) | ejecucion |
```

- [ ] **Paso 4: Verificar en el piloto**

En `~/Documents/Desarrollos/piloto-mobile-loop`, sesión nueva:

```text
proyecto-loop:loop-rules
```

Esperado: crea `.claude/rules/mobile/react-native.md` con `paths` apuntando a la estructura real del piloto (no al glob genérico del catálogo).

- [ ] **Paso 5: Commit**

```bash
cd ~/Documents/Desarrollos/proyecto-loop
git add skills
git commit -m "feat(loop): loop-rules instala las convenciones del stack desde dev-substrate"
```

---

### Tarea 9: Cerrar los dos huecos del ciclo — `loop-verify` y `loop-security`

**Files:**
- Crear: `skills/loop-verify/SKILL.md`
- Crear: `skills/loop-security/SKILL.md`
- Modificar: `templates/loop/stack.md` (bloque de comandos)
- Modificar: `skills/project-loop/SKILL.md` (etapas test y seguridad)

**Interfaces:**
- Consume: `.loop/plan.md` (tests esperados por tarea), `.loop/stack.md` (comandos).
- Produce: `.loop/test-<T-00X>.log` como evidencia; hallazgos en `.loop/review-log.md` que `fix-loop` ya sabe consumir.

- [ ] **Paso 1: Dar a `stack.md` un contrato de comandos**

En `templates/loop/stack.md`, agregar al final:

```markdown
## Comandos del proyecto (contrato para loop-verify)
| Acción | Comando |
|--------|---------|
| test (suite completa) | `<comando>` |
| test (archivo/patrón) | `<comando> <patrón>` |
| typecheck | `<comando>` |
| lint | `<comando>` |
| build | `<comando>` |
```

- [ ] **Paso 2: `skills/loop-verify/SKILL.md`**

```markdown
---
name: loop-verify
description: >-
  Etapa de test del loop: corre la verificación real de la tarea activa, guarda la
  salida como evidencia y decide verde/rojo. No marca nada verde sin haber ejecutado
  el comando. Trigger con "verificá la tarea", "corré los tests", o vía project-loop.
disable-model-invocation: true
effort: medium
---

# loop-verify — Etapa (7) Test

## 0. Reanudar
Leé `.loop/state.md`, `.loop/plan.md` (la `tarea_activa` y sus **tests esperados**)
y la tabla de comandos de `.loop/stack.md`.

Si `stack.md` no tiene comandos cargados, deducilos del repo (`package.json`,
`Makefile`, `pyproject.toml`), **escribilos en `stack.md`** y seguí.

## 1. Ejecutar
Corré, en este orden y parando en el primer rojo:
1. los tests de la tarea (patrón acotado, no la suite entera si se puede);
2. typecheck;
3. lint.

Guardá la salida completa en `.loop/test-<TAREA>.log`.

## 2. Cotejar contra el plan
Los "tests esperados" de la tarea en `plan.md` tienen que existir de verdad y haber
corrido. Si la tarea declaraba un test que no existe, eso es un hallazgo de severidad
alta, aunque la suite esté en verde.

## 3. Decidir
- **Verde** = comando ejecutado + exit 0 + los tests esperados presentes. Nada más cuenta.
- **Rojo** → registrá los hallazgos en `.loop/review-log.md`, poné `etapa = correccion`
  y devolvé control para que entre `fix-loop`.

Nunca declares verde algo que no ejecutaste. Si no pudiste correr el comando, el
estado es "bloqueado", no "verde".

## 4. Cierre
Actualizá `state.md`: `ultima_skill = loop-verify`, etapa resultante, ruta del log en bitácora.
```

- [ ] **Paso 3: `skills/loop-security/SKILL.md`**

```markdown
---
name: loop-security
description: >-
  Revisión de seguridad de la tarea activa, para tareas que tocan autenticación,
  autorización, aislamiento de tenant, dinero, secretos o entrada externa. Trigger
  vía project-loop cuando la tarea toca esas áreas, o "revisá la seguridad de esto".
disable-model-invocation: true
context: fork
agent: dev-substrate:security-reviewer
---

# loop-security — Revisión de seguridad de la tarea

Aplica SOLO si la tarea activa toca alguna de estas áreas; si no, salteala y decilo:
autenticación, autorización, `tenant_id` / RLS, dinero, secretos y configuración,
entrada externa, webhooks, subida de archivos, operaciones privilegiadas.

## 1. Alcance
Leé el diff de la tarea activa (`git diff` del último commit) y el código directamente afectado.

## 2. Revisión
Separá siempre:
- **vulnerabilidades verificadas** (con evidencia y precondiciones de explotación);
- **riesgos probables**;
- **endurecimiento opcional**.

Para multi-tenant, no alcanza con que exista la política RLS: verificá que la consulta
no la esquive (service_role, consultas administrativas, jobs).

## 3. Salida
Registrá los hallazgos materiales en `.loop/review-log.md` con el mismo formato
`H-00X` que usa `fix-loop`, con severidad. Si no hay nada material, decilo explícitamente.
```

- [ ] **Paso 4: Encadenar en `project-loop`**

En la tabla de la máquina de estados, reemplazar la fila de `test` por:

```markdown
| test | `loop-verify` | correccion si rojo · si verde y la tarea toca auth/tenant/dinero/secretos → `loop-security` · si no, cerrar tarea |
| seguridad | `loop-security` | correccion si hay hallazgos, si no cerrar tarea |
```

- [ ] **Paso 5: Verificar que `loop-security` resuelve el agente del otro plugin**

`loop-security` vive en `proyecto-loop` y forkea a un agente que vive en `dev-substrate`.
Los agentes de plugin se referencian con ID scoped (`plugin:nombre`), pero esto hay que
comprobarlo, no asumirlo. Sesión nueva, en el piloto:

```text
proyecto-loop:loop-security
```

- Si arranca el subagente: queda como está.
- Si no resuelve el agente: sacar `context: fork` y `agent:`, y reemplazarlos por
  `model: opus` + `effort: high` + `disallowed-tools: Edit Write NotebookEdit`.
  La revisión pierde el aislamiento de contexto pero conserva modelo y restricción de herramientas.

- [ ] **Paso 6: Verificar `loop-verify` en el piloto**

En `~/Documents/Desarrollos/piloto-mobile-loop`, sesión nueva:

```text
proyecto-loop:loop-verify
```

Esperado: corre jest, escribe `.loop/test-<tarea>.log` con la salida real, y reporta verde citando el exit code.

- [ ] **Paso 7: Commit**

```bash
cd ~/Documents/Desarrollos/proyecto-loop
git add skills templates
git commit -m "feat(loop): loop-verify con evidencia obligatoria y loop-security como etapa del ciclo"
```

---

### Tarea 10: Piloto real en un repo existente

Nada de esto vale hasta que corra sobre un repo de verdad. El candidato es un repo interno brownfield con SAP y Docker, que es exactamente el caso que el sustrato cubre y el loop no.

**Files:**
- Crear (en el repo piloto): `CLAUDE.md`, `.claude/settings.json`, `.claude/rules/**`

- [ ] **Paso 1: Clonar o abrir el repo piloto localmente**

- [ ] **Paso 2: Correr la entrada brownfield**

Sesión nueva en la raíz del repo:

```text
/substrate-init sap-integration
```

- [ ] **Paso 3: Verificar los tres mecanismos, uno por uno**

1. **Reglas cargan por `paths`:** abrí un archivo bajo `sap/` y preguntá qué instrucciones tiene cargadas. Debe aparecer la regla de SAP B1 y **no** la de React.
2. **El hook de formato dispara:** pedí un cambio trivial en un archivo `.ts` y confirmá que queda formateado sin que Claude corriera prettier a mano.
3. **Las deny bloquean:** pedí explícitamente leer `.env`. Debe rechazarse por regla de permisos, no por criterio del modelo.

- [ ] **Paso 4: Commitear la configuración en el repo piloto**

```bash
git add CLAUDE.md .claude/settings.json .claude/rules
git commit -m "chore: configuración de Claude Code (sustrato: reglas, permisos, hooks)"
```

- [ ] **Paso 5: Anotar el resultado**

Si algo no funcionó como dice este plan, corregir la skill o la plantilla en `dev-substrate` **antes** de replicar en los demás repos.

---

## Fuera de alcance de este plan (fase siguiente)

Se dejan afuera a propósito, para que este plan cierre en algo que funcione:

- **`loop-ship`** — deploy al servidor interno siguiendo el patrón ya establecido (un directorio por proyecto, compose propio, entrada en el reverse proxy, elección de puerto libre). Es la skill de mayor valor operativo pendiente, pero necesita que el ciclo esté cerrado primero.
- **`loop-adopt`** — llevar un repo existente al ciclo completo del loop (construir `.loop/` desde el código). `substrate-init` cubre ya la mitad útil.
- **`loop-status`** — lectura barata del estado (`model: haiku`, solo lectura).
- **`sandbox`** — enforcement a nivel de sistema operativo para secretos. Hay que evaluar el impacto en Docker y en los comandos de red antes de habilitarlo.
- **Reducir el ruido de skills.** Tenés ~150 skills listadas por sesión (small-business, human-resources, figma, design). `skillOverrides` **no** sirve para eso: no afecta a skills de plugins. Se gestiona desde el panel de plugins de la app, deshabilitando los que no usás. **No** usar `disableBundledSkills`: se llevaría puestos `/code-review`, `/init` y `/security-review`, de los que este plan depende.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| El marketplace no acepta dos plugins con sources mixtos | Fallback documentado en Tarea 7 paso 5 |
| `context: fork` rompe el encadenado del loop | Tarea 2 es una prueba empírica con reversión definida |
| El hook de formato falla en un repo sin prettier/ruff | El comando termina en `exit 0` siempre; nunca bloquea la edición |
| `Read(**/.env)` bloquea un `.env.example` que necesitás | Las deny van enumeradas, no con comodín `.env*` |
| Cambios en `~/.claude/` sin versionar se pierden | Tarea 0 se espeja en `dev-substrate/templates/` |
| Un agente de `dev-substrate` no resuelve desde una skill de `proyecto-loop` | Tarea 9 paso 5: fallback sin fork, conservando modelo y restricción de herramientas |
