#!/usr/bin/env python3
"""Vendorea el loop en un proyecto: arma su .claude/ a partir del plugin.

    uv run python scripts/vendorear.py --destino <ruta-del-proyecto>

Los plugins no cargan en sesiones cloud: lo que llega es lo commiteado en el
repo. Por eso el loop se copia al .claude/ de cada proyecto. Este script es la
única transformación entre el plugin y un proyecto; lo usan la Action que
regenera la plantilla y la skill loop-actualizar.

Solo gestiona lo suyo: lo que quedó listado en .claude/loop/MANIFIESTO. Las
reglas que instaló loop-rules, las skills propias del proyecto y las claves
ajenas de .claude/settings.json no se tocan.

Es transaccional: arma todo el vendoreo nuevo en un directorio temporal, y
solo si terminó sin errores reemplaza lo anterior. Si algo falla, el proyecto
queda como estaba: esa garantía cubre el armado. El reemplazo final son varios
renames en el mismo disco, y un corte justo ahí puede dejarlo a medias; en ese
caso, volver a correr el script lo repara.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

RAIZ = Path(__file__).resolve().parent.parent

# ${CLAUDE_PLUGIN_ROOT} apunta a la raíz de CADA plugin, así que se reescribe
# distinto según de qué plugin venga el archivo.
PREFIJO_LOOP = ".claude/loop"
PREFIJO_SUBSTRATE = ".claude/loop/plugins/dev-substrate"
FUENTES = (
    ("skills", None, PREFIJO_LOOP),
    ("plugins/dev-substrate/skills", "plugins/dev-substrate/agents", PREFIJO_SUBSTRATE),
)
# Recursos no ejecutables: .claude/loop/ es un espejo de su ubicación en el plugin.
RECURSOS = (
    "templates",
    "references",
    "herramientas",
    "plugins/dev-substrate/rules",
    "plugins/dev-substrate/presets",
    "plugins/dev-substrate/templates",
)
# Las únicas raíces cuyo contenido el loop gestiona, y por lo tanto puede borrar.
RAICES_GESTIONADAS = (".claude/skills", ".claude/agents")
PLUGINS_GLOBALES = (
    "proyecto-loop@proyecto-loop-local",
    "dev-substrate@proyecto-loop-local",
)
# Solo los namespaces propios: los de otros plugins (engineering:, design:) quedan.
NAMESPACE_PROPIO = re.compile(r"\b(?:proyecto-loop|dev-substrate):(?=[a-z])")
TEXTO = {".md", ".txt", ".json", ".yaml", ".yml"}


def reescribir(texto: str, prefijo: str, vendoreadas: tuple[str, ...] = ()) -> str:
    """Adapta un archivo del plugin para que viva dentro de un proyecto.

    Las skills de terceros vendoreadas viven en .claude/skills/<nombre>, sin el
    namespace del plugin que las trae en la máquina local: sus citas pasan a corto.
    """
    texto = NAMESPACE_PROPIO.sub("", texto.replace("${CLAUDE_PLUGIN_ROOT}", prefijo))
    for nombre in vendoreadas:
        texto = re.sub(rf"(?<![\w-])[a-z0-9-]+:{re.escape(nombre)}(?![\w-])", nombre, texto)
    return texto


def prefijo_de(ruta_relativa: str) -> str:
    if ruta_relativa.startswith("plugins/dev-substrate"):
        return PREFIJO_SUBSTRATE
    return PREFIJO_LOOP


def leer_texto(f: Path) -> str:
    """Lee un archivo de texto del plugin, o aborta nombrando el que falló."""
    try:
        return f.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise SystemExit(f"{f}: no es UTF-8 válido ({e.reason}). "
                         "El proyecto no se tocó.") from None


def copiar_archivo(origen: Path, destino: Path, prefijo: str,
                   vendoreadas: tuple[str, ...] = ()) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if origen.suffix in TEXTO:
        destino.write_text(reescribir(leer_texto(origen), prefijo, vendoreadas),
                           encoding="utf-8")
    else:
        shutil.copy2(origen, destino)


def copiar(origen: Path, destino: Path, prefijo: str,
           vendoreadas: tuple[str, ...] = ()) -> None:
    """Copia un árbol reescribiendo los archivos de texto; el resto, byte a byte."""
    for f in sorted(origen.rglob("*")):
        if f.is_file():
            copiar_archivo(f, destino / f.relative_to(origen), prefijo, vendoreadas)


def borrar(p: Path) -> None:
    if p.is_dir():
        shutil.rmtree(p)
    elif p.exists():
        p.unlink()


def leer_version(raiz: Path) -> str:
    return json.loads((raiz / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]


def validar_manifiesto(previas: set[str]) -> None:
    """Un manifiesto solo puede listar entradas directas de RAICES_GESTIONADAS.

    Una entrada que se sale de ahí —`..`, una ruta absoluta, otra carpeta— haría
    que el re-vendoreo borrara algo que no es suyo. Se aborta sin tocar nada.
    """
    for rel in sorted(previas):
        partes = Path(rel).parts
        if (Path(rel).is_absolute() or ".." in partes or len(partes) != 3
                or "/".join(partes[:2]) not in RAICES_GESTIONADAS):
            raise SystemExit(f"MANIFIESTO inválido: {rel!r} no es una ruta que el loop "
                             "gestione. No se borró nada; revisá el archivo a mano.")


def rechazar_enlaces(destino: Path, rels: Iterable[str]) -> None:
    """Aborta si una ruta gestionada o alguno de sus ancestros es un enlace simbólico.

    shutil.rmtree tira un OSError crudo al borrar a través de un symlink en la
    fase de swap; mejor cortar acá, antes de armar el temporal y de borrar nada.
    """
    for rel in rels:
        partes = Path(rel).parts
        for i in range(1, len(partes) + 1):
            parcial = destino / Path(*partes[:i])
            if parcial.is_symlink():
                raise SystemExit(f"{parcial.relative_to(destino)}: es un enlace simbólico; "
                                 "el loop no borra a través de enlaces. El proyecto no se tocó.")


def planificar(raiz: Path) -> list[tuple[Path, str, str]]:
    """Qué skills y agentes van a dónde: (origen, destino relativo, prefijo)."""
    plan: list[tuple[Path, str, str]] = []
    vistos: set[str] = set()
    for skills, agentes, prefijo in FUENTES:
        for d in sorted((raiz / skills).iterdir()):
            if not (d / "SKILL.md").is_file():
                continue
            if d.name in vistos:
                raise SystemExit(f"skill duplicada entre plugins: {d.name}")
            vistos.add(d.name)
            plan.append((d, f".claude/skills/{d.name}", prefijo))
        if agentes:
            for a in sorted((raiz / agentes).glob("*.md")):
                plan.append((a, f".claude/agents/{a.name}", prefijo))
    return plan


def desactivar_plugins_globales(destino: Path) -> None:
    """Que en local corra la copia vendoreada y no la del plugin global."""
    p = destino / ".claude/settings.json"
    datos = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    habilitados = datos.setdefault("enabledPlugins", {})
    for plugin in PLUGINS_GLOBALES:
        habilitados[plugin] = False
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def obtener_tercero(url: str, sha: str, cache: Path) -> Path:
    """Trae el repo de origen en un commit exacto: por SHA, nunca por rama."""
    d = cache / sha
    marcador = d / ".completo"
    # git init crea d/.git antes del fetch: si quedó a medias por un corte,
    # el marcador no está y hay que rehacer el clon desde cero.
    if d.exists() and not marcador.is_file():
        shutil.rmtree(d)
    if not marcador.is_file():
        d.mkdir(parents=True, exist_ok=True)
        for cmd in (
            ["git", "init", "-q"],
            ["git", "fetch", "-q", "--depth", "1", url, sha],
            ["git", "checkout", "-q", "--detach", "FETCH_HEAD"],
        ):
            try:
                subprocess.run(cmd, cwd=d, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                stderr = (e.stderr or "").strip()
                detalle = f" stderr: {stderr[:500]}" if stderr else ""
                raise SystemExit(
                    f"{url}: falló '{' '.join(cmd)}' para el commit {sha}. "
                    f"El proyecto no se tocó.{detalle}"
                ) from None
        marcador.touch()
    return d


def nombre_declarado(skill_md: Path) -> str | None:
    m = re.search(r"^name:\s*(\S+)", leer_texto(skill_md), re.M)
    return m.group(1) if m else None


def planificar_terceros(terceros: dict, cache: Path) -> list[tuple[Path, str, dict]]:
    """Trae cada skill de terceros y confirma que declare el nombre esperado."""
    plan: list[tuple[Path, str, dict]] = []
    for nombre, t in sorted(terceros.items()):
        repo = obtener_tercero(t["url"], t["sha"], cache)
        skill_md = repo / t["ruta"] / "SKILL.md"
        if not skill_md.is_file():
            raise SystemExit(f"{nombre}: no hay SKILL.md en {t['ruta']} del commit "
                             f"{t['sha']}. El proyecto no se tocó.")
        real = nombre_declarado(skill_md)
        if real != nombre:
            raise SystemExit(f"{nombre}: la skill en {t['ruta']} declara name={real!r}")
        if not (repo / "LICENSE").is_file():
            raise SystemExit(f"{nombre}: el repo de origen no tiene LICENSE")
        plan.append((repo, f".claude/skills/{nombre}", t))
    return plan


def escribir_terceros_md(loop: Path, plan: list[tuple[Path, str, dict]]) -> None:
    lineas = ["# Skills de terceros vendoreadas", ""]
    if not plan:
        lineas.append("Ninguna. Este vendoreo se hizo sin skills de terceros.")
    else:
        lineas += ["Copiadas sin modificar desde su repo de origen, fijadas por commit.",
                   "Cada una trae su `LICENSE`.", "",
                   "| Skill | Origen | Commit | Licencia |", "|---|---|---|---|"]
        for _, rel, t in plan:
            lineas.append(f"| `{rel.rsplit('/', 1)[1]}` | {t['url']} | "
                          f"`{t['sha']}` | {t['licencia']} |")
    (loop / "TERCEROS.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def vendorear(raiz: Path, destino: Path, terceros: dict | None = None,
              cache: Path | None = None) -> list[str]:
    """Arma o actualiza el .claude/ de `destino`. Devuelve las rutas gestionadas."""
    if terceros and cache is None:
        with tempfile.TemporaryDirectory() as tmp:
            return vendorear(raiz, destino, terceros, Path(tmp))
    claude = destino / ".claude"
    loop = destino / PREFIJO_LOOP
    manifiesto = loop / "MANIFIESTO"
    previas = (set(manifiesto.read_text(encoding="utf-8").split())
               if manifiesto.exists() else set())
    validar_manifiesto(previas)
    plan = planificar(raiz)
    plan_terceros = planificar_terceros(terceros, cache) if terceros else []
    rels_propias = {rel for _, rel, _ in plan}
    for _, rel, _ in plan_terceros:
        if rel in rels_propias:
            nombre = rel.rsplit("/", 1)[1]
            raise SystemExit(f"{nombre}: el tercero tiene el mismo nombre que una skill "
                             "del loop. El proyecto no se tocó.")

    # Antes de tocar nada: no pisar lo que el proyecto creó por su cuenta.
    for rel in [r for _, r, _ in plan] + [r for _, r, _ in plan_terceros]:
        if (destino / rel).exists() and rel not in previas:
            raise SystemExit(f"{rel} ya existe y no es del loop: no se pisa")

    rechazar_enlaces(destino, previas | {PREFIJO_LOOP} | {rel for _, rel, _ in plan}
                     | {rel for _, rel, _ in plan_terceros})

    # 1. Armar el vendoreo completo en un temporal, en el mismo disco para que
    #    el reemplazo sea un rename. Si algo falla acá, el proyecto no se tocó.
    claude.mkdir(parents=True, exist_ok=True)
    # Un corte a mitad de una corrida anterior pudo dejar un temporal sin
    # reemplazar; se limpia antes de arrancar para que no lo levante un commit.
    for viejo in claude.glob(".vendoreo-*"):
        if viejo.is_dir() and not viejo.is_symlink():
            shutil.rmtree(viejo)
    temporal = Path(tempfile.mkdtemp(prefix=".vendoreo-", dir=claude))
    try:
        gestionadas: list[str] = []
        vendoreadas = tuple(rel.rsplit("/", 1)[1] for _, rel, _ in plan_terceros)
        for origen, rel, prefijo in plan:
            if origen.is_dir():
                copiar(origen, temporal / rel, prefijo, vendoreadas)
            else:
                copiar_archivo(origen, temporal / rel, prefijo, vendoreadas)
            gestionadas.append(rel)
        for repo, rel, t in plan_terceros:
            shutil.copytree(repo / t["ruta"], temporal / rel)  # código ajeno: sin reescribir
            shutil.copy2(repo / "LICENSE", temporal / rel / "LICENSE")
            gestionadas.append(rel)
        for r in RECURSOS:
            copiar(raiz / r, temporal / PREFIJO_LOOP / r, prefijo_de(r), vendoreadas)
        (temporal / PREFIJO_LOOP / "VERSION").write_text(
            leer_version(raiz) + "\n", encoding="utf-8")
        escribir_terceros_md(temporal / PREFIJO_LOOP, plan_terceros)
        (temporal / PREFIJO_LOOP / "MANIFIESTO").write_text(
            "\n".join(gestionadas) + "\n", encoding="utf-8")

        # 2. Recién ahora se reemplaza: borrar lo gestionado antes y mover lo nuevo.
        for rel in previas:
            borrar(destino / rel)
        borrar(loop)
        for rel in gestionadas + [PREFIJO_LOOP]:
            dst = destino / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            (temporal / rel).rename(dst)
    finally:
        shutil.rmtree(temporal, ignore_errors=True)

    desactivar_plugins_globales(destino)
    return gestionadas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Vendorea el loop en un proyecto.")
    ap.add_argument("--destino", required=True, type=Path, help="raíz del proyecto")
    ap.add_argument("--origen", type=Path, default=RAIZ, help="raíz de proyecto-loop")
    ap.add_argument("--sin-terceros", action="store_true",
                    help="no bajar skills de terceros (para probar sin red)")
    a = ap.parse_args(argv)
    origen = a.origen.resolve()
    terceros = (None if a.sin_terceros
                else json.loads((origen / "terceros.json").read_text(encoding="utf-8")))
    with tempfile.TemporaryDirectory() as cache:
        rutas = vendorear(origen, a.destino.resolve(), terceros, Path(cache))
    print(f"vendoreado: {len(rutas)} rutas · versión {leer_version(origen)} "
          f"· {len(terceros or {})} de terceros → {a.destino}/.claude")
    return 0


if __name__ == "__main__":
    sys.exit(main())
