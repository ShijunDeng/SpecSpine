# Test impact packet

Feature ID: test-impact-packet
Priority: high
Owner: Platform Team
Milestone: 2026.5
Target Release: 2026.5
Project: Native feature bundles
Effort: M
Status: validated

## Why

Agents and reviewers need a local way to choose focused tests after source edits without relying on remote CI, broad test discovery, or conversational guesses about which files matter.

## Users

- Implementation agents deciding which local tests to run after code edits.
- Review agents checking whether proposed test commands are grounded in source and feature evidence.
- Maintainers wiring CI or pre-review workflows around local SpecSpine packets.

## Scope

- Add `specspine tests impact [path]`.
- Add `--json`, repeated `--changed PATH`, and `--feature SLUG`.
- Build a static graph from `src/specspine/*.py` modules to `tests/test_*.py`.
- Include optional local feature Test Coverage targets.
- Recommend commands without executing them.

## Non-Goals

- Running tests or subprocesses.
- Calling network services, GitHub APIs, token providers, or upstream CLIs.
- Inferring runtime coverage from execution traces.
- Replacing full test discovery when static impact cannot find a direct match.

## Acceptance Criteria

- [x] AC001: Report-only mode emits stable JSON with source modules, test files, recommendations, summary, commands, and safety notes.
- [x] AC002: Changed source files recommend impacted `tests.test_*` unittest modules when a static mapping exists.
- [x] AC003: Changed test files recommend their own unittest module.
- [x] AC004: Unmapped changed files include the full unittest discovery command as an explicit fallback.
- [x] AC005: `--feature SLUG` includes local feature Test Coverage target paths and commands.
- [x] AC006: Invalid feature slugs return `2`, missing feature bundles return `1` with a report, and the command remains local/read-only.

## Edge Cases

- Tests may import modules with `import specspine.foo`, `from specspine.foo import name`, or `from specspine import foo`.
- Test Coverage targets may include `::` selectors; impact recommendations should normalize the owning test file.
- Source files without direct tests should not pretend to be covered; full discovery remains the conservative fallback.

## Constraints

- Use Python standard library parsing and local file reads only.
- Keep output deterministic for agents and tests.
- Do not create server files, remote sync files, or token-aware code paths.

## Traceability Notes

- Covered by `tests/test_impact.py`.
