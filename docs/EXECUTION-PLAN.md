# Execution plan — `design-craft`

Companion to [`DESIGN-PLAN.md`](DESIGN-PLAN.md), which holds the shape spec's table of
contents, the routing discipline, the answers to the open questions, and the recommendations
on the five reserved decisions. This document holds milestones, gates, and the frozen CLI
contracts.

**Status: plan only. No skill exists in this repo.** Milestone M0 has not started.

**Appendix A is load-bearing.** The CLI contracts are dual-homed — they live here and in each
skill's `scripts/README.md`, and the rule inherited from `ux-audit` is *change both in the same
commit or don't change them*. M0's gate makes that rule a test rather than a promise.

---

## Milestone map

| # | Milestone | Blocks on | Owner approval |
|---|---|---|---|
| M0 | Repo scaffold, the gate, CI | — | D5 (repo name) before M1 |
| M1 | `SKILL-SHAPE.md`, `_template/`, the trigger ledger | M0 | D2 (routing), D4 (migration) |
| M2 | `lib/fixtures.py` — the shared gate runner | M1 | — |
| M3 | `design-diagram` — the first skill built *to* the spec | M1, M2 | D3 (which skill second) |
| M4 | Export + install path | M3 | harness Plan 1 phase 6 |
| M5 | `slop-detect` — conditional | M4, starter-pack Plan 2 phase 1 | **required, twice** |
| M6 | Disposition review — migration, critique, extract | M3 (M5 if built) | D4 re-decided |

---

## M0 — Repo scaffold, the gate, and CI

**What changes.** The repository gets its gate before it gets any content, so that every
later milestone has something to fail against. `./test.sh` is written first and passes with
zero skills present — it discovers skills by directory and asserts nothing about a set that
is empty. The checks it performs are the ones from `DESIGN-PLAN.md` §5 Q6, each written as a
separate function so a milestone can add its check without touching the others. Everything on
this path imports stdlib only, so CI needs a stock Python and nothing else. The root
`CLAUDE.md` records the pack's own conventions, mirroring what `ux-audit/CLAUDE.md` does for
one skill.

**Files created**

```
README.md
CLAUDE.md
test.sh
.github/workflows/ci.yml
scripts/check_caps.py
scripts/check_contracts.py
scripts/check_ledger.py
scripts/README.md
lib/__init__.py
```

**Gate.** `./test.sh` exits 0 on a checkout with no skills, and exits non-zero for each of
these deliberate breakages, verified one at a time: a `scripts/README.md` line edited so it
no longer matches Appendix A (`check_contracts.py`); a duplicate phrase added to the ledger
(`check_ledger.py`); a file pushed past its cap (`check_caps.py`). `.github/workflows/ci.yml`
runs `./test.sh` on push and on pull request, green, on a runner with no virtualenv and no
Pillow installed.

**Cross-repo dependency.** None.

**Owner approval.** D5 — the repo name — should be settled before M1 writes the spec, since
the spec is the first document that names the pack in prose that other repos will cite.

---

## M1 — The shape spec, the template, and the trigger ledger

**What changes.** `SKILL-SHAPE.md` is written to the table of contents in `DESIGN-PLAN.md` §2,
with every part carrying its **confirmed / corrected / proposed** marking and its **mandatory /
conditional** marking in the document itself — a reader must be able to tell, without leaving
the file, which rules are descriptions of a working skill and which are proposals nobody has
run yet. `_template/` is a skeleton, not a skill: every mandatory part present as a stub with
its contract stated and its content marked `TODO`. `docs/TRIGGER-LEDGER.md` is seeded with
every trigger phrase claimed today by `ux-audit`, `project-starter-pack`'s three skills, and
the harness's `/ux-audit` and `/improve` — including the collisions that already exist between
those, recorded as known and owned elsewhere rather than silently omitted.

The milestone's own instrument is `scripts/check_shape.py`, which takes a skill directory and
verifies the mandatory parts and the caps. It is what turns the acceptance test into a command.

**Files created**

```
SKILL-SHAPE.md
docs/TRIGGER-LEDGER.md
scripts/check_shape.py
_template/SKILL.md
_template/CONVENTIONS.md
_template/references/_format.md
_template/references/output-contract.md
_template/references/rubric.md
_template/scripts/README.md
_template/scripts/validate_output.py
_template/fixtures/clean/expected.json
_template/fixtures/README.md
```

**Gate.** Two commands, both checkable:

