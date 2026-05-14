# Quality Gate Definitions

Feature ID: quality-gate-definitions
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

Repository-level quality policy needs a local machine-readable view before agents, reviewers, or CI can consistently understand the gates that must be satisfied before completion. Exporting the existing `quality/checklist.md` structure gives SpecSpine a deterministic bridge from human checklist prose to agent-readable gate definitions without running commands or depending on GitHub.

## Users

- Implementation agents checking what quality evidence a repository expects.
- Review agents comparing completed work against local quality policy.
- Maintainers preparing CI or branch-protection checks while keeping SpecSpine offline by default.

## Scope

- Add `specspine gates [path] [--json]`.
- Read only `quality/checklist.md` from the selected workspace.
- Parse Markdown checklist rows under `## Required Checks` into stable `GATE001` records.
- Include optional metadata fields for severity, owner, and CI check names when inline labels are present.
- Parse bullet rows under `## Definition Of Done` into stable `DOD001` records.
- Emit stable JSON with source metadata, summaries, gate records, definition-of-done records, and recommended local commands.
- Emit compact text output for humans and agents.
- Return `0` when the source exists, even if required checks are open.
- Return `1` when `quality/checklist.md` is missing while still emitting a report.
- Keep the command local, extractive, zero-dependency, network-free, GitHub-free, token-free, and non-executing.

## Non-Goals

- Executing tests, validation, status checks, shell commands, upstream CLIs, or GitHub Actions.
- Calling GitHub APIs, requiring `gh`, reading GitHub tokens, or creating remote status checks.
- Inferring gates from sections outside `## Required Checks` and `## Definition Of Done`.
- Changing `specspine validate` exit behavior or feature readiness behavior.

## Acceptance Criteria

- [x] `specspine gates --json` reads an initialized workspace and reports required checks from `quality/checklist.md`.
- [x] Required check records use stable ids `GATE001`, `GATE002`, source file, source line, text, done state, and stable metadata fields.
- [x] Definition Of Done records use stable ids `DOD001`, `DOD002`, source file, source line, and text.
- [x] JSON output includes `root`, `source_file`, `source_missing`, `required_checks`, `definition_of_done`, `summary`, and `recommended_commands`.
- [x] Recommended commands include `specspine validate . --fusion --features` and `specspine status . --json --validate`.
- [x] Text output shows the source, required check counts, Definition Of Done count, gate ids, DOD ids, and checkbox markers for required checks.
- [x] Missing `quality/checklist.md` returns code `1` and emits a report with `source_missing=true` and empty lists.
- [x] The parser ignores checklist or bullet rows outside `## Required Checks` and `## Definition Of Done`.
- [x] The command does not execute commands, call network services, call GitHub, require `gh`, read tokens, or add dependencies.
- [x] Documentation, dogfood artifacts, validation, readiness, unit tests, diff checks, and token-prefix scanning are complete.
