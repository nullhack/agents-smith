# PM_20260501_missing-feature-test-template: No test stub template for BDD feature scenarios

## Failed At

project-structuring — SA generated test stubs using `...` ellipsis bodies and carried MoSCoW tags into docstrings, instead of the established `@pytest.mark.skip(reason="not yet implemented")` pattern.

## Root Cause

The `.templates/` directory has no template for feature BDD test stubs. The `structure-project` skill references design artifacts (feature file, technical design, domain model) but provides no test stub format to follow. Without a template, the agent invented its own conventions:

1. **`...` ellipsis bodies** instead of `@pytest.mark.skip(reason="not yet implemented")` — silently passing tests instead of being explicitly skipped
2. **MoSCoW tags (`Must`/`Should`) in `@id` lines** — the feature file had `@id:xxx Must` which leaked into test docstrings
3. **Naming convention** — `test_smith_commands_<id>` used instead of `test_<feature_slug>_<id>`

## Missed Gate

The `stubs_traceable` condition checks that all `@id` tags have corresponding test stubs, but does not validate:
- Whether stubs use the correct skip pattern
- Whether docstrings contain extraneous content (MoSCoW tags)
- Whether the naming convention matches project standards

## Fix

1. **Add template** `.templates/tests/features/<feature_slug>/<rule_slug>_test.py.template` with the canonical format:
```python
import pytest

@pytest.mark.skip(reason="not yet implemented")
def test_<feature_slug>_<@id>() -> None:
    """
    <@id steps raw text including new lines>
    """
```
2. **Update `structure-project` skill** to reference the new template when generating test stubs.
3. **Update `stubs_traceable` condition** to validate stub format (skip decorator, no MoSCoW in docstrings, naming convention).

## Restart Check

SA verifies that all test stubs use `@pytest.mark.skip(reason="not yet implemented")`, have no MoSCoW tags in docstrings, and follow the `test_<feature_slug>_<id>` naming convention.