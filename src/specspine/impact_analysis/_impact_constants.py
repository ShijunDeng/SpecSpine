from __future__ import annotations

SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"

IMPACT_TYPE_FEATURE = "feature"
IMPACT_TYPE_TEST = "test"
IMPACT_TYPE_CODE = "code"

SOURCE_GLOBS = ("src/**/*.py",)
TEST_GLOBS = ("tests/**/*.py",)


__all__ = [
    "IMPACT_TYPE_CODE",
    "IMPACT_TYPE_FEATURE",
    "IMPACT_TYPE_TEST",
    "SEVERITY_HIGH",
    "SEVERITY_LOW",
    "SEVERITY_MEDIUM",
    "SOURCE_GLOBS",
    "TEST_GLOBS",
]
