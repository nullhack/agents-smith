---
name: define-done
description: "Define the quality gates that must pass before the feature is considered complete"
---

# Define Done

Load [[software-craft/code-review#key-takeaways]] before starting.

1. Define quality gates per [[software-craft/code-review#key-takeaways]] — design correctness, test quality, and conventions.
2. Incorporate quality attributes from the product definition into the gates.
3. Write results to artifacts listed in the current state's `out` attrs. If findings affect artifacts outside the `out` contract, flag them in output notes for the appropriate step.
4. Check flow transitions to determine next state.