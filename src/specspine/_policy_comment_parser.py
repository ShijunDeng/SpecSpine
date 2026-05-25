from __future__ import annotations

from ._policy_comment_strip import _strip_comment
from ._policy_subset_parser import _parse_policy_subset

_strip_comment = _strip_comment
_parse_policy_subset = _parse_policy_subset

__all__ = [
    "_parse_policy_subset",
    "_strip_comment",
]
