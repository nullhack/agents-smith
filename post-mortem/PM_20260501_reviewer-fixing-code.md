# PM_20260501_reviewer-fixing-code: Reviewer fixing code instead of rejecting and routing back to TDD

## Failed At

review-gate (Design/Structure/Conventions review) — stakeholder: "Why are reviewers not done properly? Why is R fixing code instead of moving the state back to TDD with a description of what needs to be changed?"

## Root Cause

Three process violations occurred simultaneously, all stemming from conflating the reviewer role with the implementer role:

1. **Reviewer approved despite code smells**: The design review passed on checks 4-9 (Object Calisthenics, code smells, pattern gaps) with "minor" or "acceptable trade-off" verdicts for issues that should have been REJECTED — specifically: union return type in `_filter_conflicts`, duplicated logic between `_filter_conflicts`/`_skip_unmanaged`, dead `detect_state()` method, unreachable ConflictReport path, unused `project_dir` parameter, and two duplicated write-and-commit blocks in `connect()`.

2. **Fixes applied by orchestrator instead of routing back to TDD**: When the first design review REJECTED on `.smith.yaml` inconsistency, the orchestrator fixed `technical_design.md`, `system.md`, `glossary.md`, and ADR-004 directly, then re-ran the review. This should have been: REJECT → route back to TDD cycle with findings → SE implements fixes → re-review.

3. **Conventions review bypassed the flow**: Lint errors (ruff) and type errors (pyright) were fixed directly by the orchestrator instead of being treated as review findings. The conventions review should have REJECTED with a list of violations, then routed back for the SE to fix them in a TDD cycle.

## Missed Gate

The **review-gate** state in the development flow. The flow defines three review sub-gates (Design, Structure, Conventions). Each should produce either APPROVED or REJECTED. On REJECTED, the flow should transition back to the TDD cycle with specific findings — not apply fixes inline.

The reviewer's job is to find problems and report them. The SE's job is to fix them. The orchestrator conflated these by having the reviewer/subagent report findings, then immediately fixing them itself before re-running the review.

## Fix

1. **Reviewer MUST NOT modify production code or tests.** The reviewer's output contract is findings only — a REJECTED report with file:line evidence or an APPROVED verdict. No edits.

2. **On REJECTED, route back to TDD cycle** with the specific findings as input. The SE (or orchestrator acting as SE) picks up the findings, implements fixes, re-runs tests, then re-enters the review gate.

3. **"Minor" is not a pass.** Code smells that are acknowledged but hand-waved as "acceptable trade-offs" should still be flagged. The reviewer should note them; the SE decides whether to fix or defer. Deferring requires explicit acknowledgment, not silent approval.

4. **Spec doc fixes are still code changes.** When a review finds that spec docs are inconsistent with implementation, the fix is: REJECT → route back to the appropriate flow state (e.g., technical-design or adr-draft) → that state's owner applies the fix → re-review. The orchestrator should not fix docs on behalf of another state's owner.

5. **Lint/type errors are review findings, not auto-fix opportunities.** Running `ruff --fix` or manually fixing lint errors during review is the SE's job, not the reviewer's. The conventions review should report violations; the SE fixes them in the next TDD cycle.

## Restart Check

SA verifies that:
- [ ] All three review sub-gates produce APPROVED/REJECTED verdicts without modifying any files
- [ ] On REJECTED, the flow transitions back to TDD with a findings document
- [ ] No code or spec doc changes are made during the review-gate state
- [ ] Code smells are explicitly listed in findings rather than dismissed as "minor"
