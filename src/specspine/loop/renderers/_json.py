from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_loop_packet_json",
]


def render_loop_packet_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=2, sort_keys=True) + "\n"
