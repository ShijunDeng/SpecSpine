# Repository Hygiene Scanner

Feature ID: repo-hygiene-scan
Status: validated
Priority: high
Owner: SpecSpine maintainers
Milestone: Local review evidence
Target Release: 2026.05
Project: Native feature bundles
Effort: M

## Why

Agents need a repeatable local check that catches generated cache files, denylisted source or test paths, and denylisted text cues before review or commit. The existing consistency, risk, security, provenance, and review packets help explain a feature change, but they do not provide one repository-level hygiene report that can fail in strict mode when high-risk residue is present.

## Users

- Implementation agents preparing a clean handoff.
- Review agents checking whether a workspace contains generated or denylisted residue.
- Maintainers deciding whether a local branch is clean enough to commit or push.

## Scope

- Add `specspine hygiene scan [path] [--json] [--changed PATH]... [--strict]`.
- Report generated cache artifacts, denylisted path remnants, and denylisted content cues from local workspace files.
- Normalize repeated changed paths and include them in the report without requiring a Git command.
- Return stable JSON and readable text without writing files.
- Keep the default scan advisory with exit code `0`, while `--strict` returns `1` when high-risk findings are present.
- Update generated templates, agent instructions, and project docs so new feature work can run the hygiene scan before review.

## Non-Goals

- The scanner does not delete files.
- The scanner does not replace Git status, full validation, review packets, or human code review.
- The scanner does not run shell commands, tests, network calls, upstream tools, remote APIs, or credential reads.
- The scanner does not prove that a branch is safe to release; it only reports local repository hygiene signals.

## Acceptance Criteria

- [x] AC001: The CLI exposes `specspine hygiene scan [path] [--json] [--changed PATH]... [--strict]` and emits stable text and JSON with `root`, `changed_files`, `findings`, `summary`, `recommended_commands`, and `safety_notes`.
- [x] AC002: Findings include stable `id`, `severity`, `category`, `path`, optional `line`, `message`, and `source` fields for generated artifacts, denylisted paths, and denylisted content.
- [x] AC003: Generated cache artifacts and denylisted source or test path remnants are reported without crashing on missing, binary, or unreadable files.
- [x] AC004: Denylisted content cues include local file and line metadata while avoiding file content dumps and secret value printing.
- [x] AC005: Repeated `--changed` values are normalized and de-duplicated in JSON and text output.
- [x] AC006: The default command returns `0` when the report is built, and `--strict` returns `1` when high-risk findings exist.
- [x] AC007: The command stays read-only and local: no subprocess execution, network access, remote API calls, upstream tool invocation, environment credential reads, token reads, or dependency additions.
- [x] AC008: Feature templates and generated agent instructions include `specspine hygiene scan . --json` as a pre-review command.
- [x] AC009: README, architecture, product, execution, and quality docs describe the hygiene scan workflow, JSON fields, strict mode, and safety boundary.
- [x] AC010: The `repo-hygiene-scan` dogfood bundle is validated, has checked local coverage links, and passes its default and coverage-required readiness gates.

## Edge Cases

- Generated cache directories can appear at any nested level and should be reported once per matching artifact.
- Binary or undecodable files are skipped as local read skips instead of causing scan failure.
- Scanner-owned source and test files are not scanned for denylisted content so the built-in rules can be represented safely.
- Repeated changed paths keep a deterministic order after de-duplication.
- Strict mode fails only for high-risk findings so advisory informational findings remain reviewable without blocking default use.

## Constraints

- The implementation uses only the Python standard library.
- The report is deterministic for the same local file tree and arguments.
- Recommended commands are advisory and are not executed.
- Text output must remain concise enough for agent handoffs.

## Traceability Notes

- Implementation: `src/specspine/hygiene.py` and `src/specspine/cli.py`.
- Tests: `tests/test_hygiene.py`, `tests/test_agents.py`, `tests/test_features.py`, and `tests/test_dogfood_artifacts.py`.
- Docs: `README.md`, `AGENTS.md`, `docs/architecture.md`, `specs/product.md`, `specs/architecture.md`, `execution/plan.md`, and `quality/review.md`.
