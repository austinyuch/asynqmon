# SPEC-003 Design — ui-mui4-to-mui5-migration

前置已滿足:SPEC-002(Vite)、SPEC-004 Phase A(React 17.0.2)。Lane stacked on `spec/004-react17-phase-a`。

## 盤點(2026-06-07)

- `@material-ui` import × **308**(53 檔);`makeStyles`/`withStyles` × **27 檔**(JSS)
- lab 使用:`Alert`(9)、`AlertTitle`(9)、`Autocomplete`(1)——v5 全部轉正至 `@mui/material`
- `theme.tsx` 已用 `createTheme`(非 `createMuiTheme`,少一個 codemod 面)
- `@types/recharts` 1.8.20 為 recharts v1 types,與已裝的 recharts 2.1.4 錯位 → 一併移除(v2 自帶 types)

## styling 策略:JSS → tss-react(非 @mui/styles)

`@mui/styles`(JSS legacy)**不支援 React 18**,選它會把債滾進 Phase B;`tss-react` 保留 `makeStyles` API 形狀(emotion-based、React 18 相容),且官方 codemod `v5.0.0/jss-to-tss-react` 可自動轉換 27 檔。

## 遷移步驟

1. 依賴:移除 `@material-ui/{core,icons,lab}`、`@types/recharts`;新增 `@mui/material`、`@mui/icons-material`、`@mui/lab`、`@emotion/react`、`@emotion/styled`、`tss-react`
2. codemod `@mui/codemod v5.0.0/preset-safe src`(imports、moved-lab-modules、theme breaking changes)
3. codemod `@mui/codemod v5.0.0/jss-to-tss-react src`(makeStyles → tss-react)
4. `tsc --noEmit` 迭代修殘餘(theme palette type、component prop 變更:`Hidden` 移除、`fade`→`alpha` 等)
5. `yarn build` + token gate + vitest + audit + Go 驗證

## FMEA

| Risk ID | Failure Mode | Control / Response | Sev | Occ | Det | Task Trace |
|---|---|---|---|---|---|---|
| M-R1 | codemod 轉不乾淨,殘餘手工量爆炸 | Contain:tsc 迭代清單化;>40 錯誤時暫停回報,不硬寫 | 中 | 中 | 高 | M-T2/3 |
| M-R2 | 視覺回歸(spacing/typography v5 預設變更) | **Detect 缺口**:無 E2E 截圖基線。降級:build-level gate + review.md 標 `pending-manual-visual-smoke`,不宣稱 demo-ready(false-green 防護) | 高 | 中 | 低 | M-T4 |
| M-R3 | emotion 與 Vite/React 17 整合問題 | plugin-react 支援 emotion;build 驗證 | 低 | 低 | 高 | M-T3 |
| M-R4 | bundle size 顯著變化 | Detect:gzip size 比對記錄 review.md | 低 | 中 | 高 | M-T3 |

## Tasks

- [x] M-T1 依賴替換 + codemod preset-safe + jss-to-tss-react [Implements REQ-MUI-001]
- [x] M-T2 tsc 迭代修復至 0 錯誤(殘餘清單記 review.md) [Implements REQ-MUI-001]
- [x] M-T3 `yarn build`+token gate+vitest+audit 0+Go 驗證;rebuild ui/build;bundle size 比對 [Implements REQ-MUI-002 AC3]
- [x] M-T4 closeout:review.md(視覺回歸標 pending-manual)、TESTS.md、SPECS/NEXT_STEPS、PR(base=dev,人工 merge) [Implements all]
