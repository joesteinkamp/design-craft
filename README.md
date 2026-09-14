# design-craft

The **task-craft layer** — layer 3 of a three-layer toolchain:

```
agent-global-instructions    the person layer    what's true regardless of which project is open
project-starter-pack         the project layer   what this product is, and what it may not look like
design-craft                 the task layer      invoked when the task is THIS KIND of design work
```

A layer-3 skill is invoked when the *task* is of a kind — not when a project is open, and not
as a harness feature. It carries its own corpus, scripts, and tests, and it degrades
gracefully when the project supplies nothing.
[`ux-audit`](https://github.com/joesteinkamp/ux-audit-skill) is the layer's first and, today,
only inhabitant. The layer does not need inventing; it needs specifying and populating.

## Status — M0–M2 complete; M3 onward stopped

**No skill lives here yet, and that is deliberate.** Milestone **M0 is complete**: the
repository has its gate, its frozen contracts, and CI *before* it has content, so every later
milestone has something to fail against. `./test.sh` passes on a checkout with zero skills and
is proven able to fail — each check is run against a deliberately broken fixture tree and
required to exit non-zero, because a check that cannot fail is not a gate.

**M1 is complete too.** [`SKILL-SHAPE.md`](SKILL-SHAPE.md) is the shape every skill in the layer
is built against, with each part carrying its **CONFIRMED / CORRECTED / PROPOSED** and
**mandatory / conditional** markings in the document itself — a reader can tell which rules
describe a working skill and which are proposals nobody has run. `_template/` is a skeleton
with every mandatory part stubbed and its contract stated, and it satisfies the spec it ships
beside. [`docs/TRIGGER-LEDGER.md`](docs/TRIGGER-LEDGER.md) records every phrase claimed today
across the three repositories, including the two collisions that already exist between repos
this pack does not own.

**The acceptance test is a command now:** `python3 scripts/check_shape.py <ux-audit-checkout>`
exits 0 against an unmodified checkout. If it ever fails there, the spec is wrong and gets
corrected — `ux-audit` is not edited to fit.

**M2 is complete.** `lib/fixtures.py` is the pack's one fixture runner — the generic half of
`ux-audit`'s `check_fixtures.py`, with the match predicate injected by the caller. It is an
**extraction, not a rewrite**, and its test proves that the only way it can be proven:
byte-for-byte identical output to the reference on all five shipped fixtures, then four
deliberate breakages that must fail and one boundary case that must not. Nothing else was
extracted — `lib/registry.py` waits for M3 to prove a second registry exists.

What exists: `test.sh` (13 checks, each proven able to fail), `scripts/` with four checkers,
`lib/fixtures.py`, `SKILL-SHAPE.md`, `_template/`, `docs/TRIGGER-LEDGER.md`, `CLAUDE.md`, and
CI on a stock Python — the gate path is stdlib-only by rule and may never gain a dependency.
**M3 onward is stopped, not pending.** The owner does not want `design-diagram`, which was to
be the layer's second skill and the first built *to* the spec rather than derived from one.
Without it there is no second inhabitant, and M4 (export), M5 (`slop-detect`, already
conditional and never approved) and M6 (disposition review) all existed to serve a populated
layer. They are not scheduled.

This is the conclusion `DESIGN-PLAN.md` §7 reached from the other direction — *"the evidence
supports a spec and two skills, not a layer of five"* — carried one step further by the person
who would have used them. The honest read now is **a spec and one skill**: `ux-audit`, which
already existed and stays in its own repository.

**What was built still stands on its own.** The gate, the shape spec, the ledger and the
fixture runner are a working description of what a layer-3 skill is, with a checker that
proves the description is accurate against a real skill. That has value as documentation of a
pattern even if nothing new is ever built to it — and if a second skill is ever wanted, M3's
plan is written and the scaffolding is here.

| Document | What it holds |
|---|---|
| [`docs/DESIGN-PLAN.md`](docs/DESIGN-PLAN.md) | The shape spec's table of contents, each part marked *confirmed* / *corrected* / *proposed* against `ux-audit` and *mandatory* / *conditional*; the routing discipline; the cross-repo dependencies; answers to the six open questions; recommendations on the five reserved decisions; and an honest read on whether this should be a five-skill layer at all. |
| [`docs/EXECUTION-PLAN.md`](docs/EXECUTION-PLAN.md) | Milestones M0–M6, each with the files it creates by path, a checkable gate, its cross-repo dependency, and where the owner must approve. Plus the sequence, the earliest useful stopping point, and **Appendix A** — the dual-homed CLI contracts. |

The split follows `ux-audit`'s own planning convention: a design plan for architecture, an
execution plan for milestones and frozen contracts.

## Decisions

**D1 is decided (2026-09-10):** monorepo as a *destination* — skills evolve in their
own repositories and are imported here when ready, the way `agent-global-instructions`
already treats `ux-audit`. This largely dissolves §7's "should this be five skills"
framing: the layer becomes a place skills arrive once they have earned it, not a count
decided up front. It also promotes the **import path** to the gating question, and
`DESIGN-PLAN.md` §6 D1 records what is actually true about it today.

**D4 is decided (2026-09-10):** `ux-audit` is **imported, not migrated.** It stays at
[`joesteinkamp/ux-audit-skill`](https://github.com/joesteinkamp/ux-audit-skill) and is
vendored in, which is D1's pattern applied to the skill that already followed it. The
spec's acceptance test — *describes `ux-audit` without requiring a change to it* — stays
honest for free, because the subject is not something the spec's author can edit.

**D3 is closed as moot (2026-09-10):** it asked which skill to build *second*, which
presumed the pack builds its own skills in sequence. D1 removed that premise — skills
mature in their own repositories and arrive when ready, so there is no queue to order.
Nothing replaces it.

**D5 is decided (2026-09-10):** keep the name `design-craft`. No rename.

**D2 is decided (2026-09-10):** the **trigger ledger**, with the router deferred behind
the trip-wire §3.2 states. A ledger row per trigger names the skill and its object of
attention, and the gate fails when two skills claim the same object — so defending the
boundary is a diff review rather than a judgement call. No action needed until a second
skill exists to collide with.

**All five decisions are settled.** §7's five-skill framing is dissolved by D1 rather
than answered: skills arrive when they have earned it.

## Cross-repo status, 2026-09-05

`project-starter-pack` #18 shipped the guardrail registry, its fixtures, and the token
contrast validator. That satisfies the dependency `DESIGN-PLAN.md` §4.2 recorded as unbuilt
and approval-gated, and it removes the strongest clause from decision **D3** (which skill is
built second). D3 is flagged in place for re-decision; the arguments that survive are noted
there. Nothing else in either plan changes.

## The acceptance test

> The spec must describe `ux-audit` accurately without requiring any change to `ux-audit`.
> If it doesn't, the spec is wrong, not the skill.

Milestone M1 mechanises this as `scripts/check_shape.py`, which must exit 0 against an
unmodified `ux-audit` checkout — and must keep exiting 0 after every later skill is added.

## Reading order

Start with `docs/DESIGN-PLAN.md` §1, which lists what was read and what was run, including
three findings from executing `ux-audit`'s own scripts that shape the plan more than the
roadmap does. Then §2 for the spec's table of contents, §3 for the routing discipline, and §7
for the honest read. `docs/EXECUTION-PLAN.md` is the how and the when.
