# Agent Loop Packet Quality

Feature ID: agent-loop-packet
Status: validated
Why: A loop packet is useful only if it is deterministic, local, token-free, adapter-probe-free, and precise about command execution boundaries.

## Required Checks

- [x] Unit tests cover stable builder output and required packet keys.
- [x] Unit tests cover status builder reuse with adapter probing disabled.
- [x] Unit tests cover `--json --output` writing text while stdout remains parseable JSON.
- [x] Unit tests cover output overwrite refusal and `--force`.
- [x] Unit tests cover token-free output and subprocess-free CLI behavior.
- [x] Documentation lists the command and local safety contract.
- [x] The dogfood bundle is validated across spec, execution, and quality peer files.

## Test Coverage

- [x] AC001 -> tests/test_loop.py::LoopPacketTests::test_builder_emits_local_deterministic_packet
- [x] AC002 -> tests/test_loop.py::LoopPacketTests::test_builder_emits_local_deterministic_packet
- [x] AC003 -> tests/test_loop.py::LoopPacketTests::test_builder_emits_local_deterministic_packet
- [x] AC004 -> tests/test_loop.py::LoopPacketTests::test_builder_emits_local_deterministic_packet
- [x] AC005 -> tests/test_loop.py::LoopPacketTests::test_cli_json_output_writes_text_packet
- [x] AC005 -> tests/test_loop.py::LoopPacketTests::test_cli_output_refuses_existing_file_without_force
- [x] AC005 -> tests/test_loop.py::LoopPacketTests::test_cli_output_confirmation_without_json_and_force
- [x] AC006 -> tests/test_loop.py::LoopPacketTests::test_builder_does_not_probe_adapters
- [x] AC007 -> tests/test_loop.py::LoopPacketTests::test_cli_packet_is_token_free_and_does_not_invoke_subprocesses
- [x] AC008 -> tests/test_dogfood_artifacts.py::DogfoodArtifactsTests::test_agent_loop_packet_documentation_and_dogfood_describe_workflow

## Test Plan

- Run `PYTHONPATH=src python3 -m unittest tests.test_loop`.
- Run `PYTHONPATH=src python3 -m unittest tests.test_dogfood_artifacts`.
- Run `PYTHONPATH=src python3 -m specspine validate . --fusion --features`.
- Run `PYTHONPATH=src python3 -m specspine loop packet . --json`.
- Run `PYTHONPATH=src python3 -m specspine feature ready agent-loop-packet . --json`.

## Review Notes

- The loop packet composes existing local status and readiness evidence instead of probing external adapters.
- Recommended commands are records for humans or agents to inspect later; none are executed by the exporter.
- The CLI writes only the explicit text output file requested with `--output`.

## Release Readiness

- [x] `agent-loop-packet` has complete spec, execution, and quality peer files.
- [x] Lifecycle status is `validated` across all peer files.
- [x] Acceptance criteria, implementation tasks, required checks, test coverage links, and release readiness evidence are complete.
- [x] Focused verification for this round passes.
