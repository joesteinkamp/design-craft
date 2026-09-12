# Rubric — TODO-skill-name

*(Part 6. The brief called for "named axes, a threshold, an action." The source was richer,
and **the enforceable part is not the threshold** — it is 6.5 below.)*

## Axes and weights

| Axis | What it scores | Weight |
|---|---|---|
| TODO | TODO | TODO% |

Weights sum to 100.

## Anchors

*(Part 6.3 — three points per axis. Anchors are what make two runs comparable; without them
a score is a mood.)*

| Axis | 90 | 50 | 20 |
|---|---|---|---|
| TODO | TODO | TODO | TODO |

## Bands

*(Part 6.2 — cover the full range, no gaps.)*

| Band | Definition |
|---|---|
| TODO | TODO |

**Anti-compression rule:** scores clustering in one band across different subjects are a
calibration failure, not a coincidence. Go back to the anchors.

## Procedure

*(Part 6.4)* Name the band first, then pick the number inside it. **The band wins over the
math.** If the weighted average contradicts the band definition, the band is right and the
axis scores get revisited.

## Consistency constraints

*(Part 6.5 — **the correction**. What makes a rubric real is that a script can falsify it.
These are invariants `scripts/validate_output.py` enforces, not advice.)*

- TODO, e.g. `overall ≤49 ⇒ at least one critical finding`
- TODO, e.g. `any critical ⇒ overall ≤65`
- TODO, e.g. `overall = weighted average ±1`

## Traceability

*(Part 6.6)* Every axis carries its band, its drivers, what passed, and its limitations — so
a score can be argued with rather than only accepted.
