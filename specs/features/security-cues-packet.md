# Security Cues Packet

Feature ID: security-cues-packet
Status: validated
Priority: high
Owner: platform
Milestone: local review workflows
Target Release: 0.2.x
Project: Native feature bundles
Effort: M

## Why

AI-assisted code can pass functional tests while still introducing security-sensitive changes. Reviewers need a local, token-free prompt packet that highlights changed-path text cues around secrets, authentication, sessions, shell execution, deserialization, network calls, crypto, permissions, and path traversal before a feature is merged.

## Users

- Review agents checking whether changed files contain security-sensitive cues.
- Implementation agents preparing local evidence before asking for review.
- Maintainers who need a lightweight security review prompt without running external scanners.

## Scope

- Add `specspine security cues [path] [--json] [--changed PATH]... [--feature SLUG]`.
- Classify changed paths as source, test, feature spec, feature execution, feature quality, project docs, config, or other.
- Read existing local text files up to a bounded size and report security-sensitive keyword cues with file, line, category, keyword, severity, and message metadata.
- Infer feature ids from native feature peer paths and compose coverage-required feature readiness evidence for inferred or provided feature ids.
- Emit stable JSON and readable text.
- Return `1` with a report for missing feature bundles and `2` for invalid slugs.

## Non-Goals

- Running SAST, DAST, tests, subprocesses, upstream CLIs, GitHub commands, or network calls.
- Reading or writing tokens.
- Printing source lines, file contents, or secret values.
- Treating keyword cues as proof of a vulnerability or making merge decisions automatically.

## Acceptance Criteria

- [x] AC001: `specspine security cues [path]` is registered under the `security` command group and emits readable text by default.
- [x] AC002: `--json` output includes `root`, `feature_id`, `changed_files`, `files`, `cues`, `feature_evidence`, `summary`, `recommended_commands`, and `safety_notes`.
- [x] AC003: Existing local text files are read only when they are inside the workspace and below the configured size limit; missing, binary, too-large, or outside-root files are reported without crashing.
- [x] AC004: Security-sensitive cues are emitted with id, path, category, severity, line, keyword, and message while omitting source line text and secret values.
- [x] AC005: Feature ids are inferred from native feature peer paths and deduped with the optional `--feature SLUG`.
- [x] AC006: Feature evidence includes coverage-required readiness, status, gaps, blockers, source files, missing files, and native-file existence.
- [x] AC007: Missing feature bundles return `1` with a structured report, and invalid feature slugs return `2`.
- [x] AC008: The command does not run tests, invoke subprocesses, call network services, call GitHub, invoke upstream CLIs, read environment variables, or read tokens.
- [x] AC009: Documentation, agent guidance, templates, and dogfood artifacts describe the security cues workflow and advisory-only boundary.

## Edge Cases

- No changed files should still return a workspace-level packet with conservative local review commands.
- Cues in comments and docs should be reported as review prompts, not filtered out or treated as vulnerabilities.
- Binary, too-large, missing, and outside-root paths should not break the report.

## Constraints

- Use Python standard library file reads and deterministic keyword matching only.
- Keep output free of source line contents and potential secret values.
- Keep recommended commands advisory and unexecuted.

## Traceability Notes

- Covered by `tests/test_security.py`.
- Dogfooded through this native feature bundle and project documentation updates.
