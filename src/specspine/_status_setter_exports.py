from __future__ import annotations

__all__ = [
    "_validate_enforced_feature_transition",
    "_allowed_transitions",
]


def _validate_enforced_feature_transition(*args, **kwargs):
    from .feature_status_transition import _validate_enforced_feature_transition
    return _validate_enforced_feature_transition(*args, **kwargs)


def _allowed_transitions(*args, **kwargs):
    from .feature_status_helpers import _allowed_transitions
    return _allowed_transitions(*args, **kwargs)
