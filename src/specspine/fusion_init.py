from __future__ import annotations

from pathlib import Path

from .fusion_files import FUSION_REQUIRED_FILES, build_fusion_files, build_fusion_spine_file
from .workspace import BASE_WORKSPACE_FILES, normalize_template, write_workspace_files

__all__ = [
    "init_fusion_workspace",
]


def init_fusion_workspace(
    path: Path,
    *,
    agent: str,
    force: bool = False,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
) -> list[Path]:
    root = path.expanduser().resolve()
    base_files = {
        relative_path: template
        for relative_path, template in BASE_WORKSPACE_FILES.items()
        if relative_path != ".specspine/spine.yaml"
    }
    written = write_workspace_files(root, base_files, force=force)

    spine_path = root / ".specspine" / "spine.yaml"
    base_spine = normalize_template(BASE_WORKSPACE_FILES[".specspine/spine.yaml"])
    should_write_spine = force or not spine_path.exists()
    if spine_path.exists() and spine_path.read_text(encoding="utf-8") == base_spine:
        should_write_spine = True

    if should_write_spine:
        written.extend(
            write_workspace_files(
                root,
                {
                    ".specspine/spine.yaml": build_fusion_spine_file(
                        include_openspec=include_openspec,
                        include_speckit=include_speckit,
                        include_superpowers=include_superpowers,
                    )
                },
                force=True,
            )
        )

    written.extend(
        write_workspace_files(
            root,
            build_fusion_files(
                agent,
                include_openspec=include_openspec,
                include_speckit=include_speckit,
                include_superpowers=include_superpowers,
            ),
            force=force,
        )
    )
    return written
