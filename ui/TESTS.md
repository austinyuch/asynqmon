# ui/ — Test Decision Table

| Test ID | What | Canonical Command | Owner | Evidence Ref | Task / Spec Trace | Requirement / AC Trace |
|---|---|---|---|---|---|---|
| UI-BUILD-001 | Production bundle build(CRA/webpack4) | `cd ui && NODE_OPTIONS=--openssl-legacy-provider yarn build` | team | SPEC-001 `reports/`(build log in PR)| SPEC-001 T-3 | REQ-UIVULN-002 AC1 |
| UI-AUDIT-001 | Runtime dep advisory regression(5 target packages) | `cd ui && yarn audit`(target filter 見 SPEC-001 reports 腳本) | team | `.agents/specs/001-ui-runtime-vuln-hardening/reports/audit-after.txt` | SPEC-001 T-1/T-4 | REQ-UIVULN-001 AC1-3 |
| UI-EMBED-001 | Go embed of rebuilt bundle | `go build ./... && go test -race -count=1 ./...` | team | CI build.yml run on SPEC-001 PR | SPEC-001 T-4 | REQ-UIVULN-002 AC2 |

注:CRA test runner(`yarn test`)目前無自動化案例納入治理;UI 行為驗證依賴 build + 人工 smoke,遷移後(SPEC-002)再建 E2E。
