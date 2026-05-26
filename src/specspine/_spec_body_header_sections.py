from __future__ import annotations

from ._spec_section_content import _generate_why_text
from .proposer_build_sections import _generate_scope

__all__ = [
    "_render_header_sections",
]


def _render_header_sections(parsed: dict, intent: str) -> str:
    why_text = _generate_why_text(parsed, intent)
    return (
        "## Why\n\n"
        f"{why_text}\n\n"
        "## Users\n\n"
        f"- End users who need to {parsed['action']} the {parsed['target']}\n"
        f"- Developers maintaining the {parsed['target']} functionality\n"
        f"- Operators configuring the {parsed['target']} in production\n\n"
        "## Scope\n\n"
        f"- {_generate_scope(parsed)}\n"
        f"- Support for {parsed['action']}ing the {parsed['target']} in all relevant contexts\n"
        "- Integration with existing system components\n\n"
        "## Non-Goals\n\n"
        "- This feature will not modify unrelated system behavior\n"
        "- Migration of existing data is out of scope unless explicitly required\n"
        "- Third-party integrations beyond core functionality\n"
    )
