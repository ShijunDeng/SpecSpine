from __future__ import annotations

__all__ = [
    "build_fusion_spine_file",
]


def build_fusion_spine_file(
    *,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
) -> str:
    return "\n".join(
        [
            "name: SpecSpine Workspace",
            "version: 0.1",
            "backbone:",
            "  intent: specs/intent.md",
            "  product: specs/product.md",
            "  architecture: specs/architecture.md",
            "  execution_plan: execution/plan.md",
            "  task_board: execution/tasks.md",
            "  quality_checklist: quality/checklist.md",
            "  review_notes: quality/review.md",
            "fusion:",
            "  config: .specspine/fusion.yaml",
            "  map: .specspine/fusion-map.md",
            "adapters:",
            "  openspec:",
            f"    enabled: {str(include_openspec).lower()}",
            "    config: .specspine/adapters/openspec.md",
            "  speckit:",
            f"    enabled: {str(include_speckit).lower()}",
            "    config: .specspine/adapters/speckit.md",
            "  superpowers:",
            f"    enabled: {str(include_superpowers).lower()}",
            "    config: .specspine/adapters/superpowers.md",
            "",
        ]
    )
