from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "FeatureArchivePackage",
]


@dataclass(frozen=True)
class FeatureArchivePackage:
    output_dir: Path
    readme_path: Path
    report_path: Path
    source_paths: tuple[Path, ...]
    written_paths: tuple[Path, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "output_dir": str(self.output_dir),
            "readme": str(self.readme_path),
            "report": str(self.report_path),
            "sources": [str(path) for path in self.source_paths],
            "written_paths": [str(path) for path in self.written_paths],
        }