1. `python3 scripts/check_shape.py <path-to-ux-audit-checkout>` **exits 0 against an
   unmodified `ux-audit`.** This is the brief's acceptance test, mechanised: if the checker
   fails, the spec is wrong and gets corrected — `ux-audit` is not edited. The checker must
   have been run against a read-only checkout, and the run recorded in the commit message.
2. `./test.sh` passes, with `check_ledger.py` now reading a non-empty ledger and reporting the
   pre-existing cross-repo collisions as **known**, not as failures the pack can fix.

The spec is not gated on being *written* — per the brief, that is not a gate. It is gated on
describing the one skill that exists, without touching it.

**Cross-repo dependency.** Read-only access to the `ux-audit-skill` checkout. Nothing is
written there.

**Owner approval.** D2 (routing architecture) and D4 (whether `ux-audit` migrates) both change
what the spec says. D2 determines whether Part 14's ledger stands alone or names a router;
D4 determines whether the spec is written about a skill inside the pack or outside it. Neither
blocks starting M1, both block finishing it.

---

## M2 — `lib/fixtures.py`, the shared gate runner

**What changes.** The generic half of `ux-audit`'s `check_fixtures.py` becomes the pack's one
fixture runner: the directory walk, `must_find` / `must_not_find`, `max_severity`,
`max_findings`, score bounds, baseline drift at ±10, and the itemized non-zero exit. The
skill-specific half — the match predicate — is injected by the caller. Nothing else is
extracted; `lib/registry.py` waits for M3 to prove a second registry actually exists, per the
two-consumers rule in `DESIGN-PLAN.md` §5 Q1.

**Files created**

```
lib/fixtures.py
lib/tests/test_fixtures.py
```

**Gate.** `lib/fixtures.py`, given `ux-audit`'s match predicate, reproduces
`check_fixtures.py`'s output on all five of `ux-audit`'s shipped fixtures — same PASS/FAIL per
fixture, same found/missed lines, exit 0 — run against a read-only checkout with no edits to
it. Then, one at a time: a `must_find` deleted from a fixture copy makes it fail; a
`must_not_find` principle injected into a findings copy makes it fail; a baseline moved by 11
makes it fail. `./test.sh` runs `lib/tests/test_fixtures.py` on the stdlib-only path.

**Cross-repo dependency.** Read-only `ux-audit` checkout, as the reference implementation to
reproduce.

**Owner approval.** None.

---

## M3 — `design-diagram`, the first skill built to the spec — **NOT PROCEEDING (2026-09-14)**

> **Stopped by the owner:** *"I don't need that skill. I don't get it."* Recorded here rather
> than left looking pending, so no later session picks it up as scheduled work.
>
> Two things had already narrowed the case. `DESIGN-PLAN.md` §7 concluded the evidence
> supported a spec and two skills rather than five, and the gap this skill was to fill —
> diagrams falling through to whatever the model reached for — was substantially closed on
> 2026-09-10 by a *rule* instead: `agent-global-instructions`' artifact policy now states when
> a diagram earns its place and what it must be (inline SVG or mermaid, selectable labels,
> both themes, no shapes invented to balance a composition). A rule costs nothing to maintain;
> a skill costs a corpus, a validator, fixtures and a gate.
>
> **M4, M5 and M6 are stopped with it.** M4 (export) has nothing to export, M5
> (`slop-detect`) was already conditional and never approved, and M6 (disposition review)
> reviews a populated layer. The plan below is kept as written — it is the record of a
> decision, and if a second skill is ever wanted it starts here.

**What changes.** The first skill the pack owns. It reads a described structure and a project's
`DESIGN.json` when one exists, and emits an SVG diagram whose colours resolve to that project's
tokens. It exercises the parts of the spec most at risk of being `ux-audit`-shaped: a registry
of **types** rather than principles, and a validator over an **emitted artifact** rather than
over a findings file. `runtime: stdlib` — no Pillow, no browser — so it installs by copying
files while the `.venv` question in `DESIGN-PLAN.md` §4.1 is still open. Token resolution is
written *inside* this skill, not in `lib/`; it moves to `lib/tokens.py` only when a second
consumer exists.

**Files created**

