# huayue-skills

Akashic 的个人技能集合。插件通过 `apply(ctx)` 向 `INSTALLED_ASSETS` 注册 `skills/`，登记随当前 Fiber 的 Effect 清理。身份来自 `plugin.py`，不再保留静态 Skill 声明或重复的 TOML 清单。

```text
┌──────────────────┐  register(ctx, "skills", "skills")  ┌──────────────────┐
│ huayue-skills    │ ───────────────────────────────────▶│ Assets provider  │
└──────────────────┘                                    └────────┬─────────┘
                                                                ▼
                                                  当前作用域的只读归档目录
```

Included skills:

- anthropic-diagram
- codex-usage（Codex + OpenCode Go 剩余额度查询，零安装直查）
- gh-cli
- image-generation-nano
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

- This plugin only registers the `skills/` catalog
- It does not provide MCP servers
- Asset registration is removed when its Fiber is disposed
