# PM_20260501_conflict-exit-code-removal: Planned code removed as "dead" — distinction between dead code and TDD-not-yet-reached code

## Failed At

Design review (7th pass) — reviewer flagged ConflictReport and EXIT_CONFLICT = 2 as "dead code" and "cross-document inconsistency." They were removed. On reflection, the interview notes (`IN_20260501_smith-commands-specification.md:58,66`) explicitly define exit code 2 for conflicts. The code was removed, then restored, then removed again.

## Root Cause

The reviewer operates at the feature level (current TDD examples) while the SA created typed stubs at the architecture level. Code that matches the domain model and technical design but hasn't been reached by the TDD cycle yet is **planned code**, not dead code. Dead code contradicts the architecture; planned code hasn't been exercised yet.

## Missed Gate

The review skill has no step to check whether flagged "dead code" exists in the domain model, technical design, or interview notes before recommending removal. Without this check, planned code is indistinguishable from dead code.

## Fix

1. **Remove planned code now (TDD perspective):** From a strict TDD perspective, code that no test exercises should not exist yet. ConflictReport and EXIT_CONFLICT = 2 are removed. When the feature requires exit code 2 scenarios (e.g., a fresh project with existing agentic files), they will be added back organically through the RED-GREEN-REFACTOR cycle.
2. **Process change for the template:** Stubs should be created per-feature during feature planning, not all at once during project-structuring. This eliminates the planned-but-not-reached gap entirely. The SA creates the package skeleton (directories, `__init__.py`, port interfaces, aggregate root signatures); feature planning creates typed stubs only for the examples defined in the `.feature` file.
3. **Review skill update:** Before flagging code as "dead," the reviewer must check the domain model / technical design / interview notes. Code that matches the architecture but lacks tests should be flagged as WARN (planned-not-reached), not REJECT (dead).

## Restart Check

- [x] ConflictReport and EXIT_CONFLICT = 2 removed from code
- [x] Spec docs consistent: exit codes are 0 (success) and 1 (error)
- [x] Feature file has no examples asserting exit code 2
- [ ] When a future feature requires exit code 2, it will be added via TDD (RED test first, then implementation)