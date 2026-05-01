---
name: select-feature
description: "Pick the next feature to develop based on business priority and delivery order"
---

# Select Feature

Load [[requirements/wsjf]] before starting.

1. IF more than one feature directory exists in `docs/features/` → stop; WIP limit is 1.
2. Verify that architecture covers the candidate features.
3. Score BASELINED features per [[requirements/wsjf]].
4. IF no features have `Status: BASELINED` → exit; features need scoping first.
5. Select the highest WSJF score among Dependency=0 features.
6. If all features have Dependency=1, resolve the blocking dependency first.
7. Write results to artifacts listed in the current state's `out` attrs. If findings affect artifacts outside the `out` contract, flag them in output notes for the appropriate step.
8. Check flow transitions to determine next state.