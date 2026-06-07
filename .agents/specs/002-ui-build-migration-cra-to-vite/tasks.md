# SPEC-002 Tasks — ui-build-migration-cra-to-vite

Branch lane: `spec/002-ui-build-migration-cra-to-vite`

- [x] T-1 依賴替換 + spike:移除 react-scripts/@types/jest,加 vite/@vitejs/plugin-react/vite-plugin-svgr/vitest/jsdom;確認 React 16.14 下 vite build 可起(FMEA R-3) [Implements REQ-VITE-001]
- [x] T-2 設定檔:`vite.config.ts`(base=`/[[.RootPath]]/`、outDir=build、svgr、goTemplateBaseGuard plugin、server.proxy)、`index.html` 遷移改寫、`tsconfig.json` types、`react-app-env.d.ts` → vite types、`scripts/verify-go-template-tokens.mjs` 驗證 gate [Implements REQ-VITE-001 AC2/3, REQ-VITE-003]
- [x] T-3 程式碼適配:App.tsx svg `?react` import;刪 serviceWorker.ts + index.tsx 呼叫;package.json scripts/欄位清理 [Implements REQ-VITE-001 AC3]
- [x] T-4 build 驗證:`yarn build`(含 token gate)→ commit `ui/build/`;`go build && go vet && go test -race -count=1 ./...`;index.html token 與 bundle 指紋人工複核 [Implements REQ-VITE-001 AC1/2]
- [x] T-5 audit 比對:`reports/audit-after-vite.txt`,critical/high 相對基準(58c/174h)降幅 ≥90%,殘餘逐條列 review.md(FMEA R-4) [Implements REQ-VITE-001 AC4]
- [x] T-6 test runner:汰除 App.test.tsx(現狀即壞,記 review.md)、setupTests 調整;新增 `parseFlags.test.ts`;`yarn test` 綠;openssl-legacy hack 從 Dockerfile/release.yml 移除 + Node LTS 升級 [Implements REQ-VITE-002, REQ-VITE-001 AC5]
- [ ] T-7 closeout:ui/TESTS.md + workspace TESTS.md、FORK.md、review.md、SPECS.md/NEXT_STEPS.md、PR → CI 綠 → merge [Implements all]
