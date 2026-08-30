#!/usr/bin/env bash
# commandcode-quota.sh — 查询 Command Code (GOAT 等) 订阅用量
# 只读查询，不消费任何额度。输出 JSON 到 stdout，失败输出 JSON 到 stderr 并返回非零。
set -euo pipefail

KEY_FILE="${CMD_KEY_FILE:-/srv/data/services/akashic/state/workspace/plugin-data/commandcode/api_key}"
BASE="${CMD_API_BASE:-https://api.commandcode.ai}"
TIMEOUT=15

fail() {
  echo "{\"ok\":false,\"error\":\"$1\"}" >&2
  exit 1
}

command -v curl >/dev/null 2>&1 || fail "curl not found"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"
[[ -r "$KEY_FILE" ]] || fail "api key file not found: $KEY_FILE (向用户要 Studio → API keys 的新 key)"

KEY=$(cat "$KEY_FILE")

req() {
  curl -sS -m "$TIMEOUT" -H "Authorization: Bearer $KEY" -H "accept: application/json" "$BASE$1"
}

whoami=$(req "/alpha/whoami") || fail "whoami request failed"
if ! echo "$whoami" | grep -q '"success":true'; then
  fail "whoami failed: key invalid or rejected"
fi

credits=$(req "/alpha/billing/credits") || fail "credits request failed"
sub=$(req "/alpha/billing/subscriptions") || fail "subscriptions request failed"
summary=$(req "/alpha/usage/summary") || fail "usage summary request failed"

python3 - "$whoami" "$credits" "$sub" "$summary" <<'PY'
import json, sys

whoami, credits, sub, summary = (json.loads(x) for x in sys.argv[1:])
user = whoami.get("user", {}) or {}
c = credits.get("credits", {}) or {}
w = credits.get("windowLimits", {}) or {}
d = sub.get("data", {}) or {}
s = summary or {}

out = {
    "ok": True,
    "account": user.get("userName") or user.get("name"),
    "plan": d.get("planId"),
    "status": d.get("status"),
    "period": {"start": d.get("currentPeriodStart"), "end": d.get("currentPeriodEnd")},
    "credits": {
        "monthly": c.get("monthlyCredits"),
        "purchased": c.get("purchasedCredits"),
        "free": c.get("freeCredits"),
        "belowThreshold": c.get("belowThreshold"),
    },
    "windows": {
        "fiveHour": {
            "used": (w.get("fiveHour") or {}).get("used"),
            "cap": (w.get("fiveHour") or {}).get("cap"),
            "exceeded": (w.get("fiveHour") or {}).get("exceeded"),
            "resetAt": (w.get("fiveHour") or {}).get("resetAt"),
        },
        "weekly": {
            "used": (w.get("weekly") or {}).get("used"),
            "cap": (w.get("weekly") or {}).get("cap"),
            "exceeded": (w.get("weekly") or {}).get("exceeded"),
            "resetAt": (w.get("weekly") or {}).get("resetAt"),
        },
    },
    "usage": {
        "totalCount": s.get("totalCount"),
        "totalCost": s.get("totalCost"),
        "totalTokens": s.get("totalTokens"),
        "successRate": s.get("successRate"),
    },
}
print(json.dumps(out, ensure_ascii=False, indent=2))
PY
