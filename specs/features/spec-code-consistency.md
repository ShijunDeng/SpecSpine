# Spec-Code Consistency Scanner

Feature ID: spec-code-consistency
Status: validated
Priority: high
Owner: SpecSpine maintainers
Milestone: Local review evidence
Target Release: 2026.05
Project: Native feature bundles
Effort: M

## Why

Agents need a local way to check whether a native feature still points at the code, tests, and docs that implement it. `specspine analyze` finds broad traceability gaps and `specspine tests impact` recommends test commands, but reviewers also need a compact drift packet that links feature peers to concrete local implementation references, test references, documentation references, and changed paths without executing anything.

## Users

- Implementation agents preparing a feature handoff.
- Review agents checking whether code, tests, docs, and feature artifacts changed together.
- Maintainers deciding which local validation commands should follow a feature edit.

## Scope

- Add `specspine consistency scan [path] [--json] [--feature SLUG] [--changed PATH]...`.
- Report all native features by default and one focused feature with `--feature`.
- Extract local paths from `specs/features/<slug>.md`, `execution/features/<slug>.md`, and `quality/features/<slug>.md`.
- Categorize references as implementation, test, documentation, and changed-path evidence.
- Compose local `## Test Coverage` targets from the feature tests packet.
- Return stable JSON and readable text without writing files.
- Update templates, agent instructions, and project docs so new feature work can call the scanner before review.

## Non-Goals

- The scanner does not prove tests were executed.
- The scanner does not infer semantic correctness from source code.
- The scanner does not run shell commands, network calls, upstream tools, remote APIs, or credential reads.
- The scanner does not replace readiness, verification matrix, review packet, or full validation commands.

## Acceptance Criteria

- [x] AC001: The CLI exposes `specspine consistency scan [path] [--json] [--feature SLUG] [--changed PATH]...` and emits stable text and JSON with `root`, `feature_filter`, `changed_files`, `features`, `summary`, `recommended_commands`, and `safety_notes`.
- [x] AC002: Each feature record includes `feature_id`, `status`, `source_files`, `missing_files`, `implementation_references`, `test_references`, `documentation_references`, `changed_references`, `consistency_checks`, and `summary`.
- [x] AC003: The scanner links explicit local feature paths, feature-id mentions in code/tests/docs, local test coverage targets, and caller-provided changed paths without running tests.
- [x] AC004: A missing focused feature returns exit code `1` with a structured missing-feature report, while an invalid slug returns exit code `2`.
- [x] AC005: The command stays read-only and local: no subprocess execution, network access, remote API calls, upstream tool invocation, environment credential reads, or token reads.
- [x] AC006: Feature templates and generated agent instructions include `specspine consistency scan . --feature <slug> --json` as a review command.
- [x] AC007: README, architecture, product, execution, and quality docs describe the consistency scan workflow, JSON fields, exit codes, and advisory safety boundary.
- [x] AC008: The `spec-code-consistency` dogfood bundle is validated, has checked local coverage links, and passes its default and coverage-required readiness gates.

## Edge Cases

- Missing feature peers produce a structured feature record instead of crashing.
- Partial feature bundles can still be scanned and report missing peer files.
- Repeated `--changed` values are normalized and de-duplicated.
- Coverage selectors such as `tests/test_consistency.py::ConsistencyReportTests` are normalized to local file paths for existence checks.
- Nonexistent explicit references are retained with `exists=false` so reviewers can see stale links.

## Constraints

- The implementation uses only the Python standard library and existing SpecSpine parser helpers.
- The report is deterministic for the same local file tree and arguments.
- Recommended commands are advisory and are not executed.
- Text output must remain concise enough for agent handoffs.

## Traceability Notes

- Implementation: `src/specspine/consistency.py` and `src/specspine/cli.py`.
- Tests: `tests/test_consistency.py`, `tests/test_agents.py`, `tests/test_features.py`, and `tests/test_dogfood_artifacts.py`.
- Docs: `README.md`, `AGENTS.md`, `docs/architecture.md`, `specs/product.md`, `specs/architecture.md`, `execution/plan.md`, and `quality/review.md`.
