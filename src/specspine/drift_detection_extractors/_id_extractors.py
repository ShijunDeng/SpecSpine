from __future__ import annotations

from ._regex_patterns import AC_ID_RE, TASK_ID_RE, QUALITY_CHECK_RE, COV_LINK_RE

__all__ = [
    "_extract_acs_from_spec",
    "_extract_tasks_from_execution",
    "_extract_acs_from_quality",
    "_extract_cov_links_from_quality",
    "_extract_qc_ids_from_quality",
]


def _extract_acs_from_spec(content: str) -> list[str]:
    return AC_ID_RE.findall(content)


def _extract_tasks_from_execution(content: str) -> list[str]:
    return TASK_ID_RE.findall(content)


def _extract_acs_from_quality(content: str) -> list[str]:
    return AC_ID_RE.findall(content)


def _extract_cov_links_from_quality(content: str) -> list[tuple[str, str]]:
    return COV_LINK_RE.findall(content)


def _extract_qc_ids_from_quality(content: str) -> list[str]:
    return QUALITY_CHECK_RE.findall(content)
