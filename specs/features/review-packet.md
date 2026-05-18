# Review Packet

Feature ID: review-packet
Status: validated
Priority: high
Owner: platform
Milestone: local review workflows
Target Release: 0.2.x
Project: Native feature bundles
Effort: M

## Why

Agents and maintainers need one local pre-merge packet that combines workspace validation, quality gates, static test impact, feature readiness, trace evidence, and safety boundaries. Existing commands expose each view separately, but reviewers still have to stitch the evidence together manually before deciding whether a change is ready to merge.

## Users

- Review agents checking whether an implementation follows the planned feature.
- Testing agents deciding whether focused test recommendations are grounded in local evidence.
- Maintainers who need a token-free review packet before merge or release.

## Scope

- Add `specspine review packet [path] [--json] [--feature SLUG] [--changed PATH]...`.
- Compose validation summary, quality gate definitions, static test impact, and safety notes from existing local reports.
- In feature mode, include handoff, coverage-required readiness, trace, acceptance-test packet, gaps, blockers, and source files.
- Emit stable JSON and readable text.
- Return `1` with a report for missing feature bundles and `2` for invalid slugs.

## Non-Goals

- Running tests, subprocesses, upstream CLIs, GitHub commands, or network calls.
- Reading or writing tokens.
- Replacing focused feature handoff, tests, ready, trace, gates, impact, or validation commands.
- Marking a review as remotely approved or creating remote status checks.

## Acceptance Criteria

- [x] AC001: `specspine review packet [path]` is registered under the `review` command group and emits readable text by default.
- [x] AC002: `--json` output includes `root`, `feature_id`, `changed_files`, `validation`, `quality_gates`, `test_impact`, `review_checks`, `summary`, `recommended_commands`, and `safety_notes`.
- [x] AC003: `--feature SLUG` includes native feature handoff, coverage-required readiness, trace, tests, gaps, blockers, status, and source-file evidence.
- [x] AC004: Repeated `--changed PATH` values are forwarded to static test impact recommendations.
- [x] AC005: Missing feature bundles return `1` with a structured report, and invalid feature slugs return `2`.
- [x] AC006: The command does not run tests, invoke subprocesses, call network services, call GitHub, invoke upstream CLIs, or read tokens.
- [x] AC007: Documentation, agent guidance, templates, and dogfood artifacts describe the pre-merge review packet workflow.

## Edge Cases

- A workspace review may not include a feature id; the packet should still include validation, quality gates, impact, review checks, and safety notes.
- Feature trace evidence should not be requested when the native feature bundle is missing.
- Changed files may point at source files, test files, or unmapped files; impact recommendations remain advisory.

## Constraints

- Reuse existing local report builders instead of duplicating validation, gate, impact, or feature parsing logic.
- Keep the report deterministic for agents and tests.
- Do not add runtime dependencies.

## Traceability Notes

- Covered by `tests/test_review.py`.
- Dogfooded through this native feature bundle and project documentation updates.
