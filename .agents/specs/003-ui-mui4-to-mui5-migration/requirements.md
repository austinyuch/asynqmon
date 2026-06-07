# SPEC-003 — ui-mui4-to-mui5-migration

**Status: Pending Implementation(authoring only)**

## 背景

`@material-ui/core` 4.12.3 / `@material-ui/icons` / `@material-ui/lab` 已 EOL,安全修復只進 `@mui/*` v5+(現行 major 更新)——第一類「升級也救不了」依賴,需 breaking migration。UI 大量使用 `makeStyles`(JSS)與 lab 元件。

## 前置依賴(硬性)

- **MUI v5 要求 React ^17 || ^18**:必須先完成 SPEC-004 的 Phase A(React 16 → 17,MUI v4 與 React 17 相容)後才可開始本 spec。
- 建議在 SPEC-002(Vite)完成後執行,避免在死掉的 CRA 工具鏈上做大遷移。

## 需求

### REQ-MUI-001:套件遷移

#### Acceptance Criteria

1. `@material-ui/core|icons|lab` 全數移除,改 `@mui/material`、`@mui/icons-material`、`@mui/lab`(v5 系列最新)。
2. styling engine JSS → emotion;官方 codemod(`@mui/codemod v5.0.0/preset-safe`)先行,殘餘手工修。
3. `makeStyles` 用法遷移(`tss-react` 或 `sx`/`styled`,design 階段定案);`createMuiTheme` → `createTheme`,theme palette/spacing 行為差異逐一驗證。
4. lab 元件(`Alert`、`Autocomplete`、`Pagination`、`Skeleton` 等 v5 已轉正)改自 `@mui/material` 匯入。

### REQ-MUI-002:視覺與行為回歸

#### Acceptance Criteria

1. 主要視圖(Dashboard、Queue 詳情、Task 列表各狀態、Scheduler、Servers、Redis Info、Metrics)逐頁人工/截圖比對,無布局崩壞。
2. dark mode(如有)與 theme 客製等價。
3. `yarn build`(Vite)+ Go embed 驗證綠;bundle size 變化記錄於 review.md。

## 範圍邊界

- 不重新設計 UI;1:1 等價遷移。
- react-redux / router 升級屬 SPEC-004。

## Impacts

- [Impacts: SPEC-002 建立的 build pipeline]、[Impacts: ui/TESTS.md]
- 依賴鏈:SPEC-002 → SPEC-004 Phase A → **SPEC-003** → SPEC-004 Phase B。
