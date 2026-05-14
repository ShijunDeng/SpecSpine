# Status Coverage Readiness Summaries

Feature ID: status-coverage-readiness-summaries
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

Agents can already ask whether one feature is ready with `--require-coverage`, but workspace status summaries still use default readiness. Multi-feature triage needs the same stricter coverage gate so schedulers can rank and filter release candidates without opening every feature packet.

## Users

- Scheduling agents selecting the next validated feature candidate.
- Release reviewers comparing coverage-required blockers across several native features.
- Maintainers enforcing local AC-to-test evidence before high-risk handoff.

## Scope

- Add `specspine status [path] --feature-summaries --feature-require-coverage`.
- Reject `--feature-require-coverage` without `--feature-summaries` with return code `2` and a clear summary-option error.
- Preserve default status and default feature summary JSON/text output when the flag is absent.
- When the flag is present, compute summary `ready`, `ready_summary`, `blocking_checks`, and `next_actions` with the same coverage gate as `specspine feature ready --require-coverage`.
- Add `coverage_required: true` only to summaries produced under the new flag.
- Apply `--feature-ready yes/no` filtering to coverage-required readiness when the flag is present.
- Mark text summaries with a concise coverage-required indicator.
- Keep the command local-only: no tests executed, subprocess calls, network calls, token reads, upstream CLIs, or new dependencies.

## Non-Goals

- Making coverage-required readiness the default for `status`.
- Running or inferring tests from coverage links.
- Adding repository policy configuration for mandatory coverage gates.
- Changing `feature handoff` default readiness behavior.

## Acceptance Criteria

- [x] `status --feature-summaries --feature-require-coverage --json` includes feature summaries computed with coverage-required readiness.
- [x] Default `status --feature-summaries --json` preserves the existing summary field set and readiness counts.
- [x] The new flag without `--feature-summaries` returns code `2` and the error lists `--feature-require-coverage` with the other summary-only options.
- [x] Coverage-required summaries include `coverage_required: true`; default summaries omit the field.
- [x] A default-ready feature without checked local coverage becomes not ready with `ready_summary.total` increased by one and a `feature.test_coverage` blocking next action.
- [x] `--feature-ready` filters use coverage-required readiness when `--feature-require-coverage` is present.
- [x] Text summaries show that coverage is required while default text remains unchanged.
- [x] The implementation reuses local parsers and readiness logic without subprocesses, network access, token reads, upstream CLIs, or dependencies.
- [x] This dogfood bundle is validated and passes both default and coverage-required readiness gates.
