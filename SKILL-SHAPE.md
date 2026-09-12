# The shape of a layer-3 skill

What every skill in this pack is built against. Derived from `ux-audit`, which is the only
one that exists — so this document's own acceptance test is:

> **It must describe `ux-audit` accurately without requiring any change to it.**
> If `scripts/check_shape.py` fails against an unmodified checkout, **the spec is wrong and
> gets corrected.** The skill is not edited to fit.

That test stays honest because `ux-audit` lives in its own repository (decision D4: imported,
never migrated), where this document's author cannot quietly edit the thing it is measured
against.

## How to read the markings

Every part carries two, and a reader must be able to tell which is which without leaving
this file:

| Marking | Means |
|---|---|
| **CONFIRMED** | Observed in a working skill. This is a description. |
| **CORRECTED** | The brief said one thing; the source says another. The source won. |
| **PROPOSED** | Nobody has run this. It is a rule this pack is choosing, not a finding. |
| **mandatory** | Every skill has it. `check_shape.py` fails without it where it can see it. |
| **conditional** | Required only when its stated trigger is present. |

`check_shape.py` enforces what is mechanically checkable and says so per part. Parts marked
**not mechanically checked** are review obligations — a human reads for them. Pretending
otherwise would make the checker a rubber stamp.

---

## Part 0 — What a layer-3 skill is · CONFIRMED · mandatory

Three conditions, all of which `ux-audit` meets. A candidate failing any one is a command or
a brief, not a layer-3 skill:

1. It is invoked when the **task** is of a kind — not when a project is open, and not as a
   harness feature.
2. It carries its own corpus, scripts, and tests.
3. It **degrades gracefully** when the project supplies nothing.

*Not mechanically checked* — membership is a judgement, and the ledger (Part 14) is where it
becomes reviewable.

## Part 1 — `SKILL.md`, the runtime prompt · CONFIRMED · mandatory

- **1.1 Trigger-rich description.** Frontmatter `description` naming the artifact classes and
  quoting the literal phrases a user says. *Checked: `description` present.*
