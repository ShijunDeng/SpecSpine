# Feature Task Issue Drafts Execution

Feature ID: feature-task-issue-drafts
Status: validated
Why: Provide local task-level GitHub issue draft packages from native feature execution checklists.

## Milestones

- Define the task issue draft report schema and deterministic Markdown body.
- Register the CLI command and output file behavior.
- Cover ready, partial, missing, invalid, overwrite, and offline guarantees in tests.
- Update docs, agent guidance, generated templates, and dogfood artifacts.

## Tasks

- [x] Add task issue draft dataclasses, report construction, JSON renderer, and text renderer in `src/specspine/features.py`.
- [x] Register `specspine feature task-issues` in `src/specspine/cli.py` with matching exporter semantics.
- [x] Add generated template and recommended-command references for task issue drafts.
- [x] Add unit and dogfood tests for JSON, text, partial bundles, missing bundles, invalid slugs, output overwrite, and offline guarantees.
- [x] Update README, architecture, product, execution, quality, AGENTS, and agent template docs.
- [x] Validate the dogfood bundle with readiness, report, and workspace validation commands.

## Dependencies

- Existing `feature tasks` report parsing for execution checklist records.
- Existing `feature trace` report parsing for acceptance criteria evidence.
- Existing output file conventions shared by feature exporters.

## Open Questions

- Keep task issue drafts as local Markdown packages until a future explicit sync workflow defines remote GitHub behavior.

## Agent Handoff

- Run `specspine feature task-issues feature-task-issue-drafts . --json` to inspect generated task issue drafts.
- Run `specspine feature tasks feature-task-issue-drafts . --json` for the source execution checklist.
- Run `specspine feature trace feature-task-issue-drafts . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests feature-task-issue-drafts . --json` to inspect acceptance-test context.
- Run `specspine feature ready feature-task-issue-drafts . --json` after implementation evidence is complete.
- Run `specspine feature pr feature-task-issue-drafts . --json` to draft local Pull Request review notes.
- Run `specspine validate . --fusion --features` before handoff or release.
