from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .features import (
    InvalidFeatureSlug,
    build_feature_handoff_report,
    build_feature_ready_report,
    validate_feature_slug,
)


MAX_TEXT_BYTES = 128 * 1024


@dataclass(frozen=True)
class SecurityCueReport:
    root: Path
    feature_id: str | None
    changed_files: tuple[str, ...]
    files: tuple[dict[str, Any], ...]
    cues: tuple[dict[str, Any], ...]
    feature_evidence: tuple[dict[str, Any], ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_files": list(self.changed_files),
            "cues": [dict(cue) for cue in self.cues],
            "feature_evidence": [dict(evidence) for evidence in self.feature_evidence],
            "feature_id": self.feature_id,
            "files": [dict(file) for file in self.files],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
        }


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _normalise_changed_file(root: Path, value: str) -> tuple[str, Path]:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    return _relative_path(root, resolved), resolved


def _classify_changed_file(path: str) -> str:
    if path.startswith("src/specspine/") and path.endswith(".py"):
        return "source"
    if path.startswith("tests/test_") and path.endswith(".py"):
        return "test"
    if path.startswith("specs/features/") and path.endswith(".md"):
        return "feature-spec"
    if path.startswith("execution/features/") and path.endswith(".md"):
        return "feature-execution"
    if path.startswith("quality/features/") and path.endswith(".md"):
        return "feature-quality"
    if (
        path in {"README.md", "AGENTS.md"}
        or path.startswith("docs/")
        or path
        in {
            "execution/plan.md",
            "quality/review.md",
            "specs/architecture.md",
            "specs/product.md",
        }
    ):
        return "project-doc"
    if path == "pyproject.toml" or path.startswith(".github/") or path.startswith(
        ".specspine/"
    ):
        return "config"
    return "other"


def _feature_slug_from_path(path: str) -> str | None:
    for prefix in ("specs/features/", "execution/features/", "quality/features/"):
        if path.startswith(prefix) and path.endswith(".md"):
            slug = path.removeprefix(prefix).removesuffix(".md")
            if "/" not in slug:
                try:
                    return validate_feature_slug(slug)
                except InvalidFeatureSlug:
                    return None
    return None


