# Feature Coverage Readiness

Feature ID: feature-coverage-readiness
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

Teams can already link acceptance criteria to local test files, but the release readiness gate treats those links as informational. High-risk changes need an opt-in check that proves every acceptance criterion has an explicit completed local coverage link before a feature is called ready.

## Users

- Release reviewers deciding whether a feature has enough local test evidence.
- QA and testing agents that need deterministic AC-to-test-file context.
- Maintainers who want stricter pre-release gates without breaking existing workspaces.

## Scope

- Add `--require-coverage` to `specspine feature ready <slug> [path] [--json]`.
- Keep default readiness behavior compatible when the flag is absent.
- Append a stable `feature.test_coverage` check only when coverage is required.
- Reuse `## Test Coverage` links from `quality/features/<slug>.md`.
- Require each acceptance criterion to have at least one checked coverage link whose target path is relative and exists locally.
- Report missing, unchecked, or missing-target coverage by AC id.
- Preserve local-only behavior: no test execution, subprocess calls, network calls, token reads, or new dependencies.

## Non-Goals

- Running test suites or validating test selectors.
- Inferring coverage from implementation files or test names.
- Making coverage links mandatory for default readiness.
- Calling GitHub, upstream CLIs, external APIs, or network services.

## Acceptance Criteria

- [x] Default `feature ready` output and readiness logic do not require test coverage links.
- [x] `feature ready --require-coverage` appends a stable `feature.test_coverage` check to JSON and text blocking output.
- [x] The coverage check passes when every acceptance criterion has a checked local relative coverage link whose target file exists.
- [x] The coverage check fails when an acceptance criterion has no link, only unchecked links, or only links to missing local target files, and the message lists affected AC ids.
- [x] Partial or missing feature bundles still return existing blocking checks without crashing when `--require-coverage` is used.
- [x] The coverage gate reads local Markdown coverage metadata only and does not execute subprocesses, use network access, read tokens, or add dependencies.
- [x] The `feature-coverage-readiness` dogfood bundle is validated and passes both default and coverage-required readiness gates.
