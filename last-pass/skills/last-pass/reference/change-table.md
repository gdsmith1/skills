# Change table

| # | Change | Files |
|---|--------|-------|

One row per logical change, not per file.

## Example

| # | Change | Files |
|---|--------|-------|
| 1 | Add retry with backoff to HTTP client | `src/http/client.ts`, `src/http/backoff.ts` |
| 2 | Rename `UserDTO` to `UserRecord` | `src/models/user.ts`, `src/api/users.ts`, `src/api/auth.ts` |
| 3 | Fix off-by-one in pagination | `src/api/users.ts` |
