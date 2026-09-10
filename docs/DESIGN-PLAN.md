# Design plan — `design-craft`, the task-craft layer

**Status: plan only. No skill exists in this repo, by design.** This document and
[`EXECUTION-PLAN.md`](EXECUTION-PLAN.md) are the entire deliverable of the planning session.

This is the *design* half of the pair, matching the convention the sibling skill uses:
`ux-audit` splits its planning into a design plan (frameworks, tiers, scoring model,
architecture) and an execution plan (milestones with gates, plus an appendix holding the
frozen CLI contracts). The split is kept because the second document is load-bearing —
the CLI contracts are dual-homed and must be diffable against `scripts/README.md`.

**On format.** `ux-audit` writes its two planning documents as HTML (`plan.html`,
`execution-plan.html`). These are markdown instead, for three reasons: the appendix in
`EXECUTION-PLAN.md` must be diffed line-for-line against a markdown `scripts/README.md`,
and a markdown-to-markdown diff is reviewable where a markdown-to-HTML one is not; the
pack's gate is a script that will eventually lint the line caps and the trigger ledger out
of these documents, and parsing markdown with stdlib is trivial; and neither of
`ux-audit`'s HTML plans is published in its repository, so there is no precedent to break.

---

## 1. What was read, and what was run

Everything below is derived from source read in this session, not from the brief's summary
of it. Where the brief and the source disagree, the source wins and the disagreement is
called out.

**Read:** `agent-global-instructions` — `docs/ROADMAP.md` (Plan 1 phase 6, Plan 2, Plan 3,
Sequence), `docs/GUIDE.md` §2, `skills-lock.json`, `install-commands.sh`, `test.sh`,
`audit.sh`, `commands/ux-audit.md`, `commands/improve.md`, `playbooks/web-preview.md`.
`ux-audit-skill` — `CLAUDE.md`, `SKILL.md`, `README.md`, `scripts/README.md`, all of
`references/`, all of `scripts/`, all five `fixtures/*/expected.json`.
`project-starter-pack` — `AGENTS.md`, `CLAUDE.md`, `guardrails/`, `hooks/`,
`skills/validate/SKILL.md`, `skills/extract/SKILL.md`, `templates/DESIGN.tokens.template.json`,
`test.sh`.

**Run,** against a stock `python3.11` with no virtualenv and no Pillow:

| Command | Result |
|---|---|
| `python3 scripts/build_registry.py` | Regenerated `references/registry.json` **byte-identically** — `git diff` empty. The generated file is genuinely in sync with its prose sources. |
| `python3 scripts/check_fixtures.py fixtures/` | **All five fixtures pass**, exit 0, including the clean control. |
| `python3 scripts/validate_findings.py` on all five | All **VALID**. `polished-settings` = 0 findings, overall 89. |

Three findings fall straight out of that, and they shape the plan more than the roadmap does:

1. **Four of seven scripts are pure stdlib.** `build_registry.py`, `check_fixtures.py`,
   `validate_findings.py`, `build_report.py` import nothing outside the standard library.
   Only `measure.py`, `annotate.py`, and `gen_fixtures.py` need Pillow. The entire *gate*
   path — build the registry, validate the output, diff the fixtures — runs with no venv at
   all. This is true today by accident. The spec should make it a rule.

2. **The vendored copy of `ux-audit` has already drifted from upstream, and nothing
   detects it.** `.agents/skills/ux-audit/SKILL.md` is 81 lines; upstream `HEAD` is 91. The
   vendored copy lacks `meta.candidate_stats`, `score_evidence`, `path_to_excellent`, and
   the `data_fidelity` intake — an entire release behind. `assets/report-template.html` and
   four `fixtures/*/audit/findings.json` differ too. Meanwhile
   `skills-lock.json.skills["ux-audit"].computedHash` matches the SHA-256 of **neither**
   the vendored file nor upstream's, and no script in the harness recomputes or checks it
   — `audit.sh` contains zero references to skills or to the lock. The hash is written and
   consumed only by the third-party `npx skills` CLI. **The lock does not currently verify
   what it claims to pin, even for the one file it names.**

3. **`references/report-spec.md` is 125 lines.** The brief states the pack inherits
   "reference files ≤120 lines". `ux-audit`'s own `CLAUDE.md` says something narrower —
   *"Framework files ≤120 lines each"* — and `_format.md` repeats the cap inside the
   frameworks-format contract. So the cap governs corpus files, not contract files. Writing
   the brief's paraphrase into the spec would put `ux-audit` in breach of the spec on day
   one, which the acceptance test forbids. Corrected in §2.

---

## 2. The shape spec — table of contents

This is the TOC for `SKILL-SHAPE.md`, the document milestone **M1** writes. Every part is
marked:

- **CONFIRMED** — `ux-audit` does this today; the spec describes it without requiring a change.
- **CORRECTED** — the brief's or the roadmap's description of this part is inaccurate against
  the source; the corrected wording is given.
- **PROPOSED** — `ux-audit` does not do this. It is a proposal and is labelled as one in the
  spec itself, per the anti-goals.

Each part also carries a **mandatory / conditional** marking, answering open question 2.

### Part 0 — What a layer-3 skill is · CONFIRMED · mandatory

The membership test, stated as three conditions, all of which `ux-audit` meets: it is
invoked when the *task* is of a kind (not when a project is open, and not as a harness
feature); it carries its own corpus, scripts, and tests; and it degrades gracefully when the
project supplies nothing. A candidate that fails any of the three is a command or a brief,
not a layer-3 skill.

### Part 1 — `SKILL.md`, the runtime prompt · CONFIRMED · mandatory