```
skills/design-diagram/SKILL.md
skills/design-diagram/CONVENTIONS.md
skills/design-diagram/references/_format.md
skills/design-diagram/references/types/*.md          (one per diagram type)
skills/design-diagram/references/registry.json        (generated)
skills/design-diagram/references/output-contract.md
skills/design-diagram/references/rubric.md
skills/design-diagram/scripts/README.md
skills/design-diagram/scripts/build_registry.py
skills/design-diagram/scripts/resolve_tokens.py
skills/design-diagram/scripts/validate_diagram.py
skills/design-diagram/scripts/check_fixtures.py
skills/design-diagram/scripts/gen_fixtures.py
skills/design-diagram/assets/diagram-template.svg
skills/design-diagram/fixtures/<name>/{spec.json,expected.json}
lib/registry.py
```

**Gate.** The full acceptance test, in four parts:

1. `python3 scripts/check_shape.py skills/design-diagram` exits 0 — the skill conforms to the
   spec it was built to.
2. `python3 scripts/check_shape.py <ux-audit-checkout>` **still** exits 0 — the spec did not
   drift toward the new skill and away from the old one. Both must pass in the same run.
3. A diagram generated inside `project-starter-pack`'s `examples/saga-reader/` uses that
   project's tokens: every colour literal in the emitted SVG resolves to a token in its
   `DESIGN.json`, checked by `validate_diagram.py`, exit 0. The same generation run with no
   `DESIGN.json` present degrades to the bundled defaults **and says so in its output** — the
   graceful-degradation rule, tested rather than asserted.
4. `./test.sh` passes, now covering two registries, and `lib/registry.py` is only introduced
   here — where a second registry proves it is shared rather than assumed.

**Cross-repo dependency.** Read-only access to `project-starter-pack`'s
`examples/saga-reader/DESIGN.json` as the token fixture. No change is requested there.

**Owner approval.** D3 — that `design-diagram` is the skill built second rather than
`slop-detect`. This is the recommendation in `DESIGN-PLAN.md` §6, and it is the one decision
that determines whether M3 or M5 comes first.

---

## M4 — Export and install path

**What changes.** The pack learns to ship. A build step exports each skill as a
self-contained directory, copying `lib/` into each export so that no export depends on the
monorepo layout — this is the condition attached to D1 in `DESIGN-PLAN.md` §6, and it exists
because the harness's `install_skill_link()` iterates `.agents/skills/*/` and pairs each
directory with a same-named `skill-backed: true` command, a layout the pack cannot change
from here. The milestone also produces the written ask to the harness, because three things
must be resolved there and this is the milestone that is blocked by them.

**Files created**

```
export.sh
scripts/check_export.py
docs/INSTALL.md
docs/ASK-HARNESS.md
```

**Gate.** `./export.sh <dir>` produces one directory per skill, each of which passes
`check_shape.py` **and** whose fixture check runs from the exported copy alone — no path
resolving back into this repository, verified by exporting into a temporary directory and
running the gate there with the source checkout moved aside. `check_export.py` fails if any
exported file references a path outside its own export.

**Cross-repo dependency — this is the gating risk.** `docs/ASK-HARNESS.md` states the three
asks from `DESIGN-PLAN.md` §4.1 and must be answered before the pack can claim to be
installable:

1. **A directory lock verified by the harness's own tooling.** Today `computedHash` matches
   neither the vendored `SKILL.md` nor upstream's, nothing recomputes it, and `audit.sh` never
   mentions skills — so the lock verifies nothing, and the vendored `ux-audit` has already
   drifted a full release behind upstream undetected. A `skillDir` manifest hash is the
   roadmap's proposal; the addition the pack needs is that `audit.sh` recompute and check it.
2. **A pack shape at the install boundary** — N exported directories with N command files, or
   a pack mode that links one directory. The export step is built here on the assumption of
   the first, because it needs no harness change.
3. **A `.venv` answer, for `ux-audit` only.** Vendoring copies files, not environments. The
   pack sidesteps this for its own skills by the stdlib-only gate rule and by
   `design-diagram` being `runtime: stdlib`; it does not sidestep it for `ux-audit`, whose
   `SKILL.md` line 14 points every invocation at a `.venv` that no script in that repository
   creates.

**Owner approval.** The asks go to the harness repo, which is the owner's. Nothing in M4
proceeds to "installable" without an answer to ask 1.

---

## M5 — `slop-detect` — conditional, and not yet approved

**What changes.** Conditional on two approvals and one external build. If it proceeds, it is
the **narrowed** skill from `DESIGN-PLAN.md` §5 Q4: it reads a source tree, never a rendered
page. It consumes the project's `guardrails/registry.json`, cites ban IDs, computes token-pair
contrast arithmetic in stdlib, and reports the render-dependent bans as `unmeasurable`,
naming `ux-audit` as the instrument for them. It ships **no canonical ban list**; with no
project registry it falls back to a bundled default set and the report says that it did.

