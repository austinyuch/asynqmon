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

## Phase B:React 17 → 18 + react-router 5 → 6(SPEC-003 完成後)

設計細節於 SPEC-003 merge 後補(createRoot、StrictMode 雙渲染、react-redux 8/9、router v6 API 對照表、TS 5、`**/react-router/path-to-regexp` resolution 移除)。

## Tasks(Phase A)

- [x] A-T1 bump react/react-dom 17.0.2;`yarn install` peer warning 審視;`addEventListener` 使用面盤點 [Implements REQ-R18-001]
- [x] A-T2 `yarn build`(含 token gate)+ `yarn test`;rebuild `ui/build/`;`go build && go test -race ./...`;audit 維持 0 [Implements REQ-R18-001]
- [x] A-T3 closeout:requirements Phase A AC 勾稽、SPECS/NEXT_STEPS、PR(base=dev,人工 merge) [Implements REQ-R18-001]
