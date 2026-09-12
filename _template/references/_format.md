# Corpus format contract

**Delete this file if the skill has no corpus.** Part 2.1 is conditional: a corpus is
required only where the output cites IDs a validator must resolve. A skill with only an
output contract and a rubric is complete without one.

If a corpus is added, this file moves **into the corpus directory** beside the entries it
governs (Part 2.3 — that is where `ux-audit` keeps it), and states exactly what the generator
expects, so a contributor cannot write something unparseable by accident.

## What the generator requires

TODO, for each entry:

- **Frontmatter keys** — which are required, and the valid values for each enum.
- **The ID pattern** — and the rule that **IDs are immutable once published** (Part 2.5),
  because findings and fixtures cite them.
- **The body structure** — headings, tables, whatever the parser reads.
- **The exclusion marker** — how an entry is kept out of the registry deliberately.

## Generation fails loudly

*(Part 3.2)* The generator exits non-zero on a duplicate ID, a missing required frontmatter
key, an invalid enum value, or an empty source set. **A broken source never yields a silently
wrong registry** — that is the whole reason the registry is generated rather than written.

## Caps

Corpus entries: ≤120 lines each. **This file is a contract, not corpus, so it is uncapped**
(Part 2.6) despite living in the corpus directory.
