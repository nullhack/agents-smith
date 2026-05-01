---
name: commit-implementation
description: "Commit the reviewed, passing implementation with traceability to feature files"
---

# Commit Implementation

Load [[software-craft/git-conventions#key-takeaways]] before starting.

1. Verify all tests pass and all three review gate evidences (design, structure, conventions) are present.
2. Commit with traceability per [[software-craft/git-conventions#content]] — use granular commit format with @id tags.
3. IF the commit is a refactoring (no behavior change) → use `refactor(<scope>):` type per [[software-craft/git-conventions#concepts]].
4. Write results to artifacts listed in the current state's `out` attrs. If findings affect artifacts outside the `out` contract, flag them in output notes for the appropriate step.
5. Check flow transitions to determine next state.