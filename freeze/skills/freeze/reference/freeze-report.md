# Freeze report

One file per freeze, at `.claude/freeze/FREEZE-REPORT-<YYYYMMDD-HHMMSS>.md`. Sections in this order: Goal, Spec/plan, Subagents table, one detail section per subagent.

Omit anything unverified. Write "none" for an empty field, never a guess. Resume prompts must stand alone: a fresh subagent has no other context.

## Example

```markdown
# Freeze report: 2026-10-28 14:32

## Goal
Add retry with backoff to the HTTP client and migrate callers to the new `UserRecord` type.

## Spec/plan
`docs/specs/retry-http.md`

## Subagents

| # | Name | Worktree | Status | Resume prompt |
|---|------|----------|--------|---------------|
| 1 | retry-impl | `/Users/me/repo-wt/retry` | Backoff written, tests not run | Work in `/Users/me/repo-wt/retry` on branch `feature/retry`. `src/http/backoff.ts` exists and is committed. Add retries to `src/http/client.ts`, then run `npm test` and fix failures. |
| 2 | user-rename | `/Users/me/repo-wt/rename` | Model and API done, auth not started | Work in `/Users/me/repo-wt/rename` on branch `feature/rename`. Rename `UserDTO` to `UserRecord` in `src/api/auth.ts` and any remaining usages (search to find them), then run `npm run build`. |

## 1. retry-impl
- **Worktree:** `/Users/me/repo-wt/retry`, branch `feature/retry`, uncommitted changes in `src/http/client.ts`
- **Done:** `src/http/backoff.ts` (commit `a1b2c3d`)
- **Remaining:** wire backoff into `client.ts`; run tests
- **In-flight command:** `npm test`, killed at freeze
- **Agent config:** `general-purpose`, model `claude-sonnet-5-5`, effort medium

## 2. user-rename
- **Worktree:** `/Users/me/repo-wt/rename`, branch `feature/rename`, clean
- **Done:** `src/models/user.ts`, `src/api/users.ts` (commit `d4e5f6a`)
- **Remaining:** `src/api/auth.ts`; build
- **In-flight command:** none
- **Agent config:** custom `.claude/agents/refactorer.md`, model `claude-opus-5-5`, effort high
```
