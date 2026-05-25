from __future__ import annotations

from typing import Any

from ._recommend_fallback import _build_fallback_recommendation
from ._recommend_impact import _build_recommendations_for_changed_files

__all__ = [
    "_build_recommendations_for_changed_files",
    "_build_fallback_recommendation",
]

_build_fallback_recommendation = _build_fallback_recommendation
_build_recommendations_for_changed_files = _build_recommendations_for_changed_files
