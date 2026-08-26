---
name: substrate-init
description: >-
  Configura Claude Code en un repositorio que YA existe. Analiza el stack, propone
  un CLAUDE.md corto, instala solo las reglas de la librería que aplican, y escribe
  permisos y hooks. Trigger con "configurá este repo", "instalá el sustrato",
  "preparar proyecto para Claude". Para proyectos nuevos usar
  proyecto-loop:project-init.
argument-hint: [web-saas|sap-integration|wms-sap|mobile-expo|financiera]
disable-model-invocation: true
model: opus
effort: high
---

# substrate-init — configuración de un repo existente

Preset sugerido por el usuario (puede estar vacío): $ARGUMENTS

## 0. Idempotencia
Si ya existe `.claude/rules/` o `.claude/settings.json`, **no sobrescribas**: leé lo
que hay, informá qué falta y proponé solo el delta.

## 1. Analizar el repo antes de proponer nada
Identificá, con evidencia del repositorio: propósito, lenguajes y frameworks,
arquitectura, estructura de directorios, comandos reales de test/build/lint/typecheck
(leelos de `package.json`, `Makefile`, `pyproject.toml`, la CI), motores de base de
datos, integraciones externas, runtime de despliegue y restricciones no obvias.

No inventes comandos. Si no encontrás el de test, decilo y preguntá.

## 2. CLAUDE.md
Escribí o proponé `CLAUDE.md` usando `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md`
como esqueleto.

Reglas: menos de 100 líneas, solo lo que hace falta en prácticamente toda sesión.
Nada que Claude pueda descubrir leyendo el repo (estructura de directorios, listas
de dependencias, resúmenes de arquitectura). Lo que sí va: comandos, límites del
proyecto, convenciones no obvias, reglas de negocio.

## 3. Reglas
Elegí del catálogo `${CLAUDE_PLUGIN_ROOT}/rules/` SOLO lo que el repo usa. Si el
usuario pasó un preset, arrancá de `${CLAUDE_PLUGIN_ROOT}/presets/<preset>.txt` y
ajustá según lo que encontraste.

Copiá cada regla elegida a `.claude/rules/<categoría>/<archivo>.md` y **ajustá su
frontmatter `paths` a los directorios reales de este repo**: si el Python vive solo
en `backend/`, la regla dice `backend/**/*.py`, no `**/*.py`. Un glob preciso
consume menos contexto que uno amplio.

Antes de terminar, verificá que dos reglas instaladas no matcheen los mismos
archivos con instrucciones que se contradigan.

## 4. Permisos y hooks
Copiá `${CLAUDE_PLUGIN_ROOT}/templates/settings.json` a `.claude/settings.json` y
adaptalo:
- agregá al `deny` cualquier ruta de secretos propia del repo;
- ajustá el hook de formato al formateador que el repo **realmente** usa (no impongas
  prettier a un repo con biome, ni ruff a uno con black);
- si el repo tiene typecheck, agregá el hook `Stop`:
  `{ "type": "command", "command": "<comando real> || exit 2" }`.

## 5. Cierre
Informá en una lista breve: qué se creó, qué reglas se instalaron y por qué, qué
reglas del catálogo se descartaron y por qué, y qué queda por completar a mano en el
CLAUDE.md.

Recordale al usuario que los hooks de un `settings.json` de proyecto exigen confiar
la carpeta la primera vez, y que las reglas nuevas recién se ven en una sesión nueva.
