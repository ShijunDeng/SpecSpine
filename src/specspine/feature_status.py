from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FEATURE_STATUSES,
    FEATURE_TRANSITIONS,
    FeatureBundleNotFoundError,
    FeatureStatusReport,
    FeatureStatusTransitionError,
    _relative_feature_paths,
    _transition_payload,
    feature_bundle_paths,
    get_feature_status,
    validate_feature_slug,
    validate_feature_status,
)
from .feature_ready import build_feature_ready_report

__all__ = [
    "FeatureStatusTransitionError",
    "set_feature_status",
    "_validate_enforced_feature_transition",
    "_allowed_transitions",
]


def _allowed_transitions(from_status: str) -> tuple[str, ...]:
    return FEATURE_TRANSITIONS.get(from_status, ())


def _replace_or_insert_status_line(content: str, status: str) -> str:
    lines = content.splitlines(keepends=True)
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue

        current_key, _value = stripped.split(":", 1)
        if current_key.strip().lower() == "status":
            newline = "\n" if raw_line.endswith("\n") else ""
            lines[index] = f"Status: {status}{newline}"
            return "".join(lines)

    insert_at = 0
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped or ":" not in stripped:
            continue

        current_key, _value = stripped.split(":", 1)
        if current_key.strip().lower() == "feature id":
            insert_at = index + 1
            break

    lines.insert(insert_at, f"Status: {status}\n")
    return "".join(lines)


def _validate_enforced_feature_transition(
    root: Path,
    slug: str,
    to_status: str,
    status_report: FeatureStatusReport,
) -> dict[str, object]:
    from_status = status_report.status
    if not status_report.consistent or from_status in {None, "mixed"}:
        reason = "Current peer-file statuses are missing or inconsistent."
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="current_status_inconsistent",
            transition=_transition_payload(
                from_status=from_status,
                to_status=to_status,
                enforced=True,
                allowed=False,
                reason=reason,
            ),
            message=(
                f"Cannot update feature {slug} status with enforced transition: "
                f"current status is {from_status or 'unknown'}; {reason}"
            ),
            missing_files=status_report.missing_files,
        )

    if from_status not in FEATURE_TRANSITIONS:
        reason = f"Current status '{from_status}' is not a supported lifecycle status."
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="current_status_invalid",
            transition=_transition_payload(
                from_status=from_status,
                to_status=to_status,
                enforced=True,
                allowed=False,
                reason=reason,
            ),
            message=(
                f"Cannot update feature {slug} status with enforced transition: "
                f"{reason}"
            ),
            missing_files=status_report.missing_files,
        )

    allowed_targets = FEATURE_TRANSITIONS[from_status]
    if to_status not in allowed_targets:
        if from_status == "archived":
            reason = "Archived is terminal and cannot transition to another status."
        else:
            reason = (
                f"Transition {from_status} -> {to_status} is not allowed; "
                f"allowed targets are: {', '.join(allowed_targets)}."
            )
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="transition_not_allowed",
            transition=_transition_payload(
                from_status=from_status,
                to_status=to_status,
                enforced=True,
                allowed=False,
                reason=reason,
            ),
            message=(
                f"Cannot update feature {slug} status with enforced transition: "
                f"{reason}"
            ),
            missing_files=status_report.missing_files,
        )

    transition = _transition_payload(
        from_status=from_status,
        to_status=to_status,
        enforced=True,
        allowed=True,
    )
    if to_status == "archived":
        ready_report = build_feature_ready_report(root, slug)
        if not ready_report.ready:
            reason = "Archive requires feature ready gate to pass first."
            raise FeatureStatusTransitionError(
                feature_id=slug,
                error="archive_not_ready",
                transition=_transition_payload(
                    from_status=from_status,
                    to_status=to_status,
                    enforced=True,
                    allowed=True,
                    reason=reason,
                ),
                message=(
                    f"Cannot archive feature {slug}: {reason} "
                    "Run feature ready and resolve blocking checks."
                ),
                blocking_checks=tuple(
                    check.as_dict() for check in ready_report.blocking_checks
                ),
                gaps=ready_report.gaps,
                missing_files=ready_report.missing_files,
            )

    return transition


def set_feature_status(
    root: Path,
    slug: str,
    status: str,
    *,
    enforce_transition: bool = False,
) -> FeatureStatusReport:
    slug = validate_feature_slug(slug)
    status = validate_feature_status(status)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    before = get_feature_status(resolved_root, slug)
    existing_paths = [path for path in paths.values() if path.exists()]
    if not existing_paths:
        if enforce_transition:
            reason = "Current peer-file statuses are missing or inconsistent."
            raise FeatureStatusTransitionError(
                feature_id=slug,
                error="current_status_inconsistent",
                transition=_transition_payload(
                    from_status=before.status,
                    to_status=status,
                    enforced=True,
                    allowed=False,
                    reason=reason,
                ),
                message=(
                    f"Cannot update feature {slug} status with enforced transition: "
                    f"current status is unknown; {reason}"
                ),
                missing_files=before.missing_files,
            )
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(paths.values()),
        )

    if enforce_transition:
        transition = _validate_enforced_feature_transition(
            resolved_root,
            slug,
            status,
            before,
        )
    else:
        transition = _transition_payload(
            from_status=before.status,
            to_status=status,
            enforced=False,
            allowed=True,
        )

    updated_files: list[str] = []
    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8")
        path.write_text(_replace_or_insert_status_line(content, status), encoding="utf-8")
        updated_files.append(relative_paths[kind])

    report = get_feature_status(resolved_root, slug)
    return FeatureStatusReport(
        feature_id=report.feature_id,
        status=report.status,
        consistent=report.consistent,
        files=report.files,
        missing_files=report.missing_files,
        updated_files=tuple(updated_files),
        transition=transition,
    )
