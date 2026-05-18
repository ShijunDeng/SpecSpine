# Provenance Manifest

Feature ID: provenance-manifest
Status: validated
Priority: high
Owner: platform
Milestone: local review workflows
Target Release: 0.2.x
Project: Native feature bundles
Effort: M

## Why

Agentic development workflows need audit-ready local evidence before review, release, or archive. Existing packets explain readiness, risk, security cues, and review state, but reviewers still lack a deterministic file-hash manifest that proves which local spec, execution, quality, source, and test artifacts were inspected at a point in time.

## Users

- Review agents that need stable artifact hashes before accepting handoff evidence.
- Maintainers preparing release or archive packets without calling remote services.
- Future auditors checking whether a feature's local evidence files can be tied back to exact bytes.

## Scope

- Add `specspine provenance manifest [path] [--json] [--feature SLUG] [--include PATH]...`.
- Hash existing workspace-local files with SHA-256 and report artifact path, kind, existence, byte count, and digest metadata.
- In feature mode, include spec, execution, and quality peer files plus coverage-required readiness and handoff evidence.
- Treat missing and outside-root includes as structured artifact records without crashing.
- Emit stable JSON and readable text.
- Return `1` with a report for missing feature bundles and `2` for invalid slugs.

## Non-Goals

- Running tests, subprocesses, upstream CLIs, GitHub commands, or network calls.
- Reading environment variables, token providers, or secret stores.
- Printing file contents or claiming that hashes prove commands were executed.
- Replacing review, archive, security cue, change risk, or readiness packets.

## Acceptance Criteria

- [x] AC001: `specspine provenance manifest [path]` is registered under the `provenance` command group and emits readable text by default.
- [x] AC002: `--json` output includes `root`, `feature_id`, `artifacts`, `feature_evidence`, `summary`, `recommended_commands`, and `safety_notes`.
- [x] AC003: Existing workspace-local files are hashed with SHA-256 and byte counts while file contents are never printed.
- [x] AC004: Missing and outside-root include paths are represented as artifact records without crashing.
- [x] AC005: `--feature SLUG` adds native peer artifacts and coverage-required readiness evidence, including status, ready, native-file existence, missing files, blockers, gaps, and source files.
- [x] AC006: Missing feature bundles return `1` with a structured report, and invalid feature slugs return `2`.
- [x] AC007: The command does not run tests, invoke subprocesses, call network services, call GitHub, invoke upstream CLIs, read environment variables, or read tokens.
- [x] AC008: Documentation, agent guidance, templates, and dogfood artifacts describe provenance manifests as advisory local evidence only.

## Edge Cases

- No feature and no includes should still return a workspace-level packet with conservative local review commands.
- Duplicate include paths should be deduped while preserving first occurrence order.
- Existing directories should be reported as non-file artifacts without hashes.

## Constraints

- Use only Python standard library hashing and local file metadata.
- Keep output deterministic for agents and tests.
- Keep recommended commands advisory and unexecuted.

## Traceability Notes

- Covered by `tests/test_provenance.py`.
- Dogfooded through this native feature bundle and project documentation updates.
