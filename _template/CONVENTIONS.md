# TODO-skill-name — maintainer conventions

*(Part 13. This is the **maintainer contract**, never loaded at runtime — that is `SKILL.md`.
Two documents, two audiences. Keep them separate or the runtime prompt grows past its cap.)*

## Sources of truth

TODO. Name each generated file and the source it is generated from. **Nobody hand-edits a
generated file**; regenerate it.

## The verbatim rule

TODO, **or state that this skill borrows nothing.** Part 12.3 is mandatory: a skill carrying
borrowed content declares it, because any repository absorbing this skill absorbs the
dependency. If content is copied verbatim from a source that cannot be re-derived, say so
here, mark it in the file, and say why paraphrasing would break it.

## Caps

`SKILL.md` ≤150 lines. Corpus files ≤120. Contract files uncapped — including `_format.md`,
which sits beside the corpus but is a contract, not corpus (Part 2.6).

## Script runtime

The gate path — registry build, output validation, fixture check — is **stdlib only**
(Part 3.6). A dependency is permitted only in a script the gate never calls. This is what lets
the gate run anywhere without a virtualenv; breaking it breaks CI for every skill in the pack,
not just this one.

## The maintenance loop

*(Part 11 — a skill that cannot learn rots.)*

- **Learning accumulates in:** TODO (name the file).
- **Minimum bar for an entry:** TODO (e.g. a new ID plus at least two observable symptoms).
- **Then:** regenerate the registry and re-run the fixtures.
