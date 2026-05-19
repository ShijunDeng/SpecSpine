# Spec-Backed Release Notes & Changelog Generation Execution

Feature ID: spec-release-notes
Status: implemented
Why: Aggregate validated and archived feature evidence into structured, user-facing release communication. Closes the last mile gap in spec-to-PR pipeline with deterministic, multi-format release artifacts.

## Milestones

- [x] M001: Core data structures (ReleaseEntry, BreakingChange, ReleaseNotesReport) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: Release feature collection filtering validated/archived status with metadata extraction.
- [x] M003: Feature grouping by priority/project/status/effort with sorted output.
- [x] M004: Breaking change detection using 5 regex patterns for removed args, removed fields, changed behavior, deprecations, renames.
- [x] M005: Summary computation with feature counts, breaking change counts by severity, priority breakdowns, and validation evidence totals.
- [x] M006: JSON, text, and JSON-lines renderers for multi-format release output.

## Tasks

- [x] T001: Implement ReleaseEntry dataclass with slug, title, priority, status_transition, ac_summary, validation_evidence_count, project, effort.
- [x] T002: Implement BreakingChange dataclass with feature_id, description, severity, affected_commands tuple.
- [x] T003: Implement ReleaseNotesReport dataclass with version, date_range, grouped_features, breaking_changes, summary, safety_notes.
- [x] T004: Implement _BREAKING_CHANGE_PATTERNS with 5 compiled regex patterns and severity/description tuples.
- [x] T005: Implement _extract_title using first markdown heading or feature ID fallback.
- [x] T006: Implement _extract_ac_summary counting AC items from spec's Acceptance Criteria section.
- [x] T007: Implement _count_validation_evidence counting [x] and [X] checkboxes in quality file.
- [x] T008: Implement _determine_status_transition mapping status to transition string (validated->newly validated, archived->released).
- [x] T009: Implement _collect_release_features filtering validated/archived features with metadata extraction.
- [x] T010: Implement _group_features grouping by priority/project/status/effort with sorted keys and entries.
- [x] T011: Implement _detect_breaking_changes scanning spec/execution content for breaking change patterns.
- [x] T012: Implement _compute_summary with feature counts, breaking change severity counts, priority counts, and validation evidence total.
- [x] T013: Implement _safety_notes returning immutable tuple of 3 safety messages.
- [x] T014: Implement build_release_notes_report as main entry point with since/until/group_by parameters.
- [x] T015: Implement render_release_notes_json and render_release_notes_text for standard output.
- [x] T016: Implement render_release_notes_json_lines for streaming newline-delimited JSON output.

## Dependencies

- src/specspine/features.py (FEATURE_FILE_PATHS, FEATURE_PRIORITIES, FEATURE_STATUSES, FeatureBundleNotFoundError, InvalidFeatureSlug, _extract_markdown_section, _extract_scalar, list_feature_bundles, read_feature_metadata)

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff spec-release-notes . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-release-notes . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-release-notes . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-release-notes . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace spec-release-notes . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-release-notes . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature spec-release-notes --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature spec-release-notes --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature spec-release-notes --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix spec-release-notes . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature spec-release-notes --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature spec-release-notes --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature spec-release-notes --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature spec-release-notes --json` to compose local pre-merge review evidence.
- Run `specspine feature ready spec-release-notes . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-release-notes . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-release-notes . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan spec-release-notes . --output-dir .specspine/sync-plan/spec-release-notes` to materialize local sync review artifacts.
- Run `specspine feature archive spec-release-notes . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
