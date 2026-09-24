---
name: loop-actualizar
description: >-
  Trae a este proyecto una versión más nueva del loop vendoreado. Trigger con
  "actualizá el loop", "traé la última versión del loop". Manual: reemplaza parte
  del .claude/ del proyecto y lo commitea.
argument-hint: [versión, ej. v0.8.1 — por defecto la última publicada]
disable-model-invocation: true
---

# loop-actualizar — Traer una versión nueva del loop

Este proyecto lleva el loop copiado adentro, en `.claude/`, porque los plugins no cargan
en sesiones cloud. Esa copia está fijada a una versión: una mejora al loop no llega sola.
Esta skill la trae.

## 0. Dónde estás parado

Leé `.claude/loop/VERSION`. Si no existe, este proyecto no tiene el loop vendoreado:
decilo y recomendá crear el repo desde la plantilla en vez de seguir.

Después, `git status --porcelain -- .claude` tiene que salir vacío. Si no sale vacío,
pará y listá lo que hay: actualizar sobre cambios sin commitear mezclaría el cambio de
versión con esos cambios, y el descarte del paso 2 los borraría sin aviso.

## 1. Qué versión traer

Si el usuario nombró una versión, usá esa. `.claude/loop/VERSION` guarda el número sin
`v` (`X.Y.Z`) y los tags de GitHub lo llevan con `v` (`vX.Y.Z`): son la misma versión en
dos formatos. Si el usuario la nombró sin la `v`, agregásela para el `--branch` del
clone.

Si no nombró ninguna, traé la más nueva publicada:

```bash
git ls-remote --tags --sort=-v:refname https://github.com/jhon2397/proyecto-loop.git 'v*' \
  | grep -v '\^{}' | sed -E 's#.*refs/tags/##' | head -1
```

Cada línea de `ls-remote` es `<sha>\trefs/tags/vX.Y.Z`; un tag anotado además trae una
línea hermana `...^{}` (apunta al commit que señala el tag, no es una versión aparte),
que el `grep -v` descarta. El `sed` se queda con el nombre del tag tal cual (`vX.Y.Z`):
eso es lo que va en `--branch` del clone. Para compararlo contra `.claude/loop/VERSION`
quitale la `v` inicial (en bash, `"${TAG#v}"`).

Si, sin la `v`, es la misma que dice `.claude/loop/VERSION`, decilo y terminá sin tocar
nada.

## 2. Bajar, vendorear y verificar

```bash
DIR=$(mktemp -d)
git clone -q --depth 1 --branch <versión> https://github.com/jhon2397/proyecto-loop.git "$DIR"
uv run python "$DIR/scripts/vendorear.py" --origen "$DIR" --destino .
uv run python "$DIR/scripts/verificar-vendoreo.py" --origen "$DIR" --destino .
```

**Si el verificador no da `vendoreo: OK`, no commitees.** Descartá el cambio con
`git checkout -- .claude && git clean -fdq .claude` — seguro solo porque el paso 0 ya
confirmó que `.claude/` estaba limpio antes de empezar — reportá su salida completa, y
limpiá el clon (`rm -rf "$DIR"`).

Lo mismo si `vendorear.py` falla al bajar una skill de terceros desde GitHub por un
problema de red: el mensaje de error sale del script mismo. Tratalo igual que un
verificador que no da OK — se reporta y no se commitea — y limpiá el clon con
`rm -rf "$DIR"` antes de terminar.

## 3. Qué se conserva

`vendorear.py` reemplaza solo lo que el loop gestiona, listado en `.claude/loop/MANIFIESTO`.
Quedan intactas las reglas que instaló `loop-rules` en `.claude/rules/`, las skills propias
del proyecto y las claves de `.claude/settings.json` que no son del loop.

Confirmalo con `git status --porcelain` antes de commitear: **si aparece modificado algo
fuera de `.claude/skills/`, `.claude/agents/`, `.claude/loop/` y `.claude/settings.json`,
pará, reportalo y limpiá el clon (`rm -rf "$DIR"`).**

## 4. Commit

Un solo commit, `chore(loop): actualizar a <versión>`, con la versión anterior en el
cuerpo.

Hecho el commit, limpiá el clon: `rm -rf "$DIR"`.

## 5. Después

Si la versión nueva cambió el contrato de `.loop/` —campos nuevos en `state.md`,
marcadores nuevos en `plan.md`—, avisale al usuario qué hay que completar. No los rellenes
con valores inventados.
