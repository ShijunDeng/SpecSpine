# Feature Test Packet

Feature ID: feature-test-packet
Status: validated

## Why

Testing and QA agents need a stable local packet that answers which acceptance points to test, what test plan already exists, and which evidence gaps still block confidence. Existing feature handoff, trace, ready, and PR draft views are broader than this testing-specific context, so QA work still requires manual stitching.

## Users

- QA agents preparing acceptance verification from local SpecSpine feature bundles.
- Test-focused subagents that need acceptance criteria, existing test plan evidence, gaps, and blockers without implementation instructions.
- Maintainers who need a deterministic packet that remains offline and token-free.

## Scope

- Add `specspine feature tests <slug> [path] [--json] [--output FILE] [--force]`.
- Compose the packet from local feature handoff, trace, readiness, status, and peer-file evidence.
- Export required JSON fields for feature id, status, readiness, source files, missing files, gaps, blocking checks, acceptance criteria, existing test plan, deterministic test cases, quality checks, summary counts, and recommended local commands.
- Generate one pending test case per acceptance criterion using stable ids where `TC001` maps to `AC001`.
- Render text with sources, summary, GitHub Markdown checklist test cases, existing test plan, quality checks, gaps, blocking checks, and key commands.
- Preserve existing exporter output semantics for `--json`, `--output`, and `--force`.
- Keep partial bundles usable while clearly reporting missing peer files and gaps.

## Non-Goals

- Running tests or interpreting test results.
- Generating test code, test filenames, or implementation-file guesses.
- Calling GitHub APIs, invoking upstream CLIs, using network access, reading tokens, or adding third-party dependencies.
- Replacing the broader feature handoff, traceability, readiness, or PR draft commands.

## Acceptance Criteria

- [x] `specspine feature tests <slug> [path] [--json] [--output FILE] [--force]` is registered under the `feature` command group.
- [x] The command exports only a local acceptance-test packet and does not run tests, generate test code, infer implementation files, call network services, call GitHub, invoke upstream CLIs, read tokens, or add dependencies.
- [x] JSON output includes `feature_id`, `status`, `ready`, `source_files`, `missing_files`, `gaps`, `blocking_checks`, `acceptance_criteria`, `test_plan`, `test_cases`, `quality_checks`, `summary`, and `recommended_commands`.
- [x] Test cases are deterministic with one case per acceptance criterion, so `TC001` maps to `AC001`, carries the AC text, source file, line, pending status, and explicit behavior-to-test wording.
- [x] Text output includes feature/status/ready, sources, summary, test cases, existing test plan, quality checks, gaps, blocking checks, and key commands.
- [x] Text test cases use GitHub Markdown checklist syntax and remain unchecked for QA or human verification.
- [x] `--output` writes the text packet, refuses overwrite by default, honors `--force`, and keeps stdout JSON when combined with `--json`.
- [x] Partial bundles return `0` with missing files and gaps; missing bundles return non-zero; invalid slugs return `2`.
- [x] Documentation, agent guidance, tests, and dogfood artifacts describe the testing packet workflow.
