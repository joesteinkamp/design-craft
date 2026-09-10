#!/usr/bin/env python3
"""Fail when a scripts/README.md and Appendix A of the execution plan disagree.

The CLI contracts are dual-homed on purpose: they live in docs/EXECUTION-PLAN.md
so a reader planning work sees them, and in the owning scripts/README.md so a
reader running the code sees them. Dual-homed documentation drifts unless
something compares the copies, which is what this does — in both directions, so
adding a line to one copy alone fails just as loudly as editing one.

Usage: check_contracts.py [ROOT]        exit 1 with one line per disagreement
"""
import re
import sys
from pathlib import Path

PLAN = "docs/EXECUTION-PLAN.md"
# Each entry: the plan's subsection heading, and the README that must match it.
PAIRS = [("### Pack-level — `scripts/README.md`", "scripts/README.md"),
         ("### `lib/` — `lib/README.md`", "lib/README.md")]


def fenced(text):
    """Signature lines inside ``` fences, in order, comments and padding stripped."""
    out = []
    for block in re.findall(r"^```[^\n]*\n(.*?)^```", text, re.M | re.S):
        for line in block.splitlines():
            line = line.split("#")[0].strip()
            if line:
                out.append(" ".join(line.split()))
    return out


def section(text, heading):
    """The plan text from one `###` heading up to the next one."""
    start = text.find(heading)
    if start == -1:
        return None
    nxt = text.find("\n### ", start + len(heading))
    return text[start:nxt if nxt != -1 else len(text)]


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    plan_path = root / PLAN
    if not plan_path.is_file():
        print(f"check_contracts: no {PLAN}", file=sys.stderr)
        return 2
    plan = plan_path.read_text(encoding="utf-8")

    errors = []
    for heading, readme in PAIRS:
        sec = section(plan, heading)
        rp = root / readme
        # A pair is only checked once both homes exist: lib/README.md lands with
        # lib/, and demanding it earlier would fail the gate for absent work.
        if sec is None and not rp.is_file():
            continue
        if sec is None:
            errors.append(f"{readme}: exists, but {PLAN} has no section {heading!r}")
            continue
        if not rp.is_file():
            errors.append(f"{readme}: missing, but {PLAN} documents it at {heading!r}")
            continue
        want, got = fenced(sec), fenced(rp.read_text(encoding="utf-8"))
        for line in want:
            if line not in got:
                errors.append(f"{readme}: missing contract present in {PLAN}: {line}")
        for line in got:
            if line not in want:
                errors.append(f"{readme}: contract not in {PLAN}: {line}")

    for e in errors:
        print(f"  {e}")
    if errors:
        print(f"\ncheck_contracts: {len(errors)} disagreement(s). "
              "The contracts are frozen — change both homes in one commit, or neither.")
        return 1
    print("check_contracts: contract homes agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
