from __future__ import annotations

from ._constants import GENERATED_DIRECTORY_NAMES, VCS_DIRECTORY_NAMES

__all__ = [
    "_is_generated_directory",
    "_is_vcs_directory",
]


def _is_generated_directory(name: str) -> bool:
    return name in GENERATED_DIRECTORY_NAMES


def _is_vcs_directory(name: str) -> bool:
    return name in VCS_DIRECTORY_NAMES
