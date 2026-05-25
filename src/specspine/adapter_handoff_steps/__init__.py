from __future__ import annotations

from typing import Iterable

from ..adapter_models import AdapterHandoffStep
from ._handoff_openspec import _openspec_steps
from ._handoff_speckit import _speckit_steps
from ._handoff_superpowers import _superpowers_steps
from ._handoff_utils import (
    _adapter_handoff_recommended_commands,
    _mapping_for_status,
    _replace_slug,
)

__all__ = [
    "_adapter_handoff_recommended_commands",
    "_mapping_for_status",
    "_openspec_steps",
    "_recommended_steps",
    "_replace_slug",
    "_speckit_steps",
    "_superpowers_steps",
]


def _recommended_steps(adapter_key: str, slug: str) -> tuple[AdapterHandoffStep, ...]:
    if adapter_key == "openspec":
        return _openspec_steps(slug)
    if adapter_key == "speckit":
        return _speckit_steps(slug)
    if adapter_key == "superpowers":
        return _superpowers_steps(slug)
    return ()
