from __future__ import annotations

__all__ = [
    "_join",
    "_blocked_lower_name",
    "_blocked_path_remnants",
    "_blocked_content_patterns",
]


def _join(*parts: str) -> str:
    return "".join(parts)


def _blocked_lower_name() -> str:
    return _join("m", "cp")


def _blocked_path_remnants() -> tuple[str, ...]:
    lower_name = _blocked_lower_name()
    source_prefix = "src/specspine/"
    test_prefix = "tests/test_"
    return (
        source_prefix + _join("github", "_api") + ".py",
        source_prefix + _join("github", "_auth") + ".py",
        source_prefix + lower_name + ".py",
        source_prefix + "sync.py",
        source_prefix + "guard.py",
        test_prefix + "sync.py",
        test_prefix + "guard.py",
        test_prefix + lower_name + ".py",
    )


def _blocked_content_patterns() -> tuple[str, ...]:
    lower_name = _blocked_lower_name()
    return (
        lower_name,
        lower_name.upper(),
        lower_name + "-server",
        _join("github", "-remote-", "sync"),
        _join("github", "_api"),
        _join("github", "_auth"),
        _join("SPECSPINE_", "GITHUB", "_", "TOKEN"),
        _join("token", "-stdin"),
        _join("--", "github", "-token"),
        _join("sync", "_feature_to_", "github"),
        _join("FeatureStatus", "SyncError"),
        _join("g", "hp_"),
    )
