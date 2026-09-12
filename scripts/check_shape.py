#!/usr/bin/env python3
"""Verify a skill directory against the mandatory parts of the shape spec.

Usage: check_shape.py SKILL_DIR [--spec SKILL-SHAPE.md]

Exit 1 with one line per violation, each naming the spec part it breaks.
Conditional parts are checked only when their triggering condition is present —
a skill with no corpus is never asked for a `_format.md`.

This is the brief's acceptance test mechanised: it must exit 0 against an
unmodified `ux-audit`. If it fails there, **the spec is wrong and gets corrected**
— the skill is not edited to fit. That direction is the whole point, and it is
only honest while `ux-audit` lives in its own repository (decision D4), where the
spec's author cannot quietly edit the thing the spec is measured against.

Stdlib only: this is on the gate path.
"""
import json
import sys
from pathlib import Path

SKILL_MD_CAP = 150
CORPUS_CAP = 120
# A contract file sits beside the corpus but is not corpus: it states the parser
# contract rather than carrying entries, so the corpus cap does not apply to it.
NOT_CORPUS = {"_format.md", "README.md"}


def lines(p):
    return len(p.read_text(encoding="utf-8", errors="replace").splitlines())


def has_frontmatter(p):
    try:
        with p.open(encoding="utf-8", errors="replace") as fh:
            return fh.readline().strip() == "---"
    except OSError:
        return False


def frontmatter(p):
    out, started = {}, False
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip() == "---":
            if started:
                break
            started = True
            continue
        if started and ":" in line and not line.startswith((" ", "\t", "#")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def check(skill: Path):
    bad, notes = [], []

    # --- Part 1 — SKILL.md, the runtime prompt (mandatory) ------------------
    sm = skill / "SKILL.md"
    if not sm.is_file():
        bad.append("1: no SKILL.md — a layer-3 skill is invoked by its runtime prompt")
        return bad, notes                      # nothing else is meaningful without it
    n = lines(sm)
    if n > SKILL_MD_CAP:
        bad.append(f"1.4: SKILL.md is {n} lines, cap is {SKILL_MD_CAP}")
    fm = frontmatter(sm)
    if not fm.get("description"):
        bad.append("1.1: SKILL.md frontmatter has no `description` — the trigger surface")
    if not fm.get("name"):
        bad.append("1: SKILL.md frontmatter has no `name`")

    # --- Part 2 — references/, in two kinds --------------------------------
    refs = skill / "references"
    if not refs.is_dir():
        bad.append("2.2: no references/ — every skill has at least an output contract")
    else:
        contracts = [p for p in refs.glob("*.md") if p.name not in NOT_CORPUS]
        if not contracts:
            bad.append("2.2: references/ has no contract file at its root (mandatory)")
        # The corpus is conditional. Detect it as a subdirectory of markdown that
        # carries frontmatter — that is what makes a file registry-generating.
        corpus_dirs = [d for d in refs.iterdir()
                       if d.is_dir() and any(has_frontmatter(f)
                                             for f in d.glob("*.md") if f.name not in NOT_CORPUS)]
        for d in corpus_dirs:
            if not (d / "_format.md").is_file():
                bad.append(f"2.3: {d.name}/ is a corpus but has no _format.md (parser contract)")
            for f in sorted(d.glob("*.md")):
                if f.name in NOT_CORPUS:
                    continue                    # 2.6: the cap is corpus-only
                ln = lines(f)
                if ln > CORPUS_CAP:
                    bad.append(f"2.6: {d.name}/{f.name} is {ln} lines, corpus cap is {CORPUS_CAP}")
        if corpus_dirs and not list(refs.rglob("registry.json")):
            bad.append("2.4: a corpus exists but no generated registry.json")

    # --- Part 3 — scripts/ --------------------------------------------------
    scripts = skill / "scripts"
    if not scripts.is_dir():
        bad.append("3: no scripts/ — 3.3 and 3.4 are mandatory")
    else:
        if not (scripts / "README.md").is_file():
            bad.append("3.5: scripts/ has no README.md (frozen, dual-homed CLI contracts)")
        py = [p.name for p in scripts.glob("*.py")]
        if not any(p.startswith("validate") for p in py):
            bad.append("3.3: no output validator in scripts/ (validate*.py)")
        if not any("fixture" in p and p.startswith("check") for p in py):
            bad.append("3.4: no fixture checker in scripts/ (check*fixture*.py)")

    # --- Part 4 — fixtures/ (mandatory) ------------------------------------
    fx = skill / "fixtures"
    cases = sorted(d for d in fx.iterdir() if d.is_dir()) if fx.is_dir() else []
    expected = [d / "expected.json" for d in cases if (d / "expected.json").is_file()]
    if not fx.is_dir():
        bad.append("4: no fixtures/ — a skill without fixtures cannot be regression-tested")
    elif not expected:
        bad.append("4.1: fixtures/ has no case carrying an expected.json")
    else:
        clean = 0
        for e in expected:
            try:
                data = json.loads(e.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                bad.append(f"4.1: {e.parent.name}/expected.json is unreadable ({exc.__class__.__name__})")
                continue
            if "must_find" not in data:
                bad.append(f"4.2: {e.parent.name}/expected.json has no must_find")
            if "must_not_find" not in data:
                bad.append(f"4.2: {e.parent.name}/expected.json has no must_not_find — "
                           "the must-not-find list is what makes false positives fail")
            if not data.get("must_find"):
                clean += 1
        # 4.6 is PROPOSED in the spec, not confirmed, so it reports rather than fails.
        if clean == 0:
            notes.append("4.6 (proposed): no clean control fixture — nothing forces "
                         "false positives to fail")

    # --- Part 13 — the maintainer's conventions doc (mandatory) ------------
    if not ((skill / "CLAUDE.md").is_file() or (skill / "CONVENTIONS.md").is_file()):
        bad.append("13: no CLAUDE.md or CONVENTIONS.md — the maintainer contract, "
                   "distinct from the runtime prompt")

    return bad, notes


def main():
    args = [a for a in sys.argv[1:]]
    spec = None
    if "--spec" in args:
        i = args.index("--spec")
        try:
            spec = args[i + 1]
        except IndexError:
            print("check_shape: --spec needs a path", file=sys.stderr)
            return 2
        del args[i:i + 2]
    if len(args) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2

    skill = Path(args[0])
    if not skill.is_dir():
        print(f"check_shape: {skill} is not a directory", file=sys.stderr)
        return 2
    if spec and not Path(spec).is_file():
        print(f"check_shape: no spec at {spec}", file=sys.stderr)
        return 2

    bad, notes = check(skill)
    for n in notes:
        print(f"  NOTE {n}")
    for b in bad:
        print(f"  FAIL part {b}")
    print("")
    if bad:
        print(f"check_shape: {skill.name} breaks {len(bad)} mandatory part(s). "
              "If the skill is right, the spec is wrong — correct the spec.")
        return 1
    print(f"check_shape: {skill.name} satisfies every mandatory part"
          + (f" ({len(notes)} note(s))" if notes else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
