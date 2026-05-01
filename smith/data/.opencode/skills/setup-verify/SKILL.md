---
name: setup-verify
description: "Verify transformations, clean template artifacts, and finalize the project"
---

# Setup Verify

1. Run smoke test: `uv sync --all-extras && uv run task test-fast`
2. IF smoke test fails:
   - IF failure is a stale import (contains "from app" or "import app") → fix using the same substitution pattern from `template-config.yaml`, then re-run
   - ELSE → report the error, set `tests_pass: false`, exit `failed`
3. Clean template-specific artifacts:
   - Delete `flowviz/data.js` (regeneratable)
   - Delete `docs/branding.md` (user creates their own)
   - Delete `.flowr/sessions/` contents if any exist
   - Delete `docs/adr/.gitkeep`, `docs/features/.gitkeep`, `docs/spec/` (template scaffolding)
4. Set git remote: `git remote set-url origin git@github.com:{github_username}/{project_name}.git`
5. Commit all changes: `git add -A && git commit -m "chore: initialize project from agents-smith"`
6. Set evidence:
   - `tests_pass`: true if smoke test passed
   - `imports_valid`: true if no import errors during test run
   - `artifacts_cleaned`: true if cleanup completed
7. IF all evidence is true → exit `initialized`; ELSE exit `failed`.
8. Tell the user which files were changed and next steps:

   ```bash
   # Push the initialized project
   git push -u origin main

   # Optional: rename the project folder (run from parent directory)
   cd .. && mv agents-smith {project_name}
   ```

   Then direct them to start the delivery workflow: `@product-owner` — the PO picks the first feature and begins planning.