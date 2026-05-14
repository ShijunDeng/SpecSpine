# Feature Test Coverage Links

Feature ID: feature-test-coverage-links
Status: validated

## Why

QA and testing agents can already read acceptance criteria and test plans, but they need explicit local links from acceptance criteria to existing test files when a project already has coverage. User-authored links give agents concrete affected-test context without running tests, guessing filenames, reading credentials, or calling external services.

## Users

- QA agents preparing focused acceptance verification.
- Test-focused implementation agents that need existing test context before editing.
- Maintainers reviewing whether an acceptance criterion has planned or completed local coverage.

## Scope

- Parse `## Test Coverage` in `quality/features/<slug>.md` as GitHub Markdown checklist links.
- Support rows such as `- [x] AC001 -> tests/test_features.py::FeatureBundleTests::test_name` and `- [ ] AC002 -> tests/test_features.py`.
- Export parsed coverage links in `specspine feature tests <slug> --json` and text output.
- Attach links with matching AC ids to generated test case records.
- Set test case status to `covered`, `planned`, or `pending` from linked coverage state.
- Check target path existence locally against the workspace root, using the path before any `::` selector.
- Keep the feature fully local, token-free, network-free, upstream-free, and dependency-free.

## Non-Goals

- Running tests or validating test selectors.
- Inferring test files from code changes.
- Calling GitHub, upstream CLIs, network services, or credential providers.
- Changing readiness gates to require test coverage links.

## Acceptance Criteria

- [x] `quality/features/<slug>.md` supports a `## Test Coverage` section with checklist coverage links.
- [x] Coverage link JSON records include stable ids, AC ids, target, target path, target existence, done state, text, source file, and line.
- [x] Checklist rows without a recognizable AC id do not crash and are exported with stable unknown-AC behavior.
- [x] `FeatureTestsReport` JSON includes top-level `test_coverage`, and summary includes coverage done/open/total counts.
- [x] Test cases include matching coverage links and set status to `covered`, `planned`, or `pending`.
- [x] Text output includes a Test Coverage section and shows linked targets on test case lines, with clear `None linked` text when empty.
- [x] `feature new` quality templates include Test Coverage guidance.
- [x] Unit tests cover parser behavior, JSON and text output, summary counts, coverage association, target existence, offline behavior, template generation, and dogfood readiness.
