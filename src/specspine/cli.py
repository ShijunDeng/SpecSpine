from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .adapters import (
    ADAPTER_SPECS,
    AGENT_PROFILES,
    AdapterStatus,
    build_upstream_init_commands,
    probe_adapters,
    run_upstream_initializers,
)
from .agents import AgentsFileExistsError, init_agents_file
from .features import (
    FeatureBundleExistsError,
    FeatureBundleNotFoundError,
    InvalidFeatureStatus,
    InvalidFeatureSlug,
    build_feature_trace_report,
    build_feature_tasks_report,
    build_issue_draft,
    create_feature_bundle,
    get_feature_status,
    render_feature_trace_json,
    render_feature_trace_text,
    render_feature_tasks_json,
    render_feature_tasks_text,
    render_issue_json,
    render_issue_text,
    set_feature_status,
)
from .fusion import FUSION_REQUIRED_FILES, init_fusion_workspace
from .status import build_status, render_status_json, render_status_text
from .validation import (
    build_validation_report,
    build_validation_summary,
    render_validation_json,
    render_validation_text,
    validation_exit_code,
)
from .workspace import BASE_WORKSPACE_FILES, check_workspace, init_workspace


def _print_created(paths: list[Path], root: Path) -> None:
    for path in paths:
        print(f"  created {path.relative_to(root)}")


