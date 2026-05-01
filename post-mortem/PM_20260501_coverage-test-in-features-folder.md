# PM_20260501/coverage-test-in-features-folder: Coverage-boosting test placed in features folder instead of unit folder

## Failed At

Structure review — adding a test for the `disconnect()` empty-patterns branch to reach 100% coverage.

## Root Cause

The reviewer identified that `connection.py:82` (`return []` when `has_section()` is True but `get_patterns()` returns empty) was not covered by any BDD example. Instead of flagging this as a gap that requires either a new BDD example (if the behavior is user-facing) or a unit test in `tests/unit/` (if it's an implementation branch), the SE added a test function directly to `tests/features/smith_commands/disconnect_test.py`.

The `tests/features/` folder is exclusively for BDD scenario tests that trace back to `@id` tags in the `.feature` file. The new test `test_smith_commands_disconnect_empty_patterns` has no corresponding `@id` tag in the feature file, violating the traceability contract.

## Missed Gate

The TDD skill and structure review skill both require that feature tests correspond to BDD examples. Coverage-boosting tests that exercise implementation branches not covered by BDD examples belong in `tests/unit/`, not `tests/features/`.

## Fix

1. Move `test_smith_commands_disconnect_empty_patterns` from `tests/features/smith_commands/disconnect_test.py` to `tests/unit/domain/test_connection.py` (or a new unit test file for Connection).
2. Remove the BDD-style docstring (Given/When/Then) since it's a unit test, not a feature test.
3. Write the test as a plain unit test with a descriptive function name.
4. Ensure the test still covers the `connection.py:82` branch for 100% coverage.

## Restart Check

- [ ] No tests in `tests/features/` lack a corresponding `@id` tag in the feature file
- [ ] Coverage-boosting tests are in `tests/unit/`, not `tests/features/`
- [ ] Feature tests use BDD-style docstrings with `@id` tags; unit tests use plain descriptive names