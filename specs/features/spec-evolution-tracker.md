# Spec Evolution Tracker

Feature ID: spec-evolution-tracker
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Track spec changes over time, compute semantic diffs between versions, and assess downstream impact on tasks, tests, and dependent features.

## Users

- Developers who need to understand how a feature's spec has evolved across git commits.
- Tech leads who review spec changes for breaking impacts on dependent features.
- QA engineers who need to know which ACs were added, removed, or modified between versions.
- Release managers who need change classification and remediation plans for spec modifications.

## Scope

- `get_git_diff(slug, root, base, unstaged)` returns a `DiffResult` with per-file hunks, added/removed/modified line counts, and summary.
- `classify_changes(diff_result, slug, root)` returns a `ClassificationResult` with classified changes (added/removed/modified) for ACs, tasks, and file-level modifications between base and current versions.
- `resolve_impact(changes, slug, root)` returns an `ImpactResult` with impact entries for each change, classifying severity as breaking, warning, or info based on downstream references.
- `calculate_risk_level(change, impact)` returns risk level string (breaking/warning/info) based on change type and impact severity.
- `generate_remediation_plan(changes, impacts)` returns prioritized `RemediationAction` list for non-info impacts sorted by priority (1=highest).
- `build_evolution_timeline(slug, root, limit)` returns list of `EvolutionEntry` from git log with change counts and categories (added/removed/modified).
- Change classification detects AC additions/removals, task additions/removals, file-level modifications, and metadata changes (Priority, Owner, Milestone, etc.).
- Impact resolution finds downstream references via trace reports, test reports, and feature file scanning for dependent features.
- JSON and text renderers (`render_diff_json/text`, `render_evolution_json/text`) provide structured and human-readable output.

## Non-Goals

- Does not execute tests or verify actual runtime behavior changes.
- Does not modify any feature bundles or source files.
- Does not provide real-time change monitoring; each call is a point-in-time snapshot.
- Does not handle merge conflict resolution or automatic spec reconciliation.
- Does not track changes outside of feature peer files (spec, execution, quality).

## Acceptance Criteria

- [x] AC001: `get_git_diff` returns a `DiffResult` with slug, files list of DiffFileHunk objects, and summary property computing files_changed, total_added, total_removed, total_modified.
- [x] AC002: `DiffFileHunk` includes path, diff_hunks list, added_lines, removed_lines, and modified_lines computed from hunk parsing.
- [x] AC003: `classify_changes` returns `ClassificationResult` with changes list detecting added, removed, and modified ACs and tasks between base and current versions.
- [x] AC004: Change classification handles 4 scenarios: both missing (skip), base missing/new file (all current items as added), current missing/deleted file (all before items as removed), both exist (diff-based added/removed/modified).
- [x] AC005: Metadata changes are detected by comparing Priority, Owner, Milestone, Target Release, Project, Effort, and Status fields between base and current spec.
- [x] AC006: `resolve_impact` returns `ImpactResult` with impacts list classifying removed ACs with downstream refs as breaking, modified ACs as warning/info, and added items as info.
- [x] AC007: `_find_downstream_references` discovers references in other features' acceptance criteria text, test coverage links, and feature file content using dependency patterns.
- [x] AC008: `generate_remediation_plan` produces `RemediationAction` objects with action_id, description, priority (1-3), and target_file for non-info impacts.
- [x] AC009: `build_evolution_timeline` returns `EvolutionEntry` list from git log with commit_hash, date, author, message, change_count, and categories (added/removed/modified).
- [x] AC010: `InvalidGitBaseError` raised when base reference is invalid; `GitDiffError` available for diff failures; empty `DiffResult` returned when no peer files exist.

## Edge Cases

- No peer files exist: `get_git_diff` returns empty `DiffResult` with no files; `build_evolution_timeline` returns empty list.
- Base commit doesn't have the file: all current ACs/tasks classified as added; no before content for comparison.
- Current file doesn't exist: all before ACs/tasks classified as removed.
- No git history: `build_evolution_timeline` returns empty list; classification uses current file content only.
- Circular dependencies in downstream references: `_find_downstream_references` scans each feature independently; no recursion occurs.
- Metadata fields unchanged: no metadata change entry generated; only differing metadata produces classified changes.
- Line number lookup fails: `_find_line_number` returns 0 when search text not found in content.

## Constraints

- Git operations use `subprocess.run` with 30-second timeout.
- Diff hunk parsing splits on `@@` markers; line counting excludes `+++` and `---` lines.
- Change IDs use sequential CHG{counter:03d} format; action IDs use ACT{counter:03d} format.
- Dependency patterns match: "depends on", "after", "blocked by", "requires" followed by feature slug.
- Feature ID regex matches `Feature ID: <slug>` in spec frontmatter.
- Safety: no test execution, subprocess calls (except git), network access, or token reads.

## Traceability Notes

- Source: src/specspine/evolution.py (1058 lines)
- Tests: tests/test_evolution.py
- Diff computation: src/specspine/evolution.py lines 257-309
- Change classification: src/specspine/evolution.py lines 371-561
- Impact resolution: src/specspine/evolution.py lines 631-781
- Remediation plan: src/specspine/evolution.py lines 800-896
- Evolution timeline: src/specspine/evolution.py lines 899-957
- Risk level calculation: src/specspine/evolution.py lines 784-797
- Text/JSON renderers: src/specspine/evolution.py lines 960-1058
