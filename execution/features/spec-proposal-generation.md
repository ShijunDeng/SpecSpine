# Spec Proposal Generation Execution

Feature ID: spec-proposal-generation
Status: implemented
Why: Generate structured spec bundles from natural language intent using deterministic, zero-dependency heuristics

## Milestones

- M1: Core proposer module with intent parsing and EARS generation
- M2: Task decomposition and quality check generation
- M3: CLI integration with dry-run and JSON output modes
- M4: Unit tests and validation integration

## Tasks

- [x] T001: Create `src/specspine/proposer.py` with intent parsing module
  _Boundary: src/specspine/proposer.py (new file)
  _Depends: none
  - Parse intent text into semantic components (action, target, modifiers, conditions)
  - Extract keywords for EARS criterion generation (WHEN, SHALL, IF, THEN patterns)
  - Detect complexity hints (multi-component intents, integration keywords)
  - All logic is deterministic, regex/string-based, zero dependencies

- [x] T002: Implement EARS criterion generator
  _Boundary: src/specspine/proposer.py
  _Depends: T001
  - Generate EARS-format criteria from parsed intent components
  - Pattern: "The system SHALL [behavior] WHEN [condition]" for event-driven features
  - Pattern: "The system SHALL [behavior] IF [precondition]" for conditional features
  - Pattern: "The system SHALL [behavior]" for simple features
  - Minimum 3 criteria, maximum 8 (based on intent complexity)
  - Each criterion gets a stable ID (AC001, AC002, ...)

- [x] T003: Implement task decomposition generator
  _Boundary: src/specspine/proposer.py
  _Depends: T001
  - Break intent into implementation tasks (setup, core logic, integration, verification)
  - Annotate each task with `_Boundary:` (which files/modules it touches)
  - Annotate each task with `_Depends:` (task IDs it depends on)
  - Order tasks topologically so independent tasks can run in parallel
  - Generate at least 3 tasks, maximum 12

- [x] T004: Implement quality check generator
  _Boundary: src/specspine/proposer.py
  _Depends: T001, T002
  - Generate one quality check per acceptance criterion
  - Add edge-case checks from detected modifiers (error handling, permissions, migration)
  - Generate test coverage placeholders mapping AC IDs to test file patterns
  - Add release readiness checks referencing specspine validation commands

- [x] T005: Add `build_proposal_files()` function to features.py
  _Boundary: src/specspine/features.py
  _Depends: T001, T002, T003, T004
  - Signature: `build_proposal_files(slug, intent, *, metadata=None) -> dict[str, str]`
  - Reuses existing `FEATURE_FILE_PATHS` and `normalize_template()`
  - Calls proposer module for criterion, task, and quality generation
  - Returns same dict structure as `build_feature_files()`

- [x] T006: Add `propose` subcommand to CLI
  _Boundary: src/specspine/cli.py
  _Depends: T005
  - Usage: `specspine propose <idea> <root> [--slug SLUG] [--dry-run] [--json] [--force]`
  - Auto-generates slug from intent if not provided (lowercase, hyphenated, validated)
  - `--dry-run`: prints generated Markdown to stdout, no file writes
  - `--json`: outputs structured JSON with file contents
  - `--force`: overwrites existing bundle
  - `--priority`, `--owner`, `--effort`: optional metadata overrides

- [x] T007: Write unit tests for proposer module
  _Boundary: tests/test_propose.py (new file)
  _Depends: T001, T002, T003, T004, T005, T006
  - Test intent parsing: simple, complex, multi-component intents
  - Test EARS generation: event-driven, conditional, simple patterns
  - Test task decomposition: dependency ordering, boundary annotation
  - Test quality check generation: 1:1 AC mapping, edge case detection
  - Test CLI: dry-run, json output, force overwrite, slug auto-generation
  - Test end-to-end: propose -> validate -> ready cycle

- [x] T008: Update agent guidance and documentation
  _Boundary: AGENTS.md, README.md
  _Depends: T006
  - Add `specspine propose` to AGENTS.md common commands
  - Add propose workflow to AGENTS.md working rules
  - Document propose in README.md as the recommended starting point for new features

## Dependencies

- None (zero-dependency design)
- Reuses existing `features.py`, `workspace.py`, and `validation.py` modules

## Open Questions

- Should propose support multi-language intent (non-English)?
- Should propose generate adapter-specific artifacts (OpenSpec proposal.md, design.md)?

## Agent Handoff

- Run `specspine feature handoff spec-proposal-generation . --json` before implementation or review handoff.
- Run `specspine adapters handoff spec-proposal-generation . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks spec-proposal-generation . --json` for the focused implementation checklist.
- Run `specspine feature task-issues spec-proposal-generation . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace spec-proposal-generation . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests spec-proposal-generation . --json` to build the acceptance-test packet.
- Run `specspine feature ready spec-proposal-generation . --json` after implementation evidence is complete.
- Run `specspine feature pr spec-proposal-generation . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan spec-proposal-generation . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine validate . --fusion --features` before handoff or release.
