# Change Risk Packet

Feature ID: change-risk-packet
Status: validated
Priority: high
Owner: platform
Milestone: local review workflows
Target Release: 0.2.x
Project: Native feature bundles
Effort: M

## Why

Agents and reviewers need a local way to reason about changed paths before review. Test impact and review packets explain what to run and how to review, but they do not classify whether a change touched source code, tests, feature peer files, docs, config, or unrelated files. That gap makes review handoffs less precise for multi-agent work.

## Users

- Implementation agents checking whether their edits touched high-risk areas.
- Review agents deciding which evidence should be inspected before merge.
- Maintainers who want a token-free changed-path packet before local validation or remote review.

## Scope

- Add `specspine change risk [path] [--json] [--changed PATH]... [--feature SLUG]`.
- Classify changed paths as source, test, feature spec, feature execution, feature quality, project docs, config, or other.
- Assign deterministic advisory risk levels.
- Infer feature ids from native feature peer paths and compose coverage-required readiness evidence for inferred or provided feature ids.
- Emit stable JSON and readable text.
- Return `1` with a report for missing feature bundles and `2` for invalid slugs.

## Non-Goals

- Running git, tests, subprocesses, upstream CLIs, GitHub commands, or network calls.
- Reading or writing tokens.
- Replacing test impact, review packet, feature ready, or validate commands.
- Deciding merge approval automatically.

## Acceptance Criteria

- [x] AC001: `specspine change risk [path]` is registered under the `change` command group and emits readable text by default.
- [x] AC002: `--json` output includes `root`, `feature_id`, `changed_files`, `files`, `feature_evidence`, `summary`, `recommended_commands`, and `safety_notes`.
- [x] AC003: Changed paths are classified into source, test, feature spec, feature execution, feature quality, project docs, config, or other with deterministic advisory risk levels.
- [x] AC004: Feature ids are inferred from native feature peer paths and deduped with the optional `--feature SLUG`.
- [x] AC005: Feature evidence includes coverage-required readiness, status, gaps, blockers, source files, missing files, and native-file existence.
- [x] AC006: Missing feature bundles return `1` with a structured report, and invalid feature slugs return `2`.
- [x] AC007: The command does not run tests, invoke subprocesses, call network services, call GitHub, invoke upstream CLIs, or read tokens.
- [x] AC008: Documentation, agent guidance, templates, and dogfood artifacts describe the changed-path risk workflow.

## Edge Cases

- No changed files should still return a workspace-level packet with conservative local review and validation commands.
- Repeated changed files should be deduped while preserving first-seen order.
- Invalid slugs inferred from malformed feature peer paths should be ignored rather than crashing unrelated workspace risk reports.

## Constraints

- Use deterministic path rules and existing feature report builders.
- Keep the command read-only and dependency-free.
- Keep recommended commands advisory and unexecuted.

## Traceability Notes

- Covered by `tests/test_change.py`.
- Dogfooded through this native feature bundle and project documentation updates.
