# Feature Impact Analysis

Feature ID: feature-impact-analysis
Status: implemented
Priority: medium
Owner: unassigned
Milestone: unassigned
Target Release: unassigned
Project: unassigned
Effort: unknown

## Why

Analyze the downstream impact of feature changes before implementation. Predict which features, tests, and code will be affected by proposed spec modifications.

## Users

- Developers who need to understand the blast radius of feature changes before committing modifications.
- Tech leads who review change risk and need to identify dependent features that may break.
- QA engineers who need to know which test files to update when a feature changes.
- Release managers who assess cumulative risk across multiple feature changes.

## Scope

- `analyze_feature_impact(root, slug, proposed_changes)` returns an `ImpactAnalysis` with impacted features, tests, code, risk score, mitigation steps, and recommended commands.
- `_find_affected_features` discovers downstream feature dependencies by scanning all feature bundles for references to the target slug and shared path references.
- `_find_affected_tests` discovers test files that reference the feature slug by filename content, AC text matching, and quality file coverage link extraction.
- `_find_affected_code` discovers source modules that reference the feature slug via glob patterns (src/**/*.py) and local path references in feature artifacts.
- `_compute_risk_score` computes a 0-100 risk score weighted by severity (high=15, medium=8, low=3) and item count thresholds for features (>3/+20, >1/+10), tests (>5/+15, >2/+8), and code (>5/+10, >2/+5).
- `_generate_mitigation_steps` produces actionable steps based on impacted categories and risk score thresholds (>=50: break into smaller PRs; >=75: require additional peer review).
- `_generate_recommended_commands` produces 6 standard commands for impact re-assessment, consistency scanning, test impact analysis, verification, handoff, and validation.
- Severity classification: high for high-priority dependent features, medium for tests and code references, low for quality file references.
- JSON and text renderers (`render_impact_json`, `render_impact_text`) provide structured and human-readable output.

## Non-Goals

- Does not execute tests or verify actual runtime impact; all analysis is static file scanning.
- Does not modify any files or trigger CI/CD pipelines.
- Does not predict exact behavioral changes; only identifies which artifacts reference the feature.
- Does not analyze impact across repository boundaries or external dependencies.
- Does not provide real-time impact monitoring; each call is a point-in-time snapshot.

## Acceptance Criteria

- [x] AC001: `analyze_feature_impact` returns an `ImpactAnalysis` with feature_id, total_affected, impacted_features, impacted_tests, impacted_code, risk_score, mitigation_steps, safety_notes, and recommended_commands.
- [x] AC002: `_find_affected_features` identifies downstream features by scanning all bundles for explicit slug references and shared path references from proposed_changes.
- [x] AC003: `_find_affected_tests` identifies test files via three methods: slug mention in test file content, AC text matching (first 30 chars or AC ID), and quality file coverage link extraction.
- [x] AC004: `_find_affected_code` identifies source modules via glob pattern (src/**/*.py) for slug mentions and local path references from feature artifacts starting with "src/".
- [x] AC005: Risk score computation weights high severity at 15 points, medium at 8, low at 3, with bonus points for item count thresholds, capped at 100.
- [x] AC006: `_generate_mitigation_steps` produces category-specific steps for impacted features, tests, and code, plus risk-threshold-based steps for scores >=50 and >=75.
- [x] AC007: `_generate_recommended_commands` returns 6 standard commands: impact analyze, consistency scan, tests impact, verify matrix, feature handoff, and validate.
- [x] AC008: Impact items include type (feature/test/code), id, path, severity, reason, and optional affected_acs tuple for test and code items.
- [x] AC009: FeatureBundleNotFoundError is raised when the target feature's spec file does not exist.
- [x] AC010: `render_impact_text` produces human-readable output with risk score, total affected, impacted items by category, mitigation steps, recommended commands, and safety notes.

## Edge Cases

- Feature not found: raises FeatureBundleNotFoundError with missing_paths tuple instead of returning empty analysis.
- No downstream dependencies: impacted_features, impacted_tests, and impacted_code are empty tuples; risk_score is 0.
- Test file mentions slug but has no AC references: affected_acs is empty tuple for that test impact item.
- Quality file references non-existent test file: path still included but target_exists would be false in downstream analysis.
- Proposed_changes with shared_paths containing short strings (<3 chars): filtered out to avoid false positives.
- Circular dependencies between features: _extract_slugs_from_text with valid_slugs set prevents infinite recursion.
- Source file path resolution failure: _relative_path falls back to full path.as_posix() when relative computation fails.

## Constraints

- Static analysis only; no test execution or runtime behavior verification.
- Source glob patterns limited to ("src/**/*.py",); test glob patterns limited to ("tests/**/*.py",).
- Risk score is capped at 100 maximum.
- Mitigation steps include impacted item paths truncated to first 5 items per category.
- Safety notes confirm only local workspace files are read with no subprocess, network, or token access.
- Feature slug validation follows the standard `[a-z0-9]([a-z0-9-]*[a-z0-9])?` pattern.

## Traceability Notes

- Source: src/specspine/impact_analysis.py (597 lines)
- Tests: tests/test_impact_analysis.py
- Impact item data structures: src/specspine/impact_analysis.py lines 36-82
- Affected features detection: src/specspine/impact_analysis.py lines 119-186
- Affected tests detection: src/specspine/impact_analysis.py lines 204-283
- Affected code detection: src/specspine/impact_analysis.py lines 299-353
- Risk score computation: src/specspine/impact_analysis.py lines 374-417
- Mitigation steps: src/specspine/impact_analysis.py lines 420-464
- Main entry point: src/specspine/impact_analysis.py lines 479-542
- Text/JSON renderers: src/specspine/impact_analysis.py lines 545-597
