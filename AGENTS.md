# AGENTS.md

SpecSpine is a zero-dependency Python CLI for spec-driven AI development. Treat `specs/`, `execution/`, `quality/`, and `.specspine/` as the local project context before changing code.

## Commands

```bash
PYTHONPATH=src python3 -m specspine status . --json --validate
PYTHONPATH=src python3 -m specspine status . --json --validate --feature-summaries
PYTHONPATH=src python3 -m specspine validate . --fusion --features
PYTHONPATH=src python3 -m unittest discover -s tests
```

For new user-facing requirements, create a native bundle first:

```bash
PYTHONPATH=src python3 -m specspine feature new <slug> . --title "..." --why "..."
PYTHONPATH=src python3 -m specspine feature status <slug> . --json
PYTHONPATH=src python3 -m specspine feature handoff <slug> . --json
PYTHONPATH=src python3 -m specspine feature tasks <slug> . --json
PYTHONPATH=src python3 -m specspine feature trace <slug> . --json
PYTHONPATH=src python3 -m specspine feature ready <slug> . --json
```

## Rules

- Start by reading `specspine status . --json --validate`; use `specspine status . --json --validate --feature-summaries` when choosing or comparing multiple native features; finish with `specspine validate . --fusion --features` and the unit test command above.
- Keep feature specs, implementation tasks, and quality checks traceable by `Feature ID`.
- Keep native feature peer files on a consistent lifecycle status with `specspine feature status`.
- Start implementation, acceptance, and review handoffs with `specspine feature handoff <slug> . --json`; use `feature tasks`, `feature trace`, and `feature ready` for focused follow-up views.
- OpenSpec, Spec Kit, and Superpowers are external adapters only. Do not vendor upstream source code.
- Do not read or write GitHub tokens, and do not call GitHub APIs by default.
- Use `--run-upstream` only when the user explicitly asks to invoke upstream tools.
