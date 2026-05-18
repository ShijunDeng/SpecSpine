# Spec Proposal Generation

Feature ID: spec-proposal-generation
Status: validated
Priority: high
Owner: SpecSpine maintainers
Milestone: SDD workflow completion
Target Release: 0.3.0
Project: Native feature bundles
Effort: L

## Why

Developers describe features in natural language but must manually translate intent into structured spec bundles. Competing SDD tools (OpenSpec, GSD, cc-sdd, Shotgun) all generate rich spec artifacts from rough descriptions. Without this capability, SpecSpine requires users to hand-write spec content, creating friction at the most important entry point of the workflow. `specspine propose` fills spec, execution, and quality files with structured content derived from the intent, turning a rough description into an implementation-ready feature bundle with EARS acceptance criteria, dependency-annotated tasks, and quality checks.

## Users

- Developers using SpecSpine who want to quickly create feature bundles from natural language ideas
- AI coding agents that need structured context from informal intent descriptions
- Teams adopting SDD who want deterministic, zero-dependency spec generation

## Scope

- New CLI subcommand: `specspine propose <idea> <root> [--slug SLUG] [--dry-run] [--json] [--force]`
- Deterministic, zero-dependency intent parsing (no LLM calls, no network access)
- EARS-format acceptance criterion generation from intent keywords and patterns
- Task decomposition with boundary and dependency annotations
- Quality check generation from acceptance criteria
- Feature metadata extraction (priority keywords, effort hints, project context)
- Dry-run mode: preview generated content without writing files
- Output to standard feature bundle paths (`specs/features/`, `execution/features/`, `quality/features/`)
- Adapter-aware proposal notes (how the intent maps to OpenSpec/Spec Kit/Superpowers formats)

## Non-Goals

- LLM-based generation (requires network, API keys, non-zero deps)
- Codebase indexing or analysis (separate feature; Shotgun territory)
- Direct upstream tool invocation (use `--run-upstream` for that)
- Interactive Q&A refinement (can be a future enhancement)
- Modifying existing feature bundles (only creates new bundles)

## Acceptance Criteria

- [x] AC001: `specspine propose "add dark mode toggle" . --slug dark-mode-toggle` creates all three native feature files with populated content (no TODO placeholders in Why, Scope, Acceptance Criteria, Tasks, and Required Checks sections).
- [x] AC002: The generated spec file contains at least 3 EARS-format acceptance criteria derived from the intent text.
- [x] AC003: The generated execution file contains at least 3 tasks with `_Boundary:` and `_Depends:` annotations.
- [x] AC004: The generated quality file contains quality checks that map 1:1 to acceptance criteria.
- [x] AC005: `--dry-run` prints the generated content to stdout without creating or modifying any files.
- [x] AC006: `specspine validate . --features` passes on the generated bundle (all structural contracts satisfied).
- [x] AC007: The command works with zero external dependencies (`PYTHONPATH=src python3 -m specspine`).
- [x] AC008: If a feature bundle with the same slug already exists, the command fails with a clear error unless `--force` is provided.
- [x] AC009: `--json` outputs the generated content as structured JSON for agent consumption.
- [x] AC010: Complex multi-part intents (containing "and", "with", "plus", ";") produce decomposed acceptance criteria and tasks reflecting each component.

## Edge Cases

- Empty or whitespace-only intent text should return a clear error
- Very long intent text (>5000 chars) is handled gracefully with deterministic truncation and text/JSON warnings
- Special characters in intent should not break slug auto-generation
- Unicode characters in intent should be preserved in generated content
- Intent text with only punctuation should return a clear error

## Constraints

- Must remain zero-dependency Python (no external packages beyond stdlib)
- Must not make network calls or require API keys
- Must produce deterministic output for the same input intent
- Generated slugs must pass existing `validate_feature_slug()` validation
- Must integrate with existing `build_feature_files()` template system

## Traceability Notes

- AC001-AC010 map to test cases in `tests/test_propose.py`
- Long-intent truncation and dry-run conflict behavior are covered in `tests/test_propose.py`
- Tasks T001-T008 implement the proposer module and CLI integration
- Quality checks verify EARS format, task annotations, and validation compliance
