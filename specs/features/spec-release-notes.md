# Spec-Backed Release Notes & Changelog Generation

Feature ID: spec-release-notes
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Aggregate validated and archived feature evidence into structured, user-facing release communication. Closes the last mile gap in spec-to-PR pipeline with deterministic, multi-format release artifacts.

## Users

- Release managers who need automated release notes from validated and archived features.
- Engineering managers who need release summaries with feature counts, priority breakdowns, and breaking change reports.
- Developers who need to understand which features are included in a release and their status transitions.
- QA engineers who need validation evidence counts per feature for release readiness assessment.

## Scope

- `build_release_notes_report(root, since, until, group_by)` returns a `ReleaseNotesReport` with version, date_range, grouped_features, breaking_changes, summary, and safety_notes.
- `_collect_release_features` collects features with status "validated" or "archived", extracting title, priority, status_transition, ac_summary, validation_evidence_count, project, and effort.
- `_group_features` groups features by priority, project, status, or effort with sorted groups and sorted entries within each group.
- `_detect_breaking_changes` scans spec and execution content for breaking change patterns: removed CLI args (high), removed required fields (high), changed defaults/behavior (medium), deprecated args (low), renamed args (medium).
- `_compute_summary` computes features_total, features_validated, features_archived, breaking_changes by severity, priority_counts, and total_validation_evidence.
- `_determine_status_transition` maps status to transition string: validated->"newly validated", archived->"released (archived)", implemented->"implemented (pending validation)".
- `_extract_ac_summary` counts acceptance criteria from spec file's Acceptance Criteria section.
- `_count_validation_evidence` counts checked items ([x] or [X]) in quality file.
- `render_release_notes_json` produces standard JSON output; `render_release_notes_text` produces markdown-formatted release notes.
- `render_release_notes_json_lines` produces newline-delimited JSON with one JSON object per line for streaming consumption.
- Date range formatting: since+both->"since..until", since only->"since..latest", until only->"initial..until", neither->"all".

## Non-Goals

- Does not execute tests, invoke subprocesses, call network services, or read tokens.
- Does not modify any feature bundles or generate actual release artifacts on disk.
- Does not publish release notes to any external system or API.
- Does not include features that are not validated or archived in the release.
- Does not provide real-time release monitoring; each call is a point-in-time snapshot.

## Acceptance Criteria

- [x] AC001: `build_release_notes_report` returns a `ReleaseNotesReport` with version="1", date_range, grouped_features dict, breaking_changes list, summary dict, and safety_notes tuple.
- [x] AC002: `_collect_release_features` only includes features with status "validated" or "archived"; skips other statuses and invalid slugs.
- [x] AC003: `ReleaseEntry` includes slug, title (extracted from first markdown heading or feature ID), priority, status_transition, ac_summary, validation_evidence_count, project, and effort.
- [x] AC004: `_group_features` groups by priority/project/status/effort with sorted group keys and sorted entries within each group by slug.
- [x] AC005: `_detect_breaking_changes` uses 5 regex patterns to detect removed CLI args, removed required fields, changed defaults/behavior, deprecated args, and renamed args.
- [x] AC006: Breaking change severity: high for removed CLI args and required fields, medium for changed behavior and renamed args, low for deprecations.
- [x] AC007: `BreakingChange` includes feature_id, description, severity, and affected_commands tuple sorted and deduplicated.
- [x] AC008: `_compute_summary` computes features_total, features_validated, features_archived, breaking_changes by severity (high/medium/low), priority_counts, and total_validation_evidence.
- [x] AC009: `render_release_notes_text` produces markdown with Summary, Features by Priority, Features (grouped), Breaking Changes, and Safety Notes sections.
- [x] AC010: `render_release_notes_json_lines` produces newline-delimited JSON with type:"release_notes" header, type:"feature" entries, and type:"breaking_change" entries.

## Edge Cases

- No validated or archived features: grouped_features is empty dict; summary shows all zeros; text output has empty Features section.
- Feature with no spec file: title defaults to slug with hyphens replaced by spaces and title-cased; ac_summary shows "No acceptance criteria section found".
- Feature with no quality file: validation_evidence_count is 0.
- Breaking change pattern matches multiple times: deduplicated by description; affected_commands deduplicated using set.
- Group by invalid key: defaults to "all" group containing all features.
- Since/until date range formatting: handles all 4 combinations (both, since only, until only, neither).
- JSON lines format: each entry is a complete valid JSON object on its own line for streaming parsers.

## Constraints

- Breaking change detection uses heuristic regex patterns on spec/execution content; not guaranteed to catch all breaking changes.
- Title extraction uses first markdown heading (line starting with "# "); falls back to feature ID.
- Validation evidence counting uses `[x]` and `[X]` checkbox patterns only.
- Grouping keys are sorted alphabetically; entries within groups sorted by slug.
- Safety notes confirm no commands executed, no tests run, no subprocess/network/token access.
- Feature status filtering is strict: only "validated" and "archived" included.

## Traceability Notes

- Source: src/specspine/release.py (464 lines)
- Tests: tests/test_release.py
- Release data structures: src/specspine/release.py lines 22-84
- Breaking change patterns: src/specspine/release.py lines 86-112
- Title extraction: src/specspine/release.py lines 115-122
- AC summary: src/specspine/release.py lines 125-132
- Validation evidence counting: src/specspine/release.py lines 135-143
- Status transition: src/specspine/release.py lines 146-155
- Feature collection: src/specspine/release.py lines 158-230
- Feature grouping: src/specspine/release.py lines 233-255
- Breaking change detection: src/specspine/release.py lines 258-304
- Summary computation: src/specspine/release.py lines 307-337
- Main entry point: src/specspine/release.py lines 348-378
- Text/JSON renderers: src/specspine/release.py lines 381-464
