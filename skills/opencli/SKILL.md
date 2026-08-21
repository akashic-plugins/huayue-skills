---
name: opencli
description: OpenCLI 适配器操作。用 opencli 命令操作 B站、GitHub、DeepSeek 平台、HackerNews、V2EX 等站点，获取结构化数据。触发词：opencli, 用 opencli, 查 B站, B站热榜, bilibili, 查 GitHub, GitHub 通知, DeepSeek 用量, hackernews, v2ex, opencli browser
metadata: {"akashic": {"always": false, "requires": {"bins": ["opencli"], "env": []}}}
---

# OpenCLI 使用指南

基于官方 opencli-usage + opencli-browser 改造，详见 references/。

## 核心约束（优先级最高）

1. **所有需要 Browser Bridge 的 adapter 命令必须追加** `--window background --site-session persistent --keep-tab true`，不得因为命令能运行就省略；只有 `PUBLIC/LOCAL` 策略可以不加
2. **优先用 adapter 命令**（`opencli <site> <command>`），零 Token 消耗；跑不通才退到 browser
3. **结构化输出** `-f json`，不要硬编码 adapter 列表——用 `opencli list -f json` 查
4. 策略标签：`PUBLIC` 无浏览器要求；`COOKIE/INTERCEPT/UI` 需要 Browser Bridge 插件

## 花月环境的浏览器所有权

```text
┌─ /usr/bin/chromium → ~/.config/chromium/Default
│  ├─ 持有花月哥哥的真实登录态与 OpenCLI 扩展
│  └─ OpenCLI Adapter 常驻窗口应位于 Hyprland special:opencli
└─ cloakbrowser.service → ~/.cloakbrowser/profile
   └─ 独立 CDP 浏览器，不持有 OpenCLI 扩展；不要用于 OpenCLI 登录态任务
```

- `--window background` 只表示 Chrome API 不主动聚焦，**不保证 Hyprland 不把新窗口映射到当前 workspace**。
- 优先复用已经位于 `special:opencli` 的常驻 `OpenCLI Adapter` 窗口；adapter 命令使用 `--window background --site-session persistent --keep-tab true`。
- 执行不熟悉的 adapter 命令前先读 `opencli <site> <command> --help -f json`。只要 `browser_common_options` 中出现 `window`、`site-session`、`keep-tab`，上述三个参数就是强制参数。
- 不要为了修复 Bridge 断连启动独立 profile、复制 cookie、删除 `Singleton*`，也不要改动 `~/.config/chromium`。
- 不要把“daemon 在线”当成“浏览器可用”；Browser Bridge 健康必须由 `opencli doctor` 的 Extension 与 Connectivity 同时为 OK 证明。

## 常用站点速查

### 公开数据（不需要浏览器）

```bash
opencli hackernews top -f json --limit 10
opencli v2ex hot -f json --limit 10
opencli arxiv recent --category cs.AI -f json --limit 10
opencli reddit hot -r programming -f json --limit 3
opencli 36kr hot -f json --limit 10
opencli wttr weather -l "Beijing" -f json
opencli producthunt today -f json --limit 10
```

### 登录态（走 Browser Bridge 自动复用你的会话）

```bash
# B站
opencli bilibili hot -f json --limit 10 --window background --site-session persistent --keep-tab true
opencli bilibili search "<关键词>" -f json --limit 10 --window background --site-session persistent --keep-tab true
opencli bilibili video "<BVID>" -f json --window background --site-session persistent --keep-tab true
opencli bilibili history -f json --window background --site-session persistent --keep-tab true
opencli bilibili me -f json --window background --site-session persistent --keep-tab true
opencli bilibili whoami -f json --window background --site-session persistent --keep-tab true

# GitHub
opencli github whoami -f json --window background --site-session persistent --keep-tab true
# 其他能力先查询当前版本，禁止沿用旧命令名
opencli github --help -f json

# DeepSeek 用量（两步：打开页面 → 提取）
opencli browser --window background akashic open "https://platform.deepseek.com/usage"
opencli browser --window background akashic extract

# YouTube
opencli youtube video "<id>" -f json
opencli youtube search "<关键词>" -f json --limit 10
```

### Browser 操作（adapter 不够用时）

```
opencli browser --window background <session> <command>
```
核心命令：`bind` `unbind` `open` `state` `extract` `click` `type` `select` `find` `eval` `screenshot` `network`

每次 action 前先 `state` 或 `find` 获取目标，用数字 ref 而非 CSS 选择器。
Session 用 stable 名称。一次性 browser session 用完执行 `close`；不要关闭位于 `special:opencli` 的 adapter 常驻窗口或用于保持 Bridge 在线的持久 site session。`unbind` 只适合绑定用户标签页的场景。
详见 references/opencli-browser.SKILL.md。

## 登录态维护

- `opencli auth status` 查看各站登录态
- 登录态通过 Browser Bridge 自动复用，哪个站掉了你登一次就行
- 不用 `login` 命令——你有插件不需要

### Bridge 断连诊断

1. 运行 `opencli doctor`，分别记录 Daemon、Extension、Connectivity。
2. 若 Daemon OK、Extension MISSING，检查 `/usr/bin/chromium` 是否正以真实 Default profile 运行；不要被 9222 上的 CloakBrowser 进程误导。
3. 若真实 Chromium 未运行，明确报告“真实 profile 浏览器未启动/常驻窗口丢失”，不要声称无头 Chromium 天然不能加载扩展。
4. 若真实 Chromium 在运行但扩展仍断连，再执行一次 `opencli daemon restart` 并重新运行 `opencli doctor`；仍失败则保留原始错误，不静默改用独立 profile。
5. PUBLIC/LOCAL adapter 不依赖 Bridge；只有 COOKIE/INTERCEPT/UI 和 `opencli browser` 必须在 doctor 绿色后执行。

## 注意事项

- 所有 `browser` 命令都用 `opencli browser --window background <session> <command>`；不要把 `--window` 放在 leaf command 后面
- adapter 与 `browser` namespace 的参数位置不同：adapter 的后台参数放在 leaf command 后。错误：`opencli bilibili history -f json`；正确：`opencli bilibili history -f json --window background --site-session persistent --keep-tab true`
- adapter 报错时先试 `opencli <site> --help` 或加 `-v`；官方有 autofix 机制（详见 references）
- 大型页面 extract 后读 content 字段，内容超长时分页
- 不要做让花月哥哥不开心的事
