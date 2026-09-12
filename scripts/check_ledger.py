#!/usr/bin/env python3
"""Fail when two skills claim the same trigger phrase.

The routing decision (DESIGN-PLAN.md D2) is ledger-first: a row per object of
attention, naming its owner and the phrases it claims. The ledger's whole value is
that a collision is a failing test rather than a judgement call — so this fails on
a phrase claimed twice, and on a description carrying a phrase the ledger does not
list.

Collisions between repositories the pack does not own are reported as KNOWN and do
not fail: the pack cannot resolve them, and failing on them would make the gate
permanently red for something outside its control.

Usage: check_ledger.py [ROOT]        exit 1 with one line per real collision
"""
import re
import sys
from pathlib import Path

LEDGER = "docs/TRIGGER-LEDGER.md"
OWN_REPO = "design-craft"
KNOWN_HEADING = "## Known collisions"


def rows(text):
    """Parse the pipe table: object | owner | repo | phrases."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or "---|" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[1].lower() == "owner":
            continue
        phrases = [p.strip().strip("`").strip('"').lower()
                   for p in re.split(r",(?![^(]*\))", cells[3]) if p.strip()]
        out.append({"object": cells[0], "owner": cells[1].strip("`"),
                    "repo": cells[2].strip("`"), "phrases": phrases})
    return out


def known_rows(text):
    """Rows of the Known-collisions table: shared term | owner A | owner B | note.

    These collide on a concept rather than a literal phrase — "audit" means a
    rendered surface to one skill and a source tree to another — so the duplicate
    check above cannot see them. They are declared instead, and reported, because
    a collision nobody can act on still has to be visible to whoever adds the
    next skill.
    """
    start = text.find(KNOWN_HEADING)
    if start == -1:
        return []
    nxt = text.find("\n## ", start + len(KNOWN_HEADING))
    return rows(text[start:nxt if nxt != -1 else len(text)])


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    lp = root / LEDGER
    # The ledger lands in M1. Its absence before then is not a failure — but once
    # it exists it is checked, so nothing can add a colliding row unnoticed.
    if not lp.is_file():
        print(f"check_ledger: no {LEDGER} yet (written in M1) — nothing to check")
        return 0

    entries = rows(lp.read_text(encoding="utf-8"))
    if not entries:
        print(f"check_ledger: {LEDGER} has no parsable rows", file=sys.stderr)
        return 2

    declared = known_rows(lp.read_text(encoding="utf-8"))
    entries = [e for e in entries if e not in declared]
    seen, failures, known = {}, [], []
    for d in declared:
        known.append(f'{d["object"]} — {d["owner"]} vs {d["repo"]} (declared, owned elsewhere)')
    for e in entries:
        for ph in e["phrases"]:
            if ph in seen:
                prev = seen[ph]
                pair = sorted([prev["repo"], e["repo"]])
                # Ours-vs-ours, or ours-vs-theirs, is ours to fix. Theirs-vs-theirs
                # is not, and is logged instead.
                if OWN_REPO in pair:
                    failures.append(
                        f'phrase claimed twice: "{ph}" by {prev["owner"]} ({prev["repo"]}) '
                        f'and {e["owner"]} ({e["repo"]})')
                else:
                    known.append(f'"{ph}" — {prev["owner"]} ({prev["repo"]}) vs {e["owner"]} ({e["repo"]})')
            else:
                seen[ph] = e

    for k in known:
        print(f"  KNOWN  {k}")
    for f in failures:
        print(f"  FAIL   {f}")
    print("")
    if failures:
        print(f"check_ledger: {len(failures)} collision(s) the pack owns, "
              f"{len(known)} known and owned elsewhere")
        return 1
    print(f"check_ledger: {len(entries)} row(s), no collision the pack owns "
          f"({len(known)} known, owned elsewhere)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
