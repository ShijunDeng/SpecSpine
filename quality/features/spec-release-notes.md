# Spec-Backed Release Notes & Changelog Generation Quality

Feature ID: spec-release-notes
Status: implemented
Why: Aggregate validated and archived feature evidence into structured, user-facing release communication. Closes the last mile gap in spec-to-PR pipeline with deterministic, multi-format release artifacts.

## Required Checks

- [x] QC001: All 10 acceptance criteria verified against release.py implementation - dataclasses, feature collection, grouping, breaking change detection, summary computation, and multi-format renderers match spec.
- [x] QC002: Test coverage in test_release.py proves release feature collection filtering validated/archived status.
- [x] QC003: Test coverage proves breaking change detection using 5 regex patterns for removed args, fields, changed behavior, deprecations, and renames.
- [x] QC004: `specspine feature ready spec-release-notes . --json` has no blocking checks after evidence is complete.
- [x] QC005: `specspine validate . --fusion --features` passes.

## Test Coverage

Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

- [x] AC001 -> tests/test_release.py
- [x] AC002 -> tests/test_release.py
- [x] AC003 -> tests/test_release.py
- [x] AC004 -> tests/test_release.py
- [x] AC005 -> tests/test_release.py
- [x] AC006 -> tests/test_release.py
- [x] AC007 -> tests/test_release.py
- [x] AC008 -> tests/test_release.py
- [x] AC009 -> tests/test_release.py
- [x] AC010 -> tests/test_release.py

## Test Plan

- Unit tests for ReleaseEntry, BreakingChange, ReleaseNotesReport dataclasses and as_dict methods.
- Unit tests for _extract_title verifying markdown heading extraction and feature ID fallback.
- Unit tests for _extract_ac_summary verifying AC counting from spec section.
- Unit tests for _count_validation_evidence verifying [x]/[X] checkbox counting.
- Unit tests for _determine_status_transition verifying status-to-transition mapping.
- Unit tests for _collect_release_features filtering validated/archived features only.
- Unit tests for _group_features verifying grouping by priority/project/status/effort with sorted output.
- Unit tests for _detect_breaking_changes verifying 5 regex pattern matching and deduplication.
- Unit tests for _compute_summary verifying feature counts, breaking change severity counts, and priority breakdowns.
- Integration tests for end-to-end release notes generation with real feature bundles.

## Review Notes

- Release notes generation is read-only file analysis with no modification or external publishing.
- Breaking change detection uses heuristic regex patterns; not guaranteed to catch all breaking changes.
- Multi-format output supports JSON, markdown text, and newline-delimited JSON for streaming.
- Safety notes consistently confirm no commands executed, no tests run, no external access.

## Release Readiness

- [x] RR001: All 10 acceptance criteria, 16 tasks, 5 required checks, and test plan evidence are complete.
- [x] RR002: `specspine feature pr spec-release-notes . --json` output is ready for reviewers.
- [x] RR003: `specspine tests impact . --feature spec-release-notes --json` has been reviewed for focused local test commands.
- [x] RR004: `specspine consistency scan . --feature spec-release-notes --json` has been reviewed for local spec-code-test-doc drift.
- [x] RR005: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
- [x] RR006: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
- [x] RR007: `specspine coverage plan . --feature spec-release-notes --json` has been reviewed if missing AC coverage remains.
- [x] RR008: `specspine verify matrix spec-release-notes . --json` has been reviewed for AC-level verification evidence.
- [x] RR009: `specspine change risk . --feature spec-release-notes --json` has been reviewed for changed-path risk evidence.
- [x] RR010: `specspine security cues . --feature spec-release-notes --json` has been reviewed for security-sensitive cues.
- [x] RR011: `specspine provenance manifest . --feature spec-release-notes --json` has been reviewed for local evidence hashes.
- [x] RR012: `specspine review packet . --feature spec-release-notes --json` has been reviewed for local pre-merge evidence.
- [x] RR013: `specspine feature sync-plan spec-release-notes . --json` has been reviewed before any remote GitHub sync.
- [x] RR014: `specspine feature archive spec-release-notes . --json` has been reviewed before marking status archived.
- [x] RR015: `specspine feature ready spec-release-notes . --json` and `specspine validate . --fusion --features` have been run.
- [x] RR016: No known blockers remain, or blockers are documented in review notes.
