---
name: accept-feature
description: "Validate business behavior against BDD scenarios from the end user's perspective"
---

# Accept Feature

Load [[requirements/gherkin#key-takeaways]] and [[software-craft/test-design#key-takeaways]] before starting.

1. Verify all BDD scenarios pass from the end user's perspective, not the test harness, per [[software-craft/test-design#key-takeaways]].
2. IF a scenario passes in the test harness but fails from the user's perspective → flag it as a semantic alignment gap per [[software-craft/test-design#concepts]].
3. Verify quality attributes are met.
4. Verify definition of done criteria are satisfied.
5. Write results to artifacts listed in the current state's `out` attrs. If findings affect artifacts outside the `out` contract, flag them in output notes for the appropriate step.
6. Check flow transitions to determine next state.