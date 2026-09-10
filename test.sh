#!/usr/bin/env bash
# Gate for the design-craft pack. Runs before the pack has content, on purpose:
# every later milestone needs something to fail against.
#
#   ./test.sh
#
# Everything on this path is stdlib-only Python plus bash, so CI needs a stock
# interpreter and nothing else. No virtualenv, no Pillow, no browser.
#
# Skills are discovered by directory (skills/*/) and nothing is asserted about a
# set that is empty — M0 ships no skills. Because a check that cannot fail is not
# a gate, each check is also run against a deliberately broken fixture tree and
# required to exit non-zero. That is what makes this a gate at M0 rather than at
# whichever milestone first ships content.
set -uo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
command -v "$PY" >/dev/null 2>&1 || { echo "need python3" >&2; exit 2; }

pass=0; fail=0
ok()  { pass=$((pass+1)); printf '  ok   %s\n' "$1"; }
bad() { fail=$((fail+1)); printf '  FAIL %s\n' "$1"; }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/dc-test.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

echo "== discovery =="
skill_count=0
if [ -d "$DIR/skills" ]; then
  skill_count="$(find "$DIR/skills" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')"
fi
ok "skills discovered by directory ($skill_count present)"

echo ""
echo "== checks against the real tree =="
for c in check_contracts check_caps check_ledger; do
  if "$PY" "$DIR/scripts/$c.py" "$DIR" >/dev/null 2>&1; then
    ok "$c passes"
  else
    bad "$c passes"
    "$PY" "$DIR/scripts/$c.py" "$DIR" 2>&1 | sed 's/^/       /'
  fi
done

echo ""
echo "== each check can fail (deliberate breakages) =="

# 1. A contract edited in one home only. The frozen-contract rule exists because
#    dual-homed docs drift; this proves the drift is caught.
B1="$TMP/b1"; mkdir -p "$B1/docs" "$B1/scripts" "$B1/lib"
cp "$DIR/docs/EXECUTION-PLAN.md" "$B1/docs/"; cp "$DIR/lib/README.md" "$B1/lib/"
sed 's/check_caps\.py \[ROOT\]/check_caps.py [ROOT] [--strict]/' "$DIR/scripts/README.md" > "$B1/scripts/README.md"
if "$PY" "$DIR/scripts/check_contracts.py" "$B1" >/dev/null 2>&1; then
  bad "check_contracts fails when one contract home is edited alone"
else
  ok "check_contracts fails when one contract home is edited alone"
fi

# 2. A file pushed past its cap. Synthetic because M0 ships no skills — the cap
#    only means something once a SKILL.md exists to exceed it.
B2="$TMP/b2"; mkdir -p "$B2/skills/oversized"
"$PY" - "$B2/skills/oversized/SKILL.md" <<'PYEOF'
import sys
open(sys.argv[1], "w").write("x\n" * 200)
PYEOF
if "$PY" "$DIR/scripts/check_caps.py" "$B2" >/dev/null 2>&1; then
  bad "check_caps fails on a SKILL.md over 150 lines"
else
  ok "check_caps fails on a SKILL.md over 150 lines"
fi

# 3. Two of the pack's own rows claiming one phrase. Collisions between repos the
#    pack does not own are KNOWN, not failures — so the fixture uses our own repo
#    on both sides, which is the case the pack can actually fix.
B3="$TMP/b3"; mkdir -p "$B3/docs"
cat > "$B3/docs/TRIGGER-LEDGER.md" <<'LEDEOF'
| Object of attention | Owner | Repo | Claimed phrases |
|---|---|---|---|
| A described structure | `design-diagram` | `design-craft` | "draw a diagram", "sketch the flow" |
| Something else | `other-skill` | `design-craft` | "draw a diagram" |
LEDEOF
if "$PY" "$DIR/scripts/check_ledger.py" "$B3" >/dev/null 2>&1; then
  bad "check_ledger fails when two of our own rows claim one phrase"
else
  ok "check_ledger fails when two of our own rows claim one phrase"
fi

# 4. The same collision, but between repos the pack does not own: reported, not fatal.
B4="$TMP/b4"; mkdir -p "$B4/docs"
cat > "$B4/docs/TRIGGER-LEDGER.md" <<'LEDEOF'
| Object of attention | Owner | Repo | Claimed phrases |
|---|---|---|---|
| A rendered surface | `ux-audit` | `ux-audit-skill` | "UX review" |
| A source tree | `validate` | `project-starter-pack` | "UX review" |
LEDEOF
if "$PY" "$DIR/scripts/check_ledger.py" "$B4" >/dev/null 2>&1; then
  ok "check_ledger reports a collision owned elsewhere without failing"
else
  bad "check_ledger reports a collision owned elsewhere without failing"
fi

echo ""
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
