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


def reescribir(texto: str, prefijo: str) -> str:
    """Adapta un archivo del plugin para que viva dentro de un proyecto."""
    return NAMESPACE_PROPIO.sub("", texto.replace("${CLAUDE_PLUGIN_ROOT}", prefijo))


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


def copiar_archivo(origen: Path, destino: Path, prefijo: str) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if origen.suffix in TEXTO:
        destino.write_text(reescribir(leer_texto(origen), prefijo), encoding="utf-8")
    else:
        shutil.copy2(origen, destino)


def copiar(origen: Path, destino: Path, prefijo: str) -> None:
    """Copia un árbol reescribiendo los archivos de texto; el resto, byte a byte."""
    for f in sorted(origen.rglob("*")):
        if f.is_file():
            copiar_archivo(f, destino / f.relative_to(origen), prefijo)


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


def vendorear(raiz: Path, destino: Path) -> list[str]:
    """Arma o actualiza el .claude/ de `destino`. Devuelve las rutas gestionadas."""
    claude = destino / ".claude"
    loop = destino / PREFIJO_LOOP
    manifiesto = loop / "MANIFIESTO"
    previas = (set(manifiesto.read_text(encoding="utf-8").split())
               if manifiesto.exists() else set())
    validar_manifiesto(previas)
    plan = planificar(raiz)

    # Antes de tocar nada: no pisar lo que el proyecto creó por su cuenta.
    for _, rel, _ in plan:
        if (destino / rel).exists() and rel not in previas:
            raise SystemExit(f"{rel} ya existe y no es del loop: no se pisa")

    rechazar_enlaces(destino, previas | {PREFIJO_LOOP} | {rel for _, rel, _ in plan})

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
        for origen, rel, prefijo in plan:
            if origen.is_dir():
                copiar(origen, temporal / rel, prefijo)
            else:
                copiar_archivo(origen, temporal / rel, prefijo)
            gestionadas.append(rel)
        for r in RECURSOS:
            copiar(raiz / r, temporal / PREFIJO_LOOP / r, prefijo_de(r))
        (temporal / PREFIJO_LOOP / "VERSION").write_text(
            leer_version(raiz) + "\n", encoding="utf-8")
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
    a = ap.parse_args(argv)
    rutas = vendorear(a.origen.resolve(), a.destino.resolve())
    print(f"vendoreado: {len(rutas)} skills y agentes · versión "
          f"{leer_version(a.origen)} → {a.destino}/.claude")
    return 0


if __name__ == "__main__":
    sys.exit(main())
