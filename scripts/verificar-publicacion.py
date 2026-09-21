#!/usr/bin/env python3
"""Chequeo de publicación: que no haya nombres internos en archivos versionados.

    uv run python scripts/verificar-publicacion.py

Los patrones concretos viven en scripts/nombres-internos.txt, que está
git-ignored: enumerarlos dentro del repo público sería publicar exactamente
lo que este chequeo existe para evitar. Una línea por patrón; las líneas que
empiezan con # son comentarios.

La comparación es por subcadena y SENSIBLE A MAYÚSCULAS: un nombre filtrado
con otra capitalización no se detecta. Agregá las variantes que te importen
como patrones separados.

Cubre el contenido actual de los archivos versionados, NO la historia de git:
que los commits viejos no carguen nombres internos es un chequeo aparte.

Salida: 0 = verificado limpio · 1 = hay nombres internos, o el chequeo no
pudo verificar todo lo que debía.
"""
import pathlib
import subprocess
import sys

PATRONES = pathlib.Path("scripts/nombres-internos.txt")


def aviso(*lineas):
    """AVISO nunca aprueba: el chequeo no llegó a verificar lo que debía."""
    for linea in lineas:
        print(linea)
    return 1


def main():
    crudo = PATRONES.read_text() if PATRONES.exists() else ""
    patrones = [
        p.strip()
        for p in crudo.splitlines()
        if p.strip() and not p.lstrip().startswith("#")
    ]
    if not patrones:
        return aviso(
            f"AVISO: {PATRONES} falta, está vacío o solo tiene comentarios.",
            "Una línea por nombre interno a vigilar. Sin patrones no se",
            "verifica nada: completalo antes de publicar.",
        )

    try:
        salida = subprocess.run(
            ["git", "ls-files", "-z"], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        return aviso(f"AVISO: no se pudo listar los archivos versionados: {e}")

    versionados = [f for f in salida.split("\0") if f]
    if not versionados:
        return aviso(
            "AVISO: git no devolvió archivos versionados.",
            "El chequeo no verificó nada: ¿estás en la raíz del repo?",
        )

    hallazgos = []
    ilegibles = []
    leidos = 0
    for f in versionados:
        try:
            texto = pathlib.Path(f).read_text(errors="ignore")
        except OSError as e:
            ilegibles.append(f"{f} ({e.__class__.__name__})")
            continue
        leidos += 1
        for n, linea in enumerate(texto.splitlines(), 1):
            for pat in patrones:
                if pat in linea:
                    hallazgos.append(f"{f}:{n} contiene {pat!r}")

    if hallazgos:
        print("FALLA: hay nombres internos en archivos versionados:")
        for h in hallazgos:
            print("  -", h)
        return 1

    if ilegibles:
        return aviso(
            f"AVISO: {len(ilegibles)} archivo(s) versionado(s) no se pudieron leer.",
            "No se puede afirmar que el repo esté limpio sin haberlos revisado:",
            *[f"  - {i}" for i in ilegibles],
        )

    print(
        f"sin nombres internos: OK · {len(patrones)} patrón(es) · "
        f"{leidos} archivos leídos de {len(versionados)} versionados"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
