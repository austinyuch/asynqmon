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

Cross-cutting evidence:`.agents/specs/TESTS.md`(rollup)、`ui/TESTS.md`(row-level)、FORK.md divergence 表。
