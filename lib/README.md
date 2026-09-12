# `lib/` — shared library, frozen contracts

Dual-homed with Appendix A of [`docs/EXECUTION-PLAN.md`](../docs/EXECUTION-PLAN.md), under the
same rule: **change both in the same commit or don't change them.** These are library entry
points, not CLIs — the caller owns the exit code.

`fixtures.run` is **frozen** — it landed in M2. `registry.build` is still **(proposed)** and may
change freely until M3, per the two-consumers rule: nothing is extracted into `lib/` until a
second consumer proves the abstraction is real.

```
fixtures.run(fixture_root, match_predicate) -> (failures, notes)   # frozen, M2
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
