# SPEC-003 Review — ui-mui4-to-mui5-migration

## Verdict: CONDITIONAL PASS(build-level 驗證全綠;視覺回歸 pending-manual,見 Residual)

## AC 驗證

### REQ-MUI-001
1. ✅ `@material-ui/{core,icons,lab}` 全移除;`@mui/material` 5.18.x、`@mui/icons-material`、`@mui/lab` 5.0.0-alpha、emotion 11、tss-react 4.9。殘餘 `@material-ui` import = 0。
2. ✅ codemod 先行:`v5.0.0/preset-safe`(41 檔 ok,1 error——SettingsView 的 `/es/` 深路徑 import,手工修)+ `v5.0.0/jss-to-tss-react`(26 檔 ok)。
3. ✅ styling 採 **tss-react**(非 @mui/styles,React 18 相容,不滾債進 Phase B);`makeStyles` 全數遷移,含三個 codemod 無法處理的 hotspot:
   - `App.tsx`:closure-theme workaround → tss params idiom(`makeStyles<{theme}>()`),保留「theme 在 ThemeProvider 之外計算」的原語意;`mixins.toolbar` 加 `CSSObject` cast
   - `MetricsFetchControls.tsx`:JSS props-callback styles → tss params;**v5 Button 移除 `label` slot**,typography 樣式併入 root
   - `TablePaginationActions.tsx`:`createStyles` wrapper 移除
4. ✅ lab 元件(Alert/AlertTitle/Autocomplete)由 codemod 轉至 `@mui/material`;其餘 v5 breaking changes 手工修:`theme.palette.type`→`mode`(並移除 `adaptV4Theme`,直接用 v5 theme shape)、Grid `justify`→`justifyContent`、Select onChange → `SelectChangeEvent`、ClickAwayListener event type、Autocomplete `renderOption` 新簽名(`(liProps, option)` + `<li>`)。
5. ✅ `@types/recharts`(v1 types,與 recharts 2 錯位)移除。

### REQ-MUI-002
1. ⚠️ **pending-manual-visual-smoke**(FMEA M-R2):無 E2E 截圖基線,主要視圖逐頁比對未執行。本 review 驗證層級為 **hybrid(build-level)**:tsc 0 錯誤、vite build + token gate、vitest 3/3、Go embed 測試綠。**不宣稱 demo-ready**;人工 merge 前建議至少跑一次 `make docker` + 瀏覽器 smoke(Dashboard/Queues/Tasks/Metrics/Settings/Dark mode)。
2. ✅(理論等價)theme palette 數值未變,dark mode 走 `mode: "dark"`;`isDarkTheme` 原本就讀 `palette.mode`(v4 時代的 forward-compat 寫法,v5 下自然正確)。
3. ✅ bundle:1,150.59 kB(329.07 gzip,MUI4/JSS)→ 1,218.69 kB(356.13 gzip,MUI5/emotion),+8% gzip,記錄在案(M-R4)。

## FMEA 回顧

| Risk | 結果 |
|---|---|
| M-R1(codemod 殘餘爆量) | 66 → 0 tsc 錯誤,三輪迭代,未觸發 >40 暫停線(峰值集中於可批次處理的 destructure 模式) |
| M-R2(視覺回歸) | **open**——降級為 CONDITIONAL PASS + pending-manual 標記,無 false-green 宣稱 |
| M-R3(emotion/Vite 整合) | 未發生 |
| M-R4(bundle size) | +8% gzip,可接受,已記錄 |

## Residual / Out of Scope

- 視覺回歸人工 smoke 由 maintainer 在 merge 前執行(或併入 Phase B 後一次驗)。
- react-redux 7 / router 5 / TS 4.9 → SPEC-004 Phase B。
