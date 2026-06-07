# SPEC-004 Design — ui-react16-to-react18-router6-migration

兩 phase 與 SPEC-003 交錯(peer-dependency 約束):002 → **Phase A** → 003 → **Phase B**。

## Phase A:React 16.14 → 17.0.2

### 盤點

- `@types/react ^17.0.29` / `@types/react-dom ^17.0.9` **本來就是 v17**(upstream 既有的 types/runtime 錯位),Phase A 反而消除此錯位。
- 相容性:MUI v4(4.12.x 官方支援 React 17)、react-redux 7.2、react-router 5、Vite plugin-react automatic runtime(17 原生支援)——皆相容。
- `ReactDOM.render` 在 17 仍為正式 API(18 才換 `createRoot`,屬 Phase B)。
- 行為差異:event delegation 從 `document` 移到 root container;codebase 無直接 `document.addEventListener` 與 React 合成事件混用的模式(盤點 `addEventListener` 使用面驗證)。

### 變更

`react`/`react-dom` → `17.0.2`(僅版本 bump,無 API 變更)。

### Phase A FMEA

| Risk ID | Failure Mode | Control / Response | Sev | Occ | Task Trace |
|---|---|---|---|---|---|
| A-R1 | event delegation 變更影響全域 listener | Detect:grep `addEventListener` 盤點 + build/test;App 為標準 MUI 元件樹,無已知混用 | 中 | 低 | A-T1, A-T2 |
| A-R2 | 隱性 peer-dep 衝突(yarn1 不強制) | Detect:`yarn install` warning 審視 + build | 低 | 中 | A-T1 |

## Phase B:React 17 → 18 + react-router 5 → 6 + TS 5(stacked on SPEC-003)

### 變更面

| 項目 | 內容 |
|---|---|
| React | 18.3.1;`ReactDOM.render` → `createRoot`(index.tsx);StrictMode 保留(雙渲染檢視副作用) |
| react-redux | 7.2 → 9.x(自帶 types,移除 `@types/react-redux`);`connect` API 不變 |
| @reduxjs/toolkit | 1.6 → 2.x;store.ts 用 plain `configureStore`/`combineReducers`,無自訂 middleware,升版無 API 面 |
| react-router-dom | 5.3 → 6.30(自帶 types,移除 `@types/react-router-dom`);`Switch`→`Routes`、Route children→`element`、`useHistory`→`useNavigate`(×12,`history.push(x)`→`navigate(x)`、`goBack()`→`navigate(-1)`、`history.location`→`useLocation()`)、`useRouteMatch`→`useMatch`(ListItemLink:`{path, end:true, caseSensitive:true}`);paths.ts 維持 `window.ROOT_PATH` 前綴絕對路徑(不採 basename,行為等價) |
| TypeScript | 4.9 → 5.x(vitest 4 types 可解析,tsconfig 移除 test exclude) |
| recharts | 2.1.4 → 2.x 最新(React 18 peer 自 2.1.10 起) |
| resolutions | 移除 `**/react-router/path-to-regexp`(router 6 內建 matcher,SPEC-001 該 pin 功成身退) |
| @testing-library/* | 移除(自 SPEC-002 汰除 boilerplate 後零使用,且 v12 不相容 React 18;待元件測試/E2E 建立時再以現役版本引入) |

### Phase B FMEA

| Risk ID | Failure Mode | Control / Response | Sev | Occ | Task Trace |
|---|---|---|---|---|---|
| B-R1 | StrictMode 雙渲染暴露副作用(polling/Redux dispatch) | Detect:vitest + build;Contain:殘餘行為差異列 review,視覺/行為 smoke 與 SPEC-003 併一次人工驗 | 中 | 中 | B-T3 |
| B-R2 | router 6 路由匹配語意差異(trailing slash、`exact` 移除後的全等匹配) | Routes 預設即全等;`paths.HOME` 為 `${ROOT_PATH}/` 需驗證;Detect:tsc + 路由清單逐條對照 | 高 | 中 | B-T2 |
| B-R3 | TS5 暴露新型別錯誤連鎖 | Contain:迭代修;>40 暫停回報 | 中 | 中 | B-T2 |
| B-R4 | recharts 2.x 升版 API 漂移(QueueMetricsChart 等) | Detect:tsc + build | 中 | 低 | B-T2 |

### Tasks(Phase B)

- [x] B-T1 依賴 bump + resolutions/types 清理 + `yarn install` [Implements REQ-R18-002/003/004]
- [x] B-T2 程式碼遷移:createRoot、Routes/element、useNavigate ×12、useMatch、useLocation;tsc 迭代至 0 [Implements REQ-R18-002/003]
- [x] B-T3 驗證鏈:build+token gate+vitest+audit 0+Go;bundle size 記錄 [Implements REQ-R18-002 AC2]
- [x] B-T4 closeout:review.md、TESTS.md、FORK.md、SPECS/NEXT_STEPS、PR(base=dev,人工 merge) [Implements all]

## Tasks(Phase A)

- [x] A-T1 bump react/react-dom 17.0.2;`yarn install` peer warning 審視;`addEventListener` 使用面盤點 [Implements REQ-R18-001]
- [x] A-T2 `yarn build`(含 token gate)+ `yarn test`;rebuild `ui/build/`;`go build && go test -race ./...`;audit 維持 0 [Implements REQ-R18-001]
- [x] A-T3 closeout:requirements Phase A AC 勾稽、SPECS/NEXT_STEPS、PR(base=dev,人工 merge) [Implements REQ-R18-001]
