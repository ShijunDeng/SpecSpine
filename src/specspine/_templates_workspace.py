from __future__ import annotations

__all__ = [
    "SPINE_YAML_TEMPLATE",
    "GITKEEP_CONTENT",
]

SPINE_YAML_TEMPLATE = """
    name: SpecSpine Workspace
    version: 0.1
    backbone:
      intent: specs/intent.md
      product: specs/product.md
      architecture: specs/architecture.md
      execution_plan: execution/plan.md
      task_board: execution/tasks.md
      quality_checklist: quality/checklist.md
      review_notes: quality/review.md
    adapters:
      openspec:
        enabled: false
        config: .specspine/adapters/openspec.md
      speckit:
        enabled: false
        config: .specspine/adapters/speckit.md
      superpowers:
        enabled: false
        config: .specspine/adapters/superpowers.md
"""

GITKEEP_CONTENT = ""
