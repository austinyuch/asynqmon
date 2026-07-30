# ui/ — Test Decision Table

| Test ID | What | Canonical Command | Owner | Evidence Ref | Task / Spec Trace | Requirement / AC Trace |
|---|---|---|---|---|---|---|
| UI-BUILD-001 | Production bundle build(CRA/webpack4) | `cd ui && yarn build`(tsc --noEmit + vite build + go-template token gate) | team | SPEC-001 `reports/`(build log in PR)| SPEC-001 T-3 / SPEC-002 T-4 | REQ-UIVULN-002 AC1 |
| UI-AUDIT-001 | Runtime dep advisory regression(5 target packages) | `cd ui && yarn audit`(target filter 見 SPEC-001 reports 腳本) | team | `.agents/specs/001-ui-runtime-vuln-hardening/reports/audit-after.txt` | SPEC-001 T-1/T-4 | REQ-UIVULN-001 AC1-3 |
| UI-EMBED-001 | Go embed of rebuilt bundle | `go build ./... && go test -race -count=1 ./...` | team | CI build.yml run on SPEC-001 PR | SPEC-001 T-4 | REQ-UIVULN-002 AC2 |

| UI-UNIT-001 | Vitest unit(parseFlags fallback + react-window v2 GroupSelect sizing/row behavior) | `cd ui && yarn test` | team | SPEC-002 PR CI log;CR-2026-07-30-005 local/hosted CI(6/6) | SPEC-002 T-6;CR-2026-07-30-005 UIMOD-T2/T5 | REQ-VITE-002 AC1;REQ-UIMOD-001 |
| UI-BUNDLE-001 | Route-level lazy chunks, entry-size budget, committed embed assets | `cd ui && yarn build` | team | CR-2026-07-30-005 review report(entry 1,244,238→415,980 bytes;aggregate 1,260,924 bytes) | CR-2026-07-30-005 UIMOD-T4/T5 | REQ-UIMOD-004 |
| UI-E2E-001 | 功能性 browser smoke(7 案例,CI gate) | `cd ui && npx playwright test e2e/smoke.spec.ts`(需 demo env,CI 自帶) | team | PR #24/#25 build.yml e2e 7/7;retry-state bounded auto-wait `3c0d1ef`;CR-2026-07-30-005 run 30544864270 7/7 | SPEC-005 Q-T1;CR-2026-07-30-002/005 | REQ-QG-001;REQ-UIMOD-001/004 |
| UI-LINT-001 | eslint flat config(0 errors / 0 warnings) | `cd ui && yarn lint` | team | CR-2026-07-30-003 local + hosted build lint | SPEC-005 Q-T2;CR-2026-07-30-003 | REQ-QG-002 |
| UI-TOKEN-001 | Go template token gate(post-build) | `cd ui && node scripts/verify-go-template-tokens.mjs` | team | build script 內建,SPEC-002 PR | SPEC-002 T-2/T-4 | REQ-VITE-001 AC2/3 |

注:CRA boilerplate `App.test.tsx`(「learn react link」)已汰除——其斷言與實際 App 不符,現狀即失敗且從未在 CI 執行;E2E 使用 real backend 與非同步 worker 狀態,斷言採 bounded Playwright auto-wait。