- **1.2 Progressive-disclosure tiers**, naming which files load when, keyed to a mode.
- **1.3 A stated never-load set**, with its scope consequence spelled out — `ux-audit` names
  `fogg.md` and states the consequence ("never claim effectiveness, timing, or conversion
  impact").
- **1.4 Line cap ≤150.** `ux-audit` is 91. *Checked.*
- **1.5 The non-restatement rule.** `SKILL.md` links to a contract and never restates it.
  **This is a distinct mechanism from progressive disclosure**, and it is what actually keeps
  the file inside its cap.
- **1.6 Skill-root resolution.** A stated rule for locating the skill's own files from
  `SKILL.md`'s location — the `$SKILL` convention.

## Part 2 — `references/`, in two kinds · CORRECTED · corpus conditional, contracts mandatory

The brief described `references/` as one thing. The source holds **two structurally different
kinds of file**, and a skill can have the second without the first.

- **2.1 The corpus** — frontmatter-bearing, ID-bearing, registry-generating, capped.
  **Conditional:** required only where the skill's output cites IDs a validator must resolve.
- **2.2 The contracts** — no frontmatter, no IDs, not in the registry, always loaded, and
  **not covered by the corpus cap**. **Mandatory:** every skill has at least an output
  contract. *Checked.*
- **2.3 `_format.md`** — the parser contract, stating exactly what the generator expects.
  Lives **beside the corpus**, inside its directory. **Conditional on 2.1.** *Checked.*
- **2.4 The generated registry** — never hand-edited, regenerated after any source change.
  **Conditional on 2.1.** *Checked: a registry exists where a corpus does.*
- **2.5 Immutable IDs** — never change once published, because findings and fixtures cite
  them.
- **2.6 The 120-line cap applies to corpus files only.** *Corrected:* contract files are
  uncapped, and `_format.md` is a contract despite its location. *Checked.*

## Part 3 — `scripts/` · CONFIRMED, with one correction · partly mandatory

- **3.1 Deterministic measurement where measurement is possible**, reporting
  `"kind": "unmeasurable"` rather than guessing. **Conditional** — see Part 7.
- **3.2 A generator for every generated file**, failing loudly: exit on a duplicate ID, a
  missing frontmatter key, an invalid category, an empty source set.
- **3.3 A validator for the skill's own output**, exiting 1 with itemized errors.
  **Mandatory.** *Checked.*
- **3.4 A fixture checker** exiting non-zero. **Mandatory.** *Checked.*
- **3.5 Frozen, dual-homed CLI contracts** in `scripts/README.md` and Appendix A of the
  execution plan — change both in one commit or neither. **Mandatory.** *Checked: the README
  exists; `check_contracts.py` compares the two homes.*
- **3.6 Dependency tiering.** *Proposed, and free:* the gate path — registry build, output
  validation, fixture check — imports **stdlib only**, so the gate runs anywhere without a
  virtualenv. A dependency is permitted only in scripts the gate never calls. `ux-audit`
  already satisfies this; the spec makes it a rule rather than an accident.

## Part 4 — `fixtures/` · CONFIRMED · mandatory

- **4.1 Inputs plus `expected.json`.** *Checked.*
- **4.2 `must_find` *and* `must_not_find`.** The must-not-find list is the point: it is what
  makes a manufactured finding fail. *Checked.*
- **4.3 Caps and tolerances** — `max_severity`, `max_findings`, `min_overall` / `max_overall`,
  `baseline_scores` with ±10 drift.
- **4.4 A checker that exits non-zero.**
- **4.5 Fixtures are generated, not collected** — synthesized deterministically, which is what
  makes a fixture re-derivable rather than an opaque binary. **Conditional:** only where
  inputs are synthesizable.
- **4.6 At least one clean fixture. PROPOSED as a rule** — `ux-audit` ships one, but nothing
  required it. *Reported as a note, not a failure, because it is proposed.*

## Part 5 — `assets/` · CONFIRMED · conditional

Output template, self-contained, zero network requests — every image embedded.
**Conditional:** only for skills that emit a rendered artifact.

## Part 6 — The rubric · CORRECTED · mandatory

The brief said "named axes, a threshold, a defined action at the threshold." The source is
richer, and the difference matters: **the enforceable part is not a threshold.**

- **6.1 Named axes with weights.**
- **6.2 Band definitions covering the full range**, plus an explicit anti-compression rule —
  clustering in one band is a calibration failure.
- **6.3 Three-point anchors per axis.**
- **6.4 A stated procedure** — name the band first, then pick the number; **band wins over
  math**.
- **6.5 Machine-checkable consistency constraints between findings and scores.** Not a
  threshold with an action, but invariants a validator enforces. **This is the correction:
  what makes a rubric real is that a script can falsify it.**
- **6.6 Score traceability** — per-axis drivers, passes, and limitations, so a score can be
  argued with.

*Not mechanically checked by `check_shape.py`:* the invariants are per-skill, and each
skill's own validator enforces them.

## Part 7 — The evidence rule, in three classes · CONFIRMED then EXTENDED · mandatory

- **7.1 `measured:`** — no numeric claim without a script-produced measurement.
- **7.2 `observed:`** — unmeasured suspicion is capped at medium severity and must be phrased
  as suspicion.
- **7.3 `quoted:`** — *proposed extension.* Where a skill can measure nothing, evidence
  degrades to a verbatim excerpt plus a locator. A claim with neither a measurement nor a
  quote is `observed:` and takes the cap. This is what lets the rule survive into skills with
  no measurable surface without becoming decorative.

## Part 8 — The candidate funnel and the honesty accounting · CONFIRMED · mandatory

**The most transferable part of the skill, and absent from the brief.** Part 7 governs claims
that are made; this governs claims that are **not** made, so a short output reads as rigor
rather than thinness.

- **8.1 A suppression contract** — named gates, each with a worked drop example, and the
  silence rule: a dropped candidate does not reappear as a low-severity finding.
- **8.2 Count the funnel** — generated, dropped, merged, capped, reported, with the arithmetic
  enforced by the validator.
- **8.3 Record what passed.**
- **8.4 Record what could not be judged**, and cap any projection while that backlog is
  non-empty.
- **8.5 Record what was deliberately excluded.**
- **8.6 A clean result is a valid result**, and fixtures enforce it.

## Part 9 — Intake and calibration · CONFIRMED · conditional

One bounded intake round, exactly the questions listed, each with a stated calibration
consequence — an answer must change what is judged. **Conditional:** required only where the
skill's judgement is calibrated by context it cannot infer.

## Part 10 — Output location and delivery · CONFIRMED · mandatory

A deterministic output directory, the named file set, and a delivery contract stating what is
handed back — including the honesty notes from Part 8.

## Part 11 — The maintenance loop · CONFIRMED · mandatory

A named promotion path from a real-world failure into the corpus: a new ID, a minimum bar of
observable symptoms, then regenerate. Every skill names **the file its learning accumulates
in** and **the minimum bar for an entry**. A skill that cannot learn rots.

## Part 12 — Provenance and the unparaphrasable · CONFIRMED as convention, PROPOSED as enforced · conditional

- **12.1 The convention, as practised** — redundant markings: a comment at the head of the
  file naming the source, a hard rule in the conventions doc, and inline verbatim markers.
  **Nothing enforces any of them.**
- **12.2 The mechanism.** *Proposed:* frontmatter `provenance: {source, retrieved,
  verbatim_ranges}` plus a checker that hashes the marked ranges and fails when they change
  without a provenance bump. That turns "do not paraphrase" from a note into a test.
- **12.3 The inheritance warning. Mandatory:** a skill carrying borrowed content declares it,
  and **any repo absorbing that skill absorbs the dependency.** This is a standing argument
  against migration.

## Part 13 — The maintainer's conventions doc · CONFIRMED · mandatory

**Absent from the brief, and load-bearing.** Two documents, two audiences: `SKILL.md` is the
runtime prompt, loaded per invocation; the conventions doc is the **maintainer contract**,
never loaded at runtime. It carries sources of truth, the verbatim rule, the caps, the script
runtime, the workflows, and the maintenance loop.

In this pack that is one root `CLAUDE.md` plus a per-skill `CONVENTIONS.md` for anything
skill-specific. *Checked: one of the two exists.*

## Part 14 — The trigger ledger · PROPOSED · mandatory

Every skill registers its **object of attention** and the phrases it claims in
`docs/TRIGGER-LEDGER.md`. A phrase claimed twice by rows this pack owns is a failing test;
a collision with a repository the pack does not own is declared and reported, not failed.

New, and the pack's answer to its sharpest risk: without it, two skills quietly compete for
the same request and the winner is whichever description the model liked. *Checked by
`check_ledger.py`, not `check_shape.py`.*
