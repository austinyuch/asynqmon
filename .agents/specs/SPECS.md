# SPECS Registry — austinyuch/asynqmon

| Spec | Status | Depends On | Impacts | Open Change Requests |
|---|---|---|---|---|
| [001-ui-runtime-vuln-hardening](./001-ui-runtime-vuln-hardening/) | Completed(PR #2,merged 2026-06-07) | PR #1 security hardening baseline | FORK.md divergence table | — |
| [002-ui-build-migration-cra-to-vite](./002-ui-build-migration-cra-to-vite/) | Pending Implementation | — | Dockerfile、release.yml、FORK.md、ui/TESTS.md | — |
| [003-ui-mui4-to-mui5-migration](./003-ui-mui4-to-mui5-migration/) | Pending Implementation | SPEC-002、SPEC-004 Phase A(React ≥17) | ui/TESTS.md | — |
| [004-ui-react16-to-react18-router6-migration](./004-ui-react16-to-react18-router6-migration/) | Pending Implementation | Phase A:SPEC-002;Phase B:SPEC-003 | SPEC-001 resolutions(path-to-regexp 移除)、ui/TESTS.md | — |

建議執行順序:**002 → 004 Phase A → 003 → 004 Phase B**(peer-dependency 約束,詳各 spec Impacts)。

## External Contract Notes

| Contract | Authority | Source of Truth | Pin/Version |
|---|---|---|---|
| npm security advisories | external(GitHub Advisory DB) | `ui/package.json` resolutions + `yarn.lock` | 見 SPEC-001 design |
| upstream hibiken/asynqmon | external(upstream repo) | `master` mirror branch + FORK.md | sync log 見 FORK.md |
| asynq fork dependency | external(austinyuch/asynq) | `go.mod` | v0.26.0-team.1 / x v0.1.0-team.1 |
