from __future__ import annotations

from ._content_reader import load_feature_contents
from ._section_extractor import extract_draft_sections

__all__ = [
    "load_feature_contents",
    "extract_draft_sections",
]


def __getattr__(name: str) -> object:
    if name == "load_feature_contents":
        from ._content_reader import load_feature_contents as _func
        return _func
    if name == "extract_draft_sections":
        from ._section_extractor import extract_draft_sections as _func
        return _func
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
