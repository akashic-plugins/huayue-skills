# huayue-skills

Akashic personal skills bundle.

插件优先使用 Composition API v3 的 `core.skills` 能力登记整个 `skills/` catalog；迁移期保留 API v2 `skill_roots()`，只用于旧 Core 兼容和同输入行为等价验证。

```text
┌─────────────────────┐  inject core.skills  ┌──────────────────┐
│ huayue-skills Fiber │ ────────────────────▶ │ PluginSkills     │
└──────────┬──────────┘                       └────────┬─────────┘
           │ register("skills")                       │ freeze
           ▼                                          ▼
    plugin source tree                         generation catalog
```

Included skills:

- anthropic-diagram
- codex-usage
- gh-cli
- image-generation-nano
- opencli
- paper-explainer
- playwright-browser
- yt-dlp-downloader

## Install

```bash
python main.py plugin-install --source https://github.com/akashic-plugins/huayue-skills --marketplace github
```

Akashic 会自动加载插件，不需要重启。

## Update

在可编辑源码仓库中修改 `skills/`，完成验证并推送后，重新执行安装命令：

```text
┌─ 编辑 /mnt/data/coding/akashic-plugin/huayue-skills/skills/
├─ 提交并推送到 GitHub
├─ 再次执行 plugin-install
└─ Akashic watcher 自动热重载
```

不要直接修改 `~/.akashic-plugin/cache`；该目录只是安装产物。重复安装会更新代码，并保留插件 data。

## Notes

- This plugin only provides `skills/` through `core.skills`
- It does not provide MCP servers
- It does not provide lifecycle hooks
