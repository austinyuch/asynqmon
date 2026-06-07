# SPEC-001 Tasks — ui-runtime-vuln-hardening

Branch lane: `spec/001-ui-runtime-vuln-hardening`(single writable worktree)

- [x] T-1 採集修復前基準:`yarn audit` 摘要與 5 目標套件 advisory → `reports/audit-before.txt` [Implements REQ-UIVULN-001]
- [x] T-2 修改 `ui/package.json`:axios → 0.32.0(direct);resolutions:prismjs 1.30.0、decode-uri-component 0.2.2、`react-router/path-to-regexp` 1.9.0、d3-color 3.1.0(條件性,FMEA R-2);`yarn install` 更新 lock;驗證 express `path-to-regexp@0.1.7` entry 未變(FMEA R-3) [Implements REQ-UIVULN-001]
- [x] T-3 `NODE_OPTIONS=--openssl-legacy-provider yarn build`;若 d3-color 致 build 失敗 → 移除該 resolution 重跑並記錄(FMEA R-2);commit 新 `ui/build/` [Implements REQ-UIVULN-002]
- [x] T-4 驗證:`reports/audit-after.txt` 比對;bundle 指紋檢查(axios 版本字串);`go build && go vet && go test -race -count=1 ./...` [Implements REQ-UIVULN-001, REQ-UIVULN-002]
- [x] T-5 新增 `githooks/pre-push`(govulncheck,fail-closed);本機實跑一次;`FORK.md` 記錄啟用方式與 UI resolutions divergence [Implements REQ-UIVULN-003]
- [x] T-6 closeout:`ui/TESTS.md` + workspace `TESTS.md` rollup、`review.md`、`SPECS.md` / `NEXT_STEPS.md` 回寫、PR → CI 綠 → merge [Implements all]
