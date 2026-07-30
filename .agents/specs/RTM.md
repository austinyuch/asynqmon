# RTM — workspace traceability rollup(derived;truth 在各 spec 文件)

| Requirement | Spec / Phase | Design / Tasks | Verdict(review.md) | Evidence |
|---|---|---|---|---|
| REQ-UIVULN-001 runtime 依賴漏洞收斂 | SPEC-001 | 001/design.md(FMEA R1-R5)、tasks T1-T6 | PASS | `001/reports/audit-before\|after.txt`;PR #2 CI |
| REQ-UIVULN-002 bundle 重建與內嵌驗證 | SPEC-001 | 同上 | PASS | bundle 指紋;go test(PR #2 CI) |
| REQ-UIVULN-003 govulncheck pre-push hook | SPEC-001 | tasks T-5 | PASS | `githooks/pre-push`;每次 push 實跑 |
| REQ-VITE-001 build 工具鏈遷移 | SPEC-002 | 002/design.md(token-gate FMEA)、tasks T1-T7 | PASS | audit 376→0;`002/reports/audit-after-vite.txt`;token gate 常駐 build script |
| REQ-VITE-002 test runner 遷移 | SPEC-002 | 同上 | PASS | Vitest 3/3(PR #4 CI) |
| REQ-VITE-003 TS/lint 鏈 | SPEC-002 | 同上 | PASS(eslint 留 IL-002) | tsc in build script |
| REQ-R18-001 React 17 過渡(Phase A) | SPEC-004A | 004/design.md Phase A、A-T1~T3 | PASS | PR #6 CI;peer 衝突清零 |
| REQ-MUI-001 套件遷移 | SPEC-003 | 003/design.md(M-R1~R4)、M-T1~T4 | PASS | tsc 66→0;PR #7 CI |
| REQ-MUI-002 視覺與行為回歸 | SPEC-003 | 同上 | PASS | **smoke 12/12**:`003/reports/smoke/`(12 截圖 + SMOKE_REPORT.md) |
| REQ-R18-002 React 18 | SPEC-004B | 004/design.md Phase B、B-T1~T4 | PASS | PR #8 CI;smoke 0 console errors |
| REQ-R18-003 react-router 6 | SPEC-004B | 同上 | PASS | smoke deep-link/client-nav;path-to-regexp pin 退役 |
| REQ-R18-004 TypeScript 5 | SPEC-004B | 同上 | PASS | tsc 139→0;vitest types 原生解析 |

| REQ-QG-001 UI E2E 正式基線 | SPEC-005 | 005/design.md(Q-R1/Q-R4)、Q-T1/T4 | PASS | `ui/e2e/smoke.spec.ts` 7/7;PR #24/#25 hosted E2E;retry-state bounded auto-wait `3c0d1ef` |
| REQ-QG-002 eslint 鏈 | SPEC-005 | 005/design.md、Q-T2;CR-2026-07-30-003 | PASS | `yarn lint` 0 errors / 0 warnings;CI lint step;`SplitButton` lazy Popper anchor |
| REQ-QG-003 Metrics 真實驗證 | SPEC-005 | 005/design.md(Q-R2)、Q-T3 | PASS | `docs/manual/assets/metrics-live-01/02.png`(61 svg data paths);IL-R09 |
| REQ-LSS-001 local SBOM/CVE | SPEC-006 | 006/design.md、LSS-T1/T2/T5 | PASS | CycloneDX 501 components after asynq team.2 re-pin;Trivy 1 disclosed/0 blocking;Semgrep 0;govulncheck 0 |
| REQ-LSS-002 pinned CISA KEV | SPEC-006 | 006/design.md、LSS-T1/T2 | PASS | 8 security correlation/unit tests;catalog receipt SHA-256+freshness;KEV exact matches 0 |
| REQ-LSS-003 shift-left activation | SPEC-006 | 006/design.md、LSS-T3/T5;CR-2026-07-30-004 | PASS | `scripts/local-ci.sh --full`;owned Go package scope excludes `node_modules`;`githooks/pre-push`;hosted build/E2E/CodeQL |
| REQ-LSS-004 applicable upgrades | SPEC-006 | 006/design.md、LSS-T4/T5 | PASS with bounded VEX | Go/UI lockfiles upgraded;embedded bundle rebuilt;RSC-only GHSA disposition tracked;PR #24/#25 |
| REQ-UIMOD-001 React 18-compatible virtualization | SPEC-004 CR-2026-07-30-005 | UIMOD-T2/T5 | PASS | react-window 2.3.0;focused Vitest 3/3;UI suite 6/6;hosted E2E 7/7 |
| REQ-UIMOD-002 maintained package-manager path | SPEC-004 CR-2026-07-30-005 | UIMOD-T1/T5 | PASS | Yarn 4.18.0 immutable install;DEP0169 absent;all install surfaces and Actions v6 aligned |
| REQ-UIMOD-003 warning-free Prism resolution | SPEC-004 CR-2026-07-30-005 | UIMOD-T3/T5 | PASS | react-syntax-highlighter 16.1.1;Prism resolution warning absent;security 0 blocking |
| REQ-UIMOD-004 route-level code splitting | SPEC-004 CR-2026-07-30-005 | UIMOD-T4/T5 | PASS | entry 1,244,238→415,980 bytes;aggregate 1,260,924 bytes;token gate + hosted E2E 7/7 |

Cross-cutting evidence:`.agents/specs/TESTS.md`(rollup)、`ui/TESTS.md`(row-level)、FORK.md divergence 表。
