from __future__ import annotations

__all__ = [
    "ADAPTER_HANDOFF_SAFETY_FLAGS",
]

ADAPTER_HANDOFF_SAFETY_FLAGS: dict[str, bool] = {
    "creates_remote": False,
    "executed": False,
    "requires_network": False,
    "requires_token": False,
    "safe_to_auto_run": False,
}
