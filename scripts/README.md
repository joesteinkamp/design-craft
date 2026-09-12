# Pack-level scripts — frozen CLI contracts

**These contracts are dual-homed and frozen.** They live here and in Appendix A of
[`docs/EXECUTION-PLAN.md`](../docs/EXECUTION-PLAN.md). **Change both in the same commit or
don't change them** — `check_contracts.py` fails the gate when the two copies disagree, in
either direction, so adding a line here alone fails as loudly as editing one.

A contract is **(proposed)** until the script it describes lands, and may change freely until
then. It freezes on that script's first commit. Every script here is stdlib-only, and the ones
on the gate path may never gain a dependency — CI runs on a stock Python with no virtualenv.

```
check_shape.py SKILL_DIR [--spec SKILL-SHAPE.md]        # frozen, M1
```
Verifies a skill directory against the mandatory parts of the shape spec. Exit 1 with one line
per violation, naming the spec part number. Conditional parts are checked only when the
triggering condition is present — a skill with no corpus is not asked for `_format.md`.
Caps enforced: `SKILL.md` ≤150 lines; corpus files ≤120 lines; **contract files uncapped**.

```
check_caps.py [ROOT]                                    # frozen, M0
check_contracts.py [ROOT]                               # frozen, M0
check_ledger.py [ROOT]                                  # frozen, M0
check_export.py EXPORT_DIR                              # (proposed, M4)
```
Each exits 1 with itemized errors. `check_contracts.py` diffs every `scripts/README.md`
against this appendix and fails on any disagreement in either direction.
`check_ledger.py` fails on a phrase claimed twice, and on a `description` containing a phrase
the ledger does not list; entries owned by another repository are reported as **known
collisions**, not as failures.

```
export.sh DEST                                          # (proposed, M4)
```
Writes one self-contained directory per skill under `DEST`, `lib/` copied into each. No file
in an export may reference a path outside that export.

## Discovery, and the empty set

Every check discovers skills by directory (`skills/*/`) and asserts nothing about a set that
is empty. The pack ships no skills at M0 by design: the gate exists before the content so that
every later milestone has something to fail against. A check that cannot fail is not a gate,
so `test.sh` proves each one fails by running it against a deliberately broken fixture tree
rather than waiting for real content to break.
