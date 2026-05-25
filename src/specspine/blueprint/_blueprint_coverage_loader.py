from __future__ import annotations

from pathlib import Path

from ..features import (
    FeatureBundleNotFoundError,
    feature_bundle_paths,
    validate_feature_slug,
)
from ..proposer import ACTION_VERBS, MODIFIER_PREPOSITIONS, TARGET_NOUNS

from .blueprint_entities import _derive_error_paths, _identify_data_entities
from .blueprint_extraction import (
    _collect_all_ac_items,
    _extract_behavioral_domains,
)

__all__ = [
    "BlueprintLoadResult",
    "load_blueprint_data",
]


class BlueprintLoadResult:
    def __init__(
        self,
        slug: str,
        resolved_root: Path,
        ac_list: list,
        domains: dict,
    ) -> None:
        self.slug = slug
        self.resolved_root = resolved_root
        self.ac_list = ac_list
        self.domains = domains


def load_blueprint_data(root: Path, slug: str) -> BlueprintLoadResult:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    spec_path = paths["spec"]

    if not spec_path.exists():
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(paths.values()),
        )

    spec_content = spec_path.read_text(encoding="utf-8")
    ac_list = _collect_all_ac_items(spec_content, slug)

    if not ac_list:
        domains: dict = {}
    else:
        domains = _extract_behavioral_domains(spec_content, slug)

    return BlueprintLoadResult(
        slug=slug,
        resolved_root=resolved_root,
        ac_list=ac_list,
        domains=domains,
    )
