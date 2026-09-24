from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def escribir(p: Path, texto: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto)


@pytest.fixture
def plugin(tmp_path: Path) -> Path:
    """Un plugin mínimo con la misma forma que proyecto-loop."""
    r = tmp_path / "plugin"
    escribir(r / ".claude-plugin/plugin.json",
             json.dumps({"name": "proyecto-loop", "version": "9.9.9"}))
    escribir(r / "skills/etapa/SKILL.md",
             "---\nname: etapa\n---\n"
             "Copiá `${CLAUDE_PLUGIN_ROOT}/templates/loop/plan.md` "
             "y después `dev-substrate:substrate-init`.\n")
    escribir(r / "templates/loop/plan.md", "# Plan\n")
    escribir(r / "references/ui-patterns.md", "# UI\n")
    escribir(r / "plugins/dev-substrate/skills/substrate-init/SKILL.md",
             "---\nname: substrate-init\n---\n"
             "Elegí del catálogo `${CLAUDE_PLUGIN_ROOT}/rules/`.\n")
    escribir(r / "plugins/dev-substrate/agents/architect.md",
             "---\nname: architect\n---\nArquitecto.\n")
    escribir(r / "plugins/dev-substrate/rules/api/rest.md", "regla\n")
    escribir(r / "plugins/dev-substrate/presets/base.txt", "api/rest.md\n")
    escribir(r / "plugins/dev-substrate/templates/CLAUDE.md", "# CLAUDE\n")
    return r


@pytest.fixture
def repo_tercero(tmp_path: Path) -> dict:
    """Un repo git local que hace de repo de origen de una skill de terceros.

    La carpeta se llama distinto que la skill a propósito: pasa lo mismo con
    design-taste-frontend, que en su repo vive en skills/taste-skill.
    """
    d = tmp_path / "tercero"
    escribir(d / "LICENSE", "MIT License\n")
    escribir(d / "skills/carpeta-distinta/SKILL.md",
             "---\nname: skill-ajena\n---\nUsa `${CLAUDE_PLUGIN_ROOT}` propio.\n")
    for cmd in (["git", "init", "-q"],
                ["git", "add", "-A"],
                ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"],
                ["git", "config", "uploadpack.allowAnySHA1InWant", "true"]):
        subprocess.run(cmd, cwd=d, check=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, check=True,
                         capture_output=True, text=True).stdout.strip()
    return {"skill-ajena": {"url": d.as_uri(), "sha": sha,
                            "ruta": "skills/carpeta-distinta", "licencia": "MIT"}}
