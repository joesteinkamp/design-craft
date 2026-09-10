# `lib/` — shared library, frozen contracts

Dual-homed with Appendix A of [`docs/EXECUTION-PLAN.md`](../docs/EXECUTION-PLAN.md), under the
same rule: **change both in the same commit or don't change them.** These are library entry
points, not CLIs — the caller owns the exit code.

Both are **(proposed)**: the scripts land in later milestones and the contracts may change
freely until then. `lib/` exists at M0 so the export path (M4) has something to copy, and so
these contracts have a home to be checked against.

```
fixtures.run(fixture_root, match_predicate) -> (failures, notes)   # (proposed, M2)
```
Library entry point, not a CLI. Reproduces `ux-audit`'s `check_fixtures.py` semantics:
`must_find` / `must_not_find` / `max_severity` / `max_findings` / `min_overall` / `max_overall`
/ `baseline_scores` at ±10. A fixture with no audit output is skipped, not failed. The caller
supplies the match predicate and owns the non-zero exit.

```
registry.build(source_dir, schema) -> dict                          # (proposed, M3)
```
Frontmatter + three-column table parse, `sys.exit` on a duplicate ID, a missing required
frontmatter key, an invalid enum value, or an empty source set. `schema` carries the caller's
vocabulary — its valid categories, its ID pattern, its required keys, and its exclusion marker.
