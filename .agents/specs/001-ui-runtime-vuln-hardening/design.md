# SPEC-001 Design — ui-runtime-vuln-hardening

## 方案選擇

### 修復機制:直接升版 vs yarn resolutions

| 依賴 | 機制 | 理由 |
|---|---|---|
| `axios` | **直接升版** `package.json` → `0.32.0` | direct dependency;0.x 系列 API 與 0.21 相容(`AxiosError` 在 0.x 是 type-only export,`ui/src/utils.ts` 僅作型別使用) |
| `prismjs` | **resolution** `"prismjs": "1.30.0"` | transitive(react-syntax-highlighter → refractor);1.30.0 同時涵蓋 ReDoS 與 CVE-2024-53382 |
| `decode-uri-component` | **resolution** `"decode-uri-component": "0.2.2"` | transitive(query-string);semver-compatible patch |
| `path-to-regexp` | **scoped resolution** `"**/react-router/path-to-regexp": "1.9.0"(yarn1 scoped path 須從 direct dep 起算,故用 `**` 前綴)` | 必須 scoped:全域 force 會把 express 鏈的 `0.1.7` 一起改成 1.9.0,破壞 webpack-dev-server(AC REQ-UIVULN-001.2) |
| `d3-color` | **resolution** `"d3-color": "3.1.0"`(條件性) | transitive(recharts → d3-interpolate 2,range `1 - 2`);3.1.0 超出 range 但 API 相容。風險:d3-color 3.x 為 ESM-only,webpack 4 可解析 ESM 但需驗證;失敗則回退(見 FMEA R-2) |

### Contract / SSOT

本 spec 的「契約」即依賴 pin 清單,SSOT = `ui/package.json` 的 `resolutions` 區塊 + `yarn.lock`。
- Contract Authority:**external**(GitHub Advisory DB / npm audit endpoint)
- Source of Truth:`ui/package.json` resolutions(版控內)
- Pin/Version:如上表;audit 比對基準存於 `reports/audit-before.txt` / `reports/audit-after.txt`

### govulncheck pre-push hook(REQ-UIVULN-003)

仿 austinyuch/asynq `githooks/pre-push`:單一 module,對 root 跑 `govulncheck ./...`。
`PATH` 需涵蓋 `$(go env GOPATH)/bin`;binary 不存在時提示安裝指令並 fail-closed。

## Lightweight FMEA

| Risk ID | Failure Mode | Effect | Cause | Control / Planned Response | Sev | Occ | Det | Task Trace |
|---|---|---|---|---|---|---|---|---|
| R-1 | 改了 package.json/lock 但沒重建 `ui/build/` | 修復假象:bundle 仍含舊漏洞碼(false-green) | `ui/build` 是 committed artifact,易被忽略 | **Prevent**:REQ-UIVULN-002 AC1 強制 rebuild+commit;**Detect**:AC3 bundle 指紋檢查 | 高 | 中 | 中 | T-3, T-4 |
| R-2 | d3-color 3.x(ESM-only)讓 webpack4 build 失敗或產出壞 chunk | UI build 紅或圖表頁面 runtime 掛 | CRA4/webpack4 對 ESM-only 套件支援邊緣 | **Contain**:條件性 resolution——build 失敗即移除該條 resolution,在 review.md 記 residual risk(moderate ReDoS,輸入面為自家 metrics 資料,實際暴露低) | 中 | 中 | 低 | T-2, T-3 |
| R-3 | 全域 path-to-regexp resolution 改掉 express 的 0.1.7 | `yarn start`(webpack-dev-server)壞掉,開發流程中斷 | resolutions 預設全域生效 | **Prevent**:scoped `react-router/path-to-regexp`;**Detect**:AC2 檢查 lock 中 0.1.7 entry 未變 | 中 | 高 | 中 | T-2 |
| R-4 | axios 0.21→0.30 行為差異(error shape、defaults) | API 錯誤處理 UI 行為改變 | 0.x 內部重構 | **Detect**:tsc(yarn build 內含)+ 全 src grep axios 用法人工複核(65 處集中於 api.ts) | 中 | 低 | 中 | T-2, T-3 |
| R-5 | Node 25 本機 build 與 CI/Docker 的 Node 18 產出不一致 | bundle 內容漂移 | 本機無 Node 18 | **Contain**:openssl-legacy-provider 兩邊一致;bundle 為 minified 產物,差異僅 hash;以 build 成功 + go test 為準,Docker stage 仍會在 publish 時用自己的 toolchain 重建 | 低 | 中 | 高 | T-3 |

## 驗證計畫

1. `reports/audit-before.txt`:修復前 `yarn audit --summary` + 5 目標套件的 advisory 行
2. 修復 → `yarn install`(更新 lock)→ 檢查 lock(R-3)
3. `NODE_OPTIONS=--openssl-legacy-provider yarn build` → commit `ui/build`
4. `reports/audit-after.txt`:修復後 audit,比對 5 目標套件歸零
5. Go:`go build && go vet && go test -race -count=1 ./...`
6. hook:`bash githooks/pre-push` 手動跑一次
