from __future__ import annotations

from pathlib import Path

from .adapters import (
    ADAPTER_SPECS,
    build_upstream_init_commands,
    get_agent_profile,
)
from .workspace import BASE_WORKSPACE_FILES, normalize_template, write_workspace_files


FUSION_REQUIRED_FILES = {
    ".specspine/fusion.yaml": "",
    ".specspine/fusion-map.md": "",
    ".specspine/adapters/openspec.md": "",
    ".specspine/adapters/speckit.md": "",
    ".specspine/adapters/superpowers.md": "",
    "quality/superpowers.md": "",
}


def build_fusion_files(
    agent: str,
    *,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
) -> dict[str, str]:
    profile = get_agent_profile(agent)
    enabled_keys = [
        key
        for key, enabled in (
            ("openspec", include_openspec),
            ("speckit", include_speckit),
            ("superpowers", include_superpowers),
        )
        if enabled
    ]

    commands = build_upstream_init_commands(
        agent=agent,
        include_openspec=include_openspec,
        include_speckit=include_speckit,
        include_superpowers=include_superpowers,
    )
    command_lines = [
        f"  - {command.key}: \"{command.display() or command.description}\""
        for command in commands
    ]
    upstream_init_yaml = "\n".join(command_lines) if command_lines else "  []"

    files: dict[str, str] = {
        ".specspine/fusion.yaml": "\n".join(
            [
                "name: SpecSpine Fusion",
                "version: 0.1",
                "integration_mode: adapter",
                "vendored_upstream_code: false",
                "agent:",
                f"  key: {profile.key}",
                f"  openspec_tool: {profile.openspec_tool}",
                f"  speckit_integration: {profile.speckit_integration}",
                "upstreams:",
                "  openspec:",
                f"    enabled: {str(include_openspec).lower()}",
                f"    role: \"{ADAPTER_SPECS['openspec'].role}\"",
                f"    repo: \"{ADAPTER_SPECS['openspec'].upstream_url}\"",
                f"    license: \"{ADAPTER_SPECS['openspec'].license_name}\"",
                "    adapter: \".specspine/adapters/openspec.md\"",
                "  speckit:",
                f"    enabled: {str(include_speckit).lower()}",
                f"    role: \"{ADAPTER_SPECS['speckit'].role}\"",
                f"    repo: \"{ADAPTER_SPECS['speckit'].upstream_url}\"",
                f"    license: \"{ADAPTER_SPECS['speckit'].license_name}\"",
                "    adapter: \".specspine/adapters/speckit.md\"",
                "  superpowers:",
                f"    enabled: {str(include_superpowers).lower()}",
                f"    role: \"{ADAPTER_SPECS['superpowers'].role}\"",
                f"    repo: \"{ADAPTER_SPECS['superpowers'].upstream_url}\"",
                f"    license: \"{ADAPTER_SPECS['superpowers'].license_name}\"",
                "    adapter: \".specspine/adapters/superpowers.md\"",
                "workflow:",
                "  intent: [\"specs/intent.md\", \"openspec proposal\", \"speckit specify\"]",
                "  product_spec: [\"specs/product.md\", \"speckit specify\", \"openspec specs\"]",
                "  architecture: [\"specs/architecture.md\", \"openspec design\", \"speckit plan\"]",
                "  execution: [\"execution/plan.md\", \"execution/tasks.md\", \"speckit tasks\"]",
                "  quality: [\"quality/checklist.md\", \"quality/superpowers.md\", \"superpowers skills\"]",
                "upstream_init:",
                upstream_init_yaml,
                "",
            ]
        ),
        ".specspine/fusion-map.md": f"""
            # SpecSpine Fusion Map

            SpecSpine is the project-local backbone. It does not vendor OpenSpec, Spec Kit, or Superpowers code. It records how those tools are connected and invokes them through their public installation and command surfaces.

            ## Enabled Upstreams

            {", ".join(enabled_keys) if enabled_keys else "none"}

            ## Responsibility Split

            | Layer | SpecSpine Role | Upstream Role |
            | --- | --- | --- |
            | Why | Keep intent, users, constraints, and outcome signals in `specs/intent.md`. | Spec Kit's specify phase and OpenSpec proposals sharpen the "what" and "why". |
            | What | Keep product scope, non-goals, workflows, and acceptance criteria in `specs/product.md`. | Spec Kit specs and OpenSpec spec deltas provide detailed requirements artifacts. |
            | How | Keep architectural decisions and execution plans in `specs/architecture.md` and `execution/plan.md`. | Spec Kit plan/tasks and OpenSpec design/tasks drive implementation structure. |
            | Finish Well | Keep quality gates, review notes, and release readiness in `quality/`. | Superpowers provides brainstorming, writing-plans, TDD, subagent execution, code review, and verification discipline. |

            ## Agent Profile

            - Agent: `{profile.key}`
            - OpenSpec tool id: `{profile.openspec_tool}`
            - Spec Kit integration key: `{profile.speckit_integration}`
            - Superpowers: {profile.superpowers_hint}

            ## Operating Rule

            When upstream files and SpecSpine files disagree, treat it as spec drift. Resolve the discrepancy in the spec layer before implementation continues.
        """,
        ".specspine/adapters/openspec.md": f"""
            # OpenSpec Adapter

            Upstream: {ADAPTER_SPECS["openspec"].upstream_url}
            License: {ADAPTER_SPECS["openspec"].license_name}
            Integration mode: external CLI, no vendored source code.

            ## Role

            OpenSpec owns lightweight change proposals, spec deltas, design notes, task lists, validation, and archive flow.

            ## Install

            ```bash
            {ADAPTER_SPECS["openspec"].install_hint}
            ```

            ## Initialize Through SpecSpine

            ```bash
            specspine fuse . --agent {profile.key} --run-upstream
            ```

            Equivalent OpenSpec command:

            ```bash
            openspec init . --tools {profile.openspec_tool}
            ```

            ## Expected Artifacts

            - `openspec/specs/`
            - `openspec/changes/`
            - `openspec/config.yaml`

            SpecSpine references these artifacts but does not replace OpenSpec's own lifecycle.
        """,
        ".specspine/adapters/speckit.md": f"""
            # Spec Kit Adapter

            Upstream: {ADAPTER_SPECS["speckit"].upstream_url}
            License: {ADAPTER_SPECS["speckit"].license_name}
            Integration mode: external Specify CLI, no vendored source code.

            ## Role

            Spec Kit owns the structured specify, plan, tasks, and implement workflow for AI coding agents.

            ## Install

            ```bash
            {ADAPTER_SPECS["speckit"].install_hint}
            ```

            ## Initialize Through SpecSpine

            ```bash
            specspine fuse . --agent {profile.key} --run-upstream
            ```

            Equivalent Spec Kit command:

            ```bash
            specify init . --integration {profile.speckit_integration}
            ```

            ## Expected Artifacts

            - `.specify/`
            - `specs/`
            - agent-specific command or skill files

            SpecSpine keeps a higher-level backbone and lets Spec Kit manage its own generated agent integration files.
        """,
        ".specspine/adapters/superpowers.md": f"""
            # Superpowers Adapter

            Upstream: {ADAPTER_SPECS["superpowers"].upstream_url}
            License: {ADAPTER_SPECS["superpowers"].license_name}
            Integration mode: installed agent plugin/extension, no vendored source code.

            ## Role

            Superpowers is the quality discipline layer. SpecSpine expects the agent to use Superpowers skills for:

            - brainstorming
            - writing-plans
            - test-driven-development
            - subagent-driven-development or executing-plans
            - requesting-code-review
            - verification-before-completion
            - finishing-a-development-branch

            ## Install

            {profile.superpowers_hint}

            ## Contract

            SpecSpine does not copy skill files. It records that Superpowers should be installed in the active AI coding agent and uses `quality/superpowers.md` as the project-local policy bridge.
        """,
        "quality/superpowers.md": """
            # Superpowers Quality Policy

            Use Superpowers as the quality discipline layer for SpecSpine work.

            ## Before Implementation

            - Use brainstorming to refine unclear intent.
            - Use writing-plans to create task-level implementation plans.
            - Confirm acceptance criteria are present before writing code.

            ## During Implementation

            - Prefer test-driven-development for behavior changes.
            - Keep tasks traceable to the current spec and plan.
            - Use subagent-driven-development or executing-plans for multi-step work.

            ## Before Completion

            - Run verification-before-completion.
            - Request code review against the spec and implementation plan.
            - Record unresolved findings in `quality/review.md`.
        """,
    }

    return files


def build_fusion_spine_file(
    *,
    include_openspec: bool = True,
    include_speckit: bool = True,
    include_superpowers: bool = True,
) -> str:
    return "\n".join(
        [
            "name: SpecSpine Workspace",
            "version: 0.1",
            "backbone:",
            "  intent: specs/intent.md",
            "  product: specs/product.md",
            "  architecture: specs/architecture.md",
            "  execution_plan: execution/plan.md",
            "  task_board: execution/tasks.md",
            "  quality_checklist: quality/checklist.md",
            "  review_notes: quality/review.md",
            "fusion:",
            "  config: .specspine/fusion.yaml",
            "  map: .specspine/fusion-map.md",
            "adapters:",
            "  openspec:",
            f"    enabled: {str(include_openspec).lower()}",
            "    config: .specspine/adapters/openspec.md",
            "  speckit:",
            f"    enabled: {str(include_speckit).lower()}",
            "    config: .specspine/adapters/speckit.md",
            "  superpowers:",
            f"    enabled: {str(include_superpowers).lower()}",
            "    config: .specspine/adapters/superpowers.md",
            "",
        ]
    )


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
