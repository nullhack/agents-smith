# PM_20260501_moscow-gherkin-tags: MoSCoW priority injected into Gherkin @id tags

## Failed At

bdd-features — stakeholder: "why should must etc [be] in the top of the examples?"

## Root Cause

The `moscow.md` knowledge file instructs the PO to "classify each candidate Example as Must/Should/Could" but doesn't specify where to record the classification. The `feature.feature.template` has no field for MoSCoW priority. The agent conflated classification (an internal triage step) with Gherkin output, appending MoSCoW labels to the `@id` tag line (`@id:SC-001 Must`) and later as separate tags (`@must @id:...`), neither of which belongs in the feature file.

## Missed Gate

The `write-bdd-features` skill loads `[[requirements/moscow]]` and `[[requirements/gherkin]]` but neither document states where MoSCoW classification should be recorded or that it should NOT appear in the .feature file. The skill instructions say "Classify each Example per [[requirements/moscow]]" without specifying the output location. The template's `@id:<unique-id>` format gives no hint about priority tagging.

## Fix

1. **`moscow.md`**: Add a note that MoSCoW classification is for internal triage only and must NOT appear as Gherkin tags or in the .feature file. Priority can be tracked in stories.md or a separate planning artifact.
2. **`write-bdd-features` skill (SKILL.md)**: Clarify step 4 — "Classify each Example per [[requirements/moscow]]" → add "Record classification in stories.md; do NOT add MoSCoW tags to Examples in the .feature file."
3. **`feature.feature.template`**: Add a comment in the template that `@id:` tags are for traceability only, not for priority classification.

## Restart Check

SA verifies that no `.feature` file contains `@must`, `@should`, `@could`, or MoSCoW labels on `@id` lines.