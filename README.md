# SpecSpine

SpecSpine is a spec-driven AI development hub. It connects why to build, what to build, and how to finish with quality into one reliable engineering backbone.

中文定位：

> 规范驱动的 AI 开发中枢，把“为什么做、做什么、如何高质量完成”串成一条可靠主干。

## Why SpecSpine

AI-assisted development is strongest when the team can keep intent, scope, implementation, and quality in the same loop. SpecSpine is designed to make that loop explicit.

It borrows the strengths of spec-first tools and high-quality execution workflows:

- **Intent first**: clarify the problem, users, constraints, and success signals.
- **Spec as backbone**: turn intent into product scope, feature specs, and technical decisions.
- **Execution with discipline**: break specs into traceable plans, tasks, checks, and handoffs.
- **Quality by default**: keep acceptance criteria, tests, review notes, and release readiness visible.

## Current Status

This repository is an early project skeleton. It includes:

- A zero-dependency Python CLI.
- A workspace initializer: `specspine init`.
- Default spec templates for intent, product, architecture, features, quality, and execution.
- A lightweight test suite and GitHub Actions CI.

## Install Locally

```bash
python3 -m pip install -e .
```

Then run:

```bash
specspine --help
```

You can also run the CLI without installation:

```bash
python3 -m specspine --help
```

## Quick Start

Create a SpecSpine workspace in an existing product repository:

```bash
specspine init .
```

Or create one in a new directory:

```bash
specspine init ./my-product
```

The command creates:

```text
.specspine/
  spine.yaml
specs/
  intent.md
  product.md
  architecture.md
  features/
execution/
  plan.md
  tasks.md
quality/
  checklist.md
  review.md
```

## Core Workflow

1. **Intent**
   - Why are we doing this?
   - Who is it for?
   - What outcome proves it worked?

2. **Spec**
   - What exactly should be built?
   - What is out of scope?
   - What constraints shape the solution?

3. **Plan**
   - How will the work be decomposed?
   - What decisions need to be made?
   - What risks need active handling?

4. **Execute**
   - What tasks are being worked?
   - What artifacts prove progress?
   - What changed from the original plan?

5. **Quality**
   - What tests and reviews are required?
   - What acceptance criteria must pass?
   - What is needed before release?

## CLI

```bash
specspine init [path]
```

Initializes the SpecSpine workspace structure.

```bash
specspine doctor [path]
```

Checks whether a directory contains the expected SpecSpine files.

## Design Principles

- **Specs are living artifacts**, not one-time documents.
- **AI agents need context boundaries**, not just prompts.
- **Execution should be traceable back to intent**.
- **Quality should be represented before implementation starts**.
- **The tool should fit existing repos**, not force a monorepo or platform migration.

## Roadmap

- Feature spec lifecycle commands.
- Task decomposition from specs.
- Quality gate definitions.
- Agent handoff packets.
- Adapter layer for OpenSpec, Spec Kit, Superpower, and other workflow engines.
- GitHub issue and pull request synchronization.

## Development

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Run the CLI from source:

```bash
PYTHONPATH=src python3 -m specspine doctor .
```

## License

License is TBD.
