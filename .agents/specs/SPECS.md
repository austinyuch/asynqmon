# SPECS Registry — austinyuch/asynqmon

| Spec | Status | Depends On | Impacts | Open Change Requests |
|---|---|---|---|---|
| [001-ui-runtime-vuln-hardening](./001-ui-runtime-vuln-hardening/) | Completed(PR #2,merged 2026-06-07) | PR #1 security hardening baseline | FORK.md divergence table | — |
| [002-ui-build-migration-cra-to-vite](./002-ui-build-migration-cra-to-vite/) | Completed(PR #4)| — | Dockerfile、release.yml、FORK.md、ui/TESTS.md | — |
| [003-ui-mui4-to-mui5-migration](./003-ui-mui4-to-mui5-migration/) | Completed(PR #7;smoke 12/12)| SPEC-002、SPEC-004A | ui/TESTS.md | — |
| [004-ui-react16-to-react18-router6-migration](./004-ui-react16-to-react18-router6-migration/) | Completed(A:PR #6;B:PR #8;smoke 12/12)| A:SPEC-002;B:SPEC-003 | SPEC-001 resolutions(path-to-regexp 已移除)、ui/TESTS.md | — |

| [005-quality-gaps](./005-quality-gaps/) | Completed(PR #18;E2E CI gate + eslint + Metrics 驗證)| SPEC-002~004 | build.yml、docs/manual+review、ISSUE_LOG | — |

建議執行順序:**002 → 004 Phase A → 003 → 004 Phase B**(peer-dependency 約束,詳各 spec Impacts)。

## External Contract Notes

| Contract | Authority | Source of Truth | Pin/Version |
|---|---|---|---|
| npm security advisories | external(GitHub Advisory DB) | `ui/package.json` resolutions + `yarn.lock` | 見 SPEC-001 design |
| upstream hibiken/asynqmon | external(upstream repo) | `master` mirror branch + FORK.md | sync log 見 FORK.md |
| asynq fork dependency | external(austinyuch/asynq) | `go.mod` | v0.26.0-team.1 / x v0.1.0-team.1 |
