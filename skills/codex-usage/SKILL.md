---
name: codex-usage
description: 查询本机 Codex 与 OpenCode Go 订阅的剩余额度（Rate Limit 余量、重置时间、Reset 次数、计划类型）。当用户问"Codex 额度/用量还剩多少"、"opencode-go 还能用多久"、"5 小时限制还有多少"、"订阅快满了没"、"rate limit 状态"、"查一下 token 限额"时使用。零安装，直接读本机标准登录文件查询。
---

# Codex & OpenCode Go 额度查询

直接查询本机两条订阅的**剩余额度**。只读，不需要安装任何 CLI 或服务，不读聊天记录、不做任何写操作。

## 数据源（本机标准位置，登录过就有）

```
Codex:       ~/.codex/auth.json（OAuth 登录态）+ codex app-server JSON-RPC
             account/rateLimits/read
OpenCode Go: ~/.local/share/opencode/auth.json（Go API key）+ GET
             https://opencode.ai/zen/go/v1/usage（官方 usage 端点）
```

两个文件都是本机 CLI 登录后自动生成的，不涉及隐私外传；查询只向 opencode.ai 官方端点发一次读请求。

## 执行

脚本相对本 SKILL.md 位于 `scripts/usage_query.py`，用系统 python3 运行：

```bash
python3 scripts/usage_query.py all        # 两个源都查
python3 scripts/usage_query.py codex      # 只查 Codex
python3 scripts/usage_query.py opencode-go  # 只查 OpenCode Go
```

返回 JSON。任何源失败时对应字段为 `{"error": "..."}`，且整体退出码非 0。

## 汇报格式（重要）

**以"剩余"为口径**，不主动报"用了多少"：

```text
Codex (Pro):
  周窗口：剩 57% · 重置 08-18 09:16 · Reset 次数 0

OpenCode Go:
  5 小时：剩 92% · 重置 08-13 05:56
  周窗口：剩 84% · 重置 08-17 08:00
  月窗口：剩 42% · 重置 08-19 17:25
```

- `remaining_percent` 是剩余百分比（100 - used）。
- `resets_at_local` 是重置的本地时间。
- 用户如果追问"用了多少"，再报 `used_percent`。
- 只有窗口接近耗尽（剩余 < 20%）或 `status != ok`、`reached` 非空时，才提醒一句需要注意，不要每次渲染警告。

## 边界

- Codex 需要 `codex` CLI 可执行（`~/.local/bin/codex` 或 PATH）；找不到时报错。
- 没有对应登录文件时直接报"未登录"，不要编数据。
- 脚本只读：不消费 Reset credits，不修改任何配置。
