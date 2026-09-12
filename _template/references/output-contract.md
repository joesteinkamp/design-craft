# Output contract — TODO-skill-name

**SINGLE SOURCE OF TRUTH for this skill's output.** `SKILL.md` links here and never restates
it *(Part 1.5 — this is the mechanism that keeps the runtime prompt inside its cap, and it is
distinct from progressive disclosure)*.

Contract files are **not** covered by the corpus line cap (Part 2.2).

## Shape

TODO: the exact structure the skill emits. Every field, its type, and whether it is required.
`scripts/validate_output.py` enforces this file — if the two disagree, the validator is
wrong or this file is, and one of them changes.

## Suppression gates

*(Part 8.1 — each gate needs a worked drop example, not just a name.)*

| Gate | Drops | Worked example |
|---|---|---|
| TODO | TODO | TODO |

**The silence rule:** a candidate that fails any gate is dropped **silently**. It does not
appear as a low-severity finding instead. Reporting a dropped candidate at lower severity is
how a suppression contract becomes decorative.

## Honesty accounting

*(Part 8.2–8.5 — required in every output.)*

- **Funnel counts:** generated, dropped by gate, merged away, capped, reported. The
  arithmetic is checked by the validator.
- **What passed:** the checks that were run and came back clean.
- **What could not be judged:** and any projection is capped while this list is non-empty.
- **What was deliberately excluded:** and why.

A clean result is a valid result (Part 8.6).