1.1 **Trigger-rich description.** Frontmatter `description` naming the artifact classes and
quoting the literal phrases a user says. *Confirmed:* `ux-audit`'s ends with three quoted
phrases.
1.2 **Progressive-disclosure tiers**, naming which files load when, keyed to a mode.
*Confirmed:* §3 — always-load contracts, Tier 1 always, Tier 2 on flow mode.
1.3 **A stated never-load set.** *Confirmed:* `status: informational` files, `fogg.md` named
explicitly, with the scope consequence spelled out ("never claim effectiveness, timing, or
conversion impact").
1.4 **Line cap ≤150.** *Confirmed:* 91 lines.
1.5 **The non-restatement rule.** SKILL.md links to a contract and never restates it.
*Confirmed:* `report-spec.md` declares itself "SINGLE SOURCE OF TRUTH … SKILL.md links here
and never restates it." **This is a distinct mechanism from progressive disclosure and the
brief's seven-part list omits it** — it is what actually keeps SKILL.md inside its cap.
1.6 **Skill-root resolution.** A stated rule for locating the skill's own files from
SKILL.md's location. *Confirmed:* the `$SKILL` convention in `ux-audit` line 13.

### Part 2 — `references/`, in two kinds · CORRECTED · corpus conditional, contracts mandatory

The brief describes `references/` as one thing: "prose corpus, a `_format.md` contract, a
generated registry, stable immutable IDs." The source holds **two structurally different
kinds of file in one directory**, and a skill can have the second without the first.

2.1 **The corpus** — `references/frameworks/*.md`. Frontmatter-bearing, ID-bearing,
registry-generating, capped at 120 lines, governed by `_format.md`. **Conditional:** required
only where the skill's output cites IDs a validator must resolve.
2.2 **The contracts** — `references/{scoring,filter,report-spec}.md`. No frontmatter, no IDs,
not in the registry, always loaded, **not covered by the 120-line cap** (`report-spec.md` is
125). **Mandatory:** every skill has at least an output contract.
2.3 **`_format.md`** — the parser contract, stating exactly what the generator expects.
*Confirmed.* **Conditional on 2.1 existing.**
2.4 **The generated registry** — `registry.json`, never hand-edited, regenerated after any
source change. *Confirmed.* **Conditional on 2.1.**
2.5 **Immutable IDs** — never change once published, because findings and fixtures cite
them. *Confirmed*, and observable: `polished-settings/expected.json` cites `DARK-01`…`DARK-06`
and `RF-08` by ID.
2.6 **The 120-line cap applies to corpus files only.** *Corrected*, per §1 finding 3.

### Part 3 — `scripts/` · CONFIRMED, with one correction · partly mandatory

3.1 **Deterministic measurement where measurement is possible.** *Confirmed:* `measure.py`,
which reports `"kind": "unmeasurable"` rather than guessing. **Conditional** — see the
evidence rule, Part 7.
3.2 **A generator for every generated file.** *Confirmed:* `build_registry.py`,
`gen_fixtures.py`. Generation fails loudly: `sys.exit` on duplicate ID, missing frontmatter
key, invalid category, no principle rows, no framework files.
3.3 **A validator for the skill's own output**, exiting 1 with itemized errors. *Confirmed:*
`validate_findings.py`, 12 numbered check classes. **Mandatory.**
3.4 **A fixture checker** exiting non-zero. *Confirmed:* `check_fixtures.py`. **Mandatory.**
3.5 **Frozen, dual-homed CLI contracts** in `scripts/README.md` and the execution plan's
appendix; change both in one commit or don't change them. *Confirmed.* **Mandatory.**
3.6 **Dependency tiering.** *Proposed, and free:* the gate path (registry build, output
validation, fixture check) must import stdlib only, so the gate runs anywhere without a
virtualenv. Pillow — or any other dependency — is permitted only in scripts the gate does
not call. `ux-audit` already satisfies this; the spec makes it a rule rather than an accident.
This is the single cheapest mitigation for the unsolved `.venv` bootstrap (§4).

### Part 4 — `fixtures/` · CONFIRMED · mandatory

4.1 **Inputs plus `expected.json`.** *Confirmed.*
4.2 **`must_find` *and* `must_not_find`.** *Confirmed*, and the clean control
(`polished-settings`) exists precisely to make false positives fail: *"The must-NOT-find
list is the point: no manufactured findings."*
4.3 **Caps and tolerances** — `max_severity`, `max_findings`, `min_overall`/`max_overall`,
`baseline_scores` with ±10 drift. *Confirmed.*
4.4 **A checker that exits non-zero.** *Confirmed.*
4.5 **Fixtures are generated, not collected** — `gen_fixtures.py` synthesizes the screenshots
deterministically. *Confirmed*, and **the brief's list omits it.** It is what makes a fixture
re-derivable rather than an opaque binary. **Conditional:** only where inputs are synthesizable.
4.6 **At least one clean fixture per skill.** *Proposed as a rule* (`ux-audit` ships one, but
nothing requires it).

### Part 5 — `assets/` · CONFIRMED · conditional

Output template, self-contained, zero network requests. *Confirmed:* `build_report.py`
base64-embeds every image. **Conditional:** only for skills that emit a rendered artifact.

### Part 6 — The rubric · CORRECTED · mandatory

The brief says "named axes, a threshold, a defined action at the threshold." The source is
richer and the difference matters, because the enforceable part is not a threshold.

6.1 **Named axes with weights.** *Confirmed:* six categories, 30/15/15/15/15/10.
6.2 **Band definitions covering the full range**, plus an explicit anti-compression rule
("clustering 70–89 is a calibration failure"). *Confirmed.*
6.3 **Three-point anchors per axis** (90 / 50 / 20). *Confirmed.*
6.4 **A stated procedure** — name the band first, then pick the number; band wins over math.
*Confirmed.*
6.5 **Machine-checkable consistency constraints between findings and scores** — not a
threshold with an action, but a set of invariants a validator enforces: `overall ≤49 ⇒ ≥1
critical`; `any critical ⇒ overall ≤65`; `overall ≥90 ⇒ zero critical/high`; `≥2 DARK-* ⇒
trust_persuasion ≤35`; `overall = weighted average ±1`. *Confirmed*, enforced in
`validate_findings.py` checks 9–10. **This is the correction: what makes the rubric real is
that a script can falsify it.**
6.6 **Score traceability** — per-axis `band` / `drivers` / `passes` / `limitations`, with
`score <90 ⇒ ≥1 driver or limitation` and `score ≥90 ⇒ ≥1 pass`. *Confirmed.*

### Part 7 — The evidence rule, in three classes · CONFIRMED then EXTENDED · mandatory

7.1 **`measured:`** — no numeric claim without a script-produced measurement.
*Confirmed:* SKILL.md §4 and `validate_findings.py` check 5.
7.2 **`observed:`** — unmeasured suspicion is capped at medium severity and must be phrased
as suspicion ("appears low-contrast — verify"). *Confirmed.*
7.3 **`quoted:`** — *proposed extension, and the answer to open question 3.* Where a skill
can measure nothing, evidence degrades to a verbatim excerpt from the artifact plus a
locator. A claim with neither a measurement nor a quote is `observed:` and takes the
severity cap. This lets the rule survive into skills with no measurable surface without
becoming decorative.

### Part 8 — The candidate funnel and the honesty accounting · CONFIRMED · mandatory

**Absent from the brief's seven-part list, and the most transferable part of the skill.**
Part 7 governs claims that are made; this governs claims that are *not* made, so that a
short output reads as rigor rather than thinness.

8.1 **A suppression contract.** *Confirmed:* `filter.md`'s four gates — Blocker, Standard,
Clutter, Steelman — each with a worked drop example, and the silence rule ("a candidate that
fails any gate is dropped silently — it does not appear as a low-severity finding instead").
8.2 **Count the funnel.** *Confirmed:* `meta.candidate_stats` {generated, gate_dropped,
merged_away, capped, reported}, with the arithmetic enforced by validator check 12.
8.3 **Record what passed.** *Confirmed:* `clean_checks`.
8.4 **Record what could not be judged.** *Confirmed:* `path_to_excellent.verification_backlog`,
and the projection capped at 89 while the backlog is non-empty.
8.5 **Record what was deliberately excluded.** *Confirmed:*
`meta.calibration_exclusions`, driven by `data_fidelity`.
8.6 **A clean result is a valid result.** *Confirmed*, and fixture-enforced.

### Part 9 — Intake and calibration · CONFIRMED · conditional

One bounded intake round, exactly the questions listed, each with a stated calibration
consequence. *Confirmed:* `ux-audit` §1 — four questions, one round, and each answer changes
what is judged (touch ⇒ 44px, wireframe ⇒ skip contrast). **Conditional:** required only
where the skill's judgement is calibrated by context it cannot infer.

### Part 10 — Output location and delivery · CONFIRMED · mandatory

Deterministic output directory (`audits/<slug>-<YYYY-MM-DD>/`), the named file set, and a
delivery contract stating what is handed back — including the honesty notes. *Confirmed:*
§7 and §9.

### Part 11 — The maintenance loop · CONFIRMED · mandatory

A named promotion path from real-world failure into the corpus: a new ID, ≥2 observable
symptoms, then regenerate the registry. *Confirmed:* `CLAUDE.md` "Maintenance loop" and
`recurring-failures.md`, whose header says so in-file. Generalized in the spec as: every
skill names the file its learning accumulates in and the minimum bar for an entry. A skill
that cannot learn rots.

### Part 12 — Provenance and the unparaphrasable · CONFIRMED as convention, PROPOSED as enforced · conditional

12.1 **The convention, as practised.** *Confirmed:* three redundant markings — an HTML
comment at the head of the file naming the source, a hard rule in `CLAUDE.md`, and inline
"(verbatim)" markers on the affected headings. Nothing enforces any of them.
12.2 **The mechanism.** *Proposed:* frontmatter `provenance: {source, retrieved,
verbatim_ranges}` plus a `check_provenance.py` that hashes the marked ranges and fails the
gate when they change without an accompanying provenance bump. Answers open question 5.
12.3 **The inheritance warning.** *Mandatory in the spec:* a skill that carries borrowed
content declares it, and any repo absorbing that skill absorbs the dependency. See §4.

### Part 13 — The maintainer's conventions doc · CONFIRMED · mandatory

**Absent from the brief's seven-part list.** `ux-audit` ships `CLAUDE.md` alongside
`SKILL.md`, and the brief's own reading order ("read this before SKILL.md") concedes it is
load-bearing. The two documents have different audiences: `SKILL.md` is the runtime prompt
loaded per invocation; `CLAUDE.md` is the maintainer contract, never loaded at runtime. It
carries sources of truth, the verbatim rule, the caps, the script runtime, the workflows,
and the maintenance loop. In the pack this becomes one root `CLAUDE.md` plus a per-skill
`CONVENTIONS.md` for anything skill-specific.

### Part 14 — The trigger ledger · PROPOSED · mandatory

New, and the pack's answer to the sharpest risk. See §3.

---

## 3. Routing discipline

**The collision is already real, and it is cross-repo.** Read the descriptions side by side:

| Skill | Repo | Fires on |
|---|---|---|
| `ux-audit` | `ux-audit-skill` | "audit/review/critique a design, screenshot, mockup, or UI flow"; *"audit this design"*, *"UX review"*, *"what's wrong with this screen"* |
| `validate` | `project-starter-pack` | *"audit the code against the briefs"*, **"find anti-patterns in the repo"**, "review against DESIGN.md" |
| `extract` | `project-starter-pack` | *"extract the briefs"*, "reverse engineer the design system" |
| `/improve` | `agent-global-instructions` | multi-role review of a diff, **including a UI/UX role** |

A `slop-detect` described as "find AI-slop tells in this project" is a near-verbatim
collision with `validate`'s "find anti-patterns in the repo". A `design-extract` collides
with `extract` on its name. A `design-critique` collides with `/improve`'s UI/UX role. **Two
of the four collisions the pack would create are with skills the pack does not own**, which
means an architecture decision taken inside this repo cannot fix them.

That reframes the choice. The recommendation is therefore two things, not one.

### 3.1 The primary mechanism: a trigger ledger with a failing test

`docs/TRIGGER-LEDGER.md` lists every trigger phrase claimed by every skill and command in
all three repos, with its owner and its **object of attention**. `test.sh` fails when two
entries claim the same phrase, and fails when a skill's `description` contains a phrase the
ledger does not list. This is cheap, it is checkable, and it is the only mechanism that
reaches across repo boundaries — a new skill's description is diffed against the ledger
before it ships, and the ledger names skills the pack does not own.

The ledger's organising column is **object of attention**, because that — not the verb — is
what actually separates these skills:

| Object | Owner | Input |
|---|---|---|
| A rendered surface (pixels) | `ux-audit` | screenshots |
| A source tree (code, styles, prose) | `slop-detect` *(pack)* / `validate` *(starter-pack)* | files |
| An artifact this session is about to emit | `design-critique` *(pack)* | in-memory draft |
| A specification for a drawing | `design-diagram` *(pack)* | a described structure + `DESIGN.json` |
| An existing product's identity | `design-extract` *(pack)* / `extract` *(starter-pack)* | a URL or a repo |

Written that way, `ux-audit` and `slop-detect` stop colliding: one reads pixels, the other
reads files, and neither can do the other's job. That distinction only holds if `slop-detect`
never renders a page — which is independently the recommendation in §5, question 4.

### 3.2 The architecture: hybrid, with the router deferred behind a stated trip-wire

**Recommended: hybrid.** Peers for skills whose object of attention is distinct and whose
descriptions can be held disjoint by the ledger; one router for any group that fails that
test.

**And the router is not built until a group fails it.** Building a five-verb router before
the pack's second skill exists is the ceremony the brief warns about elsewhere; the roadmap
ships one skill at a time and the ledger holds until two entries actually converge. The
trip-wire is stated now so it is not a judgement call later:

> **A router materialises the moment two skills in the pack claim overlapping objects of
> attention, or the moment the ledger check fails twice on the same phrase pair.**
> At that point the overlapping skills' `SKILL.md`s become `references/verbs/<verb>.md` under
> one entry skill, and the entry skill's own `SKILL.md` carries dispatch and shared intake only.

The 150-line objection to routers is answerable and should be answered in the spec:
`ux-audit` drives a nine-step procedure from 91 lines by linking out to contracts and
loading corpus files per tier. A router carrying dispatch plus a shared intake round, with
each verb's procedure in a reference file, is comfortably inside the cap. What a router
genuinely costs is migration: if `ux-audit` ever moves in, its `SKILL.md` stops being a
`SKILL.md`. That is one more reason migration stays last, and a reason to prefer never
(§6, decision 4).

**Rejected: pure peers.** The brief's own objection is correct and the evidence supports it
— descriptions drift toward each other as skills grow, and here two of the neighbours are
outside the repo and will drift without consulting it.

**Rejected: a single verb router for everything.** It forces `design-diagram` — which
produces rather than reviews, and shares no intake with the review verbs — through a
dispatch layer that buys it nothing.

---

## 4. Cross-repo dependencies

### 4.1 Distribution — `agent-global-instructions` Plan 1 phase 6 · **the gating risk**

The brief calls this the gating risk. Reading the source makes it worse than stated, and
also more tractable.

**What is actually broken today, verified:**

- **The lock verifies nothing.** `computedHash` matches neither the vendored `SKILL.md` nor
  upstream's; nothing in the repo recomputes it; `audit.sh` never mentions skills.
- **The vendored copy has already drifted** — a full release behind upstream, silently.
- **`ux-audit` as distributed does not run.** `SKILL.md` line 14 instructs every invocation
  to use `$SKILL/.venv/bin/python`. There is no `requirements.txt`, no bootstrap script, and
  no Makefile anywhere in the repository; `.venv/` is gitignored. The skill runs on the
  author's machine because that checkout has a hand-built venv and a hand-written
  `ln -s`. **A vendored copy on any other machine has a first instruction that points at an
  interpreter which does not exist.** "A pack that cannot be installed is not a pack" — the
  one skill in the layer is, today, in that condition everywhere but one laptop.
- **The installer is per-skill by construction.** `install_skill_link()` iterates
  `.agents/skills/*/`, and each directory must correspond to a same-named canonical command
  carrying `skill-backed: true`. A five-skill pack vendored as one directory gets **one**
  symlink under one name; vendored as five directories it needs five command files and five
  lock entries, and the shared `lib/` has no home in either arrangement.

**What the pack needs resolved, stated as three asks:**

1. **A directory lock whose hash is computed and checked by this repo's own tooling** — a
   manifest hash over the sorted file list plus each file's hash, recomputed by `audit.sh`.
   The roadmap already proposes `skillDir`; the addition is that verification must not
   depend on a third-party CLI, because today's does and it does not work.
2. **A decision on pack shape at the install boundary:** either the pack *exports* N
   per-skill directories (each self-contained, `lib/` copied in at export time), or
   `install-commands.sh` grows a pack mode that links one directory and N command files.
   The first requires no harness change and is therefore what the pack should build toward.
3. **A `.venv` answer.** Vendoring copies files, not environments — this is genuinely
   unsolved and the roadmap does not address it.

**What the pack does while waiting** — and this is the substantive mitigation:

> **The gate path is stdlib-only** (Part 3.6). Verified: registry build, output validation
> and fixture diff all run on a stock `python3` with no venv. So the pack's *tests* never
> need a venv, and CI never needs one.
>
> **Every skill declares its dependency tier in frontmatter** — `runtime: stdlib` or
> `runtime: stdlib+pillow` — and a skill whose scripts are all stdlib installs by copying
> files, full stop. `design-diagram`, the recommended second skill, is designed to be
> `runtime: stdlib`: SVG generation and structural validation are string and arithmetic
> work. **The pack therefore ships an installable skill before the venv question is
> answered**, and the venv question narrows to "how does `ux-audit` get Pillow", which is
> one skill's problem and not the layer's.

### 4.2 The guardrail registry — `project-starter-pack` Plan 2 phase 1

**Status update, 2026-09-05: this dependency is satisfied.** `guardrails/registry.json`
shipped in `project-starter-pack` #18, along with `build-guardrails.sh`, `guardrails/_format.md`,
per-ban `trips`/`clean` fixtures, and hooks that read the registry instead of hardcoding greps.
The owner approval this section said was required was given. Verified at merge: `./test.sh`
336 passed / 0 failed, ten live detectors proven in both directions, and `registry.json`
rebuilding byte-identically from the prose.

*The original analysis, kept because the design conclusions below were drawn from it:*
`slop-detect` is designed to consume `guardrails/registry.json`. That file did not exist;
the guardrails were five prose files, 253 lines, and the three hooks hardcoded a grep subset.
Creating the registry meant restructuring guardrails, and `project-starter-pack/AGENTS.md`
lists *"a change would grow the command surface, or add a slot, question, or guardrail"*
among the things that require asking the owner first. So it was not merely unbuilt; it was
gated on an approval in a repo this plan does not own.

**What the pack needs:** ban IDs (`DES-04`, `WRT-11`, …), a `detect:` field or `manual`, a
severity, and a stable `registry.json` path relative to a project root.

**What the pack does while waiting:** nothing that depends on it. This was the principal
argument for building `design-diagram` second rather than `slop-detect` (§6, decision 3) —
and it is the part of that argument that has now expired, since there is no longer anything
to wait for. The arguments that survive are listed under D3.
When `slop-detect` is eventually built, the degradation rule is fixed by the anti-goals: with
no project registry it falls back to a bundled default set **and the report says it did**.
The bundled set is a fallback, never a canonical rule set, and it is never the source that a
project's bans are authored into.

### 4.3 The `qualia` dependency

`ux-audit`'s filter gates, severity definitions, calibration bands, and conciseness contract
are copied verbatim from `~/projects/qualia`, with a warning that paraphrasing breaks
calibration. `qualia` is a local path. It is not among the repositories reachable from this
session, and it was not read. **The provenance is therefore unverifiable by anyone but the
owner**, and any repo that absorbs `ux-audit` absorbs an unverifiable dependency. Part 12
gives the spec a way to *mark* it; nothing gives the pack a way to *check* it. This is a
standing argument against migration (§6, decision 4).

---

## 5. Open questions, answered

### Q1 — What is genuinely shared across skills?

Answered by reading the two candidate scripts line by line rather than by name.

- **`check_fixtures.py` — genuinely shared. Build `lib/fixtures.py` first.** Of its 100
  lines, the fixture-directory walk, `must_find` / `must_not_find` / `max_severity` /
  `max_findings` / score-bound / baseline-drift checks and the itemized non-zero exit are
  entirely generic. Only the match predicate is skill-specific (`any_principles` +
  `screen_index` + box IoU). Extract the runner, inject the predicate. This is the pack's
  gate; one implementation of the gate is the whole point of a pack.
- **`build_registry.py` — shared core, injected vocabulary.** Of its 82 lines, roughly 25
  are generic (frontmatter parse, three-column table parse, duplicate-ID exit, JSON emit)
  and the rest are `ux-audit`'s vocabulary: its six categories, the `WCAG-\d+\.\d+\.\d+` ID
  exception, the `tier` field, the `status: informational` exclusion. Shared as
  `lib/registry.py` taking a schema dict from the caller's `_format.md`. Worth it at two
  registries; not at one.
- **Token resolution from `DESIGN.json` — *not* shared yet, and this is a correction to the
  roadmap.** `ux-audit` does not read `DESIGN.json` at all — verified, zero references
  anywhere in its tree. So the roadmap's "build it once and share it" describes two
  hypothetical consumers, neither of which exists. The resolution is non-trivial (a default
  `color` block plus a `themes.<mode>.color` override layer, `$value` unwrapping, numeric
  slots emitted bare) and getting it wrong once in two places would be bad — but its shape
  cannot be known before one real consumer exists. **Write it inside `design-diagram`;
  extract it when `slop-detect` becomes the second consumer.**
- **A report template — not shared.** `ux-audit`'s is audit-specific: screenshot overlays,
  hover popovers, a delta section. A diagram skill emits SVG. Superficially similar,
  structurally unrelated.

**The rule the spec states:** `lib/` gains a module when a **second** consumer exists, never
in anticipation of one. Day-one `lib/` is exactly `fixtures.py` and `registry.py`, and even
`registry.py` waits until skill two actually needs a registry.

### Q2 — Does every skill need a registry?

**No, and the test is mechanical:** a registry is required iff the skill's output cites
stable IDs that a validator must resolve. Applied:

| Skill | Registry? | Why |
|---|---|---|
| `ux-audit` | **Yes** | findings cite `principles[]`; validator check 2 resolves every one |
| `slop-detect` | **Consumes one, ships none** | it cites the *project's* ban IDs; shipping its own recreates the drift the effort exists to remove |
| `design-diagram` | **Yes, small** | the emitted SVG should declare its type ID and the validator should resolve it against the type registry |
| `design-critique` | **No** | ~6 axes, cited by name, no IDs in output — a rubric reference, not a registry |
| `design-extract` | **No** | its output is a `DESIGN.json`, validated against a schema, not against citations |

Mandatory for every skill regardless of size: an output contract (2.2), a validator (3.3),
fixtures with a clean control (Part 4), the evidence rule (Part 7), the funnel accounting
(Part 8), a maintenance loop (Part 11), and a ledger entry (Part 14). Conditional: the
corpus, `_format.md`, the registry, `assets/`, measurement scripts, and intake. A spec that
forces a registry onto a six-axis critique skill will be ignored, and rightly.

### Q3 — What can each proposed skill actually measure?

- **`ux-audit`** — contrast and size, via `measure.py`. Reports `unmeasurable` rather than
  guessing. Established.
- **`design-diagram`** — **the strongest measurable surface of the five, and all of it
  stdlib.** Structural validation of emitted SVG (required elements, arity, attribute
  presence); **token conformance** — every colour literal in the output resolves to a
  `DESIGN.json` token, which is exact, deterministic, and falsifiable; label geometry —
  overflow and collision detection from a character-width table, which is approximate and so
  must report a tolerance and fall back to `unmeasurable` at the edges, exactly as
  `measure.py` does.
- **`slop-detect`** — regex-detectable bans over source, plus OKLCH→sRGB→relative-luminance
  contrast arithmetic on `DESIGN.json` token pairs, which is pure stdlib. Render-dependent
  bans are **not** measurable without a browser; see Q4.
- **`design-critique`** — measures nothing about the artifact. It can measure only its own
  output: word caps, band↔severity consistency, score arithmetic.
- **`design-extract`** — its output is checkable by the layer below: the emitted
  `DESIGN.json` must pass the starter pack's `validate-tokens.sh` (Plan 2 phase 3).

**What the evidence rule says where nothing can be measured** — the three-class rule from
Part 7.3. `measured:` (a script produced the number) → `quoted:` (a verbatim excerpt plus a
locator into the artifact) → `observed:` (neither; capped at medium and phrased as
suspicion). A critique skill's evidence is a quote. The severity cap and the suspicion
phrasing are what carry over intact; the rule degrades without becoming decorative.

### Q4 — Does `slop-detect` need a browser?

**It would need one to do the job as pitched. Recommendation: don't give it one — narrow
the skill instead.**

The design bans a regex genuinely cannot check are the rendered ones: *"no more than one
decisive accent … on ≤10% of surface"* (needs a rendered area calculation), *"no gray text
on colored backgrounds — contrast verified, not eyeballed"* (needs computed styles, unless
it is done from tokens), and the composition tells — identical-card grids, the tilted
screenshot with a glow (need a DOM, arguably vision).

The dependency cost is decisive. `playwright-cli` is documented in
`agent-global-instructions/playbooks/web-preview.md` as an **operator-machine tool**, not a
repo dependency: nothing installs it, nothing pins it, and the playbook is mostly a warning
about leaked browser processes that survive the session and break the user's Chrome. Taking
it as a dependency breaks the pack's stated runtime (stdlib + Pillow, offline), breaks the
installs-by-copying-files property that §4.1 shows is already fragile, and imports a
documented cleanup hazard into a skill invoked casually.

**So: `slop-detect` reads source, never pixels.** Concretely it keeps the `detect:` bans
over the tree at full breadth (versus the hook's near-zero-false-positive subset), the
whole-tree scope the hook lacks, the report with severity and ban-ID citations, and token
contrast arithmetic — which is stdlib and covers the *"contrast verified, not eyeballed"*
ban better than a browser would, at its source. It declares the rendered bans
`unmeasurable` and names `ux-audit` as the instrument for them, in the report.

This narrowing costs the skill its headline claim and pays for it twice: it removes the
trigger collision with `ux-audit` (pixels versus files, §3.1), and it removes a dependency
the pack cannot install. If a browser is wanted later it arrives as an optional
`--rendered` mode that exits with a clear message when `playwright-cli` is absent — never a
hard dependency, never on the gate path.

### Q5 — How does the spec express borrowed-verbatim content?

**As a first-class, checkable concept — Part 12.** Today `ux-audit` marks it three ways (a
provenance comment at the head of the file, a hard rule in `CLAUDE.md`, inline "(verbatim)"
markers on headings) and enforces it zero ways. The spec keeps all three as required
convention and adds a mechanism: frontmatter `provenance: {source, retrieved,
verbatim_ranges}`, and `check_provenance.py` on the gate path, hashing the marked ranges and
failing when they change without a provenance bump. That turns "do not paraphrase" from a
note into a test.

**And the plan records what could not be resolved:** `qualia` is a local path outside the
reachable repositories. It was not read. The pack can *mark* borrowed content, but it cannot
verify that `ux-audit`'s copies are faithful, and neither can anyone but the owner.
Migrating `ux-audit` into the pack inherits that unverifiable dependency wholesale — an
argument that belongs in decision 4, not a detail.

### Q6 — What does the pack use as its gate?

**`./test.sh` at the pack root, and CI on day one.**

Both sibling repos converge on exactly `./test.sh`, so the pack matches rather than invents.
The gate runs, in order: rebuild every registry and fail if the working tree changes
(proving generated files are never hand-edited — this check works today, verified byte-identical);
run every skill's validator against every shipped fixture output; run every skill's fixture
check including the clean controls; check line caps (SKILL.md ≤150, corpus files ≤120);
check the trigger ledger for overlapping phrases and for descriptions carrying unlisted
phrases; check provenance hashes; diff each `scripts/README.md` against Appendix A of the
execution plan and fail when they disagree.

**CI on day one: yes.** `agent-global-instructions` has CI; `project-starter-pack` has
`./test.sh` and no CI, which the roadmap notes as a gap; `ux-audit` is run by hand. The pack
should not inherit the weakest of the three. It is cheap here precisely because the gate is
stdlib-only: a GitHub Actions job needs `actions/checkout` and a stock Python. No venv, no
Pillow, no browser. The scripts that need Pillow are, by rule (3.6), not on the gate path.

---

## 6. Decisions reserved for the owner

Each is a recommendation with its trade-off, not a choice made.

### D1 — Monorepo or repo-per-skill

> **DECIDED, 2026-09-10 (owner).** Monorepo — but as a **destination, not a
> workshop.** Skills are evolved in their own repositories and imported here when
> ready. That is a third pattern this section did not offer, and it is already how
> `agent-global-instructions` treats `ux-audit`: developed at
> `joesteinkamp/ux-audit-skill`, vendored into `.agents/skills/`, never edited in
> place.
>
> Two consequences follow. **It largely dissolves §7's framing:** the layer stops
> being a five-skill plan decided up front and becomes a place where skills arrive
> once they have earned it, so "should this be five skills" is answered by what
> matures, not by a count. And **the import path is the thing to get right**,
> because it is now load-bearing rather than incidental — see the note under D1's
> condition below.

**Recommend: monorepo**, agreeing with the roadmap, with one condition attached.

*For:* one `test.sh`, one CI job, one `lib/`, one place the shape spec lives next to the
things it governs. Repo-per-skill at five skills means five gates that drift.

*The condition:* the monorepo must **export** per-skill directories, not merely contain
them. `install_skill_link()` iterates `.agents/skills/*/` and pairs each directory with a
same-named command carrying `skill-backed: true` — a layout the pack cannot change from
here. So the pack's build step copies `lib/` into each exported skill directory, making each
export self-contained. Without that, the monorepo is undeployable through the only installer
that exists.

*Trade-off:* the export step is new machinery that repo-per-skill does not need, and a
shared `lib/` means a change to `fixtures.py` can break every skill's gate at once. Against
that: it breaks them all in CI, in one run, which is the point.

*Migration cost:* near zero today, because the pack has no skills.

**The import path, checked 2026-09-10.** With D1 decided as import-when-ready, the
integrity of an import matters more than the monorepo/multi-repo choice did. What is
actually true today: `skills-lock.json` is **`npx skills`' lockfile
([skills.sh](https://skills.sh)), not a format this toolchain owns**, and no script
in `agent-global-instructions` reads it — `install-commands.sh` names it only in a
comment. It records one `skillPath` and one `computedHash` per skill, and for
`ux-audit` that path is `SKILL.md`, while the vendored tree is **66 files** across
`references/`, `scripts/`, `fixtures/` and `assets/`. So 65 of 66 files are pinned by
nothing, and a change to any of them is invisible.

This makes the roadmap's Plan 1 phase 6 — "teach `skills-lock.json` about
directories" — wrong about ownership: the schema belongs to a third-party tool, and
the scripts that phase lists as touched (`install.sh`, `converge.sh`, `audit.sh`) do
not read the lock at all. Whether `npx skills` supports a directory mode is not
documented on skills.sh and was not determined. The options that do not depend on
that answer: verify the vendored tree independently with a manifest hash the harness
computes and checks itself, or vendor via a mechanism that hashes trees natively.
**This is now the gating question for D1 as decided**, and it is a harness question,
not a `design-craft` one. If `ux-audit` migrates
later (see D4) the cost is that repo's history, its published URL, and the lock entry that
points at it.

### D2 — Routing architecture

**Recommend: hybrid, ledger-first, router deferred behind the stated trip-wire (§3.2).**

*Trade-off:* more moving parts than either pure option, and the boundary needs defending
each time a skill is added — the brief says so and it is right. The defence is that the
boundary is written down as a column in the ledger (object of attention) and checked by
`test.sh`, so defending it is a diff review rather than a judgement call. The residual risk
is real: the ledger cannot *stop* `project-starter-pack` or the harness from adding a
colliding phrase; it can only make the collision visible the next time the pack's gate runs.

### D3 — Which skill is built second

> **CLOSED AS MOOT, 2026-09-10 (owner).** The question presumed the pack builds its own
> skills in a sequence it controls. D1 removed that premise: skills mature in their own
> repositories and are imported when ready, so there is no build order here to decide.
> Everything below is kept as the record of a question that stopped applying, not as a
> pending choice.

*The case for `slop-detect` first,* which the roadmap makes: it proves the cross-repo seam,
it closes the audit's headline gap, and it is the skill with the clearest user demand.

*The case for `design-diagram`,* which the evidence supported at the time: it depends on
nothing that does not exist — `DESIGN.json` ships as a template and as a worked example
(`examples/saga-reader/DESIGN.json`) — where `slop-detect` depended on a registry that was
unbuilt, whose construction was gated on an owner approval **in another repo**, and whose
headline capability is the part §5 Q4 recommends cutting.

> **Re-decide this, 2026-09-05.** The registry shipped (§4.2), so the strongest clause above
> — the unbuilt, approval-gated dependency — no longer holds, and the trade-off accepted
> below ("the cross-repo seam stays unproven for longer") now buys less than it did. Two
> arguments survive intact and may still be sufficient on their own: `design-diagram` is
> `runtime: stdlib`, so it ships while the `.venv` question in §4.1 is open; and it stresses
> the spec harder, being the first skill with a registry of *types* rather than principles
> and the first to validate an emitted artifact. §5 Q4's recommendation to cut the browser
> from `slop-detect` is also untouched. This is the owner's call, not a mechanical
> consequence of the merge. `design-diagram` is
`runtime: stdlib`, so it ships an installable skill while the `.venv` question is still open
(§4.1). And it stresses the spec harder: it is the first skill to have a registry of *types*
rather than *principles*, and the first to validate an *emitted artifact* rather than a
findings file — which is exactly where a spec derived from one auditing skill is most likely
to turn out to describe only that skill.

*Trade-off:* the cross-repo seam stays unproven for longer, and the gap `slop-detect` closes
stays open. Accepted, because a second skill that ships beats a second skill that blocks on
two external approvals.

### D4 — Whether `ux-audit` migrates in at all

> **DECIDED, 2026-09-10 (owner): imported, never migrated.** This is D1's pattern applied
> to the skill that already followed it, and it matches the recommendation below by a
> shorter route — the pack does not need a reason to leave `ux-audit` alone, because
> importing is now simply what the pack does with every skill.

**Recommend: migration-never as the default; re-decide at M6 only if a concrete need
appears.** This departs from the roadmap's migration-last.

*Why:* the roadmap's stated reason to migrate is that it is the acceptance test for Plan 1
phase 6's directory lock. But the **pack itself is a directory** — locking the pack tests
the lock exactly as well, and sooner. With that reason removed, migration buys tidiness and
costs three things: it risks the only proven artifact in the layer; it imports the
unverifiable `qualia` dependency (§4.3) into a repo that otherwise has none; and under a
router (§3.2) `ux-audit`'s `SKILL.md` would stop being a `SKILL.md` at all. Meanwhile the
spec's acceptance test — *describes `ux-audit` without requiring a change to it* — is
strictly easier to keep honest while `ux-audit` is an independent subject rather than
something the spec's author can quietly edit.

*Trade-off, stated plainly:* the pack cannot share `lib/` with `ux-audit`, so if `ux-audit`
ever wants the shared fixture runner it must either vendor it or duplicate it. And the pack
ships with no proven skill inside it until `design-diagram` lands, which makes the spec's
first milestone feel thinner than it is.

### D5 — The repo name

> **DECIDED, 2026-09-10 (owner): keep `design-craft`.** No rename; the deadline this
> section attached to M1 is discharged.

**Recommend: keep `design-craft`.** The brief calls it a roadmap placeholder, and it is —
but the repository now exists under that name, the roadmap's diagram uses it, and
`docs/GUIDE.md` will need to name it. Alternatives worth a moment: `design-tasks` (accurate,
flat), `craft` (short, collides with nothing, says less). The rename cost is currently small
and rising: one GitHub rename with redirects, one `source` string in `skills-lock.json`, and
whatever documentation names it by then. **If it is going to change, it should change before
M1 writes the spec.**

---

## 7. Honest read: should this be a five-skill layer?

**No. The evidence supports a spec and two skills, not a layer of five.** The brief asked for
this to be said plainly if the investigation found it, and it did.

**What genuinely generalises** — and it is a lot, enough to justify writing the spec at all:
the gate discipline (fixtures with must-not-find and a clean control), generated files with
loud failure, output validation as a script rather than a promise, the evidence rule with
its severity cap, the funnel accounting that makes silence legible, line caps with
progressive disclosure, and the maintenance loop. Those are transferable to any skill that
produces judgements, and none of them is specific to auditing screenshots.

**What does not generalise, and the roadmap treats as if it does:** the shape of
`references/`. `ux-audit` has a prose corpus with immutable IDs because UX heuristics are
*published and citable* — Nielsen, WCAG, Gestalt. Diagram types are not a published corpus.
Critique axes are not a published corpus. And design bans explicitly **must not** become one
inside a skill; the anti-goals forbid it and the whole effort exists to stop that drift. So
"references/ = prose corpus + `_format.md` + registry + immutable IDs" is one skill's answer
to one skill's problem, not the layer's shape. The spec must mark it conditional — Part 2
does — or the first small skill built to it will carry a registry it does not need and the
spec will be ignored thereafter.

**On the count of five, taken one at a time:**

- **`ux-audit`** exists, works, and is recommended to stay where it is (D4).
- **`design-diagram`** is the one clearly-earned new skill: a real gap (the Output artifacts
  rule covers HTML and Markdown and stops), no dependency that does not exist, and the
  strongest measurable surface in the set.
- **`slop-detect`** is defensible only after §5 Q4's narrowing, and narrowed it overlaps
  substantially with `project-starter-pack`'s `validate` skill plus its edit hook — same
  registry, same source tree, same bans. The honest question is whether it is a *third
  consumer of the guardrail registry* or a **depth mode of `validate`**, and the second
  reading is at least as strong. It should not be built until the registry exists and that
  question has been put to the owner.
- **`design-critique`** is, on its own description, a step other skills take before emitting
  — not something a user says. A thing with no user-facing trigger is not a skill; it is a
  reference and a validator that other skills load. Part 7.3's `quoted:` class and Part 6's
  rubric are exactly the machinery it needs, and both can live in `lib/` and a shared
  `references/critique.md` without a `SKILL.md` ever existing.
- **`design-extract`** collides with `project-starter-pack`'s `extract` by name and by
  purpose, and its output is validated by a starter-pack script (Plan 2 phase 3). It is
  better proposed as a *mode* of that skill, in that repo, than as a fifth skill here.

**The recommendation, then:** build the spec and `design-diagram`, keep `ux-audit` where it
is and describe it, and treat the remaining three as candidates that must each pass the
Part 0 membership test and clear the ledger before anyone writes a `SKILL.md`. That is a
smaller layer than the roadmap proposes and a real one. Four half-built skills is not.
