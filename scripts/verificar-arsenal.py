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
CATALOGO = "references/ui-patterns.md"
DEPENDENCIAS = "references/dependencias-externas.md"


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

    # 0a. Sin filas, los chequeos 1 y 7 iteran sobre el vacío y aprueban sin mirar nada.
    if not filas:
        errores.append(
            f"{LOOP}: la tabla de la máquina de estados no produjo ninguna fila "
            "(¿cambió el formato?). Los chequeos 1 y 7 dependen de ella: sin filas "
            "no verifican nada."
        )

    # 0b. Pérdida parcial: una fila cuya SEGUNDA celda empieza con un nombre entre
    #     backticks nombra una skill. Si el patrón de extracción no la capturó, esa
    #     etapa dejó de verificarse mientras el validador sigue diciendo OK. Es el
    #     caso peor, porque no se nota. Se mira la estructura de celdas y no la
    #     presencia de backticks: una fila de checkpoint puede citar un archivo.
    for linea in loop.splitlines():
        cruda = linea.strip()
        if not cruda.startswith("|"):
            continue
        celdas = [c.strip() for c in cruda.strip("|").split("|")]
        if len(celdas) < 2 or not re.match(r"^`[a-z:-]+`", celdas[1]):
            continue
        if not re.match(r"^\| (\w+) \| `([a-z:-]+)`", linea):
            errores.append(
                f"{LOOP}: la fila {cruda[:50]!r} nombra la skill {celdas[1]} en su "
                "segunda celda pero el patrón de extracción no la captura: esa etapa "
                "NO se está verificando"
            )

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
    for campo in ("mobile", "supabase_hosting", "matriz_dispositivos", "deuda_dispositivos"):
        if f"**{campo}:**" not in estado:
            errores.append(f"state.md no declara el campo `{campo}`")

    # 6. Cada regla del catálogo de UI tiene sus tres partes y su marca.
    #    Un principio disfrazado de regla chequeable da falsos verdes en la revisión.
    catalogo = open(CATALOGO).read()
    reglas = re.split(r"^## (UI-\d+)[^\n]*$", catalogo, flags=re.M)[1:]
    if not reglas:
        errores.append(
            f"{CATALOGO} no tiene ninguna regla UI-XXX: "
            "¿se truncó el archivo o cambió el nivel de encabezado?"
        )
    for nombre, cuerpo in zip(reglas[::2], reglas[1::2]):
        encabezado = catalogo[catalogo.index(f"## {nombre}"):].split("\n", 1)[0]
        if "[chequeable]" not in encabezado and "[principio]" not in encabezado:
            errores.append(f"{nombre} no está marcada [chequeable] ni [principio]")
        for parte in ("**Qué.**", "**Por qué.**", "**Cómo se verifica.**"):
            if parte not in cuerpo:
                errores.append(f"{nombre} no tiene la sección {parte}")

    # 7. Los puntos de entrada manuales llevan el flag; y ninguno está encadenado.
    ENTRADAS = ("project-loop", "loop-adopt", "loop-status", "loop-ship", "loop-pitch",
                "loop-actualizar")
    for n in ENTRADAS:
        if n not in skills:
            errores.append(f"falta la skill de entrada `{n}`")
        elif not skills[n].get("disable-model-invocation"):
            errores.append(f"`{n}` es punto de entrada y le falta disable-model-invocation")
        elif n in encadenadas:
            errores.append(f"`{n}` lleva el flag pero la tabla la encadena: se va a rechazar")

    # 7b. Y al revés: una skill con el flag que no sea punto de entrada es el error original.
    for n, fm in sorted(skills.items()):
        if fm.get("disable-model-invocation") and n not in ENTRADAS:
            errores.append(
                f"`{n}` lleva disable-model-invocation pero no es punto de entrada: "
                "si alguna skill la encadena, el harness la va a rechazar en medio del ciclo"
            )

    # 8. Las skills de otros plugins se citan con su nombre completo. Con el nombre corto
    #    la herramienta Skill no las encuentra y el modelo improvisa en su lugar, sin aviso.
    #    EXTERNAS refleja los nombres tal como los lista una sesión (2026-10-09); si se suma
    #    una skill nueva al arsenal, se agrega acá después de verla en esa lista.
    EXTERNAS = {
        "anthropic-skills:frontend-design",
        "anthropic-skills:ui-ux-pro-max",
        "react-native-best-practices:react-native-best-practices",
        "accesslint:audit",
        "design:design-critique",
        "engineering:architecture",
        "engineering:code-review",
        "engineering:debug",
        "engineering:deploy-checklist",
        "engineering:system-design",
        "figma:figma-design-to-code",
        "figma:figma-generate-design",
        "figma:figma-use",
        "superpowers:brainstorming",
        "superpowers:test-driven-development",
    }
    NOMBRE_CORTO = {e.split(":")[1]: e for e in EXTERNAS if e.split(":")[1] != e.split(":")[0]}
    NOMBRE_CORTO.update({
        "accesslint": "accesslint:audit",
        "react-native-best-practices": "react-native-best-practices:react-native-best-practices",
    })
    sustrato = "plugins/dev-substrate"
    propias = {f"proyecto-loop:{n}" for n in skills}
    propias |= {f"dev-substrate:{os.path.basename(d)}" for d in glob.glob(f"{sustrato}/skills/*")}
    propias |= {
        f"dev-substrate:{os.path.basename(a)[:-3]}" for a in glob.glob(f"{sustrato}/agents/*.md")
    }
    for f in sorted(glob.glob(SKILLS)):
        n = f.split("/")[1]
        for tok in sorted(set(re.findall(r"`([a-z0-9-]+(?::[a-z0-9-]+)?)`", open(f).read()))):
            if tok in NOMBRE_CORTO:
                errores.append(f"`{n}` cita `{tok}`: el nombre completo es `{NOMBRE_CORTO[tok]}`")
            elif ":" in tok and tok not in EXTERNAS | propias | {"file:line"}:
                errores.append(f"`{n}` cita `{tok}`, que no es una skill conocida")

    # 9. Una skill que fija `model:` y le pregunta algo al usuario tiene que preguntar con
    #    AskUserQuestion. Una pregunta en texto cierra el turno y la respuesta corre con el
    #    modelo de la sesión, no con el de la skill (medido en una corrida de project-init:
    #    59 llamadas en opus con `model: sonnet` declarado).
    PREGUNTAN = (
        "project-init", "requirements-analysis", "loop-design",
        "loop-adopt", "loop-ship", "loop-pitch",
    )
    for n in PREGUNTAN:
        if n in skills and skills[n].get("model"):
            texto = open(f"skills/{n}/SKILL.md").read()
            if "## Preguntas al usuario: siempre con `AskUserQuestion`" not in texto:
                errores.append(
                    f"`{n}` fija model: y pregunta al usuario, pero le falta la sección "
                    "de preguntas con AskUserQuestion: la respuesta correría con otro modelo"
                )

    # 9b. El orquestador tampoco puede bloquear AskUserQuestion: sus checkpoints le piden
    #     respuesta al usuario y, en texto, esa respuesta corre con el modelo de la sesión.
    loop_fm = skills.get("project-loop", {})
    if "AskUserQuestion" in str(loop_fm.get("disallowed-tools", "")):
        errores.append(
            "`project-loop` bloquea AskUserQuestion: sus checkpoints preguntarían en texto "
            "y el resto de la corrida saldría del modelo de la skill"
        )
    if "## Preguntas: pocas, y siempre con `AskUserQuestion`" not in loop:
        errores.append("`project-loop` no tiene la sección de preguntas con AskUserQuestion")

    # 10. Toda skill que invoca una dependencia externa apunta a la regla de
    #    degradación. Sin eso, en una sesión cloud la revisión ausente se saltea
    #    callada y el loop dice "revisado" sin haber revisado.
    deps = open(DEPENDENCIAS).read() if os.path.exists(DEPENDENCIAS) else ""
    externas = re.findall(r"^\| `([^`]+)` \|", deps, re.M)
    if not externas:
        errores.append(f"{DEPENDENCIAS} no lista ninguna dependencia externa")
    for f in sorted(glob.glob(SKILLS)):
        texto = open(f).read()
        usadas = [e for e in externas if f"`{e}`" in texto]
        if usadas and "references/dependencias-externas.md" not in texto:
            errores.append(f"`{f.split('/')[1]}` usa {', '.join(usadas)} "
                           f"y no cita {DEPENDENCIAS}")

    # 11. Toda skill externa que una etapa cita (chequeo 8) tiene su fila en la tabla de
    #     dependencias (chequeo 10). Si falta, en la nube nadie sabe qué dejó sin revisar.
    for f in sorted(glob.glob(SKILLS)):
        texto = open(f).read()
        for e in sorted(EXTERNAS):
            if f"`{e}`" in texto and e not in externas:
                errores.append(f"`{f.split('/')[1]}` cita `{e}`, que no tiene fila en {DEPENDENCIAS}")

    # 12. Lo que una etapa dice que corrió tiene que poder comprobarse. Medido: en 30
    #     corridas forkeadas, ninguna invocó una skill y varias anotaron
    #     "engineering:code-review (inline)". La línea `Skills invocadas:` es el contrato
    #     entre la etapa y el orquestador; sin ella, el nombre de una skill no prueba nada.
    CONTRATO = "`Skills invocadas: <lista separada por comas, o \"ninguna\">`"
    for n in ("code-exec", "loop-review"):
        if CONTRATO not in open(f"skills/{n}/SKILL.md").read():
            errores.append(f"`{n}` no cierra su resumen con la línea {CONTRATO}")
    if "## 2.d Lo que una etapa dice que corrió, se comprueba" not in loop:
        errores.append("`project-loop` no comprueba la línea `Skills invocadas:` de las etapas")

    # 13. El orquestador no implementa. Sin esta sección, cuando el plan se traba resuelve
    #     en su propio hilo (medido: 33 llamadas sin lanzar una etapa) y escribe etapas
    #     que no existen en la enumeración.
    if "## 2.e Vos no implementás, tampoco para destrabar" not in loop:
        errores.append("`project-loop` no tiene la sección 2.e (el orquestador no implementa)")
    if ".loop/review-log.md" not in open("skills/code-exec/SKILL.md").read():
        errores.append("`code-exec` no manda sus NO VERIFICADO a .loop/review-log.md")

    if errores:
        print("FALLA:")
        for e in errores:
            print("  -", e)
        return 1
    print(f"OK · {len(skills)} skills · {len(filas)} etapas encadenadas · sin bloqueos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
