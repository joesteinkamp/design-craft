# Fixtures — TODO-skill-name

*(Part 4, mandatory. A skill without fixtures cannot be regression-tested, and a skill that
cannot be regression-tested rots silently.)*

## Shape

One directory per case: the inputs, plus `expected.json`.

## `expected.json`

| Key | Part | Meaning |
|---|---|---|
| `must_find` | 4.2 | Findings that must appear. An empty list makes this a **clean control**. |
| `must_not_find` | 4.2 | Findings that must **not** appear. **This is the point of the file.** |
| `max_severity` | 4.3 | No observed finding above this. |
| `max_findings` | 4.3 | Cap on reported findings. |
| `min_overall` / `max_overall` | 4.3 | Score bounds. |
| `baseline_scores` | 4.3 | Recorded scores, tolerance ±10. `null` = not recorded. |

## The clean control

*(Part 4.6 — proposed as a rule; `ux-audit` ships one and nothing required it.)*

At least one fixture with an empty `must_find` and a populated `must_not_find`. **A test suite
that only checks for misses cannot catch a false positive**, and false positives are what kill
a judgement skill: one manufactured finding and nobody trusts the clean results either.

`clean/` is that fixture. Fill in its inputs and its `must_not_find`.

## Generated, not collected

*(Part 4.5, conditional)* Where inputs can be synthesized, generate them deterministically
rather than committing opaque binaries — that is what makes a fixture re-derivable by someone
who did not create it.
