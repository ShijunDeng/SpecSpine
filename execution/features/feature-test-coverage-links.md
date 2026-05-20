# Feature Test Coverage Links Execution

Feature ID: feature-test-coverage-links
Status: validated
Why: Testing agents need explicit local coverage links from acceptance criteria to existing test files without relying on inference or external services.

## Milestones

- Define the local Test Coverage metadata shape and parser behavior.
- Add coverage links to the acceptance-test packet report, JSON renderer, and text renderer.
- Update generated quality templates and project guidance.
- Add focused tests for parser, packet output, status mapping, target existence, offline behavior, and dogfood readiness.
- Add this validated dogfood bundle with a real link to an existing test file.

## Tasks

- [x] AC001 Add a `FeatureTestCoverageLink` record and `## Test Coverage` parser in `src/specspine/features.py`.
- [x] AC002 Add `test_coverage` to `FeatureTestsReport` JSON and summary counts.
- [x] AC003 Attach matching coverage links to acceptance test cases and derive `covered`, `planned`, or `pending` status.
- [x] AC004 Render Test Coverage in text output and show linked targets on test case lines.
- [x] AC005 Update the `feature new` quality template with Test Coverage guidance.
- [x] AC006 Update README, architecture, product, execution, review, and agent guidance.
- [x] AC007 Add unit tests and dogfood artifact coverage for explicit coverage links.
- [x] AC008 Add tests for parser behavior, JSON and text output, summary counts, coverage association, target existence, offline behavior, template generation, and dogfood readiness.

## Dependencies

- Existing feature bundle path helpers, checklist parser conventions, and acceptance-test packet composition.
- Python standard library path checks only.
- Existing unit tests under `tests/`.

## Open Questions

- Should a future readiness gate optionally require every acceptance criterion to have at least one completed local coverage link?
