# huayue-skills

Akashic personal skills bundle.

Included skills:

- anthropic-diagram
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

- This plugin only provides `skills/`
- It does not provide MCP servers
- It does not provide lifecycle hooks
