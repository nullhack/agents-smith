# ADR_20260501_smith-yaml-metadata

## Status

Superseded — The stakeholder decided smith should be stateless. Connection state is now inferred from the `# smith managed` section in `.gitignore`, with source metadata stored in the section header (e.g., `# smith managed source:agents-smith`). No separate `.smith.yaml` file is created. This decision supersedes ADR-004's original recommendation of a dedicated metadata file.

## Context

smith needs to persist connection state between commands. `smith status` must report which template source was used and when the connection was established. `smith update` must know which template source to refresh from. `smith disconnect` must know what to remove. This state must survive process termination — it cannot be in-memory only.

Forces:
- The connection state must be queryable by `smith status` without re-deriving it
- `smith update` must know the original template source (default agents-smith, or `--from <path/url>`)
- The project directory is the only reliable persistence location (smith has no config directory)
- Zero runtime dependency constraint means no PyYAML or other parsing libraries
- The metadata file is created on connect and removed on disconnect, following the same lifecycle as the agentic files

## Interview

| Question | Answer |
|---|---|
| How should smith persist connection state? | Simple YAML file in the project root (.smith.yaml) |

## Decision

Use a `.smith.yaml` file in the project root to persist connection state. The file contains `template_source` and `connected_at` fields in simple `key: value` format. The file is created on `smith connect`, read by `smith status` and `smith update`, and removed on `smith disconnect`.

## Reason

A simple key-value YAML file in the project root is the most discoverable and debuggable persistence mechanism. It's human-readable, version-controllable, and can be parsed without PyYAML by using a simple line-splitting approach. The file follows the same lifecycle as the agentic files (created on connect, removed on disconnect).

## Alternatives Considered

- **SQLite database in .smith/:** Over-engineered for two fields. Rejected because it adds binary state and requires a runtime dependency for proper SQLite handling.
- **JSON file (.smith.json):** Valid alternative, but JSON is less human-readable for simple key-value data and doesn't support comments. Rejected in favor of YAML's comment support for explaining fields.
- **No persistence (derive state from file presence):** Fragile — cannot distinguish between "connected with default agents-smith" and "files happened to be there." Also cannot determine the original `--from` source for `smith update`. Rejected because it violates the consistency invariant.
- **Git configuration (git config):** Only works in git repositories. smith must work in non-git directories. Rejected.

## Consequences

- (+) Connection state is human-readable and debuggable
- (+) `.smith.yaml` follows the same lifecycle as the agentic files — created on connect, removed on disconnect
- (+) Simple format parseable without PyYAML — maintains zero runtime dependency constraint
- (+) `smith status` can report template source and connection time without re-deriving
- (-) `.smith.yaml` is visible in the project directory — mitigated by adding it to the managed .gitignore section
- (-) If a user manually edits `.smith.yaml`, state could become inconsistent — mitigated by documenting that `.smith.yaml` is managed by smith and should not be edited manually
- (-) Simple YAML format cannot represent complex nested structures — mitigated by YAGNI; only two fields are needed

## Risk Assessment

| Risk | Probability | Impact | Mitigation | Accepted? |
|------|------------|--------|------------|-----------|
| User manually edits .smith.yaml causing inconsistent state | Low | Medium | Document in .smith.yaml comments that it is managed by smith; detect corruption on status/update commands | Yes |
| .smith.yaml conflicts with other tools using same filename | Low | Low | The `.smith.` prefix is specific to this tool; collision is unlikely | Yes |
| Simple YAML parser cannot handle edge cases | Low | Low | Only two fields with string values; no complex types needed | Yes |