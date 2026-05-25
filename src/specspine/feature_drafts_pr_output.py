from __future__ import annotations

import json

from .feature_bundle import PullRequestDraft

__all__ = [
    "render_pull_request_json",
    "render_pull_request_text",
]


def render_pull_request_json(draft: PullRequestDraft) -> str:
    return json.dumps(draft.as_dict(), indent=2, sort_keys=True) + "\n"


def render_pull_request_text(draft: PullRequestDraft) -> str:
    return f"Title: {draft.title}\n\n{draft.body}"
