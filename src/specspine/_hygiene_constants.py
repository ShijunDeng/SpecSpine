from __future__ import annotations

__all__ = [
    "GENERATED_DIRECTORY_NAMES",
    "GENERATED_FILE_NAMES",
    "GENERATED_FILE_SUFFIXES",
    "CONTENT_SCAN_EXCLUDED_PATHS",
    "VCS_DIRECTORY_NAMES",
    "SEVERITIES",
    "CATEGORIES",
]

GENERATED_DIRECTORY_NAMES = ("__pycache__", ".pytest_cache")
GENERATED_FILE_NAMES = (".DS_Store",)
GENERATED_FILE_SUFFIXES = (".pyc", ".pyo")
CONTENT_SCAN_EXCLUDED_PATHS = (
    "src/specspine/hygiene.py",
    "tests/test_hygiene.py",
)
VCS_DIRECTORY_NAMES = (".git", ".hg", ".svn")
SEVERITIES = ("critical", "high", "medium", "low")
CATEGORIES = ("forbidden_content", "forbidden_path", "generated_artifact")