**Files created** (only if approved)

```
skills/slop-detect/SKILL.md
skills/slop-detect/CONVENTIONS.md
skills/slop-detect/references/output-contract.md
skills/slop-detect/references/rubric.md
skills/slop-detect/references/fallback-bans.md       (fallback only — never canonical)
skills/slop-detect/scripts/README.md
skills/slop-detect/scripts/scan_tree.py
skills/slop-detect/scripts/contrast.py
skills/slop-detect/scripts/validate_output.py
skills/slop-detect/scripts/check_fixtures.py
skills/slop-detect/fixtures/<ban-id>/{trips,clean,expected.json}
lib/tokens.py                                        (extracted here — second consumer)
```

**Gate.** It runs against a real starter-pack project, cites ban IDs that resolve in that
project's `guardrails/registry.json`, and its fixtures pass **including the clean ones** —
the clean fixtures are the point, since a grep-based detector dies of false positives.
Separately: run with no project registry present, the output states that the bundled fallback
was used. And `check_shape.py` still exits 0 against `ux-audit` and against `design-diagram`.

**Cross-repo dependency.** `project-starter-pack` Plan 2 phase 1 — the guardrail registry —
which does not exist. The pack needs ban IDs, a `detect:` field or `manual`, a severity, and a
stable registry path relative to a project root.

**Owner approval — required twice, and this is why M5 is last of the build milestones.**
First, in `project-starter-pack`: its `AGENTS.md` lists *"a change would grow the command
surface, or add a slot, question, or guardrail"* among the things that require asking, and
building the registry restructures all five guardrail files. Second, here: `DESIGN-PLAN.md` §7
argues that once narrowed, `slop-detect` overlaps substantially with that repo's own
`validate` skill plus its edit hook — same registry, same tree, same bans — and that it may be
better built as a **depth mode of `validate`, in that repo**, than as a skill here. That
question should be answered before any file in this milestone is written.

---

## M6 — Disposition review

**What changes.** No new skill. A written review, once the spec has survived contact with at
least one skill built to it, that settles three things the plan deliberately left open: whether
`ux-audit` migrates in (D4, recommended **never** — the pack itself is a directory and tests
the lock just as well, and migration imports the unverifiable `qualia` dependency); whether
`design-critique` is a skill at all or a shared rubric plus validator that other skills load,
given it has no phrase a user actually says; and whether `design-extract` belongs here or as a
mode of `project-starter-pack`'s existing `extract`, which it collides with by name and whose
output a starter-pack script already validates.

**Files created**

```
docs/DISPOSITION.md
```

**Gate.** Each of the three questions answered with a decision and a reason, and each answer
reflected in `docs/TRIGGER-LEDGER.md` — a skill that is not going to be built has its claimed
phrases released back, so the ledger never reserves a trigger surface for something nobody is
writing.

**Cross-repo dependency.** None to proceed. D4's answer depends on M4 ask 1 having been
resolved, since "the pack installs as one locked directory" is the property migration was
supposed to prove.

**Owner approval.** All three are the owner's calls. This milestone exists to put them, once,
with evidence from a spec that has been used rather than only written.

---

## Sequence

M0 → M1 → M2 → M3 → M4 → (M5 if approved) → M6.

M2 can run in parallel with M1's later half once the spec's Part 4 is settled, since the
fixture runner's contract is fixed by `ux-audit`'s existing `expected.json` shape and not by
anything the spec changes. Nothing else parallelises usefully: M3 is the test of M1, and M4 is
the test of M3.

### The earliest point at which stopping still leaves something useful

**After M3.** At that point the pack has a shape spec that has been proven twice — it
describes an untouched `ux-audit` and it describes a skill built to it from scratch — plus one
working skill that fills a real gap, plus a gate and CI that keep both honest. That is the
outcome the brief names as real: *a spec with one skill built to it*. Everything after M3 is
distribution and expansion.

Stopping earlier is worth less but is not worthless. **After M1** the pack has a spec that
demonstrably describes the one skill in the layer, which is a durable artifact even if no
second skill is ever written — it is the document that says what the existing skill is, and
`check_shape.py` keeps that claim true. **After M2** it additionally has the shared gate
runner, which `ux-audit` could adopt whether or not it ever migrates.

