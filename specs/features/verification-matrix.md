# Verification Matrix

Feature ID: verification-matrix
Status: validated
Priority: high
Owner: platform
Milestone: local review workflows
Target Release: 0.2.x
Project: Native feature bundles
Effort: M

## Why

Agentic development workflows need a compact way to inspect whether each feature acceptance criterion has local verification evidence before review, release, or archive. Existing trace, tests, readiness, impact, review, and provenance packets are useful individually, but reviewers still need one AC-level view that connects criteria, test cases, coverage links, gaps, blockers, and safe follow-up commands.

## Users

- Review agents that need to compare AC completion against local test coverage evidence.
- QA agents that need a focused feature-level verification packet before writing or running tests.
- Maintainers preparing release or archive checks without calling remote services.

## Scope

- Add `specspine verify matrix <slug> [path] [--json]`.
- Compose existing feature trace, feature tests, and coverage-required feature readiness evidence.
- Emit one matrix row per acceptance criterion with mapped test cases, mapped coverage links, coverage completeness, verification status, and gap reasons.
- Return a structured report for missing feature bundles and stable errors for invalid slugs.
- Document that verified rows are local evidence only and do not prove tests were run.

## Non-Goals

- Running test commands, subprocesses, upstream tools, GitHub commands, or network calls.
- Creating new test code or inferring implementation files.
- Reading environment variables, tokens, or secret stores.
- Replacing feature readiness, coverage debt, review packets, or provenance manifests.

## Acceptance Criteria

- [x] AC001: `specspine verify matrix <slug> [path]` is registered under the `verify` command group and emits readable text by default.
- [x] AC002: `--json` output includes `root`, `feature_id`, `status`, `ready`, `matrix`, `evidence`, `summary`, `recommended_commands`, and `safety_notes`.
- [x] AC003: Each acceptance criterion row includes the AC source record, mapped test cases, mapped coverage links, `coverage_complete`, `verification_status`, and `gap_reasons`.
- [x] AC004: A checked AC with at least one checked coverage link to an existing local target is marked `verified`.
- [x] AC005: A checked AC with missing, unchecked, or missing-target coverage remains `unverified` with explicit gap reasons.
- [x] AC006: Missing feature bundles return `1` with a structured report, and invalid feature slugs return `2`.
- [x] AC007: The command does not run tests, invoke subprocesses, call network services, call GitHub, invoke upstream CLIs, read environment variables, or read tokens.
- [x] AC008: Documentation, agent guidance, generated templates, and dogfood artifacts describe the verification matrix as advisory local evidence only.

## Edge Cases

- A feature with no acceptance criteria should produce an empty matrix and a zero AC summary.
- Partial bundles should preserve missing file evidence from the existing trace, tests, and readiness reports.
- Multiple coverage links for one AC should mark the row complete when at least one checked target exists.

## Constraints

- Use only existing SpecSpine local reports and Python standard library data structures.
- Keep output deterministic for agents and tests.
- Keep recommended commands advisory and unexecuted.

## Traceability Notes

- Covered by `tests/test_verification.py`.
- Dogfooded through this native feature bundle and project documentation updates.
