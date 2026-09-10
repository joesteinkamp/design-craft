#!/usr/bin/env python3
"""Fail when a file exceeds the line cap the shape spec sets for its kind.

Caps exist because a skill is loaded into a prompt: a SKILL.md nobody can read
in one pass is not progressive disclosure, it is a wall. Contract files are
uncapped by rule — a frozen CLI contract is reference, not runtime prompt.

Usage: check_caps.py [ROOT]        exit 1 with one line per file over cap
"""
import sys
from pathlib import Path

SKILL_MD_CAP = 150
CORPUS_CAP = 120
UNCAPPED = {"README.md", "CLAUDE.md"}   # contract and convention files


def lines(p):
    return len(p.read_text(encoding="utf-8", errors="replace").splitlines())


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    skills = root / "skills"
    over = []
    # Discovery is by directory. With no skills present there is nothing to cap,
    # and an empty set is a pass rather than an error — M0 ships no skills.
    for skill in sorted(p for p in skills.glob("*") if p.is_dir()) if skills.is_dir() else []:
        sm = skill / "SKILL.md"
        if sm.is_file() and lines(sm) > SKILL_MD_CAP:
            over.append(f"{sm.relative_to(root)}: {lines(sm)} lines > {SKILL_MD_CAP}")
        for f in sorted((skill / "references").rglob("*.md")) if (skill / "references").is_dir() else []:
            if f.name in UNCAPPED:
                continue
            if lines(f) > CORPUS_CAP:
                over.append(f"{f.relative_to(root)}: {lines(f)} lines > {CORPUS_CAP}")
    for o in over:
        print(f"  {o}")
    if over:
        print(f"\ncheck_caps: {len(over)} file(s) over cap")
        return 1
    print("check_caps: every file within cap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
