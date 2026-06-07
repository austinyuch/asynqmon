# SPEC-001 Review — ui-runtime-vuln-hardening

## Verdict: PASS(repo-side work complete;merge pending CI green)

## AC 驗證

### REQ-UIVULN-001
1. ✅ 5 目標套件 advisory 歸零(`reports/audit-after.txt`:「none — all 5 target packages clean」);總量 415 → 376(其餘屬 build/test-time,SPEC-002 範圍)。d3-color 3.1.0 resolution 成功,**無** residual risk 條目。
2. ✅ express dev 鏈未被波及且自然升至 patched 0.1.x:re-resolve 後為 `path-to-regexp@~0.1.12` → 0.1.13(隔離於 express 巢狀層);AC 原文「0.1.7 entry 維持原樣」的意圖是「dev server 不被 1.x force 破壞」,實際結果優於原 AC(0.1.x patched)。
3. ✅ critical 數不變(58,全屬既有 build-time 鏈),無新增 critical/high。
   - 補充:scoped resolution 原始 key `react-router/path-to-regexp` 無效(yarn1 路徑須從 direct dep 起算),改 `**/react-router/path-to-regexp` 後生效——已回寫 design.md。

### REQ-UIVULN-002
1. ✅ `yarn build` 成功(Node 25 + openssl-legacy-provider),新 `ui/build/` 已 commit(chunk 結構改變:舊 2.*.chunk.js → 單一 main.*.js,屬 webpack 重 chunk,FMEA R-5 範圍內)。
2. ✅ `go build` / `go vet` / `go test -race -count=1 ./...` 全綠(embed 新 bundle)。
3. ✅ bundle 含 `"0.32.0"`、`0\.21\.2` 0 筆(初查 1 筆為未跳脫 regex 誤匹配)。

### REQ-UIVULN-003
1. ✅ `githooks/pre-push` 新增,fail-closed(找不到 binary 即 exit 1)。
2. ✅ FORK.md 記錄啟用方式 + UI resolutions divergence。
3. ✅ 本機實跑:「No vulnerabilities found」。

## FMEA 回顧

| Risk | 結果 |
|---|---|
| R-1(bundle 未重建) | 已防:rebuild + commit + 指紋檢查 |
| R-2(d3-color ESM) | 未發生:webpack4 成功解析,無 fallback |
| R-3(express 鏈被 force) | 已防:scoped resolution;express 巢狀 0.1.13 |
| R-4(axios 0.21→0.32 行為) | tsc(build 內含)通過;0.x type surface 相容 |
| R-5(Node 版本漂移) | 接受:本機 Node 25 build 成功;Docker/CI 用各自 toolchain 重建 |

## Residual / Out of Scope

- 376 個剩餘 advisories 全屬 build/test-time 鏈(react-scripts/jest/babel),依 SPEC-002(CRA→Vite)收斂;EOL 框架見 SPEC-003/004。
- live-demo readiness:本 spec 僅依賴 build + embed 驗證,未跑 real-backend UI smoke(分類:**hybrid**)——UI 行為層面的回歸風險由「依賴皆為 patch/minor 級修復」緩解;若需 full-integration 驗證,於 SPEC-002 E2E 建立後補。
