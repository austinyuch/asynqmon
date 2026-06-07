# SPEC-004 Review — ui-react16-to-react18-router6-migration

## Verdict: PASS(build-level 全綠 + full-integration browser smoke 12/12,evidence:../003-ui-mui4-to-mui5-migration/reports/smoke/)

## Phase A(React 16.14 → 17.0.2)— PR #6

1. ✅ react/react-dom 17.0.2;消除 upstream 既有的 types(v17)/runtime(v16)錯位。
2. ✅ `addEventListener` 全 codebase 零使用,event delegation 變更無影響面;build/test/audit 0/Go 全綠。
3. ✅ 附帶:`redux-devtools` devDep 移除(零 import,RTK 內建 devTools;它是唯一 React≤16 peer 衝突源)。

## Phase B(React 17 → 18 + router 5 → 6 + TS 5)— PR #8

### REQ-R18-002:React 18
1. ✅ `ReactDOM.render` → `createRoot`(index.tsx);StrictMode 保留。
2. ✅ runtime smoke 已執行(polling 下各頁渲染與導航正常,0 console errors);automatic batching 無觀察到行為異常。
3. ✅ react-redux 7.2 → 9.3(`connect` API 不變,自帶 types,`@types/react-redux` 移除);RTK 1.6 → 2.12(store.ts 為 plain configureStore,無 middleware 客製;legacy 窄型 action union reducers 使 RTK2 推導 preloadedState 為 never → 以 cast + 註解處理,runtime shape 不變)。

### REQ-R18-003:react-router 6
1. ✅ `Switch`→`Routes`、Route children→`element`(9 條路由)、`useHistory`→`useNavigate`(12 檔;`goBack()`→`navigate(-1)`、MetricsView `history.location`→`useLocation()`)、`useRouteMatch`→`useMatch`(ListItemLink,`end:true, caseSensitive:true` 對應原 `exact/strict/sensitive`)。
2. ✅ URL 結構不變:paths.ts 維持 `window.ROOT_PATH` 前綴絕對路徑(沿用原架構,不採 basename);`:qname`/`:taskId` param 語法 v6 相同;`useParams` 改 v6 慣用法(undefined-safe destructure defaults)。
3. ✅ `**/react-router/path-to-regexp` resolution 移除(SPEC-001 的 pin 功成身退,router 6 內建 matcher);audit 仍 0。

### REQ-R18-004:TypeScript 5
1. ✅ TS 4.9 → 5.9;`tsc --noEmit` 0 錯誤;vitest 4 types 可解析,tsconfig 的 test `exclude` workaround(SPEC-002 遺留)移除。
2. 連鎖修復:error helpers 改 `unknown` + `axios.isAxiosError` narrowing(~120 個 strict catch 錯誤的根修)、React 18 `forwardRef` children 不再隱含(GroupSelect)、`@types/react-window`/`@types/react-syntax-highlighter` 升現役版、lockfile `@types/react@*` 殘留 17 → resolutions 統一 18。

### 附帶清理
- `@testing-library/*` 三件移除:自 SPEC-002 汰除 boilerplate 後零使用,v12 與 React 18 不相容;待建元件測試/E2E 時以現役版本重引入。
- recharts 2.1.4 → 2.15.4(React 18 peer)。

## 驗證

tsc 0 ✓ · vite build + token gate ✓ · vitest 3/3 ✓ · yarn audit **0**(379 packages)✓ · `go build`/`go vet`/`go test -race` ✓ · bundle 356 → 347.56 kB gzip(router 6 較小)

## FMEA 回顧

| Risk | 結果 |
|---|---|
| B-R1(StrictMode 雙渲染) | **closed**——runtime smoke 0 page/console errors |
| B-R2(路由匹配語意) | **closed**——deep-link refresh(?status= 各 tab)+ client-side nav 實測通過 |
| B-R3(TS5 連鎖) | 139 → 0,三輪;主因單一模式(strict catch),未觸發暫停線 |
| B-R4(recharts 漂移) | tsc/build 無 API 面錯誤 |

## Residual / Out of Scope

- browser smoke 已執行(full-integration,12/12);證據見 SPEC-003 reports/smoke/。
- EOL 債清零:React 18.3 / MUI 5.18 / router 6.30 / TS 5.9 / Vite 8 全為現役 supported 線;`yarn audit` 0。
