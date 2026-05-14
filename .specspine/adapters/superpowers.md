# Superpowers Adapter

Upstream: https://github.com/obra/superpowers
License: MIT
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

Install the Superpowers plugin from the Codex plugin marketplace.

## Contract

SpecSpine does not copy skill files. It records that Superpowers should be installed in the active AI coding agent and uses `quality/superpowers.md` as the project-local policy bridge.
