from __future__ import annotations

import json

from ..feature_bundle import IssueDraft

__all__ = [
    "render_issue_json",
    "render_issue_text",
]


def render_issue_json(draft: IssueDraft) -> str:
    return json.dumps(draft.as_dict(), indent=2, sort_keys=True) + "\n"


def render_issue_text(draft: IssueDraft) -> str:
    return f"Title: {draft.title}\n\n{draft.body}"
