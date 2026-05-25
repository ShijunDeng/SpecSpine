from __future__ import annotations

from ._policy_comment_parser import (
    _parse_policy_subset,
    _strip_comment,
)
from ._policy_scalar_utils import (
    _clean_scalar,
    _dedupe_strings,
)

__all__ = [
    "_clean_scalar",
    "_dedupe_strings",
    "_parse_policy_subset",
    "_strip_comment",
]

_clean_scalar = _clean_scalar
_dedupe_strings = _dedupe_strings
_parse_policy_subset = _parse_policy_subset
_strip_comment = _strip_comment
