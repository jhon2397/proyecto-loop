# Plantilla de proyecto-loop

Repo plantilla. Cada proyecto nuevo nace de acá con el loop adentro, así corre igual en
una sesión cloud de Claude Code que en una máquina local.

## Cómo arrancar un proyecto

1. En GitHub, **Use this template** → crear un repo nuevo, privado.
2. Abrir una sesión cloud sobre ese repo: la app de escritorio con **Cloud**,
   claude.ai/code, o la app móvil.
3. Escribir `/project-loop`.

`project-init` va a preguntar si el proyecto tiene mobile y dónde corre Supabase en
producción, y arma el resto.

## Qué hay adentro

- `.claude/skills/`, `.claude/agents/` — el loop, vendoreado.
- `.claude/loop/` — plantillas, referencias y catálogo de reglas. No carga solo.
- `.claude/loop/TERCEROS.md` — skills de terceros incluidas y sus licencias.

Este repo se regenera solo con cada versión de proyecto-loop. No lo edites a mano.

Si estás leyendo esto en un proyecto que ya nació de esta plantilla, este README no es
para vos: reemplazalo por el de tu proyecto. Lo de "no editar a mano" vale solo para
este repo plantilla, no para lo que armaste a partir de él.
