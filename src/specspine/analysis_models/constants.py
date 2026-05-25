from __future__ import annotations

__all__ = [
    "SEVERITIES",
    "AC_REFERENCE_RE",
    "TEST_TARGET_RE",
    "QUALITY_REFERENCE_RE",
    "VAGUE_TERMS",
    "TEXT_MAX_ISSUES_PER_FEATURE",
    "TEXT_MAX_RECOMMENDATIONS",
]

SEVERITIES = ("critical", "high", "medium", "low")
AC_REFERENCE_RE = __import__("re").compile(r"\bAC[-\s]?0*(\d{1,})\b", __import__("re").IGNORECASE)
TEST_TARGET_RE = __import__("re").compile(r"\b(?:tests?/|test_|_test\b|pytest|unittest)\b", __import__("re").IGNORECASE)
QUALITY_REFERENCE_RE = __import__("re").compile(r"\b(?:Q|COV|TC)[-\s]?0*(\d{1,})\b", __import__("re").IGNORECASE)
VAGUE_TERMS = (
    "appropriate",
    "easy",
    "efficient",
    "fast",
    "flexible",
    "intuitive",
    "performant",
    "reliable",
    "robust",
    "scalable",
    "seamless",
    "simple",
    "user-friendly",
)
TEXT_MAX_ISSUES_PER_FEATURE = 8
TEXT_MAX_RECOMMENDATIONS = 12
