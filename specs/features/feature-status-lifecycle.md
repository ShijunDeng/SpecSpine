# Feature Status Lifecycle

Feature ID: feature-status-lifecycle
Status: validated

## Why

Native feature bundles currently start at `Status: proposed` but have no local way to advance through planning, implementation, review, and archive states. That makes long-running work hard for agents to read because every feature looks like a proposal even after it has shipped.

## Users

- AI coding agents that need a compact, machine-readable feature state before planning or editing.
- Maintainers who want feature specs, execution notes, and quality records to move together.
- CI and local scripts that validate feature bundle consistency without external services.

## Scope

- Define the native lifecycle states `proposed`, `planned`, `in-progress`, `implemented`, `validated`, and `archived`.
- Add `specspine feature status <slug> [path] [--set STATUS] [--json]`.
- Report mixed or inconsistent peer file statuses clearly.
- Update existing peer files in place when `--set` is provided.
- Include feature status and consistency in `specspine status . --json`.
- Validate allowed status values and cross-file status consistency under `validate --features`.
- Keep the workflow local-only with no GitHub token reads and no GitHub API calls.

## Non-Goals

- Automatic transition rules between lifecycle states.
- GitHub issue or pull request synchronization.
- External OpenSpec, Spec Kit, or Superpowers lifecycle mapping.
- A database, daemon, or new runtime dependency.

## Acceptance Criteria

- [x] Agents can query a feature bundle status as text or stable JSON.
- [x] Agents can set any allowed lifecycle status across existing peer files.
- [x] Invalid status values and invalid slugs return code `2`.
- [x] Partial bundles report missing files and update only existing peer files.
- [x] Feature validation accepts all allowed statuses and rejects invalid or mixed statuses.
- [x] Repository status JSON lists this feature with a consistent `validated` status.
- [x] Documentation and project artifacts describe the lifecycle behavior.
