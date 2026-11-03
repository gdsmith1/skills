# Duplication report

One row per new function, module, type, etc.

| Component | Verdict | Evidence |
|-----------|---------|----------|

Verdicts:
- **Reused existing**: the branch correctly calls what was already there.
- **Justified new**: name the concrete use case existing code could not serve.
- **Duplicate**: point to the existing function or file that should be used instead.

## Example

| Component | Verdict | Evidence |
|-----------|---------|----------|
| `backoff()` | Justified new | No existing retry helper; searched `src/` and `docs/ARCHITECTURE.md` |
| `formatDate()` | Duplicate | Use `utils/date.ts:formatISO` |
| `UserRecord` | Reused existing | Extends `BaseRecord` in `models/base.ts` |
