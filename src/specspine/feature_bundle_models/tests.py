from __future__ import annotations

from dataclasses import dataclass

from ._tests_report_model import FeatureTestsReport as _BaseFeatureTestsReport
from ._tests_report_summary import compute_tests_report_summary
from ._tests_report_serialization import serialize_tests_report

__all__ = [
    "FeatureTestsReport",
]


@dataclass(frozen=True)
class FeatureTestsReport(_BaseFeatureTestsReport):

    @property
    def summary(self) -> dict[str, object]:
        return compute_tests_report_summary(self)

    def as_dict(self) -> dict[str, object]:
        return serialize_tests_report(self)
