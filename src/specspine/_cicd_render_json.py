from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_pipeline_json",
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
