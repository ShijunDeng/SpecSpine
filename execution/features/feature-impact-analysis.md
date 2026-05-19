# Feature Impact Analysis Execution

Feature ID: feature-impact-analysis
Status: implemented
Why: Analyze the downstream impact of feature changes before implementation. Predict which features, tests, and code will be affected by proposed spec modifications.

## Milestones

- [x] M001: Core data structures (ImpactItem, ImpactAnalysis) implemented with frozen dataclasses and as_dict serialization.
- [x] M002: Downstream feature dependency detection via slug reference scanning and shared path matching.
- [x] M003: Test file impact detection via content scanning, AC text matching, and quality link extraction.
- [x] M004: Source code impact detection via glob patterns and local path reference resolution.
- [x] M005: Risk score computation with severity weighting and item count thresholds.
- [x] M006: Mitigation step generation with category-specific and risk-threshold-based recommendations.
- [x] M007: Recommended command generation for standard impact analysis workflow.
- [x] M008: JSON and text renderers for impact analysis output.

## Tasks

- [x] T001: Implement ImpactItem dataclass with type, id, path, severity, reason, affected_acs fields.
- [x] T002: Implement ImpactAnalysis dataclass with feature_id, total_affected, impacted_features/tests/code, risk_score, mitigation_steps, safety_notes, recommended_commands.
- [x] T003: Implement _relative_path utility with ValueError fallback to full path.
- [x] T004: Implement _read_text utility with OSError and UnicodeDecodeError handling.
- [x] T005: Implement _extract_acceptance_criteria to parse AC items from spec content with ID and text extraction.
- [x] T006: Implement _find_affected_features scanning all slugs for dependency references and shared path matches.
- [x] T007: Implement _extract_slugs_from_text using EXPLICIT_DEP_PATTERNS for dependency extraction.
- [x] T008: Implement _find_affected_tests with three detection methods: content scanning, AC text matching, quality link extraction.
- [x] T009: Implement _find_referenced_acs extracting AC IDs from test file content.
- [x] T010: Implement _find_affected_code via src/**/*.py glob scanning and local path reference resolution.
- [x] T011: Implement _module_name utility converting file paths to dotted module names.
- [x] T012: Implement _find_slug_symbols extracting def/class symbols from lines mentioning the slug.
- [x] T013: Implement _compute_risk_score with severity weighting (high=15, medium=8, low=3) and count thresholds.
- [x] T014: Implement _generate_mitigation_steps with category-specific and risk-threshold steps.
- [x] T015: Implement _generate_recommended_commands returning 6 standard commands.
- [x] T016: Implement analyze_feature_impact as main entry point with FeatureBundleNotFoundError for missing specs.
- [x] T017: Implement render_impact_json and render_impact_text for output formatting.

## Dependencies

- src/specspine/consistency.py (LOCAL_PATH_RE)
- src/specspine/dependency.py (EXPLICIT_DEP_PATTERNS, _list_feature_slugs, _read_all_feature_content)
- src/specspine/features.py (FEATURE_FILE_PATHS, FEATURE_DIRECTORIES, FeatureBundleNotFoundError, InvalidFeatureSlug, read_feature_metadata, validate_feature_slug)

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff feature-impact-analysis . --json` before implementation or review handoff.
- Run `specspine adapters handoff feature-impact-analysis . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks feature-impact-analysis . --json` for the focused implementation checklist.
- Run `specspine feature task-issues feature-impact-analysis . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace feature-impact-analysis . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests feature-impact-analysis . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature feature-impact-analysis --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature feature-impact-analysis --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature feature-impact-analysis --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix feature-impact-analysis . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature feature-impact-analysis --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature feature-impact-analysis --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature feature-impact-analysis --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature feature-impact-analysis --json` to compose local pre-merge review evidence.
- Run `specspine feature ready feature-impact-analysis . --json` after implementation evidence is complete.
- Run `specspine feature pr feature-impact-analysis . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan feature-impact-analysis . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan feature-impact-analysis . --output-dir .specspine/sync-plan/feature-impact-analysis` to materialize local sync review artifacts.
- Run `specspine feature archive feature-impact-analysis . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
