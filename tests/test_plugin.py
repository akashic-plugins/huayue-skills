from __future__ import annotations

import hashlib
import shutil
import stat
from pathlib import Path

import pytest

import plugin as plugin_module
from agent.plugin_composition import (
    CompositionRoot,
    Context,
    PluginRuntime,
)
from agent.plugin_composition.assets import INSTALLED_ASSETS
from agent.plugins.composable import ComposablePlugin
from agent.plugins.manager import PluginManager
from agent.plugins.selection import PluginSelection
from agent.plugins.snapshot import bind_runtime_snapshot, reset_runtime_snapshot
from agent.plugins.static_manifest import load_static_plugin_manifest
from bus.event_bus import EventBus
from plugins.assets import plugin as assets_plugin

PLUGIN_ROOT = Path(__file__).parents[1]
ASSETS_ROOT = Path(assets_plugin.__file__).resolve().parents[0]
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


def _runtime(plugin_id: str, plugin_dir: Path, tmp_path: Path) -> PluginRuntime:
    return PluginRuntime(
        plugin_id=plugin_id,
        generation_id="test-generation",
        plugin_dir=plugin_dir,
        data_dir=tmp_path / "plugin-data" / plugin_id,
        workspace=tmp_path / "workspace",
        config={},
    )


@pytest.mark.asyncio
async def test_v3_skills_preserve_source_tree_and_cleanup_receipt(
    tmp_path: Path,
) -> None:
    plugin = ComposablePlugin.from_module(plugin_module, load_static_plugin_manifest(PLUGIN_ROOT))
    source_roots = (PLUGIN_ROOT / "skills",)
    root = CompositionRoot("huayue-skills-parity")

    _ = await root.mount(
        assets_plugin.apply, name="assets",
        runtime=_runtime("assets", ASSETS_ROOT, tmp_path),
    )
    _ = await root.mount(
        plugin_module.apply,
        name="huayue-skills",
        inject=plugin.inject,
        runtime=_runtime("huayue-skills", PLUGIN_ROOT, tmp_path),
    )

    receipt = root.receipt()
    assert "huayue-skills:asset:skills:skills" in receipt.effects
    assert receipt.ready is True
    assert receipt.external_effects == ()

    await root.dispose()

    assert root.receipt().effects == ()


def test_static_manifest_matches_pure_v3_module() -> None:
    manifest = load_static_plugin_manifest(PLUGIN_ROOT)

    assert manifest.name == plugin_module.name == "huayue-skills"
    assert manifest.version == plugin_module.version == "2.0.0"
    assert manifest.api_version == plugin_module.api_version == 3
    assert not hasattr(plugin_module, "HuayueSkillsPlugin")


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
    _ = shutil.copytree(
        ASSETS_ROOT,
        plugin_home / "assets",
        ignore=shutil.ignore_patterns(
            ".git",
            ".pytest_cache",
            "__pycache__",
        ),
    )
    workspace = tmp_path / "workspace"
    manager = PluginManager(
        [plugin_home],
        event_bus=EventBus(),
        workspace=workspace,
        installed_cache_root=tmp_path / "plugin-home" / "cache",
    )
    PluginSelection(workspace).initialize()
    await manager.load_all()

    try:
        generation = manager.generation("huayue-skills")
        snapshot = manager.current_snapshot
        assert generation is not None and snapshot is not None
        assert isinstance(generation.instance, ComposablePlugin)
        root = snapshot.composition_root
        assert root is not None
        lease = manager._snapshot_store.lease()  # pyright: ignore[reportPrivateUsage]
        token = bind_runtime_snapshot(lease)
        try:
            assets = root.context.require(INSTALLED_ASSETS)()
        finally:
            reset_runtime_snapshot(token)
            await lease.release()
        selected = [item for item in assets if item.owner_id == "huayue-skills"]
        assert len(selected) == 1
        archived = selected[0].root_dir
        assert archived.is_relative_to(workspace / "runtime/plugin-archives")
        assert _tree_receipt((archived,)) == _tree_receipt((PLUGIN_ROOT / "skills",))
        source_names = {
            path.parent.name
            for path in (plugin_home / "huayue-skills" / "skills").glob("*/SKILL.md")
        }
        assert source_names == EXPECTED_SKILLS
    finally:
        await manager.terminate_all()

    assert root.receipt().effects == ()
