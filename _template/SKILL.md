---
name: TODO-skill-name
description: >
  TODO. Name the artifact classes this skill acts on, then quote the literal phrases a user
  says to trigger it — "audit this design", "draw the flow". Part 1.1: the description IS the
  trigger surface, so a vague one is a routing failure, not a documentation one. Register the
  phrases you claim in docs/TRIGGER-LEDGER.md (Part 14) or two skills will compete for them.
---

<!-- SKELETON. Every mandatory part of SKILL-SHAPE.md is present as a stub with its contract
     stated. Fill the TODOs; delete nothing without checking the spec part it belongs to.
     Cap: 150 lines (Part 1.4). The way you stay inside it is Part 1.5 — link to a contract,
     never restate it. -->

**Skill root.** Resolve this skill's own files relative to this file's location; refer to it
as `$SKILL` below. *(Part 1.6 — without this, a skill breaks when vendored into a new tree.)*

## 1. Intake

TODO, **or delete this section.** Part 9 is conditional: keep it only where judgement is
calibrated by context that cannot be inferred. One bounded round, and **every question must
change what is judged** — a question whose answer changes nothing is a delay, not calibration.

## 2. What loads, and when

*(Part 1.2 — progressive disclosure, keyed to a mode.)*

| Tier | Loads | When |
|---|---|---|
| Always | `$SKILL/references/output-contract.md`, `$SKILL/references/rubric.md` | every invocation |
| Tier 1 | TODO | TODO |
| Tier 2 | TODO | TODO |

**Never load:** TODO — name the files, **and state the scope consequence of not loading
them** (Part 1.3). "Never claim X" is the shape: a never-load set without a consequence is
just an omission.

## 3. Evidence

*(Part 7, three classes. Not negotiable per-skill.)*

- `measured:` — no numeric claim without a script-produced measurement.
- `observed:` — unmeasured suspicion, capped at medium severity, phrased as suspicion.
- `quoted:` — a verbatim excerpt plus a locator, where nothing can be measured.

A claim with none of the three does not ship.

## 4. The funnel

*(Part 8 — this governs what you do NOT report, so that a short output reads as rigor
rather than thinness.)*

Apply the gates in `$SKILL/references/output-contract.md`. A candidate failing a gate is
**dropped silently** — it does not reappear as a low-severity finding. Count the funnel,
record what passed, record what could not be judged, record what was deliberately excluded.

## 5. Scoring

Use `$SKILL/references/rubric.md`. Name the band first, then pick the number; **the band
wins over the math** (Part 6.4).

## 6. Output

TODO: the deterministic output directory and the named file set (Part 10). State what is
handed back, **including the honesty notes from the funnel.**
