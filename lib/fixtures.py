"""The pack's fixture runner — the generic half of a fixture check.

Extracted from `ux-audit`'s `scripts/check_fixtures.py`, which remains the
reference implementation. The generic half is here: the directory walk,
`must_find` / `must_not_find`, `max_severity`, `max_findings`, score bounds,
baseline drift at +/-10, and the itemized failure list. **The skill-specific half
— how an expectation matches a finding — is injected by the caller**, because
that is the only part that knows what a finding looks like.

The caller owns the non-zero exit. This returns what failed and what to say; it
does not decide what that means for a process.

Stdlib only: this is on the gate path (shape spec Part 3.6) and may never gain a
dependency.

Contract (frozen, dual-homed in lib/README.md and the execution plan's Appendix A):

    run(fixture_root, match_predicate) -> (failures, notes)

`match_predicate(expectation, findings) -> finding | None` decides whether an
expectation is satisfied by any finding. A fixture with no audit output is
**skipped, not failed** — an un-run fixture is missing evidence, not evidence of
a problem.
"""
import json
from pathlib import Path

SEV_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
BASELINE_TOLERANCE = 10


def check_one(fixture_dir, match_predicate):
    """One fixture. Returns (failures, notes), or (None, [reason]) when skipped."""
    fixture_dir = Path(fixture_dir)
    expected = json.loads((fixture_dir / "expected.json").read_text(encoding="utf-8"))
    audit_path = fixture_dir / "audit" / "findings.json"
    if not audit_path.is_file():
        return None, [f"{fixture_dir.name}: no audit yet (skipped)"]

    data = json.loads(audit_path.read_text(encoding="utf-8"))
    findings = data.get("findings", [])
    scores = data.get("scores", {}) or {}
    fails, notes = [], []

    for exp in expected.get("must_find", []):
        hit = match_predicate(exp, findings)
        if hit:
            notes.append(f"  found: {exp['note']} -> {hit['id']}")
        else:
            fails.append(f"MISSED must-find: {exp['note']} "
                         f"(any of {exp['any_principles']})")

    # The must-NOT-find list is the point of a fixture suite: it is what makes a
    # manufactured finding fail, which a must-find list alone can never do.
    for exp in expected.get("must_not_find", []):
        hit = match_predicate(exp, findings)
        if hit:
            fails.append(f"FORBIDDEN hit: {exp['note']} -> {hit['id']} ({hit.get('issue')})")

    if "max_severity" in expected:
        cap = SEV_ORDER[expected["max_severity"]]
        for f in findings:
            if SEV_ORDER.get(f.get("severity"), 0) > cap:
                fails.append(f"SEVERITY over cap: {f.get('id')} is {f.get('severity')} "
                             f"(cap {expected['max_severity']})")

    if "max_findings" in expected and len(findings) > expected["max_findings"]:
        fails.append(f"TOO MANY findings: {len(findings)} > {expected['max_findings']}")

    overall = scores.get("overall")
    # The reference indexes `overall` directly; guarding None here is strictly more
    # defensive and cannot change the result on any fixture that records a score.
    if overall is not None:
        if "min_overall" in expected and overall < expected["min_overall"]:
            fails.append(f"SCORE low: overall {overall} < {expected['min_overall']}")
        if "max_overall" in expected and overall > expected["max_overall"]:
            fails.append(f"SCORE high: overall {overall} > {expected['max_overall']}")
    elif "min_overall" in expected or "max_overall" in expected:
        fails.append("SCORE missing: expected bounds but findings.json records no overall")

    base = expected.get("baseline_scores")
    if base:
        for k, v in base.items():
            got = scores.get(k)
            if got is None or abs(got - v) > BASELINE_TOLERANCE:
                fails.append(f"DRIFT: scores.{k} {got} vs baseline {v} "
                             f"(±{BASELINE_TOLERANCE})")
    elif base is None and "baseline_scores" in expected:
        notes.append("  baseline not recorded yet — drift check skipped")

    return fails, notes


def run(fixture_root, match_predicate):
    """Every fixture under `fixture_root`. Returns (failures, notes).

    `notes` carries the rendered report in order — one `PASS`/`FAIL`/`SKIP` line
    per fixture followed by that fixture's detail — so a caller can print it
    verbatim and reproduce the reference layout. `failures` is flat and
    fixture-qualified, so the caller can count it and choose its exit code.
    """
    root = Path(fixture_root)
    failures, notes = [], []
    for fdir in sorted(p for p in root.iterdir() if (p / "expected.json").is_file()):
        fails, fnotes = check_one(fdir, match_predicate)
        if fails is None:
            notes.append(f"SKIP {fnotes[0]}")
            continue
        notes.append(f"{'FAIL' if fails else 'PASS'} {fdir.name}")
        notes.extend(fnotes)
        for f in fails:
            notes.append(f"  !! {f}")
            failures.append(f"{fdir.name}: {f}")
    return failures, notes
