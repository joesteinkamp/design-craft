# design-craft — conventions

The task-craft layer. Skills are invoked when the *task* is of a kind, not when a
project is open and not as a harness feature. Read `docs/DESIGN-PLAN.md` for the
architecture and `docs/EXECUTION-PLAN.md` for the milestones; this file is the
short list of rules that hold while working in here.

## The pack is a destination, not a workshop

Decision D1: **skills evolve in their own repositories and are imported when
ready.** A skill directory here is a vendored copy of something that matured
elsewhere, the way `agent-global-instructions` treats `ux-audit`. Do not develop a
new skill in place — that is what its own repo is for.

The consequence: an import is the moment integrity matters. Verify a vendored tree
rather than trusting it, and never edit a vendored copy in place.

## The gate

`./test.sh` at the root, stdlib-only, and it ran before the pack had content on
purpose — every milestone needs something to fail against. Two rules keep it
honest:

- **Discovery is by directory, and an empty set passes.** No check asserts anything
  about skills that are not there.
- **A check that cannot fail is not a gate.** Each check is run against a
  deliberately broken fixture tree and required to exit non-zero. Add a check, add
  its breakage in the same commit.

Nothing on the gate path may gain a dependency. CI runs a stock Python; if a step
needs `pip install`, that step does not belong on the gate.

## Frozen, dual-homed contracts

Every CLI contract lives twice: in the owning `scripts/README.md` and in Appendix A
of `docs/EXECUTION-PLAN.md`. **Change both in the same commit or neither** —
`check_contracts.py` compares them in both directions, so adding a line to one
alone fails as loudly as editing one.

A contract is `(proposed)` until its script lands and may change freely until then;
it freezes on that script's first commit, and the marker changes in the same commit.

## Routing

Decision D2: the **trigger ledger** (`docs/TRIGGER-LEDGER.md`, written in M1) is the
mechanism; a router is a contingency behind the trip-wire in `DESIGN-PLAN.md` §3.2,
not a plan. A phrase claimed twice by rows this pack owns is a failing test.
Collisions between repositories the pack does not own are reported as known and do
not fail — the pack cannot resolve them.

## The acceptance test for the spec

> The spec must describe `ux-audit` accurately without requiring any change to it.

`ux-audit` stays in its own repository (D4: imported, never migrated), which is
what keeps that test honest — the subject is not something the spec's author can
quietly edit to fit.
