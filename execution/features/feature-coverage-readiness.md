# Feature Coverage Readiness Execution

Feature ID: feature-coverage-readiness
Status: validated
Why: Release reviewers need an optional stricter readiness gate that turns explicit local AC-to-test coverage links into blocking evidence without changing default readiness behavior.

## Milestones

- Extend the readiness report builder with an opt-in coverage-required mode.
- Register the CLI `--require-coverage` flag under `specspine feature ready`.
- Reuse the existing `## Test Coverage` parser and target existence semantics.
- Add focused tests for compatibility, pass/fail cases, output shape, exit codes, partial bundles, and local-only safety.
- Update project docs and agent guidance for high-risk or pre-release usage.
- Dogfood the feature with validated artifacts and checked local coverage links.

## Tasks

- [x] Add `require_coverage` support to `build_feature_ready_report` while preserving default report compatibility.
- [x] Add the `--require-coverage` CLI flag for `specspine feature ready`.
- [x] Implement the `feature.test_coverage` readiness check from existing parsed coverage links.
- [x] Include `coverage_required` in JSON only when the opt-in gate is active.
- [x] Add tests for default compatibility, passing coverage, failing coverage, text output, JSON output, exit codes, partial bundles, and local-only safety.
- [x] Update README, architecture, product, execution, review, and agent guidance.
- [x] Validate this dogfood bundle with default readiness, coverage-required readiness, and fused feature validation.

## Dependencies

- Existing `parse_test_coverage` behavior in `src/specspine/features.py`.
- Existing acceptance criteria parsing from native feature spec files.
- Python standard library `Path.exists` checks for local target files.
- Existing unit test suite under `tests/`.

## Open Questions

- Should a future workspace-level policy let maintainers require coverage readiness for selected priority levels automatically?
- Should a later report include separate counts for missing, unchecked, and missing-target coverage links?
