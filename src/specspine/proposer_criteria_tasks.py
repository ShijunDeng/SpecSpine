from __future__ import annotations

__all__ = [
    "generate_tasks",
    "generate_quality_checks",
]


def generate_tasks(parsed_intent: dict, criteria: list[dict]) -> list[dict]:
    action = parsed_intent["action"]
    target = parsed_intent["target"]
    tasks: list[dict] = []

    tasks.append(
        {
            "id": "T001",
            "text": f"Set up file structure and module scaffolding for {action} {target}",
            "boundary": f"Project structure and module creation for {target}",
            "depends": "none",
        }
    )

    for criterion in criteria[:3]:
        criterion_text = criterion["text"].replace("The system SHALL ", "")
        tasks.append(
            {
                "id": f"T{len(tasks) + 1:03d}",
                "text": f"Implement core logic: {criterion_text}",
                "boundary": f"Core behavior for {criterion['pattern']} criterion {criterion['id']}",
                "depends": "T001",
            }
        )

    tasks.append(
        {
            "id": f"T{len(tasks) + 1:03d}",
            "text": f"Wire CLI interface and validate {action} {target} integration",
            "boundary": f"CLI integration and validation for {target}",
            "depends": ", ".join(t["id"] for t in tasks[1:]),
        }
    )

    tasks.append(
        {
            "id": f"T{len(tasks) + 1:03d}",
            "text": f"Add unit tests, integration tests, and documentation for {action} {target}",
            "boundary": f"Test suite and documentation for {target}",
            "depends": tasks[-1]["id"],
        }
    )

    return tasks


def generate_quality_checks(criteria: list[dict]) -> list[str]:
    checks: list[str] = []
    for criterion in criteria:
        checks.append(
            f"Verify {criterion['id']}: {criterion['text']}"
        )
    return checks
