from __future__ import annotations

from ._handoff_report_model import FeatureHandoffReport as _FeatureHandoffReportBase
from ._handoff_report_summary import get_handoff_summary
from ._handoff_report_serialization import handoff_report_as_dict

__all__ = [
    "FeatureHandoffReport",
]


class FeatureHandoffReport(_FeatureHandoffReportBase):

    @property
    def summary(self) -> dict[str, object]:
        return get_handoff_summary(self)

    def as_dict(self) -> dict[str, object]:
        return handoff_report_as_dict(self)
