---
name: review-structure
description: "Verify test coverage, test quality, and behavior-vs-implementation coupling"
---

# Review Structure

Load [[software-craft/test-design]], [[software-craft/tdd]], and [[software-craft/code-review]] before starting.

1. Declare adversarial stance per [[software-craft/code-review#concepts]] — default hypothesis: "tests might be coupled to the wrong thing."
2. Verify tests specify observable behaviour, not implementation details, per [[software-craft/test-design#key-takeaways]].
3. IF a test breaks when refactoring preserves behaviour → flag it as implementation-coupled per [[software-craft/test-design#concepts]].
4. Verify tests operate at the same abstraction level as their acceptance criteria per [[software-craft/test-design#key-takeaways]].
5. Verify test coverage meets the project threshold.
6. Stop at the first failure per [[software-craft/code-review#key-takeaways]] — write a minimal REJECTED report with file:line evidence.
7. Write results to artifacts listed in the current state's `out` attrs. If findings affect artifacts outside the `out` contract, flag them in output notes for the appropriate step.
8. Check flow transitions to determine next state.