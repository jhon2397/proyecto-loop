# Catálogo de reglas

Estos archivos **no se cargan solos**: son el catálogo del que `substrate-init`
(repos existentes) y `loop-rules` (proyectos nuevos) copian a `.claude/rules/`
del repo destino.

## Los `paths` de acá son defaults, no la respuesta final

Están escritos para **layout monorepo** (`apps/web/**`, `mobile/**`, `backend/**`).
Un repo plano —una app Expo con `index.ts` y `src/` en la raíz, por ejemplo— no
matchea la mayoría de ellos.

**Al instalar una regla hay que anclarle el `paths` a la estructura real del repo.**
Es un paso obligatorio de ambas skills, no una optimización. Una regla cuyo glob no
matchea nada es peor que no tenerla: ocupa lugar en el catálogo y da la falsa
sensación de que la convención está cubierta.

## Colisiones

Dos reglas no deben matchear el mismo archivo con instrucciones que se contradigan:
si dos aplican, Claude puede seguir cualquiera.

El caso conocido es `frontend/react-typescript.md` vs `mobile/react-native.md`.
En monorepo se separan solos por directorio. **En un repo plano no se pueden
distinguir por ruta**: ahí hay que elegir cuál instalar, no las dos.

## Cuándo se dispara una regla con `paths` (verificado)

Se dispara cuando Claude abre un archivo que matchea **con la herramienta `Read`**.
Una lectura por Bash (`cat`, `head`, `sed`) **no** la activa.

Verificado con el hook `InstructionsLoaded` sobre dos sesiones: la que leyó el
archivo solo con `cat` no cargó ninguna regla; la que además usó `Read` cargó las
tres que matcheaban, con `load_reason: path_glob_match` y los globs ya expandidos.

Consecuencia práctica: **en modo auto**, que prefiere Bash para leer, una regla con
`paths` puede no activarse en lecturas rápidas. Sí se activa en el caso que más
importa —cuando Claude va a editar el archivo— porque ahí lo abre con `Read`.

Criterio: si la regla es corta y debe regir siempre, no le pongas `paths` y aceptá
el costo de contexto. Reservá `paths` para las reglas de dominio (SAP, HANA, WMS),
que son largas y solo importan dentro de sus directorios.

## Expansión de llaves: funciona

`"**/*.{ts,tsx}"` expande correctamente. Verificado: una regla con tres grupos de
llaves cargó con sus 16 globs ya expandidos. Las reglas de este catálogo que usan
llaves (`rest.md`, `react-typescript.md`, `react-native.md`) no corren riesgo.

## Reglas mutuamente excluyentes

Algunas reglas cubren el mismo terreno con tecnologías distintas y matchean los
mismos archivos. **Instalá una, nunca las dos:**

| No convivir | Motivo |
|-------------|--------|
| `backend/python-flask.md` · `backend/python-fastapi.md` | los dos matchean `**/*.py` |
| `database/mysql.md` · `database/postgres.md` | los dos matchean `**/*.sql` y migraciones |
| `frontend/react-typescript.md` · `mobile/react-native.md` (en repo plano) | no se distinguen por ruta |

## Sobre `domain/money-pyg.md`

Codifica una **decisión de proyecto** (guaraní entero, sin centavos), no una verdad
universal. Un sistema de pagos que maneja moneda extranjera usa `NUMERIC` con escala,
y esa también es una decisión correcta. Instalala solo donde esa decisión esté tomada;
la parte universal —nunca `float` para dinero— ya está en las reglas de base de datos.
