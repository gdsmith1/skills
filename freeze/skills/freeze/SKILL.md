---
name: freeze
description: Pause all running subagents and record where each left off in a single report. Use when the user asks to "freeze" an orchestrated, multi-subagent run so it can be resumed later from a fresh context.
disable-model-invocation: true
---

# Freeze

**Important**: record only what you have verified. If a fact is unclear, leave it out of the report; a fresh agent will rediscover it, and a wrong fact taints its context.

You are the orchestrator. Run the phases in order. No user approval is needed to proceed.

## 1. List subagents

List every running subagent you are managing (use ListAgents and your own records). Show the user the list (name, worktree, task) before doing anything else, then continue.

## 2. Pause

Stop each subagent cleanly. Let it finish its current atomic step (a file write, a commit) where it can, then stop it (SendMessage to ask it to halt, TaskStop if it does not). Confirm no processes it started are still running, and end any that are. Do not commit, stash, or discard its work.

## 3. Collect facts

For each subagent, gather from the worktree and its transcript:

- **Worktree:** absolute path, branch, and whether there are uncommitted changes (`git status`, `git log`).
- **Done:** completed work, each item backed by evidence (a commit, a file, a passing command).
- **Remaining:** work still to do, taken from its original assignment, not guessed.
- **In-flight command:** the command running at interruption, and whether it finished, was killed, or is unknown.
- **Agent config:** model, effort level, and agent type: a custom definition (give the file path) or a built-in one (`general-purpose`, `Explore`, etc.).

Also find the spec or plan file you were orchestrating from, if there is one.

## 4. Write the report

Write one file, `.claude/freeze/FREEZE-REPORT-<YYYYMMDD-HHMMSS>.md`, with the overall goal, the spec or plan path (if any), a table of subagents with a self-contained resume prompt for each, and a detail section per subagent. Write each resume prompt from verified facts only. Format and example: [reference/freeze-report.md](reference/freeze-report.md).

## 5. Hand off

Tell the user the report path and ask them to run `/clear`, then `/unfreeze @<report path>`.
