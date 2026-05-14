# Feature Summary Metadata

Feature ID: feature-summary-metadata
Status: validated
Priority: high
Owner: SpecSpine maintainers

## Why

Multi-feature workspaces need local triage data that survives before remote GitHub issue, Pull Request, or project sync exists. Priority and owner metadata let agents choose important work and route responsibility without reading tokens, calling GitHub, or inferring intent from prose.

## Users

- Maintainers comparing several native feature bundles.
- Implementation agents selecting the next high-impact local requirement.
- Review and release agents preparing later GitHub issue or Pull Request synchronization.

## Scope

- Treat `Priority:` and `Owner:` in `specs/features/<slug>.md` as the native source of truth.
- Generate new feature specs with `Priority: medium` and `Owner: unassigned`.
- Add `priority` and `owner` to opt-in JSON feature summaries.
- Show priority and owner in text feature summaries.
- Filter summaries with repeated `--feature-priority` and `--feature-owner` options.
- Sort summaries by priority in `high`, `medium`, `low`, then `unknown` order.
- Keep missing or unsupported priorities as `unknown` and missing or blank owners as `unassigned`.

## Non-Goals

- Calling GitHub APIs, using `gh`, reading tokens, or creating remote project fields.
- Adding dependencies or upstream source code.
- Requiring priority or owner metadata for feature validation.
- Duplicating priority and owner in execution or quality peer files.

## Acceptance Criteria

- [x] `feature new` writes `Priority: medium` and `Owner: unassigned` in the generated spec file.
- [x] `status --json --feature-summaries` includes `priority` and `owner` for every summary while default status JSON remains compact.
- [x] Missing or unsupported priority values display as `unknown`.
- [x] Missing or blank owner values display as `unassigned`.
- [x] `status --feature-summaries` text output shows priority and owner on each summary row.
- [x] `--feature-priority` filters by `high`, `medium`, `low`, and `unknown`, is repeatable, and requires `--feature-summaries`.
- [x] Invalid priority filters return code `2` with a clear error.
- [x] `--feature-owner` filters by case-insensitive exact owner matches, is repeatable, and treats `unassigned` as missing owner.
- [x] `--feature-sort priority` orders `high`, `medium`, `low`, and `unknown`, with `--feature-sort-desc` reversing that order.
- [x] The implementation is local, zero-dependency, token-free, and network-free.