def _print_adapter_statuses(statuses: list[AdapterStatus] | None = None) -> None:
    if statuses is None:
        statuses = probe_adapters()

    print("External adapters:")
    for status in statuses:
        marker = "ok" if status.available else "missing"
        version = f" ({status.version})" if status.version else ""
        print(f"  [{marker}] {status.display_name}{version}")
        print(f"      {status.detail}")
        if not status.available:
            print(f"      install: {status.install_hint}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="specspine",
        description="SpecSpine: the backbone for spec-driven AI execution.",
    )
    parser.add_argument("--version", action="version", version=f"specspine {__version__}")

    subcommands = parser.add_subparsers(dest="command", required=True)

    init_parser = subcommands.add_parser("init", help="initialize a SpecSpine workspace")
    init_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    init_parser.add_argument("--force", action="store_true", help="overwrite existing SpecSpine files")

    agents_parser = subcommands.add_parser("agents", help="manage AI coding agent instructions")
    agents_subcommands = agents_parser.add_subparsers(dest="agents_command", required=True)
    agents_init_parser = agents_subcommands.add_parser(
        "init",
        help="create project-local AGENTS.md instructions",
    )
    agents_init_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    agents_init_parser.add_argument("--force", action="store_true", help="overwrite AGENTS.md")

    fuse_parser = subcommands.add_parser(
        "fuse",
        help="initialize the OpenSpec + Spec Kit + Superpowers fusion layer",
    )
    fuse_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    fuse_parser.add_argument(
        "--agent",
        choices=sorted(AGENT_PROFILES),
        default="codex",
        help="AI coding agent profile used by upstream adapters",
    )
    fuse_parser.add_argument("--force", action="store_true", help="overwrite SpecSpine fusion files")
    fuse_parser.add_argument(
        "--run-upstream",
        action="store_true",
        help="run upstream initializer commands after writing SpecSpine files",
    )
    fuse_parser.add_argument("--skip-openspec", action="store_true", help="do not enable the OpenSpec adapter")
    fuse_parser.add_argument("--skip-speckit", action="store_true", help="do not enable the Spec Kit adapter")
    fuse_parser.add_argument("--skip-superpowers", action="store_true", help="do not enable the Superpowers adapter")

    feature_parser = subcommands.add_parser("feature", help="manage native SpecSpine features")
    feature_subcommands = feature_parser.add_subparsers(dest="feature_command", required=True)

    feature_new_parser = feature_subcommands.add_parser(
        "new",
        help="create a traceable feature bundle",
    )
    feature_new_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_new_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_new_parser.add_argument("--title", help="human-readable feature title")
    feature_new_parser.add_argument("--why", help="short reason this feature matters")
    feature_new_parser.add_argument("--force", action="store_true", help="overwrite existing feature files")

    feature_issue_parser = feature_subcommands.add_parser(
        "issue",
        help="draft a local GitHub issue from a native feature bundle",
    )
    feature_issue_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_issue_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_issue_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_issue_parser.add_argument(
        "--output",
        help="write the issue body to a file instead of printing the text draft",
    )
    feature_issue_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_tasks_parser = feature_subcommands.add_parser(
        "tasks",
        help="export executable checklist tasks from a native feature bundle",
    )
    feature_tasks_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_tasks_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_tasks_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_tasks_parser.add_argument(
        "--output",
        help="write the text task list to a file instead of printing it",
    )
    feature_tasks_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_trace_parser = feature_subcommands.add_parser(
        "trace",
        help="export a traceability handoff from a native feature bundle",
    )
    feature_trace_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_trace_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_trace_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    feature_trace_parser.add_argument(
        "--output",
        help="write the text trace handoff to a file instead of printing it",
    )
    feature_trace_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing output file",
    )

    feature_status_parser = feature_subcommands.add_parser(
        "status",
        help="read or advance a native feature lifecycle status",
    )
    feature_status_parser.add_argument("slug", help="feature id, such as add-dark-mode")
    feature_status_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    feature_status_parser.add_argument("--set", dest="set_status", help="set the feature lifecycle status")
    feature_status_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )

    doctor_parser = subcommands.add_parser("doctor", help="check SpecSpine workspace files")
    doctor_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    doctor_parser.add_argument(
        "--fusion",
        action="store_true",
        help="also require SpecSpine fusion files",
    )
    doctor_parser.add_argument(
        "--adapters",
        action="store_true",
        help="also check external adapter availability",
    )

    status_parser = subcommands.add_parser("status", help="summarize SpecSpine workspace status")
    status_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    status_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for agents and scripts",
    )
    status_parser.add_argument(
        "--adapters",
        action="store_true",
        help="also check external adapter availability",
    )
    status_parser.add_argument(
        "--validate",
        action="store_true",
        help="include a validation summary in the status output",
    )

    validate_parser = subcommands.add_parser("validate", help="validate SpecSpine workspace contracts")
    validate_parser.add_argument("path", nargs="?", default=".", help="workspace path")
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="print stable JSON for CI and agents",
    )
    validate_parser.add_argument(
        "--fusion",
        action="store_true",
        help="also require and validate SpecSpine fusion files",
    )
    validate_parser.add_argument(
        "--features",
        action="store_true",
        help="also validate native feature bundle consistency",
    )
    validate_parser.add_argument(
        "--adapters",
        action="store_true",
        help="also check enabled external adapter availability",
    )

    adapters_parser = subcommands.add_parser("adapters", help="inspect external adapter integration")
    adapters_subcommands = adapters_parser.add_subparsers(dest="adapters_command", required=True)

    adapters_subcommands.add_parser("doctor", help="check OpenSpec, Spec Kit, and Superpowers availability")
    adapters_subcommands.add_parser("install-hints", help="print upstream install commands and links")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        root = Path(args.path).expanduser().resolve()
        written = init_workspace(root, force=args.force)
        if written:
            print(f"Initialized SpecSpine workspace at {root}")
            _print_created(written, root)
        else:
            print(f"SpecSpine workspace already exists at {root}")
        return 0

    if args.command == "agents":
        if args.agents_command == "init":
            root = Path(args.path).expanduser().resolve()
            try:
                written = init_agents_file(root, force=args.force)
            except AgentsFileExistsError as error:
                print(str(error), file=sys.stderr)
                return 1

            print(f"Initialized SpecSpine agent instructions at {root}")
            print(f"  created {written.relative_to(root)}")
            return 0

    if args.command == "fuse":
        root = Path(args.path).expanduser().resolve()
        include_openspec = not args.skip_openspec
        include_speckit = not args.skip_speckit
        include_superpowers = not args.skip_superpowers

        written = init_fusion_workspace(
            root,
            agent=args.agent,
            force=args.force,
            include_openspec=include_openspec,
            include_speckit=include_speckit,
            include_superpowers=include_superpowers,
        )

        if written:
            print(f"Initialized SpecSpine fusion layer at {root}")
            _print_created(written, root)
        else:
            print(f"SpecSpine fusion layer already exists at {root}")

        commands = build_upstream_init_commands(
            agent=args.agent,
            include_openspec=include_openspec,
            include_speckit=include_speckit,
            include_superpowers=include_superpowers,
            force=args.force,
        )

        if not args.run_upstream:
            print("Upstream tools were not run. Use --run-upstream to invoke:")
            for command in commands:
                print(f"  {command.key}: {command.display() or command.description}")
            return 0

        results = run_upstream_initializers(root, commands)
        failed = False
        print("Upstream initializer results:")
        for result in results:
            marker = "ok" if result.returncode == 0 else "failed"
            print(f"  [{marker}] {result.key}: {result.command}")
            if result.stdout.strip():
                print(f"      {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"      {result.stderr.strip()}")
            failed = failed or result.returncode != 0
        return 1 if failed else 0

    if args.command == "feature":
        if args.feature_command == "new":
            root = Path(args.path).expanduser().resolve()
            try:
                written = create_feature_bundle(
                    root,
                    args.slug,
                    title=args.title,
                    why=args.why,
                    force=args.force,
                )
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleExistsError as error:
                print(str(error), file=sys.stderr)
                for path in error.existing_paths:
                    print(f"  existing {path.relative_to(root)}", file=sys.stderr)
                return 1

            print(f"Created SpecSpine feature bundle '{args.slug}' at {root}")
            _print_created(written, root)
            return 0

        if args.feature_command == "issue":
            root = Path(args.path).expanduser().resolve()
            try:
                draft = build_issue_draft(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature bundle: {error}", file=sys.stderr)
                return 1

            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(draft.body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write issue draft: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_issue_json(draft), end="")
            elif args.output:
                print(f"Wrote GitHub issue draft body to {output_path}")
            else:
                print(render_issue_text(draft), end="")
            return 0

        if args.feature_command == "tasks":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_feature_tasks_report(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature tasks: {error}", file=sys.stderr)
                return 1

            text_body = render_feature_tasks_text(report)
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write feature tasks: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_feature_tasks_json(report), end="")
            elif args.output:
                print(f"Wrote feature task list to {output_path}")
            else:
                print(text_body, end="")
            return 0

        if args.feature_command == "trace":
            root = Path(args.path).expanduser().resolve()
            try:
                report = build_feature_trace_report(root, args.slug)
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not read feature trace: {error}", file=sys.stderr)
                return 1

            text_body = render_feature_trace_text(report)
            if args.output:
                output_path = Path(args.output).expanduser().resolve()
                if output_path.exists() and not args.force:
                    print(
                        f"Output file already exists: {output_path}. "
                        "Use --force to overwrite it.",
                        file=sys.stderr,
                    )
                    return 1

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(text_body, encoding="utf-8")
                except OSError as error:
                    print(f"Could not write feature trace: {error}", file=sys.stderr)
                    return 1

            if args.json:
                print(render_feature_trace_json(report), end="")
            elif args.output:
                print(f"Wrote feature trace handoff to {output_path}")
            else:
                print(text_body, end="")
            return 0

        if args.feature_command == "status":
            root = Path(args.path).expanduser().resolve()
            try:
                if args.set_status:
                    report = set_feature_status(root, args.slug, args.set_status)
                    include_updated = True
                else:
                    report = get_feature_status(root, args.slug)
                    include_updated = False
            except InvalidFeatureSlug as error:
                print(str(error), file=sys.stderr)
                return 2
            except InvalidFeatureStatus as error:
                print(str(error), file=sys.stderr)
                return 2
            except FeatureBundleNotFoundError as error:
                print(str(error), file=sys.stderr)
                for path in error.missing_paths:
                    print(f"  missing {path.relative_to(root)}", file=sys.stderr)
                return 1
            except OSError as error:
                print(f"Could not update feature status: {error}", file=sys.stderr)
                return 1

            payload = report.as_dict(include_updated=include_updated)
            has_files = any(bool(file["exists"]) for file in report.files.values())
            if args.json:
                print(render_status_json(payload), end="")
            else:
                if report.consistent:
                    print(f"Feature {report.feature_id} status: {report.status}")
                else:
                    print(
                        f"Feature {report.feature_id} status: "
                        f"{report.status or 'unknown'} (mixed/inconsistent)"
                    )
                for kind, file in report.files.items():
                    marker = "ok" if file["exists"] else "missing"
                    status = file["status"] or "unknown"
                    print(f"  [{marker}] {kind}: {file['path']} ({status})")
            return 0 if has_files else 1

    if args.command == "doctor":
        required_files = dict(BASE_WORKSPACE_FILES)
        if args.fusion:
            required_files.update(FUSION_REQUIRED_FILES)

        _present, missing = check_workspace(Path(args.path), required_files=required_files)
        if missing:
            print("SpecSpine workspace is incomplete.")
            root = Path(args.path).expanduser().resolve()
            for path in missing:
                print(f"  missing {path.relative_to(root)}")
            if args.adapters:
                _print_adapter_statuses()
            return 1

        print(f"SpecSpine workspace is ready at {Path(args.path).expanduser().resolve()}")
        if args.adapters:
            statuses = probe_adapters()
            _print_adapter_statuses(statuses)
            return 0 if all(status.available for status in statuses) else 1
        return 0

    if args.command == "status":
        status = build_status(Path(args.path), include_adapters=args.adapters)
        if args.validate:
            report = build_validation_report(
                Path(args.path),
                include_fusion=True,
                include_features=True,
                include_adapters=args.adapters,
                adapter_probe=probe_adapters,
            )
            status["validation"] = build_validation_summary(
                report,
                included={
                    "workspace": True,
                    "fusion": True,
                    "features": True,
                    "adapters": bool(args.adapters),
                },
            )
        if args.json:
            print(render_status_json(status), end="")
        else:
            print(render_status_text(status), end="")
        return 0

    if args.command == "validate":
        report = build_validation_report(
            Path(args.path),
            include_fusion=args.fusion,
            include_features=args.features,
            include_adapters=args.adapters,
        )
        if args.json:
            print(render_validation_json(report), end="")
        else:
            print(render_validation_text(report), end="")
        return validation_exit_code(report)

    if args.command == "adapters":
        if args.adapters_command == "doctor":
            statuses = probe_adapters()
            _print_adapter_statuses(statuses)
            return 0 if all(status.available for status in statuses) else 1

        if args.adapters_command == "install-hints":
            for spec in ADAPTER_SPECS.values():
                print(f"{spec.display_name}:")
                print(f"  upstream: {spec.upstream_url}")
                print(f"  install: {spec.install_hint}")
            return 0

    parser.print_help()
    return 1