Stopping between M3 and M6 is the shape to avoid: `slop-detect` half-built against a registry
that does not exist yet is precisely the *four half-built skills* outcome the brief warns
about. M5 is written as conditional and last for that reason.

---

## Appendix A — CLI contracts (dual-homed)

**The rule, inherited from `ux-audit`:** these contracts are frozen. They live here and in the
owning `scripts/README.md`. **Change both in the same commit or don't change them.** M0's
`check_contracts.py` fails the gate when the two copies disagree, which is the difference
between this appendix and the one it is modelled on.

**Freezing point.** A contract below is *proposed* until the script it describes lands; it
freezes on that script's first commit. Contracts for scripts that do not exist yet are marked
**(proposed)** and may change freely until then. Every script here is stdlib-only unless its
entry says otherwise; the ones on the gate path may never gain a dependency.

### Pack-level — `scripts/README.md`

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

### `lib/` — `lib/README.md`

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

### `skills/design-diagram/scripts/README.md` — (proposed, M3)

```
build_registry.py                       # references/types/*.md -> references/registry.json
resolve_tokens.py DESIGN_JSON [--json out.json]
validate_diagram.py DIAGRAM_SVG [--tokens resolved.json]
check_fixtures.py fixtures/ [--only NAME]
gen_fixtures.py [--only NAME]
```
`resolve_tokens.py` resolves the default `color` block and each `themes.<mode>.color` override
layer, unwraps `$value`, and emits numeric slots bare. Reports a token as `unresolved` rather
than substituting a default. `validate_diagram.py` exits 1 with itemized errors: structural
violations, and any colour literal that does not resolve to a token when `--tokens` is given.

### `skills/slop-detect/scripts/README.md` — (proposed, M5, conditional)

```
scan_tree.py PATH [--registry guardrails/registry.json] [--json out.json]
contrast.py DESIGN_JSON [--pairs default]
validate_output.py findings.json
check_fixtures.py fixtures/ [--only NAME]
```
`scan_tree.py` cites ban IDs from the project registry; with none, it uses the bundled
fallback and sets `meta.fallback_used: true`, which `validate_output.py` requires to be
surfaced in the report. `contrast.py` computes OKLCH → sRGB → relative luminance in stdlib and
reports a ratio per pair; it never estimates.

### Inherited and unchanged — `ux-audit`

`ux-audit`'s contracts are reproduced in its own `scripts/README.md` and are **not** restated
here. The pack does not own them, does not freeze them, and under the recommendation in
`DESIGN-PLAN.md` §6 D4 will not absorb them. `check_shape.py` reads that skill; it never
writes to it.

---

## Appendix B — Trigger ledger, seed entries

The full ledger is written in M1 as `docs/TRIGGER-LEDGER.md` and checked by `check_ledger.py`.
These are the entries that exist **before the pack ships anything**, recorded here so M1 starts
from the real state rather than an empty file. Two collisions already exist between repositories
the pack does not own; they are logged as known, and the pack's own entries are chosen to avoid
adding a third.

| Object of attention | Owner | Repo | Claimed phrases |
|---|---|---|---|
| A rendered surface (pixels) | `ux-audit` | `ux-audit-skill` | "audit this design", "UX review", "what's wrong with this screen", audit/review/critique a design, screenshot, mockup, or UI flow |
| A source tree, against briefs | `validate` | `project-starter-pack` | "validate the briefs", "check for contradictions", "review against DESIGN.md", "audit the code against the briefs", "find anti-patterns in the repo" |
| An existing product's identity | `extract` | `project-starter-pack` | "extract the briefs", "brownfield", "reverse engineer the design system", "infer the stack from the code" |
| A recent diff, multi-role | `/improve` | `agent-global-instructions` | improvement review of recent changes, including a UI/UX role |
| A screenshot, wrapper | `/ux-audit` | `agent-global-instructions` | delegates to the `ux-audit` skill when present; inline fallback otherwise |

**Known collisions, owned elsewhere:** `ux-audit` ↔ `validate` on *audit*; `ux-audit` ↔
`/improve` on the UI/UX review surface. The pack cannot resolve either; `check_ledger.py`
reports them and does not fail on them.

**Reserved by the pack, on the objects nothing else claims:** a described structure plus
`DESIGN.json` (`design-diagram`, M3). A source tree scanned for bans (`slop-detect`, M5) is
**not** reserved here — it is the collision `DESIGN-PLAN.md` §7 raises against `validate`, and
reserving it before that question is answered would be the mistake this ledger exists to
prevent.
