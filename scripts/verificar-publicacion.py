#!/usr/bin/env python3
"""Chequeo de publicación: que no haya nombres internos en archivos versionados.

    uv run python scripts/verificar-publicacion.py

Los patrones concretos viven en scripts/nombres-internos.txt, que está
git-ignored: enumerarlos dentro del repo público sería publicar exactamente
lo que este chequeo existe para evitar.

Salida: 0 = limpio · 1 = hay nombres internos, o el chequeo no pudo correr.
"""
import pathlib
import subprocess
import sys

PATRONES = pathlib.Path("scripts/nombres-internos.txt")


def main():
    crudo = PATRONES.read_text() if PATRONES.exists() else ""
    patrones = [p.strip() for p in crudo.splitlines() if p.strip()]
    if not patrones:
        print(f"AVISO: {PATRONES} falta o está vacío.")
        print("Una línea por nombre interno a vigilar. Sin patrones no se")
        print("verifica nada: completalo antes de publicar.")
        return 1

    # Solo archivos versionados: lo que git no sigue, no se publica.
    salida = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, text=True, check=True
    ).stdout
    versionados = [f for f in salida.split("\0") if f]

    hallazgos = []
    for f in versionados:
        try:
            texto = pathlib.Path(f).read_text(errors="ignore")
        except OSError:
            continue
        for n, linea in enumerate(texto.splitlines(), 1):
            for pat in patrones:
                if pat in linea:
                    hallazgos.append(f"{f}:{n} contiene {pat!r}")

    if hallazgos:
        print("FALLA: hay nombres internos en archivos versionados:")
        for h in hallazgos:
            print("  -", h)
        return 1

    print(
        f"sin nombres internos: OK · {len(patrones)} patrón(es) · "
        f"{len(versionados)} archivos versionados"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
