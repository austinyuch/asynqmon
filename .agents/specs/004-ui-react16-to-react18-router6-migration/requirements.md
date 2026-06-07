# SPEC-004 — ui-react16-to-react18-router6-migration

**Status: Pending Implementation(authoring only)**

## 背景

React 16.13 與 react-router-dom 5.3 均為不再收安全維護的舊 major(第一類「升級也救不了」依賴)。本 spec 分兩個 phase,與 SPEC-003(MUI)交錯執行以滿足 peer-dependency 約束。

## Phase A:React 16 → 17(SPEC-003 的前置)

### REQ-R18-001:React 17 過渡

#### Acceptance Criteria

1. `react`/`react-dom` → 17.x,`@types/react*` 對齊;MUI v4 在 React 17 下功能正常(官方支援)。
2. event delegation 變更(document → root)不影響既有事件處理;build + 全頁 smoke 綠。

## Phase B:React 17 → 18 + react-router 5 → 6(SPEC-003 完成後)

### REQ-R18-002:React 18

#### Acceptance Criteria

1. `ReactDOM.render` → `createRoot`;StrictMode 雙重 render 下無副作用 bug。
2. automatic batching 行為差異審視(Redux dispatch 密集處,如 polling 更新)。
3. `react-redux` 7.2 → 8/9(React 18 相容版);`@reduxjs/toolkit` 升至相容版;TS types 全過。

### REQ-R18-003:react-router 6

#### Acceptance Criteria

1. `Switch` → `Routes`、`useHistory` → `useNavigate`、`useRouteMatch` → `useMatch`/`useParams`,route props → hooks;`path` 萬用字元與巢狀路由語意遷移。
2. 既有 URL 結構(deep links、query params,含 `query-string` 用法)完全等價——以路由清單逐條驗證。
3. path-to-regexp 1.x resolution(SPEC-001)隨 router 6 內建 matcher 汰除,從 `resolutions` 移除。

### REQ-R18-004:TypeScript 升級

#### Acceptance Criteria

1. TS 4.9 → 5.x(React 18 types 生態對齊);`tsc --noEmit` 全綠。

## 範圍邊界

- 不引入 React Server Components / Suspense data fetching 等新架構;等價遷移。
- MUI 套件本體屬 SPEC-003。

## Impacts

- [Impacts: SPEC-001 resolutions(path-to-regexp 條目移除)]、[Impacts: ui/TESTS.md]
- 依賴鏈:SPEC-002 → **Phase A** → SPEC-003 → **Phase B**。
