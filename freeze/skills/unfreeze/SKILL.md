---
name: unfreeze
description: Resume work paused by /freeze. Use when the user runs unfreeze with an @ reference to a freeze report.
disable-model-invocation: true
argument-hint: "@<freeze report path>"
---

# Unfreeze

You are an orchestrator. Your job is to resume the parallel workstreams recorded in a freeze report, each with a fresh subagent.

## The report

`$ARGUMENTS` is a freeze report. It contains, in order:

- **Goal:** the overall objective.
- **Spec/plan:** the file the previous orchestrator worked from, if any. Read it.
- **Subagents table:** one row per workstream, with its worktree, status, and a self-contained resume prompt.
- **Detail sections:** per subagent, the worktree, what is done and remaining, the command that was running when it stopped, and its agent config (type, model, effort).

Everything in the report was verified when written. Anything absent was deliberately left out as unclear: do not assume it, and let the subagents rediscover it.

Run the phases in order.

## 1. Read

Read the report and the spec or plan it names. If no report was given, ask the user for the path.

## 2. Verify

For each subagent, check that the worktree exists and its branch and commits match the report. Report mismatches to the user and wait for direction on those workstreams; do not guess.

## 3. Resume

Spawn one fresh subagent per row, in parallel, in the recorded worktree. Use the row's resume prompt, and the agent type, model, and effort from its detail section. If a custom definition file is missing, tell the user and use the closest built-in type. Do not re-run an interrupted command blindly: tell the subagent what it was and have it confirm re-running is safe.

## 4. Monitor

Run as you did before the freeze: track each subagent to completion, check results against the goal, and report to the user when all workstreams finish or any is blocked.
