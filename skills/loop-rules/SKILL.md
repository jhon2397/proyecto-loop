---
name: loop-rules
description: >-
  Instala en el proyecto las reglas con paths que corresponden a su stack, tomándolas
  del catálogo de dev-substrate, y las ancla a los directorios reales del repo.
  Se ejecuta una vez, después de plan-architect. Trigger con "instalá las reglas",
  "configurá las convenciones del stack".
effort: medium
---

# loop-rules — convenciones del stack

## 0. Reanudar
- Lee `.loop/state.md` y `.loop/stack.md`.
- Si `.claude/rules/` ya tiene contenido, **completa el delta**, no reescribas.

## 1. Elegir
Del catálogo del plugin `dev-substrate` (carpeta `rules/`) elige SOLO lo que el stack
de `stack.md` realmente usa. Los presets de `presets/*.txt` son un punto de partida
razonable según la plataforma:

| platform de state.md | preset |
|----------------------|--------|
| mobile | `mobile-expo.txt` |
| web | `web-saas.txt` |
| full-stack | `web-saas.txt` + `mobile-expo.txt` (sin duplicar) |

Si el plugin `dev-substrate` no está instalado, **dilo y sigue sin reglas**. No
inventes el contenido de una regla que no pudiste leer.

## 2. Anclar (paso obligatorio)
Copia cada regla elegida a `.claude/rules/<categoría>/<archivo>.md` y **ajusta su
`paths` a la estructura real de este repo**. Los globs del catálogo están escritos
para layout monorepo (`apps/web/**`, `mobile/**`, `backend/**`); un repo plano no
matchea casi ninguno.

Una regla cuyo glob no matchea nada es peor que no tenerla: ocupa lugar y da la falsa
sensación de que la convención está cubierta.

## 3. Decidir `paths` sí o no
Una regla con `paths` se activa cuando Claude abre un archivo que matchea **con la
herramienta `Read`**; una lectura por Bash (`cat`, `head`, `sed`) no la dispara.

- Regla **corta y transversal** que debe regir siempre → sin `paths`, carga incondicional.
- Regla **de dominio** (SAP, HANA, WMS), larga y relevante solo dentro de sus
  directorios → con `paths`.

## 4. Verificar que no se pisen
Dos reglas no deben matchear el mismo archivo con instrucciones que se contradigan:
si aplican las dos, Claude puede seguir cualquiera.

El caso conocido es `frontend/react-typescript.md` vs `mobile/react-native.md`. En
monorepo se separan por directorio; **en un repo plano no se distinguen por ruta**:
ahí se elige una, no las dos.

## 5. Cierre
- Anota en la bitácora de `state.md` qué reglas se instalaron y con qué `paths`.
- Recuerda que las reglas nuevas recién se ven en una **sesión nueva**.
- Pon **etapa = ejecucion** y devuelve control a `project-loop`.
