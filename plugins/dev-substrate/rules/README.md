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
