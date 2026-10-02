from __future__ import annotations

import hashlib
import shutil
import stat
from pathlib import Path

import pytest

from agent.plugins.composable import ComposablePlugin
from agent.plugins.manager import PluginManager
from plugins.assets import plugin as assets_module
from bus.event_bus import EventBus
from agent.plugin_composition.assets import INSTALLED_ASSETS
from tests.fixtures.plugin_workspace import initialize_plugin_workspace

PLUGIN_ROOT = Path(__file__).parents[1]
EXPECTED_SKILLS = {
    "anthropic-diagram",
    "codex-usage",
    "gh-cli",
    "image-generation-nano",
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
                    stat.S_IMODE(path.stat().st_mode) & 0o111,
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )
            )
    return tuple(receipt)






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
    core = Path(assets_module.__file__).parents[1]
    shutil.copytree(core / "assets", plugin_home / "assets")
    workspace = tmp_path / "workspace"
    initialize_plugin_workspace(workspace)
    manager = PluginManager(
        plugin_dirs=[plugin_home],
        event_bus=EventBus(),
        workspace=workspace,
        installed_cache_root=tmp_path / "plugin-home" / "cache",
    )

    await manager.load_all()

    generation = manager.generation("huayue-skills")
    root = manager.live_root
    assert generation is not None and root is not None
    assert generation.fiber is not None
    assert isinstance(generation.instance, ComposablePlugin)
    async with generation.fiber.context.runtime_scope():
        assets = root.context.require(INSTALLED_ASSETS)(generation.fiber.context)
    archived = tuple(asset.root_dir for asset in assets if asset.category == "skills")
    assert _tree_receipt(archived) == _tree_receipt((PLUGIN_ROOT / "skills",))
    assert all(
        path.is_relative_to(workspace / "runtime/plugin-archives") for path in archived
    )
    source_names = {
        path.parent.name
        for path in (plugin_home / "huayue-skills" / "skills").glob("*/SKILL.md")
    }
    assert source_names == EXPECTED_SKILLS
    assert {
        path.parent.name
        for asset in assets
        if asset.category == "skills"
        for path in asset.root_dir.glob("*/SKILL.md")
    } == EXPECTED_SKILLS

    await manager.terminate_all()

    assert root.receipt().services == ()
    assert root.receipt().effects == ()
