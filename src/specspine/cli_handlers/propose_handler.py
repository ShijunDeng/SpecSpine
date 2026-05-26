"""Handler for the `propose` CLI command."""

from __future__ import annotations

import json
from pathlib import Path

from ..features import (
    FeatureBundleExistsError,
    InvalidFeatureSlug,
    build_proposal_files,
    create_proposal_bundle,
)
from ..proposer import generate_slug_from_intent, normalize_intent


def _generate_slug_from_intent(intent: str) -> str:
    return generate_slug_from_intent(intent)


def handle_propose(args) -> int:
    """Handle the propose command. Extracted from cli._cmd_propose."""
    root = Path(args.path).expanduser().resolve()
    intent = args.intent

    try:
        intent, warnings = normalize_intent(intent)
        if args.slug:
            slug = args.slug
        else:
            slug = _generate_slug_from_intent(intent)

        from ..features import validate_feature_slug as _validate_slug

        slug = _validate_slug(slug)
    except ValueError as error:
        print(str(error), file=__import__("sys").stderr)
        return 2
    except InvalidFeatureSlug as error:
        print(str(error), file=__import__("sys").stderr)
        return 2

    if args.dry_run:
        try:
            files = build_proposal_files(
                slug,
                intent,
                priority=args.priority,
                owner=args.owner,
                milestone=args.milestone,
                target_release=args.target_release,
                project=args.project,
                effort=args.effort,
            )
        except (InvalidFeatureSlug, ValueError) as error:
            print(str(error), file=__import__("sys").stderr)
            return 2

        targets = {relative_path: root / relative_path for relative_path in files}
        existing_paths = [
            str(path.relative_to(root)) for path in targets.values() if path.exists()
        ]
        if existing_paths and not args.force:
            print(
                f"Feature bundle '{slug}' already has existing files. "
                "Use --force to overwrite them.",
                file=__import__("sys").stderr,
            )
            for path in existing_paths:
                print(f"  existing {path}", file=__import__("sys").stderr)
            return 1

        metadata = {
            "effort": args.effort,
            "milestone": args.milestone,
            "owner": args.owner,
            "priority": args.priority,
            "project": args.project,
            "target_release": args.target_release,
        }
        if args.json:
            payload = {
                "dry_run": bool(args.dry_run),
                "existing_paths": existing_paths,
                "intent": intent,
                "metadata": metadata,
                "files": dict(files),
                "slug": slug,
                "warnings": warnings,
                "written_paths": [],
            }
            print(json.dumps(payload, indent=2, sort_keys=True) + "\n", end="")
        else:
            for warning in warnings:
                print(f"Warning: {warning}")
            print(f"# Proposed feature: {slug}")
            print(f"# Intent: {intent}")
            if existing_paths:
                print("# Existing files: " + ", ".join(existing_paths))
            print()
            for relative_path, content in files.items():
                print(f"## {relative_path}")
                print()
                print(content)
                print()
        return 0

    pre_existing_paths: list[str] = []
    try:
        planned_files = build_proposal_files(
            slug,
            intent,
            priority=args.priority,
            owner=args.owner,
            milestone=args.milestone,
            target_release=args.target_release,
            project=args.project,
            effort=args.effort,
        )
        pre_existing_paths = [
            relative_path
            for relative_path in planned_files
            if (root / relative_path).exists()
        ]
        written = create_proposal_bundle(
            root,
            slug,
            intent,
            priority=args.priority,
            owner=args.owner,
            milestone=args.milestone,
            target_release=args.target_release,
            project=args.project,
            effort=args.effort,
            force=args.force,
        )
    except InvalidFeatureSlug as error:
        print(str(error), file=__import__("sys").stderr)
        return 2
    except ValueError as error:
        print(str(error), file=__import__("sys").stderr)
        return 2
    except FeatureBundleExistsError as error:
        print(str(error), file=__import__("sys").stderr)
        for path in error.existing_paths:
            print(f"  existing {path.relative_to(root)}", file=__import__("sys").stderr)
        return 1

    if args.json:
        files = build_proposal_files(
            slug,
            intent,
            priority=args.priority,
            owner=args.owner,
            milestone=args.milestone,
            target_release=args.target_release,
            project=args.project,
            effort=args.effort,
        )
        payload = {
            "dry_run": False,
            "existing_paths": pre_existing_paths,
            "intent": intent,
            "metadata": {
                "effort": args.effort,
                "milestone": args.milestone,
                "owner": args.owner,
                "priority": args.priority,
                "project": args.project,
                "target_release": args.target_release,
            },
            "files": dict(files),
            "slug": slug,
            "warnings": warnings,
            "written_paths": [str(path.relative_to(root)) for path in written],
        }
        print(json.dumps(payload, indent=2, sort_keys=True) + "\n", end="")
        return 0

    def _print_created(paths: list[Path], root_dir: Path) -> None:
        for path in paths:
            print(f"  created {path.relative_to(root_dir)}")

    for warning in warnings:
        print(f"Warning: {warning}")
    print(f"Created SpecSpine proposal bundle '{slug}' at {root}")
    _print_created(written, root)
    return 0
