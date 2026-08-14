from __future__ import annotations

import hashlib
import shutil
import stat
from pathlib import Path

import pytest

import plugin as plugin_module
from agent.plugin_composition import (
    SKILLS,
    CompositionRoot,
    Context,
    PluginRuntime,
    PluginSkills,
)
from agent.plugins.composable import ComposablePlugin
from agent.plugins.manager import PluginManager
from bus.event_bus import EventBus
from plugin import HuayueSkillsPlugin, apply, inject

PLUGIN_ROOT = Path(__file__).parents[1]
EXPECTED_SKILLS = {
    "anthropic-diagram",
    "codex-usage",
    "gh-cli",
    "image-generation-nano",
    "opencli",
    "paper-explainer",
    "playwright-browser",
    "yt-dlp-downloader",
}


def _tree_receipt(roots: tuple[Path, ...]) -> tuple[tuple[str, int, str], ...]:
    """Return a stable content and mode receipt for every plugin Skill file."""

    receipt: list[tuple[str, int, str]] = []
    for root in roots:
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            receipt.append(
                (
                    path.relative_to(root).as_posix(),
                    stat.S_IMODE(path.stat().st_mode),
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )
            )
    return tuple(receipt)


@pytest.mark.asyncio
async def test_v3_skills_match_v2_tree_and_cleanup_receipt(tmp_path: Path) -> None:
    _ = ComposablePlugin.from_module(plugin_module)
    legacy_roots = tuple(
        PLUGIN_ROOT / relative for relative in HuayueSkillsPlugin.skill_roots()
    )
    root = CompositionRoot("huayue-skills-parity")
    skills = PluginSkills()
    _ = await root.context.provide(SKILLS, skills)

    async def mount(ctx: Context) -> None:
        await apply(ctx, object())

    _ = await root.mount(
        mount,
        name="huayue-skills",
        inject=inject,
        runtime=PluginRuntime(
            plugin_id="huayue-skills",
            plugin_dir=PLUGIN_ROOT,
            data_dir=tmp_path / "plugin-data",
            workspace=tmp_path / "workspace",
            config=object(),
        ),
    )

    contribution = skills.freeze()["huayue-skills"]
    receipt = root.receipt()
    assert contribution.skill_roots == legacy_roots
    assert contribution.drift_skill_roots == ()
    assert _tree_receipt(contribution.skill_roots) == _tree_receipt(legacy_roots)
    assert receipt.ready is True
    assert receipt.writes == ()
    assert receipt.external_effects == ()

    await root.dispose()

    assert root.receipt().services == ()
    assert root.receipt().effects == ()


@pytest.mark.asyncio
async def test_v3_skills_load_through_real_generation_manager(tmp_path: Path) -> None:
    plugin_home = tmp_path / "plugins"
    _ = shutil.copytree(
        PLUGIN_ROOT,
        plugin_home / "huayue-skills",
        ignore=shutil.ignore_patterns(
            ".akashic-core",
            ".git",
            ".pytest_cache",
            "__pycache__",
        ),
    )
    workspace = tmp_path / "workspace"
    manager = PluginManager(
        plugin_dirs=[plugin_home],
        event_bus=EventBus(),
        tool_registry=None,
        workspace=workspace,
        installed_cache_root=tmp_path / "plugin-home" / "cache",
    )

    await manager.load_all()

    generation = manager.generation("huayue-skills")
    snapshot = manager.current_snapshot
    assert generation is not None and snapshot is not None
    assert isinstance(generation.instance, ComposablePlugin)
    assert generation.contributions.skill_roots == (
        plugin_home / "huayue-skills" / "skills",
    )
    assert snapshot.plugin_skill_index is not None
    source_names = {
        path.parent.name
        for path in (plugin_home / "huayue-skills" / "skills").glob("*/SKILL.md")
    }
    assert source_names == EXPECTED_SKILLS
    assert set(snapshot.plugin_skill_index.records) == EXPECTED_SKILLS
    assert manager.active_plugins()[0].skill_roots == (
        plugin_home / "huayue-skills" / "skills",
    )
    root = snapshot.composition_root
    assert root is not None
    assert "core.skills" in root.receipt().services
    assert "huayue-skills:skill:skill:skills" in root.receipt().effects

    await manager.terminate_all()

    assert root.receipt().services == ()
    assert root.receipt().effects == ()
