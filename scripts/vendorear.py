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
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

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


def copiar(origen: Path, destino: Path, prefijo: str) -> None:
    """Copia un árbol reescribiendo los archivos de texto; el resto, byte a byte."""
    for f in sorted(origen.rglob("*")):
        if not f.is_file():
            continue
        dst = destino / f.relative_to(origen)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if f.suffix in TEXTO:
            dst.write_text(reescribir(f.read_text(), prefijo))
        else:
            shutil.copy2(f, dst)


def leer_version(raiz: Path) -> str:
    return json.loads((raiz / ".claude-plugin/plugin.json").read_text())["version"]


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
    datos = json.loads(p.read_text()) if p.exists() else {}
    habilitados = datos.setdefault("enabledPlugins", {})
    for plugin in PLUGINS_GLOBALES:
        habilitados[plugin] = False
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n")


def vendorear(raiz: Path, destino: Path) -> list[str]:
    """Arma o actualiza el .claude/ de `destino`. Devuelve las rutas gestionadas."""
    loop = destino / PREFIJO_LOOP
    manifiesto = loop / "MANIFIESTO"
    previas = set(manifiesto.read_text().split()) if manifiesto.exists() else set()
    plan = planificar(raiz)

    # Antes de borrar nada: no pisar lo que el proyecto creó por su cuenta.
    for _, rel, _ in plan:
        if (destino / rel).exists() and rel not in previas:
            raise SystemExit(f"{rel} ya existe y no es del loop: no se pisa")

    for rel in previas:
        p = destino / rel
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    if loop.exists():
        shutil.rmtree(loop)

    gestionadas: list[str] = []
    for origen, rel, prefijo in plan:
        if origen.is_dir():
            copiar(origen, destino / rel, prefijo)
        else:
            dst = destino / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(reescribir(origen.read_text(), prefijo))
        gestionadas.append(rel)

    for r in RECURSOS:
        copiar(raiz / r, loop / r, prefijo_de(r))

    desactivar_plugins_globales(destino)
    loop.mkdir(parents=True, exist_ok=True)
    (loop / "VERSION").write_text(leer_version(raiz) + "\n")
    manifiesto.write_text("\n".join(gestionadas) + "\n")
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
