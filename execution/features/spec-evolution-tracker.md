# Spec Evolution Tracker Execution

Feature ID: spec-evolution-tracker
Status: implemented
Why: Track spec changes over time, compute semantic diffs between versions, and assess downstream impact on tasks, tests, and dependent features.

## Milestones

- [x] M001: Core data structures (DiffFileHunk, DiffResult, ClassifiedChange, ClassificationResult, ImpactEntry, ImpactResult, RemediationAction, EvolutionEntry) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: Git diff computation with hunk parsing and line counting for feature peer files.
- [x] M003: Change classification detecting AC/task additions, removals, modifications, and metadata changes.
- [x] M004: Downstream reference discovery across feature traces, test reports, and file content.
- [x] M005: Impact resolution with severity classification (breaking/warning/info) based on change type and downstream refs.
- [x] M006: Remediation plan generation with priority-sorted actions for non-info impacts.
- [x] M007: Evolution timeline construction from git log with change counts and categories.
- [x] M008: JSON and text renderers for diff and evolution outputs.

## Tasks

- [x] T001: Implement DiffFileHunk and DiffResult dataclasses with summary property and as_dict methods.
- [x] T002: Implement ClassifiedChange and ClassificationResult dataclasses with summary property.
- [x] T003: Implement ImpactEntry and ImpactResult dataclasses with summary property.
- [x] T004: Implement RemediationAction and EvolutionEntry dataclasses with as_dict methods.
- [x] T005: Implement GitDiffError and InvalidGitBaseError exception classes.
- [x] T006: Implement _run_git utility with 30-second subprocess timeout.
- [x] T007: Implement _parse_diff_hunks splitting diff output on @@ markers.
- [x] T008: Implement _count_lines_in_hunks counting added (+) and removed (-) lines excluding +++/--- headers.
- [x] T009: Implement get_git_diff computing per-file diff results with optional base reference and unstaged mode.
- [x] T010: Implement _extract_ac_ids and _extract_task_ids using regex patterns.
- [x] T011: Implement _extract_feature_refs using DEPENDENCY_PATTERNS and FEATURE_ID_RE.
- [x] T012: Implement _build_versioned_content loading current and git-based file content for spec/execution/quality.
- [x] T013: Implement classify_changes comparing before/after versions for AC/task additions, removals, and modifications.
- [x] T014: Implement metadata change detection comparing Priority, Owner, Milestone, Target Release, Project, Effort, Status fields.
- [x] T015: Implement _find_downstream_references scanning other features' traces, test reports, and file content.
- [x] T016: Implement resolve_impact classifying impacts as breaking/warning/info based on change type and downstream references.
- [x] T017: Implement calculate_risk_level returning risk string based on change type and impact severity.
- [x] T018: Implement generate_remediation_plan producing priority-sorted RemediationAction list for non-info impacts.
- [x] T019: Implement build_evolution_timeline from git log with diff stat parsing and category classification.
- [x] T020: Implement render_diff_json/text and render_evolution_json/text for output formatting.

## Dependencies

- src/specspine/dependency.py (build_dependency_graph)
- src/specspine/features.py (FEATURE_FILE_PATHS, InvalidFeatureSlug, build_feature_trace_report, build_feature_tests_report, feature_bundle_paths, list_feature_bundles, validate_feature_slug)

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff spec-evolution-tracker . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-evolution-tracker . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-evolution-tracker . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-evolution-tracker . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace spec-evolution-tracker . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-evolution-tracker . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature spec-evolution-tracker --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature spec-evolution-tracker --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature spec-evolution-tracker --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix spec-evolution-tracker . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature spec-evolution-tracker --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature spec-evolution-tracker --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature spec-evolution-tracker --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature spec-evolution-tracker --json` to compose local pre-merge review evidence.
- Run `specspine feature ready spec-evolution-tracker . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-evolution-tracker . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-evolution-tracker . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan spec-evolution-tracker . --output-dir .specspine/sync-plan/spec-evolution-tracker` to materialize local sync review artifacts.
- Run `specspine feature archive spec-evolution-tracker . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
