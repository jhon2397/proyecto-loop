#!/usr/bin/env python3
"""Chequeos de coherencia del arsenal. Requiere pyyaml.

    uv run --with pyyaml python scripts/verificar-arsenal.py

Verifica lo que no se ve hasta que el loop se traba en medio de un ciclo.
"""
import glob
import os
import re
import sys

import yaml

SKILLS = "skills/*/SKILL.md"
LOOP = "skills/project-loop/SKILL.md"
ESTADO = "templates/loop/state.md"


def frontmatter(path):
    s = open(path).read()
    return yaml.safe_load(s[4 : s.index("\n---\n", 4)]) or {}


def main():
    errores = []
    skills = {f.split("/")[1]: frontmatter(f) for f in sorted(glob.glob(SKILLS))}

    # Filas de la máquina de estados: | etapa | `skill` | destino |
    loop = open(LOOP).read()
    filas = re.findall(r"^\| (\w+) \| `([a-z:-]+)`", loop, re.M)
    encadenadas = {s for _, s in filas}
    # toda fila de la tabla aporta una etapa, tenga skill o sea un checkpoint
    etapas_tabla = set(re.findall(r"^\| ([a-z-]+) \|", loop, re.M)) - {"etapa actual"}

    # 1. Una etapa encadenada no puede estar reservada a invocación humana.
    for n in sorted(encadenadas):
        if ":" in n:
            continue  # skill de otro plugin
        if n not in skills:
            errores.append(f"la tabla encadena `{n}`, que no existe")
        elif skills[n].get("disable-model-invocation"):
            errores.append(
                f"`{n}` es una etapa encadenada y lleva disable-model-invocation: "
                "el harness la va a rechazar en medio del ciclo"
            )

    # 2. Toda etapa de la tabla tiene que existir en la enumeración de state.md
    enum = re.search(r"\*\*etapa:\*\* (.+)", open(ESTADO).read()).group(1)
    enum = {e.strip() for e in enum.split("|")}
    for e in sorted(etapas_tabla - enum):
        errores.append(f"la etapa `{e}` está en la tabla pero no en state.md")

    # 3. Frontmatter parseable y con nombre coherente con su carpeta
    for n, fm in skills.items():
        if fm.get("name") != n:
            errores.append(f"`{n}`: el campo name dice {fm.get('name')!r}")

    # 4. Toda ruta ${CLAUDE_PLUGIN_ROOT}/... citada por una skill tiene que existir.
    #    Si no, la skill se entera en medio de una corrida.
    for f in sorted(glob.glob(SKILLS)):
        for ruta in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", open(f).read()):
            ruta = ruta.rstrip("/.,;:)")
            if not os.path.exists(ruta):
                errores.append(f"`{f.split('/')[1]}` cita {ruta}, que no existe en el repo")

    # 5. state.md declara los campos que las skills dan por sentados.
    estado = open(ESTADO).read()
    for campo in ("mobile", "supabase_hosting", "matriz_dispositivos"):
        if f"**{campo}:**" not in estado:
            errores.append(f"state.md no declara el campo `{campo}`")

    if errores:
        print("FALLA:")
        for e in errores:
            print("  -", e)
        return 1
    print(f"OK · {len(skills)} skills · {len(filas)} etapas encadenadas · sin bloqueos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
