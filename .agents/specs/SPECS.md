# SPECS Registry — austinyuch/asynqmon

| Spec | Status | Depends On | Impacts | Open Change Requests |
|---|---|---|---|---|
| [001-ui-runtime-vuln-hardening](./001-ui-runtime-vuln-hardening/) | In Progress | —(基於 PR #1 security hardening baseline) | FORK.md divergence table | — |

## External Contract Notes

| Contract | Authority | Source of Truth | Pin/Version |
|---|---|---|---|
| npm security advisories | external(GitHub Advisory DB) | `ui/package.json` resolutions + `yarn.lock` | 見 SPEC-001 design |
| upstream hibiken/asynqmon | external(upstream repo) | `master` mirror branch + FORK.md | sync log 見 FORK.md |
| asynq fork dependency | external(austinyuch/asynq) | `go.mod` | v0.26.0-team.1 / x v0.1.0-team.1 |

## Planned(authoring 排程中)

- 002-ui-build-migration-cra-to-vite(EOL:react-scripts/CRA 已 sunset)
- 003-ui-mui4-to-mui5-migration(EOL:MUI v4)
- 004-ui-react16-to-react18-router6-migration(EOL:React 16 / react-router 5)
