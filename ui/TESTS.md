# ui/ — Test Decision Table

| Test ID | What | Canonical Command | Owner | Evidence Ref | Task / Spec Trace | Requirement / AC Trace |
|---|---|---|---|---|---|---|
| UI-BUILD-001 | Production bundle build(CRA/webpack4) | `cd ui && yarn build`(tsc --noEmit + vite build + go-template token gate) | team | SPEC-001 `reports/`(build log in PR)| SPEC-001 T-3 / SPEC-002 T-4 | REQ-UIVULN-002 AC1 |
| UI-AUDIT-001 | Runtime dep advisory regression(5 target packages) | `cd ui && yarn audit`(target filter 見 SPEC-001 reports 腳本) | team | `.agents/specs/001-ui-runtime-vuln-hardening/reports/audit-after.txt` | SPEC-001 T-1/T-4 | REQ-UIVULN-001 AC1-3 |
| UI-EMBED-001 | Go embed of rebuilt bundle | `go build ./... && go test -race -count=1 ./...` | team | CI build.yml run on SPEC-001 PR | SPEC-001 T-4 | REQ-UIVULN-002 AC2 |

| UI-UNIT-001 | Vitest unit(parseFlags fallback 行為) | `cd ui && yarn test` | team | SPEC-002 PR CI log | SPEC-002 T-6 | REQ-VITE-002 AC1 |
| UI-TOKEN-001 | Go template token gate(post-build) | `cd ui && node scripts/verify-go-template-tokens.mjs` | team | build script 內建,SPEC-002 PR | SPEC-002 T-2/T-4 | REQ-VITE-001 AC2/3 |

注:CRA boilerplate `App.test.tsx`(「learn react link」)已汰除——其斷言與實際 App 不符,現狀即失敗且從未在 CI 執行;E2E(real backend)仍為 SPEC-003/004 前置 stretch goal。
