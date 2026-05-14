# Offline Pull Request Draft Export Quality

Feature ID: feature-pr-draft
Status: validated
Why: The PR draft bridge must be reviewable, local, deterministic, and credential-free before agents rely on it.

## Required Checks

- [x] CLI parser accepts `feature pr` with `--json`, `--output`, and `--force`.
- [x] JSON output exposes the required PR draft fields with deterministic ordering.
- [x] Text output uses GitHub Markdown checklist syntax for reviewable evidence.
- [x] Partial bundles produce drafts with missing files, gaps, and blocking checks.
- [x] Missing bundles return non-zero and invalid slugs return `2`.
- [x] Output files refuse overwrite unless `--force` is passed.
- [x] Tests confirm the command does not require `gh`, GitHub tokens, subprocess calls, or network access.
- [x] Documentation and agent instructions describe the command as an offline draft bridge.

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-pr-draft . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature pr feature-pr-draft . --json`.
- Run the repository GitHub personal access token prefix scan with ripgrep.

## Review Notes

- The implementation composes existing local evidence and does not create a GitHub adapter or remote synchronization layer.
- The `--output` file contains only the PR body so callers can paste or bridge it into external tools while stdout remains JSON when requested.

## Release Readiness

- [x] Unit tests cover the new command behavior.
- [x] Dogfood feature bundle is validated and ready.
- [x] Documentation identifies the command as local, offline, and token-free.
- [x] No upstream source code is vendored.
