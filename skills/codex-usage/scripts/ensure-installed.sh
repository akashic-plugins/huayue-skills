#!/usr/bin/env bash
set -euo pipefail

REPOSITORY="https://github.com/kachofugetsu09/codex-usage.git"
REPOSITORY_SLUG="kachofugetsu09/codex-usage"

if command -v codex-usage >/dev/null 2>&1; then
  codex-usage capabilities >/dev/null
  printf '{"status":"ready","installed":true,"cli":"%s"}\n' "$(command -v codex-usage)"
  exit 0
fi

INSTALL_ROOT="${CODEX_USAGE_HOME:-${AKA_PLUGIN_DATA_DIR:-}}"
if [[ -z "$INSTALL_ROOT" ]]; then
  printf '{"error":{"message":"缺少安装目录","action":"设置 CODEX_USAGE_HOME 或 AKA_PLUGIN_DATA_DIR"}}\n' >&2
  exit 1
fi
INSTALL_DIR="${CODEX_USAGE_HOME:-$AKA_PLUGIN_DATA_DIR/codex-usage}"

for dependency in git node npm; do
  if ! command -v "$dependency" >/dev/null 2>&1; then
    printf '{"error":{"message":"缺少安装依赖: %s","required":["git","node","npm"]}}\n' "$dependency" >&2
    exit 1
  fi
done

if [[ -e "$INSTALL_DIR" && ! -d "$INSTALL_DIR/.git" ]]; then
  printf '{"error":{"message":"安装目录已存在但不是 codex-usage Git 仓库","path":"%s"}}\n' "$INSTALL_DIR" >&2
  exit 1
fi

if [[ ! -d "$INSTALL_DIR/.git" ]]; then
  mkdir -p "$(dirname "$INSTALL_DIR")"
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    gh repo clone "$REPOSITORY_SLUG" "$INSTALL_DIR" -- --depth 1 >&2
  else
    printf '{"error":{"message":"私有仓库需要 GitHub 认证","action":"安装 GitHub CLI 后运行 gh auth login，再重试"}}\n' >&2
    exit 1
  fi
fi

(cd "$INSTALL_DIR" && npm run setup >/dev/null)
codex-usage capabilities >/dev/null
printf '{"status":"ready","installed":true,"repository":"%s","cli":"%s","next":"codex-usage serve"}\n' "$INSTALL_DIR" "$(command -v codex-usage)"
