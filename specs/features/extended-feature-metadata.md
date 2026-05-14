# Extended Feature Metadata

Feature ID: extended-feature-metadata
Status: validated
Priority: high
Owner: SpecSpine maintainers
Milestone: Local triage metadata
Target Release: next
Project: Native feature bundles
Effort: M

## Why

SpecSpine feature bundles need richer local triage context before maintainers decide whether and how to sync work into GitHub Issues, Pull Requests, Projects, or upstream planning tools. Typed issue metadata trends are useful, but SpecSpine must keep the source of truth local, deterministic, token-free, and machine-consumable.

## Users

- Maintainers comparing native feature bundles before remote sync.
- Implementation agents preparing a focused local handoff.
- Review and release agents drafting issues, Pull Requests, and sync plans without calling remote services.

## Scope

- Add optional `Milestone:`, `Target Release:`, `Project:`, and `Effort:` fields to spec-level feature metadata.
- Generate new feature specs with deterministic defaults for every metadata field.
- Parse old feature specs with stable default metadata values.
- Carry extended metadata into status summaries, feature handoff JSON, feature test JSON, issue drafts, PR drafts, sync-plan JSON, and sync-plan artifacts.
- Keep existing feature summary filters and sorts compatible.
- Document the local metadata contract across user, architecture, execution, quality, and agent guidance.

## Non-Goals

- Calling GitHub APIs, invoking `gh`, reading tokens, or writing remote issue fields.
- Adding dependencies or vendoring upstream source code.
- Requiring every existing feature file to be edited before it parses successfully.
- Adding new status filters for milestone, release, project, or effort.

## Acceptance Criteria

- [x] `specspine feature new` writes default milestone, target release, project, and effort metadata.
- [x] Existing feature specs without the new fields parse with stable defaults.
- [x] Feature specs with all extended fields parse into `FeatureMetadata.as_dict()`.
- [x] `status --json --feature-summaries` includes extended metadata while old bundles remain compatible.
- [x] `status --feature-summaries` text output remains concise and shows milestone or target release context.
- [x] `feature issue`, `feature pr`, and `feature sync-plan` JSON and text outputs include extended metadata.
- [x] Sync-plan manifests and body artifacts include extended metadata.
- [x] `feature handoff --json` and `feature tests --json` include the extended metadata context.
- [x] Tests guard that the sync-plan path does not call subprocesses, network services, GitHub, or token reads.
