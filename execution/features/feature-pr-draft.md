# Offline Pull Request Draft Export Execution

Feature ID: feature-pr-draft
Status: validated
Why: Review and release agents need a Pull Request-shaped local artifact that composes SpecSpine feature evidence without touching GitHub.

## Milestones

- Implementation added the PR draft report, renderer, and CLI branch.
- Tests covered JSON, text, output overwrite rules, partial bundles, missing bundles, invalid slugs, token/API independence, and dogfood readiness.
- Documentation and agent guidance were updated to include the new local PR bridge.

## Tasks

- [x] Add a `PullRequestDraft` report and renderers in `src/specspine/features.py`.
- [x] Compose PR draft content from existing handoff, trace, readiness, release readiness, and source-file evidence.
- [x] Register `feature pr` in `src/specspine/cli.py` with JSON, output, force, and exit-code behavior matching existing exporters.
- [x] Add unit tests for text output, JSON shape, output overwrite protection, partial bundles, missing bundles, invalid slugs, and no GitHub token/API dependency.
- [x] Update README, architecture docs, product specs, project execution notes, review notes, AGENTS.md, and the generated agent template.
- [x] Add this validated dogfood feature bundle and verify it passes `feature ready`.

## Dependencies

- Existing native feature bundle parsing helpers.
- Existing `feature handoff`, `feature trace`, and `feature ready` report construction.
- Python standard library only.

## Open Questions

- Remote GitHub PR creation and synchronization remain adapter work after the offline draft format has been dogfooded.
