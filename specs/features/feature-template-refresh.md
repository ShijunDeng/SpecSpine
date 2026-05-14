# Feature Template Refresh

Feature ID: feature-template-refresh
Status: validated

## Why

`specspine feature new` still created early generic peer files while the project now has native handoff, trace, tests, ready, PR, transition, and validation workflows. New requirements should begin with enough structure for agents and reviewers to connect acceptance criteria to execution, quality evidence, and release handoff without inventing a workflow each time.

## Users

- Maintainers creating native SpecSpine feature bundles.
- Coding agents implementing features from local files.
- Review, QA, and release agents consuming trace, tests, PR drafts, and readiness gates.

## Scope

- Refresh `build_feature_files()` templates for spec, execution, and quality peer files.
- Add focused sections for edge cases, constraints, traceability notes, dependencies, open questions, and agent handoff.
- Make generated quality gates mention acceptance criteria, test coverage, docs or PR draft, `feature ready`, and `validate . --fusion --features`.
- Keep generated checklists unchecked so structural validation can pass while `feature ready` remains blocked for new empty bundles.
- Update docs, agent guidance, tests, and this dogfood bundle.

## Non-Goals

- Adding new CLI flags or changing `feature new` arguments.
- Running upstream tools, GitHub APIs, or token-reading flows.
- Making generated placeholder content count as implementation evidence.
- Replacing the existing Markdown parser or validation model.

## Acceptance Criteria

- [x] Generated spec files include Why, Users, Scope, Non-Goals, Acceptance Criteria, Edge Cases, Constraints, and Traceability Notes.
- [x] Generated execution files include Milestones, Tasks, Dependencies, Open Questions, and Agent Handoff with local handoff, tasks, trace, tests, ready, PR, and validation commands.
- [x] Generated quality files include Required Checks, Test Plan, Review Notes, and Release Readiness with unchecked local gates for acceptance criteria, test coverage, docs or PR draft, `feature ready`, and `validate . --fusion --features`.
- [x] A newly generated feature bundle passes structural feature validation but does not pass `feature ready`.
- [x] `feature trace` and `feature tests` extract placeholder checklist and test-plan evidence from the refreshed templates without crashing.
- [x] Existing overwrite and `--force` behavior remains compatible.
- [x] README, architecture docs, project specs, execution docs, quality review notes, root `AGENTS.md`, and the generated agents template describe the focused workflow guidance.
- [x] This dogfood feature bundle is validated and passes its readiness gate.

## Edge Cases

- [x] Placeholder checklist items are extractable by trace/test exporters but remain unchecked.
- [x] The quality template includes non-empty test-plan guidance without implying tests have passed.
- [x] Existing partial-file and overwrite protections behave the same after the template refresh.

## Constraints

- [x] Templates remain deterministic, ASCII, zero-dependency, and local-only.
- [x] No upstream CLIs, GitHub APIs, network calls, or token reads are introduced.
- [x] `normalize_template()` remains the template normalization path.

## Traceability Notes

- AC001 maps to T001 and Q001.
- AC002 maps to T002 and Q002.
- AC003 maps to T003 and Q003.
- AC004 and AC005 map to T004 and Q004.
- AC006 maps to existing overwrite tests and Q005.
- AC007 maps to documentation updates and Q006.
- AC008 maps to this dogfood bundle and Q007.
