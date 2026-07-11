---
name: codex-usage
description: Install, query, update, and monitor local Codex token usage, model breakdowns, five-hour and weekly rate limits, reset credits, expiration times, and daily trends through the agent-first codex-usage CLI. Use when an agent needs machine-readable Codex usage data, when codex-usage may not be installed yet, when the local dashboard service must be started or inspected, or when sync and update health must be verified without scraping the web UI.
---

# Codex Usage

Use the CLI as the source of truth. Do not scrape the dashboard or read Codex JSONL files directly.

## Ensure installation

Always detect the CLI before the first operation:

```bash
if command -v codex-usage >/dev/null 2>&1; then
  codex-usage capabilities
else
  bash scripts/ensure-installed.sh
fi
```

Resolve `scripts/ensure-installed.sh` relative to this `SKILL.md`, not the user's current directory. The script:

1. Checks `git`, `node`, and `npm` without changing the machine.
2. Uses an authenticated GitHub CLI session for the private repository; if unavailable, reports `gh auth login` as the required action.
3. Clones `https://github.com/kachofugetsu09/codex-usage.git` into `${CODEX_USAGE_HOME:-$HOME/.local/share/codex-usage}` only when absent.
4. Refuses to overwrite an unrelated directory.
5. Runs the repository's audited `npm run setup` entrypoint.
6. Verifies `codex-usage capabilities` before reporting success.

If a required program is missing, stop and report the script's JSON error. Do not replace this flow with `curl | sh`, guessed package names, or copied install commands.

## Discover capabilities

Run this first when command details may have changed:

```bash
codex-usage capabilities
```

All data commands write JSON to stdout. Failures write JSON to stderr and return a non-zero exit code.

## Query data

Choose the narrowest command that answers the request:

```bash
codex-usage usage --range today
codex-usage limits
codex-usage resets
codex-usage trend --days 180
```

Use a complete snapshot when multiple areas are required:

```bash
codex-usage snapshot --range month --trend-days 365
```

Valid ranges are `today`, `week`, `month`, and `year`.

## Run continuously

Start the local Web and API service when the user requests monitoring, the dashboard, or five-minute synchronization:

```bash
codex-usage serve
```

The default address is `http://127.0.0.1:4317`. The process stays active and refreshes its persistent index every 300 seconds. Keep the process session alive; do not start duplicate instances on the same port.

Check readiness and synchronization state with:

```bash
codex-usage health
```

Treat `ready` as healthy, `syncing` as temporary, and `degraded` as requiring inspection of `lastError`.

## Update safely

When the user asks to update the tool, run:

```bash
codex-usage update
codex-usage serve
codex-usage health
```

The updater stops the old process, rejects dirty worktrees, fast-forwards from `origin/main`, rebuilds, and refreshes the CLI and Skill. Restart only when the updater returns `restartRequired: true`.

## Safety

The tool is read-only. `resets` reports reset credits but never consumes them. Do not call Codex's reset-consumption API unless a future user request explicitly authorizes that side effect.
