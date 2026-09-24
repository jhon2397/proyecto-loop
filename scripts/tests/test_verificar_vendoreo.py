from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import vendorear

VERIF = Path(__file__).resolve().parent.parent / "verificar-vendoreo.py"


def correr(origen: Path, destino: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIF), "--origen", str(origen), "--destino", str(destino), *extra],
        capture_output=True, text=True)


@pytest.fixture
def vendoreado(plugin, tmp_path) -> Path:
    destino = tmp_path / "proyecto"
    vendorear.vendorear(plugin, destino)
    return destino


def test_aprueba_un_vendoreo_correcto(plugin, vendoreado):
    r = correr(plugin, vendoreado, "--sin-terceros")
    assert r.returncode == 0, r.stdout
    assert "vendoreo: OK" in r.stdout


def test_sin_vendoreo_avisa_y_no_aprueba(plugin, tmp_path):
    r = correr(plugin, tmp_path / "vacio", "--sin-terceros")
    assert r.returncode == 1
    assert "AVISO" in r.stdout


def romper_raiz(d):
    f = d / ".claude/skills/etapa/SKILL.md"
    f.write_text(f.read_text() + "\n${CLAUDE_PLUGIN_ROOT}/x\n")


def romper_namespace(d):
    f = d / ".claude/skills/etapa/SKILL.md"
    f.write_text(f.read_text() + "\n`dev-substrate:substrate-init`\n")


def romper_ruta(d):
    (d / ".claude/loop/templates/loop/plan.md").unlink()


def romper_version(d):
    (d / ".claude/loop/VERSION").write_text("0.0.1\n")


def romper_settings(d):
    p = d / ".claude/settings.json"
    s = json.loads(p.read_text())
    s["enabledPlugins"]["proyecto-loop@proyecto-loop-local"] = True
    p.write_text(json.dumps(s))


def romper_recurso(d):
    f = d / ".claude/loop/references/ui-patterns.md"
    f.write_text(f.read_text() + "\n${CLAUDE_PLUGIN_ROOT}/x\n")


@pytest.mark.parametrize("romper, esperado", [
    (romper_raiz, "CLAUDE_PLUGIN_ROOT"),
    (romper_namespace, "namespace"),
    (romper_ruta, "no existe"),
    (romper_version, "VERSION"),
    (romper_settings, "plugin global"),
    (romper_recurso, "CLAUDE_PLUGIN_ROOT"),
])
def test_detecta_cada_rotura(plugin, vendoreado, romper, esperado):
    romper(vendoreado)
    r = correr(plugin, vendoreado, "--sin-terceros")
    assert r.returncode == 1, r.stdout
    assert esperado in r.stdout


def test_exige_los_terceros_que_declara_el_origen(plugin, vendoreado):
    (plugin / "terceros.json").write_text(json.dumps(
        {"skill-ajena": {"url": "x", "sha": "y", "ruta": "z", "licencia": "MIT"}}))
    r = correr(plugin, vendoreado)
    assert r.returncode == 1
    assert "skill-ajena" in r.stdout


def test_archivo_no_utf8_es_falla_y_no_traceback(plugin, vendoreado):
    (vendoreado / ".claude/loop/references/ui-patterns.md").write_bytes(
        b"\xff\xfe no es utf-8")
    r = correr(plugin, vendoreado, "--sin-terceros")
    assert r.returncode == 1, r.stdout
    assert "no es UTF-8 válido" in r.stdout
    assert "Traceback" not in r.stderr


def test_sin_terceros_json_avisa_y_no_aprueba(plugin, vendoreado):
    r = correr(plugin, vendoreado)
    assert r.returncode == 1, r.stdout
    assert "AVISO" in r.stdout
    assert "terceros.json" in r.stdout
    assert "Traceback" not in r.stderr


def test_sin_plugin_json_avisa_y_no_aprueba(plugin, vendoreado):
    (plugin / ".claude-plugin/plugin.json").unlink()
    r = correr(plugin, vendoreado, "--sin-terceros")
    assert r.returncode == 1, r.stdout
    assert "AVISO" in r.stdout
    assert "plugin.json" in r.stdout
    assert "Traceback" not in r.stderr
