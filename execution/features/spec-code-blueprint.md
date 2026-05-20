# Spec-to-Code Blueprint Generator Execution

Feature ID: spec-code-blueprint
Status: implemented
Why: Deterministic implementation blueprints derived from acceptance criteria. Bridges the gap between spec generation and implementation by extracting module structure, function signatures, data entities, and error handling paths from EARS criteria.

## Milestones

- [x] Define BlueprintFunction and BlueprintModule dataclasses
- [x] Implement module extraction from AC analysis
- [x] Implement function signature generation from AC keywords
- [x] Implement error handling path extraction
- [x] Implement JSON and text renderers
- [x] Wire into CLI as `specspine blueprint` command
- [x] Write comprehensive unit tests

## Tasks

- [x] AC001 Define BlueprintFunction dataclass with name, parameters, return_type, description, ac_ids
- [x] AC002 Define BlueprintModule dataclass with module_path, responsibility, functions, ac_ids
- [x] AC003 Define BlueprintEntity dataclass for data entity extraction
- [x] AC004 Define BlueprintErrorPath dataclass for error handling analysis
- [x] AC005 Define BlueprintReport dataclass with full blueprint structure
- [x] AC006 Implement _parse_ac_for_modules to extract module structure
- [x] AC007 Implement _extract_function_signatures from action verbs and target nouns
- [x] AC008 Implement _derive_error_paths from error/exception keywords
- [x] AC009 Implement _build_blueprint_modules as main orchestration
- [x] AC010 Implement render_blueprint_json and render_blueprint_text

## Dependencies

- Feature bundle parsing (features.py) for AC extraction.
- Proposer word lists (proposer.py) for action verb and noun analysis.

## Open Questions

- None; feature is implemented and tested.

## Agent Handoff

- Run `specspine feature handoff spec-code-blueprint . --json` before implementation or review handoff.
- Run `specspine validate . --fusion --features` before handoff or release.
