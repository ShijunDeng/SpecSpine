from __future__ import annotations

__all__ = [
    "render_safety_lines",
    "render_notes_lines",
]


def render_safety_lines(report, adapter_key: str) -> list[str]:
    return [
        "## Safety",
        "",
        "- executed=false",
        "- requires_network=false",
        "- requires_token=false",
        "- creates_remote=false",
        "- safe_to_auto_run=false",
        (
            "- Artifact export does not execute upstream tools, subprocesses, "
            "network calls, GitHub operations, or token reads."
        ),
        "",
    ]


def render_notes_lines(report, adapter_key: str) -> list[str]:
    adapter = report.adapters[adapter_key]
    lines = ["## Notes", ""]
    lines.extend(f"- {note}" for note in adapter.notes)
    return lines
