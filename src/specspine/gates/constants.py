from __future__ import annotations

import re

__all__ = [
    "QUALITY_GATE_SOURCE_FILE",
    "CHECKBOX_RE",
    "BULLET_RE",
    "METADATA_TAG_RE",
    "SUPPORTED_SEVERITIES",
]

QUALITY_GATE_SOURCE_FILE = "quality/checklist.md"
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?(.+?)\s*$")
METADATA_TAG_RE = re.compile(r"\s*\[([A-Za-z][A-Za-z0-9_-]*)\s*:\s*([^\]]*?)\]\s*")
SUPPORTED_SEVERITIES = ("critical", "high", "medium", "low")
