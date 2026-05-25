from __future__ import annotations

import json

from .models import ProvenanceManifest

__all__ = [
    "render_provenance_manifest_json",
    "render_provenance_manifest_text",
]


def render_provenance_manifest_json(manifest: ProvenanceManifest) -> str:
    return json.dumps(manifest.as_dict(), indent=2, sort_keys=True) + "\n"


def render_provenance_manifest_text(manifest: ProvenanceManifest) -> str:
    summary = manifest.summary
    lines = [
        f"Provenance manifest: {manifest.root}",
        f"Feature: {manifest.feature_id or 'workspace'}",
        (
            "Summary: "
            f"artifacts={summary['artifacts_total']} "
            f"existing={summary['artifacts_existing']} "
            f"hashed={summary['hashed_artifacts']} "
            f"missing={summary['missing_artifacts']} "
            f"outside_root={summary['outside_root_artifacts']}"
        ),
        "",
        "Artifacts:",
    ]
    if manifest.artifacts:
        for artifact in manifest.artifacts:
            marker = "exists" if artifact["exists"] else "missing"
            detail = ""
            if "sha256" in artifact:
                detail = f" sha256={artifact['sha256']} bytes={artifact['bytes']}"
            elif artifact.get("reason"):
                detail = f" reason={artifact['reason']}"
            lines.append(
                f"- [{marker}] {artifact['kind']}: {artifact['path']}{detail}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Feature evidence:")
    if manifest.feature_evidence:
        for evidence in manifest.feature_evidence:
            lines.append(
                "- "
                f"{evidence['feature_id']}: "
                f"status={evidence['status']} "
                f"ready={'yes' if evidence['ready'] else 'no'} "
                f"has_native_files={'yes' if evidence['has_native_files'] else 'no'} "
                f"blocking={len(evidence['blocking_checks'])} "
                f"gaps={len(evidence['gaps'])}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Recommended commands:")
    lines.extend(f"- {command}" for command in manifest.recommended_commands)
    lines.append("")
    lines.append("Safety notes:")
    lines.extend(f"- {note}" for note in manifest.safety_notes)
    return "\n".join(lines) + "\n"
