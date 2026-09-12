# TODO-skill-name scripts — frozen CLI contracts

**Dual-homed and frozen** (Part 3.5). These contracts live here and in Appendix A of
`docs/EXECUTION-PLAN.md`. **Change both in the same commit or neither** —
`scripts/check_contracts.py` compares them in both directions.

A contract is `(proposed)` until its script lands and may change freely until then; it
freezes on that script's first commit.

**Everything here is stdlib only** (Part 3.6). The gate path may never gain a dependency —
breaking that breaks CI for every skill in the pack, not just this one.

```
validate_output.py OUTPUT_FILE          # (proposed, TODO)
check_fixtures.py [FIXTURE_ROOT]        # (proposed, TODO)
```

`validate_output.py` enforces `references/output-contract.md` and the consistency constraints
in `references/rubric.md`, exiting 1 with itemized errors (Parts 3.3, 6.5).
`check_fixtures.py` runs every fixture and exits non-zero on any failure (Part 3.4); from M2
it delegates to the pack's shared `lib/fixtures.py` rather than reimplementing it.
