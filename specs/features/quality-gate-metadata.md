# Quality Gate Metadata

Feature ID: quality-gate-metadata
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

Repository-level quality gates need enough structured context for agents, reviewers, and CI authors to audit risk and ownership without executing checks or scraping prose. Lightweight inline labels keep `quality/checklist.md` readable while making `specspine gates --json` more useful for machine consumers.

## Users

- Implementation agents deciding which quality gates need explicit evidence.
- Review agents checking quality policy coverage and ownership.
- Maintainers mapping local quality gates to CI check names without calling GitHub.

## Scope

- Parse optional `[severity: ...]`, `[owner: ...]`, and `[ci: ...]` labels from checkbox text under repository `## Required Checks`.
- Keep unlabeled gates compatible by exporting default `severity=medium`, `owner=unassigned`, and `ci_check=null`.
- Strip recognized metadata labels from the human `text` field while retaining the original row text in `raw_text`.
- Warn on unsupported severity values without failing the command.
- Add severity distribution and metadata coverage counts to the existing quality gate summary.
- Show concise metadata in text output.
- Keep the command local, non-executing, zero-dependency, network-free, GitHub-free, token-free, and upstream-CLI-free.

## Non-Goals

- Executing the labeled CI checks or commands.
- Validating that owner names map to real teams.
- Calling GitHub APIs, requiring `gh`, reading tokens, or writing branch-protection settings.
- Replacing Markdown quality checklists with a separate schema file.

## Acceptance Criteria

- [x] AC001: Unlabeled gates keep the original JSON fields and add stable default metadata fields.
- [x] AC002: Labeled gates parse severity, owner, and CI labels case-insensitively.
- [x] AC003: Recognized labels are removed from `text` and preserved through a raw source field.
- [x] AC004: Unsupported severity values keep `severity=medium` and add a gate-level metadata warning.
- [x] AC005: Summary output includes severity counts, owner coverage count, and CI check coverage count while preserving existing summary keys.
- [x] AC006: Text output displays concise gate metadata.
- [x] AC007: Missing `quality/checklist.md` still returns a stable empty report with metadata summary fields.
- [x] AC008: The feature is covered by dogfood peer files and readiness checks, including coverage-required readiness.