def _dedupe(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return tuple(deduped)


def _is_within_root(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _read_small_text(path: Path) -> tuple[str | None, str | None]:
    try:
        stat = path.stat()
    except OSError as error:
        return None, f"stat_error:{error.__class__.__name__}"
    if not path.is_file():
        return None, "not_file"
    if stat.st_size > MAX_TEXT_BYTES:
        return None, "too_large"
    try:
        raw = path.read_bytes()
    except OSError as error:
        return None, f"read_error:{error.__class__.__name__}"
    if b"\0" in raw:
        return None, "binary"
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        try:
            return raw.decode("utf-8", errors="replace"), None
        except UnicodeDecodeError:
            return None, "decode_error"


_CUE_PATTERNS: tuple[tuple[str, str, str, str, str], ...] = (
    ("token", r"\btoken\b", "medium", "credential", "Token-related text changed."),
    ("secret", r"\bsecret\b", "high", "credential", "Secret-related text changed."),
    ("password", r"\bpassword\b", "high", "credential", "Password-related text changed."),
    ("api_key", r"\bapi[_-]?key\b", "high", "credential", "API key-related text changed."),
    ("private_key", r"\bprivate[_ -]?key\b", "high", "credential", "Private key-related text changed."),
    ("auth", r"\bauth(?:entication|orization)?\b", "medium", "auth", "Authentication-related text changed."),
    ("session", r"\bsession\b", "medium", "auth", "Session-related text changed."),
    ("cookie", r"\bcookie\b", "medium", "auth", "Cookie-related text changed."),
    ("cors", r"\bcors\b", "medium", "web", "CORS-related text changed."),
    ("sql", r"\bsql\b", "medium", "data", "SQL-related text changed."),
    ("query", r"\bquery\b", "low", "data", "Query-related text changed."),
    ("subprocess", r"\bsubprocess\b", "high", "execution", "Subprocess-related text changed."),
    ("shell", r"\bshell\b", "high", "execution", "Shell-related text changed."),
    ("eval", r"\beval\b", "high", "execution", "Dynamic evaluation text changed."),
    ("exec", r"\bexec\b", "high", "execution", "Dynamic execution text changed."),
    ("pickle", r"\bpickle\b", "high", "deserialization", "Pickle-related text changed."),
    ("yaml.load", r"\byaml\.load\b", "high", "deserialization", "YAML load-related text changed."),
    ("requests", r"\brequests\b", "medium", "network", "Requests-related text changed."),
    ("urlopen", r"\burlopen\b", "medium", "network", "URL opening-related text changed."),
    ("socket", r"\bsocket\b", "medium", "network", "Socket-related text changed."),
    ("crypto", r"\bcrypto(?:graphy)?\b", "medium", "crypto", "Cryptography-related text changed."),
    ("hash", r"\bhash\b", "low", "crypto", "Hash-related text changed."),
    ("random", r"\brandom\b", "low", "crypto", "Randomness-related text changed."),
    ("permission", r"\bpermission\b", "medium", "authorization", "Permission-related text changed."),
    ("admin", r"\badmin\b", "medium", "authorization", "Admin-related text changed."),
    ("path traversal", r"\bpath traversal\b", "high", "filesystem", "Path traversal-related text changed."),
    ("../", r"\.\./", "high", "filesystem", "Parent-directory traversal text changed."),
)


def _detect_cues(path: str, category: str, text: str) -> tuple[dict[str, Any], ...]:
    cues: list[dict[str, Any]] = []
    sequence = 1
    for line_number, line in enumerate(text.splitlines(), start=1):
        for keyword, pattern, severity, cue_category, message in _CUE_PATTERNS:
            if re.search(pattern, line, flags=re.IGNORECASE):
                cues.append(
                    {
                        "category": cue_category,
                        "id": f"{path}:{line_number}:{keyword}:{sequence}",
                        "keyword": keyword,
                        "line": line_number,
                        "message": message,
                        "path": path,
                        "severity": severity,
                    }
                )
                sequence += 1
    return tuple(cues)


def _feature_evidence(root: Path, slug: str) -> dict[str, Any]:
    handoff = build_feature_handoff_report(root, slug, require_coverage=True)
    ready = build_feature_ready_report(root, slug, require_coverage=True)
    return {
        "blocking_checks": [check.as_dict() for check in ready.blocking_checks],
        "feature_id": slug,
        "gaps": [dict(gap) for gap in ready.gaps],
        "has_native_files": handoff.has_native_files,
        "missing_files": list(ready.missing_files),
        "ready": ready.ready,
        "source_files": [
            str(source["path"])
            for source in handoff.sources.values()
            if source.get("exists")
        ],
        "status": ready.status,
    }


def _recommended_commands(
    changed_files: tuple[str, ...],
    feature_ids: tuple[str, ...],
) -> tuple[str, ...]:
    commands: list[str] = []
    if changed_files:
        for path in changed_files:
            commands.append(f"specspine change risk . --changed {path} --json")
            commands.append(f"specspine review packet . --changed {path} --json")
            commands.append(f"specspine tests impact . --changed {path} --json")
    else:
        commands.extend(
            [
                "specspine change risk . --json",
                "specspine review packet . --json",
                "specspine tests impact . --json",
            ]
        )
    for slug in feature_ids:
        commands.append(f"specspine change risk . --feature {slug} --json")
        commands.append(f"specspine review packet . --feature {slug} --json")
        commands.append(f"specspine tests impact . --feature {slug} --json")
        commands.append(
            f"specspine feature ready {slug} . --json --require-coverage"
        )
    return _dedupe(commands)


def build_security_cue_report(
    root: Path,
    *,
    changed_files: tuple[str, ...] = (),
    feature: str | None = None,
) -> SecurityCueReport:
    resolved_root = root.resolve()
    feature_slug = validate_feature_slug(feature) if feature is not None else None
    normalised_pairs = [
        _normalise_changed_file(resolved_root, path) for path in changed_files
    ]
    normalised_changed_files = _dedupe([path for path, _resolved in normalised_pairs])
    resolved_by_path = {path: resolved for path, resolved in normalised_pairs}

    files: list[dict[str, Any]] = []
    cues: list[dict[str, Any]] = []
    inferred_features: list[str] = []
    severity_counts = {"high": 0, "low": 0, "medium": 0}
    categories: dict[str, int] = {}
    files_existing = 0

    for path in normalised_changed_files:
        resolved_path = resolved_by_path[path]
        category = _classify_changed_file(path)
        exists = resolved_path.exists()
        if exists:
            files_existing += 1
        categories[category] = categories.get(category, 0) + 1

        file_info: dict[str, Any] = {
            "category": category,
            "exists": exists,
            "path": path,
        }
        text: str | None = None
        if exists:
            if _is_within_root(resolved_root, resolved_path):
                text, skipped_reason = _read_small_text(resolved_path)
                file_info["text_read"] = text is not None
                if skipped_reason is not None:
                    file_info["read_skipped"] = skipped_reason
            else:
                file_info["text_read"] = False
                file_info["read_skipped"] = "outside_root"
        else:
            file_info["text_read"] = False
        files.append(file_info)

        if text is not None:
            found = _detect_cues(path, category, text)
            cues.extend(found)
            for cue in found:
                severity = str(cue["severity"])
                severity_counts[severity] += 1

        inferred = _feature_slug_from_path(path)
        if inferred is not None:
            inferred_features.append(inferred)

    feature_ids = _dedupe(
        tuple([slug for slug in inferred_features] + ([feature_slug] if feature_slug else []))
    )
    evidence = tuple(_feature_evidence(resolved_root, slug) for slug in feature_ids)
    summary = {
        "categories": dict(sorted(categories.items())),
        "changed_files": len(normalised_changed_files),
        "cues_total": len(cues),
        "feature_ids": list(feature_ids),
        "files_existing": files_existing,
        "high": severity_counts["high"],
        "low": severity_counts["low"],
        "medium": severity_counts["medium"],
    }
    safety_notes = (
        "This report is advisory only and is not proof of a vulnerability.",
        "Security cues are text hints from changed paths and local files, not SAST findings.",
        "SpecSpine did not execute commands, run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )
    return SecurityCueReport(
        root=resolved_root,
        feature_id=feature_slug,
        changed_files=normalised_changed_files,
        files=tuple(files),
        cues=tuple(cues),
        feature_evidence=evidence,
        summary=summary,
        recommended_commands=_recommended_commands(normalised_changed_files, feature_ids),
        safety_notes=safety_notes,
    )


def render_security_cue_json(report: SecurityCueReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_security_cue_text(report: SecurityCueReport) -> str:
    summary = report.summary
    lines = [
        f"Security cues report: {report.root}",
        f"Feature: {report.feature_id or 'workspace'}",
        (
            "Summary: "
            f"changed_files={summary['changed_files']} "
            f"files_existing={summary['files_existing']} "
            f"cues_total={summary['cues_total']} "
            f"high={summary['high']} "
            f"medium={summary['medium']} "
            f"low={summary['low']}"
        ),
        "Files:",
    ]
    if report.files:
        for file in report.files:
            marker = "exists" if file["exists"] else "missing"
            lines.append(f"- [{marker}] {file['category']}: {file['path']}")
    else:
        lines.append("- None.")

    lines.append("Cues:")
    if report.cues:
        for cue in report.cues:
            lines.append(
                "- "
                f"{cue['severity']} {cue['keyword']} "
                f"{cue['path']}:{cue['line']} - {cue['message']}"
            )
    else:
        lines.append("- None.")

    if report.feature_evidence:
        lines.append("Feature evidence:")
        for evidence in report.feature_evidence:
            lines.append(
                "- "
                f"{evidence['feature_id']}: "
                f"status={evidence['status']} "
                f"ready={'yes' if evidence['ready'] else 'no'} "
                f"has_native_files={'yes' if evidence['has_native_files'] else 'no'}"
            )

    lines.append("Recommended commands:")
    for command in report.recommended_commands:
        lines.append(f"- {command}")

    lines.append("Safety notes:")
    for note in report.safety_notes:
        lines.append(f"- {note}")

    return "\n".join(lines) + "\n"
