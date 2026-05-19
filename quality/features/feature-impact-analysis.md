# Feature Impact Analysis Quality

Feature ID: feature-impact-analysis
Status: implemented
Why: Analyze the downstream impact of feature changes before implementation. Predict which features, tests, and code will be affected by proposed spec modifications.

## Required Checks

- [ ] TODO: Acceptance criteria are reviewed against implementation evidence.
- [ ] TODO: Test coverage proves the changed behavior and edge cases.
- [ ] TODO: Documentation, release notes, or PR draft reflect user-facing behavior.
- [ ] TODO: `specspine feature ready feature-impact-analysis . --json` has no blocking checks after evidence is complete.
- [ ] TODO: `specspine validate . --fusion --features` passes.

## Test Coverage

Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

- [ ] AC001 -> tests/...

## Test Plan

- TODO: Add unit, integration, CLI, manual, or exploratory checks that prove each acceptance criterion.

## Review Notes

- TODO: Capture review findings, decisions, and follow-up work.

## Release Readiness

- [ ] TODO: Acceptance criteria, tasks, required checks, and test plan evidence are complete.
- [ ] TODO: Docs, release notes, or `specspine feature pr feature-impact-analysis . --json` output are ready for reviewers.
- [ ] TODO: `specspine tests impact . --feature feature-impact-analysis --json` has been reviewed for focused local test commands.
- [ ] TODO: `specspine consistency scan . --feature feature-impact-analysis --json` has been reviewed for local spec-code-test-doc drift.
- [ ] TODO: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
- [ ] TODO: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
- [ ] TODO: `specspine coverage plan . --feature feature-impact-analysis --json` has been reviewed if missing AC coverage remains.
- [ ] TODO: `specspine verify matrix feature-impact-analysis . --json` has been reviewed for AC-level verification evidence.
- [ ] TODO: `specspine change risk . --feature feature-impact-analysis --json` has been reviewed for changed-path risk evidence.
- [ ] TODO: `specspine security cues . --feature feature-impact-analysis --json` has been reviewed for security-sensitive cues.
- [ ] TODO: `specspine provenance manifest . --feature feature-impact-analysis --json` has been reviewed for local evidence hashes.
- [ ] TODO: `specspine review packet . --feature feature-impact-analysis --json` has been reviewed for local pre-merge evidence.
- [ ] TODO: `specspine feature sync-plan feature-impact-analysis . --json` or `--output-dir .specspine/sync-plan/feature-impact-analysis` has been reviewed before any remote GitHub sync.
- [ ] TODO: `specspine feature archive feature-impact-analysis . --json` has been reviewed before marking status archived.
- [ ] TODO: `specspine feature ready feature-impact-analysis . --json` and `specspine validate . --fusion --features` have been run.
- [ ] TODO: No known blockers remain, or blockers are documented in review notes.
