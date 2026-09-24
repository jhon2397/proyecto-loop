#!/usr/bin/env python3
"""Verifica que el .claude/ de un proyecto sea un vendoreo correcto del loop.

    uv run python scripts/verificar-vendoreo.py --destino <proyecto> [--origen <proyecto-loop>]

Lo corren la Action que regenera la plantilla y la skill loop-actualizar antes
de commitear. Salida: 0 = verificado · 1 = hay fallas, o no se pudo verificar.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLUGINS_GLOBALES = ("proyecto-loop@proyecto-loop-local", "dev-substrate@proyecto-loop-local")
RUTA_LOOP = re.compile(r"\.claude/loop/[\w./-]+")
NAMESPACE_PROPIO = re.compile(r"\b(?:proyecto-loop|dev-substrate):(?=[a-z])")
# Mismas extensiones de texto que reescribe vendorear.py.
TEXTO = {".md", ".txt", ".json", ".yaml", ".yml"}
# Metadatos del propio vendoreo: no son recursos espejados del plugin.
EXCLUIDOS_LOOP = {"VERSION", "MANIFIESTO", "TERCEROS.md"}


def archivos_de_texto(raiz: Path) -> list[Path]:
    """Todos los archivos de texto (según TEXTO) bajo `raiz`, si existe."""
    if not raiz.is_dir():
        return []
    return sorted(f for f in raiz.rglob("*") if f.is_file() and f.suffix in TEXTO)


def leer(f: Path) -> str | None:
    """Lee un archivo de texto propio del loop, o None si no es UTF-8 válido."""
    try:
        return f.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verifica un vendoreo del loop.")
    ap.add_argument("--destino", required=True, type=Path)
    ap.add_argument("--origen", type=Path, default=RAIZ)
    ap.add_argument("--sin-terceros", action="store_true",
                    help="el vendoreo se hizo sin skills de terceros")
    a = ap.parse_args(argv)
    d, o = a.destino.resolve(), a.origen.resolve()
    claude = d / ".claude"
    loop = claude / "loop"
    manifiesto = loop / "MANIFIESTO"
    if not manifiesto.is_file():
        print(f"AVISO: no existe {manifiesto}: no hay un vendoreo que verificar.")
        return 1

    errores: list[str] = []
    gestionadas = manifiesto.read_text(encoding="utf-8").split()

    terceros_json = o / "terceros.json"
    if a.sin_terceros:
        terceros = {}
    else:
        try:
            terceros = json.loads(terceros_json.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"AVISO: no existe {terceros_json}: no se pudo verificar el vendoreo.")
            return 1
        except json.JSONDecodeError:
            print(f"AVISO: {terceros_json} no es JSON válido: no se pudo verificar el vendoreo.")
            return 1
    de_terceros = {f".claude/skills/{n}" for n in terceros}

    plugin_json = o / ".claude-plugin/plugin.json"
    try:
        version = json.loads(plugin_json.read_text(encoding="utf-8"))["version"]
    except FileNotFoundError:
        print(f"AVISO: no existe {plugin_json}: no se pudo verificar el vendoreo.")
        return 1
    except json.JSONDecodeError:
        print(f"AVISO: {plugin_json} no es JSON válido: no se pudo verificar el vendoreo.")
        return 1
    archivo_version = loop / "VERSION"
    vendoreada = (archivo_version.read_text(encoding="utf-8").strip()
                  if archivo_version.is_file() else None)
    if vendoreada != version:
        errores.append(f"VERSION dice {vendoreada!r} y el plugin {version!r}")

    for rel in gestionadas:
        if not (d / rel).exists():
            errores.append(f"el MANIFIESTO lista {rel} y no existe")

    # Lo propio del loop: las rutas gestionadas del MANIFIESTO (menos las de
    # terceros, que se copian sin reescribir) más los recursos espejados bajo
    # .claude/loop/ (templates, references, presets de dev-substrate, etc.),
    # que el MANIFIESTO no lista pero vendorear.py también reescribe.
    archivos: list[Path] = []
    for rel in gestionadas:
        if rel in de_terceros:
            continue
        p = d / rel
        archivos += [p] if p.is_file() else archivos_de_texto(p)
    archivos += [f for f in archivos_de_texto(loop) if f.name not in EXCLUIDOS_LOOP]

    for f in archivos:
        nombre = f.relative_to(d)
        texto = leer(f)
        if texto is None:
            errores.append(f"{nombre}: no es UTF-8 válido")
            continue
        if "${CLAUDE_PLUGIN_ROOT}" in texto:
            errores.append(f"{nombre}: quedó CLAUDE_PLUGIN_ROOT sin reescribir")
        if NAMESPACE_PROPIO.search(texto):
            errores.append(f"{nombre}: quedó un namespace propio sin quitar")
        for ruta in RUTA_LOOP.findall(texto):
            ruta = ruta.rstrip("/.,;:)`")
            if not (d / ruta).exists():
                errores.append(f"{nombre}: cita {ruta}, que no existe")
    if not archivos:
        errores.append("no se revisó ningún archivo propio del loop: el vendoreo está vacío")

    for n in terceros:
        s = claude / "skills" / n
        if not (s / "SKILL.md").is_file():
            errores.append(f"falta la skill de terceros {n}")
        elif not (s / "LICENSE").is_file():
            errores.append(f"la skill de terceros {n} no trae su LICENSE")

    ajustes = claude / "settings.json"
    habilitados = (json.loads(ajustes.read_text(encoding="utf-8")).get("enabledPlugins", {})
                   if ajustes.is_file() else {})
    for p in PLUGINS_GLOBALES:
        if habilitados.get(p) is not False:
            errores.append(f"settings.json no desactiva el plugin global {p}")

    if errores:
        print("FALLA:")
        for e in errores:
            print("  -", e)
        return 1
    print(f"vendoreo: OK · versión {version} · {len(gestionadas)} rutas · "
          f"{len(archivos)} archivos revisados · {len(terceros)} de terceros")
    return 0


if __name__ == "__main__":
    sys.exit(main())
