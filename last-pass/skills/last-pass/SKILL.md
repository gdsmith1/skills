---
name: last-pass
description: Final review pass before committing or merging. Use when the user asks for a "last pass", final cleanup, or pre-merge review of uncommitted changes or an unmerged feature branch.
disable-model-invocation: true
argument-hint: "[scope, e.g. uncommitted | branch]"
---

# Last Pass

**Important**: if any fix begins to scope creep away from the current phase's task, escalate to the user immediately.

Run the phases in order.

## 1. Confirm scope

Confirm what changes the user wants a last pass on: uncommitted changes or an unmerged feature branch (diff against the default branch). Use `$ARGUMENTS` if given. Otherwise this should be obvious; if not, confirm with the user.

## 2. Change table

Write a simple table of all major changes to the repo within the scope from phase 1. A change may touch several files, and a file may hold several changes. Format and example: [reference/change-table.md](reference/change-table.md).

## 3. Reduce duplication

Reduce duplication wherever possible. For every new function, module, type, etc., search the repo for an existing equivalent: read documentation such as README.md or docs/ARCHITECTURE.md, and use semantic search for preexisting duplicates. Give each new component a verdict (Reused existing, Justified new, or Duplicate), then replace duplicates with the existing code. Format: [reference/duplication-report.md](reference/duplication-report.md).

## 4. Simplify

Simplify all code so it reads without comments. Strip comments unless they are necessary to understand the logic. Comments must not mention tickets, PRs, review discussions, or other commits; they must be relevant to the codebase and explain what the code cannot on its own.

## 5. Verify

Run all linting, building, and testing required to verify success (check the README, CI config, or package scripts for the commands). Fix issues as needed and re-run until clean.

## 6. Final report

Update the user on the actions taken in each phase with a brief summary (format and example: [reference/final-report.md](reference/final-report.md)). Include the change table and duplication verdicts, and any failures that remain.
