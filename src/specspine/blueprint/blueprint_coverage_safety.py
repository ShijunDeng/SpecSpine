from __future__ import annotations

from .blueprint_models import (
    BlueprintFunction,
)

__all__ = [
    "_derive_safety_notes",
]


def _derive_safety_notes(
    functions: list[BlueprintFunction],
    error_paths: list,
) -> tuple[str, ...]:
    notes = []

    has_validation = any("validate" in f.name.lower() or "verify" in f.name.lower() for f in functions)
    if not has_validation:
        notes.append("No explicit validation function detected; add input validation before processing.")

    has_error_handling = bool(error_paths)
    if not has_error_handling:
        notes.append("No error paths detected; ensure all external interactions have failure handling.")

    has_persistence = any(w in f.name.lower() for w in ("save", "store", "persist", "write") for f in functions)
    if has_persistence:
        notes.append("Persistence operations detected; verify transactional integrity and rollback paths.")

    notes.append("Review all generated function signatures for correct parameter types and return values.")
    notes.append("Verify error handling covers all identified failure conditions before implementation.")

    return tuple(notes)
