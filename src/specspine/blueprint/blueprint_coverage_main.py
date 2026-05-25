from __future__ import annotations

from pathlib import Path

from ._blueprint_coverage_assembler import assemble_blueprint_report
from ._blueprint_coverage_loader import BlueprintLoadResult, load_blueprint_data
from .blueprint_models import BlueprintReport

__all__ = [
    "build_spec_code_blueprint",
]


def build_spec_code_blueprint(root: Path, slug: str) -> BlueprintReport:
    load_result = load_blueprint_data(root, slug)
    return assemble_blueprint_report(
        slug=load_result.slug,
        ac_list=load_result.ac_list,
        domains=load_result.domains,
    )
