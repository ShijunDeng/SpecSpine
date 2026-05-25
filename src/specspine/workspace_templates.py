from __future__ import annotations

from .templates_backbone import (  # noqa: F401
    SPINE_YAML_TEMPLATE,
    INTENT_TEMPLATE,
    PRODUCT_TEMPLATE,
    ARCHITECTURE_TEMPLATE,
    GITKEEP_CONTENT,
)
from .templates_execution import (  # noqa: F401
    EXECUTION_PLAN_TEMPLATE,
    TASKS_TEMPLATE,
    QUALITY_CHECKLIST_TEMPLATE,
    REVIEW_NOTES_TEMPLATE,
)
from .templates_utils import normalize_template  # noqa: F401
from .templates_utils import normalize_template as _normalize

__all__ = [
    "BASE_WORKSPACE_FILES",
    "normalize_template",
]

BASE_WORKSPACE_FILES: dict[str, str] = {
    ".specspine/spine.yaml": SPINE_YAML_TEMPLATE,
    "specs/intent.md": INTENT_TEMPLATE,
    "specs/product.md": PRODUCT_TEMPLATE,
    "specs/architecture.md": ARCHITECTURE_TEMPLATE,
    "specs/features/.gitkeep": GITKEEP_CONTENT,
    "execution/plan.md": EXECUTION_PLAN_TEMPLATE,
    "execution/tasks.md": TASKS_TEMPLATE,
    "quality/checklist.md": QUALITY_CHECKLIST_TEMPLATE,
    "quality/review.md": REVIEW_NOTES_TEMPLATE,
}
