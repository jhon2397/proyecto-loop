from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

import vendorear


def test_reescribe_raiz_y_quita_namespaces_propios():
    t = "ver `${CLAUDE_PLUGIN_ROOT}/templates/x.md` y `dev-substrate:substrate-init`"
    assert vendorear.reescribir(t, ".claude/loop") == \
        "ver `.claude/loop/templates/x.md` y `substrate-init`"


def test_no_toca_namespaces_ajenos_ni_prosa():
    t = ("`engineering:code-review`, `design:design-critique`, "
         "el plugin `dev-substrate`: nada, dev-substrate: tampoco")
    assert vendorear.reescribir(t, ".claude/loop") == t


def test_vendorea_skills_agentes_y_recursos(plugin, tmp_path):
    destino = tmp_path / "proyecto"
    vendorear.vendorear(plugin, destino)
    etapa = (destino / ".claude/skills/etapa/SKILL.md").read_text()
    assert ".claude/loop/templates/loop/plan.md" in etapa
    assert "`substrate-init`" in etapa and "dev-substrate:" not in etapa
    sub = (destino / ".claude/skills/substrate-init/SKILL.md").read_text()
    assert ".claude/loop/plugins/dev-substrate/rules/" in sub
    assert (destino / ".claude/agents/architect.md").is_file()
    assert (destino / ".claude/loop/templates/loop/plan.md").is_file()
    assert (destino / ".claude/loop/plugins/dev-substrate/rules/api/rest.md").is_file()
    assert (destino / ".claude/loop/VERSION").read_text() == "9.9.9\n"


def test_toda_ruta_reescrita_existe(plugin, tmp_path):
    destino = tmp_path / "proyecto"
    vendorear.vendorear(plugin, destino)
    citadas = 0
    for f in (destino / ".claude").rglob("*.md"):
        for ruta in re.findall(r"\.claude/loop/[\w./-]+", f.read_text()):
            citadas += 1
            assert (destino / ruta.rstrip("/.,;:)`")).exists(), f"{f}: {ruta}"
    assert citadas >= 2  # un test que no encuentra rutas no prueba nada


def test_revendorear_conserva_lo_que_no_es_del_loop(plugin, tmp_path):
    destino = tmp_path / "proyecto"
    vendorear.vendorear(plugin, destino)
    propia = destino / ".claude/rules/api/mia.md"
    propia.parent.mkdir(parents=True)
    propia.write_text("regla del proyecto\n")
    skill = destino / ".claude/skills/propia/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: propia\n---\n")
    vendorear.vendorear(plugin, destino)
    assert propia.read_text() == "regla del proyecto\n"
    assert skill.is_file()


def test_revendorear_borra_lo_que_el_loop_ya_no_trae(plugin, tmp_path):
    destino = tmp_path / "proyecto"
    vendorear.vendorear(plugin, destino)
    shutil.rmtree(plugin / "skills/etapa")
    vendorear.vendorear(plugin, destino)
    assert not (destino / ".claude/skills/etapa").exists()


def test_no_pisa_una_skill_del_proyecto_con_el_mismo_nombre(plugin, tmp_path):
    destino = tmp_path / "proyecto"
    mia = destino / ".claude/skills/etapa/SKILL.md"
    mia.parent.mkdir(parents=True)
    mia.write_text("mía\n")
    with pytest.raises(SystemExit, match="etapa"):
        vendorear.vendorear(plugin, destino)
    assert mia.read_text() == "mía\n"


def test_desactiva_los_plugins_globales_sin_perder_claves(plugin, tmp_path):
    destino = tmp_path / "proyecto"
    (destino / ".claude").mkdir(parents=True)
    (destino / ".claude/settings.json").write_text(
        json.dumps({"permissions": {"allow": ["Bash(ls)"]}}))
    vendorear.vendorear(plugin, destino)
    s = json.loads((destino / ".claude/settings.json").read_text())
    assert s["permissions"] == {"allow": ["Bash(ls)"]}
    for p in vendorear.PLUGINS_GLOBALES:
        assert s["enabledPlugins"][p] is False


def test_rechaza_skill_duplicada_entre_plugins(plugin, tmp_path):
    otra = plugin / "plugins/dev-substrate/skills/etapa/SKILL.md"
    otra.parent.mkdir(parents=True)
    otra.write_text("---\nname: etapa\n---\n")
    with pytest.raises(SystemExit, match="duplicada"):
        vendorear.vendorear(plugin, tmp_path / "proyecto")


def test_manifiesto_que_se_sale_del_arbol_no_borra_nada(plugin, tmp_path):
    destino = tmp_path / "proyecto"
    vendorear.vendorear(plugin, destino)
    afuera = tmp_path / "afuera.txt"
    afuera.write_text("no me borres\n")
    m = destino / ".claude/loop/MANIFIESTO"
    m.write_text(m.read_text() + "../afuera.txt\n")
    with pytest.raises(SystemExit, match="MANIFIESTO inválido"):
        vendorear.vendorear(plugin, destino)
    assert afuera.read_text() == "no me borres\n"
    assert (destino / ".claude/skills/etapa/SKILL.md").is_file()


def test_copia_fallida_deja_intacto_el_vendoreo_anterior(plugin, tmp_path):
    destino = tmp_path / "proyecto"
    vendorear.vendorear(plugin, destino)
    roto = plugin / "skills/etapa/roto.md"
    roto.write_bytes(b"\xff\xfe esto no es utf-8")
    with pytest.raises(SystemExit, match="roto.md"):
        vendorear.vendorear(plugin, destino)
    assert (destino / ".claude/loop/VERSION").read_text() == "9.9.9\n"
    assert (destino / ".claude/loop/MANIFIESTO").is_file()
    assert (destino / ".claude/skills/etapa/SKILL.md").is_file()
    assert not list((destino / ".claude").glob(".vendoreo-*"))
    roto.unlink()
    vendorear.vendorear(plugin, destino)  # y la corrida siguiente se recupera sola
