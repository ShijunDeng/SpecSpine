from __future__ import annotations

import json

from .models import ProvenanceManifest

__all__ = [
    "render_provenance_manifest_json",
]


def render_provenance_manifest_json(manifest: ProvenanceManifest) -> str:
    return json.dumps(manifest.as_dict(), indent=2, sort_keys=True) + "\n"
