from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)
from .fusion import FUSION_REQUIRED_FILES
from .validation_models import ValidationCheck, VALIDATION_STATUSES, AdapterProbe, WORKSPACE_PLACEHOLDER_PHRASES
from .workspace import BASE_WORKSPACE_FILES, check_workspace
from .adapters import probe_adapters

__all__ = [
    "build_validation_report",
    "build_validation_summary",
    "render_validation_json",
    "render_validation_text",
    "validation_exit_code",
]


def _check(
    check_id: str,
    status: str,
    message: str,
    *,
    severity: str | None = None,
) -> ValidationCheck:
    if status not in VALIDATION_STATUSES:
        raise ValueError(f"Unsupported validation status: {status}")

    if severity is None:
        severity = {
            "fail": "error",
            "warn": "warning",
            "pass": "info",
            "skip": "info",
        }[status]

    return ValidationCheck(
        id=check_id,
        status=status,
        message=message,
        severity=severity,
    )


def _relative_paths(paths: Iterable[Path], root: Path) -> set[str]:
    return {str(path.relative_to(root)) for path in paths}


def _file_checks(
    root: Path,
    *,
    required_files: dict[str, str],
    prefix: str,
    label: str,
) -> list[ValidationCheck]:
    present_paths, missing_paths = check_workspace(root, required_files=required_files)
    present = _relative_paths(present_paths, root)
    missing = _relative_paths(missing_paths, root)

    checks: list[ValidationCheck] = []
    for relative_path in sorted(required_files):
        if relative_path in missing:
            checks.append(
                _check(
                    f"{prefix}.required_file:{relative_path}",
                    "fail",
                    f"{label} required file is missing: {relative_path}",
                )
            )
            continue

        if relative_path in present:
            checks.append(
                _check(
                    f"{prefix}.required_file:{relative_path}",
                    "pass",
                    f"{label} required file exists: {relative_path}",
                )
            )

    return checks


def _workspace_placeholder_checks(root: Path) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    for relative_path, phrases in sorted(WORKSPACE_PLACEHOLDER_PHRASES.items()):
        target = root / relative_path
        if not target.exists():
            continue

        try:
            content = target.read_text(encoding="utf-8")
        except OSError:
            continue

        if any(phrase in content for phrase in phrases):
            checks.append(
                _check(
                    f"workspace.placeholder:{relative_path}",
                    "warn",
                    f"Workspace file still contains scaffold placeholder content: {relative_path}",
                )
            )

    return checks


def _run_checks(
    root: Path,
    include_fusion: bool = False,
    include_features: bool = False,
    include_adapters: bool = False,
    adapter_probe: AdapterProbe = probe_adapters,
) -> list[ValidationCheck]:
    from .validation_feature import _feature_bundle_checks
    from .validation_fusion import (
        _fusion_contract_checks,
        _fusion_adapter_contract_checks,
        _adapter_availability_checks,
    )

    checks: list[ValidationCheck] = []

    checks.extend(
        _file_checks(
            root,
            required_files=BASE_WORKSPACE_FILES,
            prefix="workspace",
            label="Workspace",
        )
    )
    checks.extend(_workspace_placeholder_checks(root))

    if include_fusion:
        checks.extend(
            _file_checks(
                root,
                required_files=FUSION_REQUIRED_FILES,
                prefix="fusion",
                label="Fusion",
            )
        )
        checks.extend(_fusion_contract_checks(root))
        checks.extend(_fusion_adapter_contract_checks(root))

    if include_features:
        checks.extend(_feature_bundle_checks(root))

    if include_adapters:
        checks.extend(_adapter_availability_checks(root, adapter_probe=adapter_probe))

    return checks


def _summary(checks: list[ValidationCheck]) -> dict[str, int]:
    counts = {status: 0 for status in VALIDATION_STATUSES}
    for check in checks:
        counts[check.status] += 1
    counts["total"] = len(checks)
    return counts


def build_validation_report(
    path: Path,
    *,
    include_fusion: bool = False,
    include_features: bool = False,
    include_adapters: bool = False,
    adapter_probe: AdapterProbe = probe_adapters,
) -> dict[str, Any]:
    root = path.expanduser().resolve()
    checks = _run_checks(
        root,
        include_fusion=include_fusion,
        include_features=include_features,
        include_adapters=include_adapters,
        adapter_probe=adapter_probe,
    )

    summary = _summary(checks)
    return {
        "root": str(root),
        "ok": summary["fail"] == 0,
        "checks": [check.as_dict() for check in checks],
        "summary": summary,
    }


def build_validation_summary(
    report: dict[str, Any],
    *,
    included: dict[str, bool],
    include_warning_checks: bool = False,
) -> dict[str, Any]:
    failed_checks = [
        check
        for check in report["checks"]
        if check["status"] == "fail"
    ]
    summary = {
        "ok": report["ok"],
        "summary": report["summary"],
        "failed_checks": failed_checks,
        "included": included,
    }
    if include_warning_checks:
        summary["warning_checks"] = [
            check
            for check in report["checks"]
            if check["status"] == "warn"
        ]
    return summary


def render_validation_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_validation_text(report: dict[str, Any]) -> str:
    result = "ok" if report["ok"] else "failed"
    lines = [
        f"SpecSpine validation at {report['root']}",
        f"Result: {result}",
        "Checks:",
    ]

    for check in report["checks"]:
        lines.append(f"  [{check['status']}] {check['id']} - {check['message']}")

    summary = report["summary"]
    lines.append(
        "Summary: "
        f"pass={summary['pass']} "
        f"fail={summary['fail']} "
        f"warn={summary['warn']} "
        f"skip={summary['skip']} "
        f"total={summary['total']}"
    )
    return "\n".join(lines) + "\n"


def validation_exit_code(report: dict[str, Any]) -> int:
    return 1 if report["summary"]["fail"] else 0
