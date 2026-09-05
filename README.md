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

## Status — plans only

**No skill lives here yet, and that is deliberate.** This repository currently holds two
planning documents and nothing else. Milestone M0 has not started.

| Document | What it holds |
|---|---|
| [`docs/DESIGN-PLAN.md`](docs/DESIGN-PLAN.md) | The shape spec's table of contents, each part marked *confirmed* / *corrected* / *proposed* against `ux-audit` and *mandatory* / *conditional*; the routing discipline; the cross-repo dependencies; answers to the six open questions; recommendations on the five reserved decisions; and an honest read on whether this should be a five-skill layer at all. |
| [`docs/EXECUTION-PLAN.md`](docs/EXECUTION-PLAN.md) | Milestones M0–M6, each with the files it creates by path, a checkable gate, its cross-repo dependency, and where the owner must approve. Plus the sequence, the earliest useful stopping point, and **Appendix A** — the dual-homed CLI contracts. |

The split follows `ux-audit`'s own planning convention: a design plan for architecture, an
execution plan for milestones and frozen contracts.

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
