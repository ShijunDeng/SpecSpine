from __future__ import annotations


def _github_label_args(labels: tuple[str, ...]) -> tuple[str, ...]:
    args: list[str] = []
    for label in labels:
        args.extend(("--label", label))
    return tuple(args)


def _feature_issue_labels(slug: str, status: str, priority: str) -> tuple[str, ...]:
    return (
        "specspine",
        f"feature:{slug}",
        f"status:{status}",
        f"priority:{priority}",
    )


def _task_issue_labels(slug: str, status: str) -> tuple[str, ...]:
    return (
        "specspine",
        f"feature:{slug}",
        "task",
        f"status:{status}",
    )


def _pull_request_labels(slug: str, status: str) -> tuple[str, ...]:
    return (
        "specspine",
        f"feature:{slug}",
        f"status:{status}",
    )


__all__ = [
    "_feature_issue_labels",
    "_github_label_args",
    "_pull_request_labels",
    "_task_issue_labels",
]
