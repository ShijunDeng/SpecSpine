from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "AgentProfile",
    "AGENT_PROFILES",
]


@dataclass(frozen=True)
class AgentProfile:
    key: str
    openspec_tool: str
    speckit_integration: str
    superpowers_hint: str


AGENT_PROFILES: dict[str, AgentProfile] = {
    "codex": AgentProfile(
        key="codex",
        openspec_tool="codex",
        speckit_integration="codex",
        superpowers_hint="Install the Superpowers plugin from the Codex plugin marketplace.",
    ),
    "claude": AgentProfile(
        key="claude",
        openspec_tool="claude",
        speckit_integration="claude",
        superpowers_hint="Install Superpowers with /plugin install superpowers@claude-plugins-official.",
    ),
    "copilot": AgentProfile(
        key="copilot",
        openspec_tool="github-copilot",
        speckit_integration="copilot",
        superpowers_hint="Install Superpowers from the GitHub Copilot CLI plugin marketplace.",
    ),
    "cursor": AgentProfile(
        key="cursor",
        openspec_tool="cursor",
        speckit_integration="cursor-agent",
        superpowers_hint="Install Superpowers from the Cursor plugin marketplace.",
    ),
    "gemini": AgentProfile(
        key="gemini",
        openspec_tool="gemini",
        speckit_integration="gemini",
        superpowers_hint="Install Superpowers with gemini extensions install https://github.com/obra/superpowers.",
    ),
    "opencode": AgentProfile(
        key="opencode",
        openspec_tool="opencode",
        speckit_integration="opencode",
        superpowers_hint="Follow the OpenCode install instructions from the Superpowers repository.",
    ),
    "windsurf": AgentProfile(
        key="windsurf",
        openspec_tool="windsurf",
        speckit_integration="windsurf",
        superpowers_hint="Install Superpowers through Windsurf-compatible agent plugin support.",
    ),
}
