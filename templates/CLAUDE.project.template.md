# Project CLAUDE

## Project Description

- what this project does:
- primary users:
- critical services/dependencies:
- how it normally runs:

## Hard Rules

- keep changes surgical; mention unrelated issues instead of fixing them
- prefer the simplest implementation that satisfies the verified goal
- ask before destructive Git, filesystem, deployment, or data operations
- verify functionality before reporting completion

## Scope

- product goal:
- current phase:
- non-goals:
- risk-sensitive areas:

## Commands

Only list commands that differ from common defaults.

- install:
- dev:
- test:
- lint:
- typecheck:
- build:

## Rules

Path-scoped rules live in `.helix/rules/`. Each rule file starts with:

`scope: path/or/glob`

Load only matching rules for the files being touched.

## Learnings

- durable corrections go in `.helix/state/LEARNINGS.md`
- progress state goes in `.helix/state/PROGRESS.md`
- do not repeat fixed mistakes; update learnings after user correction

## Knowledge

- graph report: `.helix/kb/graphify-out/GRAPH_REPORT.md`
- overview index: `.helix/overview/INDEX.md`
- wiki index: `.helix/kb/wiki/_index.md`
