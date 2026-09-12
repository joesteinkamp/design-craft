#!/usr/bin/env python3
"""Prove lib/fixtures.py reproduces ux-audit's check_fixtures.py, then prove it can fail.

Usage: test_fixtures.py [UX_AUDIT_CHECKOUT]

Equivalence is the whole claim of M2: the generic half was *extracted*, not
rewritten, so the runner must produce byte-identical output to the reference on
all five shipped fixtures. Anything less and the extraction changed behaviour
while claiming not to.

The reference checkout is read-only. Every breakage is applied to a copy in a
temp directory — nothing is ever written to ux-audit.

Stdlib only.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib import fixtures  # noqa: E402

passed = failed = 0


def ok(msg):
    global passed
    passed += 1
    print(f"  ok   {msg}")


def bad(msg, detail=""):
    global failed
    failed += 1
    print(f"  FAIL {msg}")
    if detail:
        print("\n".join(f"       {l}" for l in detail.splitlines()[:12]))


def ux_match(exp, findings):
    """ux-audit's predicate, verbatim — the skill-specific half the caller injects."""
    for f in findings:
        if not set(exp["any_principles"]) & set(f.get("principles", [])):
            continue
        if "screen_index" in exp and f.get("screen_index") != exp["screen_index"]:
            continue
        return f
    return None


def render(root):
    """Reproduce the reference's stdout exactly, from run()'s return value."""
    failures, notes = fixtures.run(root, ux_match)
    out = "\n".join(notes)
    out += f"\n\n{len(failures)} failure(s)" if failures else "\n\nall fixture checks passed"
    return out + "\n", failures


def main():
    checkout = Path(sys.argv[1] if len(sys.argv) > 1
                    else os.environ.get("UX_AUDIT_CHECKOUT",
                                        Path.home() / "projects" / "ux-audit-skill"))
    if not (checkout / "fixtures").is_dir():
        print(f"  ok   equivalence skipped — no ux-audit checkout at {checkout}")
        print("\n1 passed, 0 failed")
        return 0

    ref = subprocess.run([sys.executable, "scripts/check_fixtures.py", "fixtures"],
                         cwd=checkout, capture_output=True, text=True)
    mine, _ = render(checkout / "fixtures")

    if mine == ref.stdout:
        ok(f"reproduces check_fixtures.py byte-for-byte on all shipped fixtures "
           f"({len(ref.stdout.splitlines())} lines)")
    else:
        import difflib
        diff = "\n".join(difflib.unified_diff(ref.stdout.splitlines(), mine.splitlines(),
                                              "reference", "lib/fixtures", lineterm=""))
        bad("reproduces check_fixtures.py byte-for-byte on all shipped fixtures", diff)

    # --- and it must be able to fail -------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "fixtures"
        shutil.copytree(checkout / "fixtures", work)

        # 1. A must_find deleted: the suite must notice the expectation is gone.
        target = next(d for d in sorted(work.iterdir())
                      if (d / "expected.json").is_file()
                      and json.loads((d / "expected.json").read_text()).get("must_find"))
        exp = json.loads((target / "expected.json").read_text())
        removed = exp["must_find"].pop(0)
        (target / "expected.json").write_text(json.dumps(exp))
        f1, _ = fixtures.run(work, ux_match)
        # Deleting an expectation cannot fail the run — it removes a requirement.
        # What must hold is that the found: line for it disappears.
        _, notes1 = fixtures.run(work, ux_match)
        if not any(removed["note"] in n for n in notes1):
            ok("a deleted must_find stops being reported as found")
        else:
            bad("a deleted must_find stops being reported as found")
        exp["must_find"].insert(0, removed)
        (target / "expected.json").write_text(json.dumps(exp))

        # 2. A must_find that can never match: the suite must FAIL.
        exp = json.loads((target / "expected.json").read_text())
        exp["must_find"].append({"any_principles": ["NOPE-99"],
                                 "note": "a principle no finding carries"})
        (target / "expected.json").write_text(json.dumps(exp))
        f2, _ = fixtures.run(work, ux_match)
        if any("MISSED must-find" in f for f in f2):
            ok("an unmatchable must_find fails the run")
        else:
            bad("an unmatchable must_find fails the run")

        # 3. A must_not_find that DOES match: the false-positive guard.
        shutil.rmtree(work); shutil.copytree(checkout / "fixtures", work)
        target = next(d for d in sorted(work.iterdir())
                      if (d / "audit" / "findings.json").is_file())
        data = json.loads((target / "audit" / "findings.json").read_text())
        principle = next(p for f in data["findings"] for p in f.get("principles", []))
        exp = json.loads((target / "expected.json").read_text())
        exp.setdefault("must_not_find", []).append(
            {"any_principles": [principle], "note": "injected forbidden principle"})
        (target / "expected.json").write_text(json.dumps(exp))
        f3, _ = fixtures.run(work, ux_match)
        if any("FORBIDDEN hit" in f for f in f3):
            ok("an injected must_not_find principle fails the run")
        else:
            bad("an injected must_not_find principle fails the run")

        # 4. A baseline moved past tolerance.
        shutil.rmtree(work); shutil.copytree(checkout / "fixtures", work)
        target = None
        for d in sorted(work.iterdir()):
            if not (d / "audit" / "findings.json").is_file():
                continue
            scores = json.loads((d / "audit" / "findings.json").read_text()).get("scores") or {}
            if scores.get("overall") is not None:
                target = d
                break
        if target is None:
            bad("a baseline moved by 11 fails the run (no fixture records a score)")
        else:
            scores = json.loads((target / "audit" / "findings.json").read_text())["scores"]
            exp = json.loads((target / "expected.json").read_text())
            exp["baseline_scores"] = {"overall": scores["overall"] + 11}
            exp.pop("min_overall", None); exp.pop("max_overall", None)
            (target / "expected.json").write_text(json.dumps(exp))
            f4, _ = fixtures.run(work, ux_match)
            if any("DRIFT" in f for f in f4):
                ok("a baseline moved by 11 fails the run (tolerance is ±10)")
            else:
                bad("a baseline moved by 11 fails the run (tolerance is ±10)")

        # 5. And 10 does not — the tolerance boundary is a decision, not an accident.
        exp["baseline_scores"] = {"overall": scores["overall"] + 10}
        (target / "expected.json").write_text(json.dumps(exp))
        f5, _ = fixtures.run(work, ux_match)
        if not any("DRIFT" in f for f in f5):
            ok("a baseline moved by exactly 10 does not fail (boundary is inclusive)")
        else:
            bad("a baseline moved by exactly 10 does not fail (boundary is inclusive)")

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
