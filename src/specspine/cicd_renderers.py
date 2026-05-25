from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_pipeline_json",
    "render_pipeline_yaml",
    "render_pipeline_text",
]


def render_pipeline_json(result: dict[str, Any]) -> str:
    serializable: dict[str, object] = {
        "feature_slug": result.get("feature_slug"),
        "jobs": [
            {
                "description": job["description"] if isinstance(job, dict) else job.description,
                "name": job["name"] if isinstance(job, dict) else job.name,
                "steps": list(job["steps"] if isinstance(job, dict) else job.steps),
            }
            for job in result["jobs"]
        ],
        "merge_conditions": [
            {
                "id": mc["id"] if isinstance(mc, dict) else mc.id,
                "required": mc["required"] if isinstance(mc, dict) else mc.required,
                "text": mc["text"] if isinstance(mc, dict) else mc.text,
            }
            for mc in result["merge_conditions"]
        ],
        "pipeline_type": result["pipeline_type"],
        "raw_content": result["raw_content"],
        "safety_notes": list(result["safety_notes"]),
    }
    return json.dumps(serializable, indent=2, sort_keys=True) + "\n"


def render_pipeline_yaml(result: dict[str, Any]) -> str:
    raw = result.get("raw_content", "")
    if raw:
        return raw
    return "# No raw content available; use render_pipeline_json instead.\n"


def render_pipeline_text(result: dict[str, Any]) -> str:
    lines = [
        f"SpecSpine CI/CD Pipeline ({result['pipeline_type']})",
        "",
    ]

    if result.get("feature_slug"):
        lines.append(f"Feature: {result['feature_slug']}")
        lines.append("")

    lines.append("Jobs:")
    for job in result["jobs"]:
        name = job["name"] if isinstance(job, dict) else job.name
        steps = job["steps"] if isinstance(job, dict) else job.steps
        desc = (
            job["description"]
            if isinstance(job, dict) and job.get("description")
            else (job.description if not isinstance(job, dict) else "")
        )
        lines.append(f"  {name}")
        if desc:
            lines.append(f"    Description: {desc}")
        for step in steps:
            lines.append(f"    - {step}")
        lines.append("")

    lines.append("Merge Conditions:")
    for mc in result["merge_conditions"]:
        req = mc["required"] if isinstance(mc, dict) else mc.required
        text = mc["text"] if isinstance(mc, dict) else mc.text
        marker = "[REQUIRED]" if req else "[OPTIONAL]"
        lines.append(f"  {marker} {text}")
    lines.append("")

    lines.append("Safety Notes:")
    for note in result["safety_notes"]:
        lines.append(f"  - {note}")
    lines.append("")

    return "\n".join(lines)
