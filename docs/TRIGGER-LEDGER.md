# Trigger ledger

The routing mechanism (decision D2). One row per **object of attention** — the thing a
skill looks at — naming its owner, the repository that owns it, and the phrases it claims.

`scripts/check_ledger.py` fails when two rows **this pack owns** claim the same phrase, so
defending a boundary is a diff review rather than a judgement call. Collisions between
repositories the pack does not own are reported as **known** and do not fail: the pack
cannot resolve them, and a permanently red gate teaches people to ignore it.

Seeded from Appendix B of `docs/EXECUTION-PLAN.md` with what is claimed **today**, so the
ledger starts from the real state rather than an empty file.

| Object of attention | Owner | Repo | Claimed phrases |
|---|---|---|---|
| A rendered surface (pixels) | `ux-audit` | `ux-audit-skill` | "audit this design", "UX review", "what's wrong with this screen" |
| A source tree, against briefs | `validate` | `project-starter-pack` | "validate the briefs", "check for contradictions", "review against DESIGN.md", "audit the code against the briefs", "find anti-patterns in the repo" |
| An existing product's identity | `extract` | `project-starter-pack` | "extract the briefs", "brownfield", "reverse engineer the design system", "infer the stack from the code" |
| A recent diff, multi-role | `/improve` | `agent-global-instructions` | "improvement review", "review the recent changes" |
| A screenshot, wrapper | `/ux-audit` | `agent-global-instructions` | "run a ux audit" |

## Known collisions, owned elsewhere

Neither is the pack's to resolve, and `check_ledger.py` reports both without failing.

These collide on a **concept**, not a literal phrase — "audit" means a rendered surface to
one skill and a source tree to another — so the duplicate-phrase check cannot see them.
They are declared here instead, in the same table shape, so that whoever adds the next
skill sees them.

| Shared term | Owner | Colliding owner | Why it is not resolvable here |
|---|---|---|---|
| audit | `ux-audit` | `validate` | One means a rendered surface, the other a source tree. The word is the same and the object is not. |
| UI/UX review | `ux-audit` | `/improve` | The harness command runs a multi-role panel that includes a UI/UX lens; the skill audits pixels against a corpus. |

## Reserved by the pack

On the objects nothing else claims:

- **A described structure plus `DESIGN.json`** — `design-diagram`, M3.

**Not reserved:** a source tree scanned for bans. That is the collision `DESIGN-PLAN.md` §7
raises against `project-starter-pack`'s `validate`, and reserving it before that question is
answered would be exactly the mistake this ledger exists to prevent.
