# PM_20260501/se-dirtying-living-docs: SE modified spec documents during TDD/review cycle without flow approval

## Failed At

Design review (passes 3–8) — the SE directly modified living specification documents (domain_model.md, technical_design.md, glossary.md, product_definition.md, system.md, context_map.md, feature file, ADRs) to fix inconsistencies found by the reviewer, without routing those changes through the appropriate flow states.

## Root Cause

The review-design skill has no instruction to distinguish between production code fixes (which the SE can make directly) and specification document fixes (which belong to different flow states and require approval). When the reviewer found cross-document inconsistencies, the SE treated spec docs the same as code — direct edit during the review cycle.

This violates the flow contract: spec documents are owned by specific states (architecture-assessment owns domain_model.md, technical-design owns technical_design.md, etc.). The development flow has no state that owns spec docs, so the SE has no authority to modify them.

## Missed Gate

The review-design skill says: "IF a smell is found → list it in findings" and "Write results to artifacts listed in the current state's out attrs. If findings affect artifacts outside the output contract, flag them in output notes for the appropriate step." The skill already instructs the SE to **flag** out-of-contract changes, not **make** them. The orchestrator ignored this instruction.

## Fix

1. **Process rule:** During TDD/review, the SE may ONLY modify production code and test code. Spec document inconsistencies must be FLAGGED in review output notes, not fixed directly.
2. **Review-design skill update:** Add an explicit rule: "NEVER modify specification documents (domain_model.md, technical_design.md, glossary.md, product_definition.md, system.md, context_map.md, ADRs, feature files) during review. These are owned by other flow states. Flag inconsistencies in output notes for the appropriate step."
3. **Flow mechanism:** When the reviewer flags spec doc inconsistencies, the orchestrator should create a separate issue/task to route those fixes through the appropriate flow state, rather than fixing them inline during development.

## Restart Check

- [ ] Review output notes contain flagged spec doc inconsistencies instead of inline fixes
- [ ] No spec documents are modified during the TDD/review cycle
- [ ] Spec doc fixes are routed through the appropriate flow state (architecture, planning, etc.)