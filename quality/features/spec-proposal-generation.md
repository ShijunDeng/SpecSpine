# Spec Proposal Generation Quality

Feature ID: spec-proposal-generation
Status: implemented
Why: Generate structured spec bundles from natural language intent using deterministic, zero-dependency heuristics

## Required Checks

- [x] [severity: high] [owner: SpecSpine maintainers] Acceptance criteria are reviewed against implementation evidence.
- [x] [severity: high] [ci: test_propose] Test coverage proves the changed behavior and edge cases.
- [x] Documentation, release notes, or PR draft reflect user-facing behavior.
- [x] `specspine feature ready spec-proposal-generation . --json` has no blocking checks after evidence is complete.
- [x] `specspine validate . --fusion --features` passes.

## Test Coverage

Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

- [x] AC001 -> tests/test_propose.py
- [x] AC002 -> tests/test_propose.py
- [x] AC003 -> tests/test_propose.py
- [x] AC004 -> tests/test_propose.py
- [x] AC005 -> tests/test_propose.py
- [x] AC006 -> tests/test_propose.py
- [x] AC007 -> tests/test_propose.py
- [x] AC008 -> tests/test_propose.py
- [x] AC009 -> tests/test_propose.py
- [x] AC010 -> tests/test_propose.py

## Test Plan

- Unit test: intent parsing with simple intent "add dark mode"
- Unit test: intent parsing with complex intent "add dark mode toggle and user preferences with persistence"
- Unit test: EARS generation produces event-driven criteria with WHEN keyword
- Unit test: EARS generation produces conditional criteria with IF keyword
- Unit test: task decomposition generates tasks with _Boundary and _Depends annotations
- Unit test: quality check generation creates 1:1 mapping with acceptance criteria
- CLI test: --dry-run mode prints content without file writes
- CLI test: --dry-run mode fails on existing bundles unless --force is passed
- CLI test: --json mode outputs structured JSON
- CLI test: long intent is truncated and warnings appear in text and JSON output
- CLI test: --force mode overwrites existing bundle
- CLI test: auto-generated slug passes validate_feature_slug() validation
- Integration test: propose -> validate . --features passes
- Integration test: propose -> feature ready passes after all sections populated

## Review Notes

- Review EARS format compliance against industry standards
- Verify task dependency ordering is topologically correct
- Confirm zero-dependency constraint is maintained (no imports beyond stdlib)
- Validate generated content has no TODO placeholders in key sections

## Release Readiness

- [x] Acceptance criteria, tasks, required checks, and test plan evidence are complete.
- [x] Docs, release notes, or `specspine feature pr spec-proposal-generation . --json` output are ready for reviewers.
- [x] `specspine feature sync-plan spec-proposal-generation . --json` has been reviewed before any remote GitHub sync.
- [x] `specspine feature ready spec-proposal-generation . --json` and `specspine validate . --fusion --features` have been run.
- [x] No known blockers remain, or blockers are documented in review notes.
