# SPEC-002 Review — ui-build-migration-cra-to-vite

## Verdict: PASS(repo-side work complete;merge pending CI green)

## AC 驗證

### REQ-VITE-001
1. ✅ Vite 8.0.16 + @vitejs/plugin-react 6.0.2 production build 成功(334ms,CRA 為 ~13.6s);react-scripts 已移除。
2. ✅ `outDir: build`,`go:embed ui/build/*` 與 `staticDirPath` 零改動;`go build`/`go vet`/`go test -race` 綠。
3. ✅ `index.html` 移至 ui/ 根,`%PUBLIC_URL%` → 字面 `/[[.RootPath]]`;`base: "/[[.RootPath]]/"` 經 `goTemplateBaseGuard` plugin + `verify-go-template-tokens.mjs` post-build gate 驗證(FMEA R-1:方括號實測未被 encode,gate 仍常駐於 build script);`REACT_APP_*` 無使用面;`process.env.NODE_ENV` → `import.meta.env.PROD`。
4. ✅ **超標**:audit 415(SPEC-001 前)→ 376(SPEC-001 後)→ **0**(critical/high 降幅 100%,AC 要求 ≥90%)。Vite 遷移消滅 build 鏈後,殘餘 7 unique(lodash via redux-devtools、@babel/runtime via MUI/testing-library)以 resolutions 收斂(lodash 4.18.1、@babel/runtime 7.29.7)。`reports/audit-after-vite.txt`。
5. ✅ openssl-legacy-provider 全數移除(Dockerfile、release.yml);Dockerfile frontend → `node:22-alpine`(corepack yarn);release.yml Node 22 + `--frozen-lockfile`(原 `rm yarn.lock` hack 移除);Makefile `--modules-folder` 技巧移除(Vite CLI 不吃未知 flag)。

### REQ-VITE-002
1. ✅ jest → Vitest 4.1.8(jsdom env);CRA boilerplate `App.test.tsx` 汰除——其「learn react link」斷言與實際 App 不符,**現狀即失敗**且 CI 從未執行;以 `parseFlags.test.ts`(3 案例,涵蓋 server-evaluated / unevaluated-template / undefined fallback)取代。`yarn test` 3/3 綠。
2. ✅ `ui/TESTS.md` 新增 UI-UNIT-001 / UI-TOKEN-001,canonical commands 更新。

### REQ-VITE-003
1. ✅ `tsc --noEmit` 納入 build script(TS 4.9 保留——TS 5 升級屬 SPEC-004 REQ-R18-004;vitest 4 的 d.ts 需 TS5 解析,故 tsconfig `exclude` test 檔,vitest 自帶 transform);eslint:CRA `eslintConfig` 移除,正式 lint 鏈留待 SPEC-004 TS5 後一併建(記為 spec-local follow-up,不阻塞)。

## 實作發現(requirements 外)

- **幽靈依賴**:`pretty-bytes` 一直由 react-scripts 鏈 hoist,從未宣告——補為直接依賴(5.6.0,CJS;v6+ ESM-only 需 TS5 moduleResolution 支援,留給 SPEC-004)。
- bundle:CRA `static/js/main.*.js`(324KB gzip)→ Vite `assets/index-*.js`(329KB gzip),SPA fallback 與 embed 路徑無 hardcode,深層路由 refresh 不受目錄名變更影響(FMEA R-2)。

## FMEA 回顧

| Risk | 結果 |
|---|---|
| R-1(token encode) | 未發生;Prevent plugin + Detect gate 雙重保留 |
| R-2(SPA fallback) | 未發生;serveFile 對任意 path 走 embed FS |
| R-3(React 16 相容) | 未發生;Vite 8 + plugin-react 6 + React 16.14 automatic runtime 可用 |
| R-4(audit 反升) | 未發生;歸零 |
| R-5(dev proxy) | `server.proxy` 已設;dev-only 非 gate |

## Residual / Out of Scope

- yarn audit = **0**;EOL majors(React 16 / MUI4 / router 5)無 advisory 但無安全維護,風險由 SPEC-003/004 收斂。
- live-demo readiness:**hybrid**——build/unit/token gate + Go embed 驗證;未跑 real-backend browser smoke。建議在 SPEC-004 Phase A 開工前以 governed runtime 做一次 full-integration smoke(記入 NEXT_STEPS)。
