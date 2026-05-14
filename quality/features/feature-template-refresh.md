# Feature Template Refresh Quality

Feature ID: feature-template-refresh
Status: validated
Why: The refreshed templates should guide new work into the current local workflow while staying deterministic, zero-dependency, and not ready by default.

## Required Checks

- [x] Unit tests cover refreshed spec, execution, and quality template sections.
- [x] Unit tests cover generated Agent Handoff commands.
- [x] Unit tests show a new generated bundle structurally validates while `feature ready` remains blocked.
- [x] Unit tests show `feature trace` and `feature tests` extract placeholder checklist and test-plan evidence.
- [x] Existing overwrite and `--force` behavior remains covered.
- [x] Documentation and agent guidance describe the focused handoff, tests, PR, ready, and validation workflow.
- [x] This dogfood bundle passes its own readiness gate.

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest discover -s tests`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine feature ready feature-template-refresh . --json`.
- Run the configured repository token-pattern scan.

## Review Notes

- Template content remains plain Markdown generated through the existing deterministic path.
- New checklist items are intentionally unchecked so a freshly generated bundle cannot pass `feature ready`.
- The execution template and handoff recommendations now point agents at the same local workflow commands.
- No new dependencies, flags, upstream calls, GitHub calls, or token reads are introduced.

## Release Readiness

- [x] Acceptance criteria and execution tasks are complete.
- [x] Unit tests, validation, feature readiness, and token-pattern scan commands pass.
- [x] README, docs, specs, execution plan, task list, quality review, root `AGENTS.md`, and generated agent template are updated.
- [x] Local PR draft workflow remains offline and token-free.
- [x] No known blockers remain.
