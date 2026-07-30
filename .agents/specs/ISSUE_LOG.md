# ISSUE_LOG — austinyuch/asynqmon

holding surface:尚未歸屬 spec/CR 的改善項。不是第二份 SPECS.md,也不是 new-spec queue。

## Open

| ID | 描述 | 來源 | 分類傾向 | 狀態 |
|---|---|---|---|---|
| — | (目前無 open items;新項目依 issue-log-manager 流程登錄) | | | |

## Resolved(追溯)

| ID | 描述 | 解法 | Resolved by |
|---|---|---|---|
| IL-R01 | `pretty-bytes` 幽靈依賴(靠 react-scripts hoisting,從未宣告) | 補為直接依賴 5.6.0 | SPEC-002(PR #4) |
| IL-R02 | `@types/react` v17 vs React 16 runtime 錯位(upstream 既有) | React 17 對齊,後續 18 + resolutions 統一 | SPEC-004(PR #6/#8) |
| IL-R03 | CodeQL action v1 停服、docker-publish 在 PR 上必失敗 | 升 v3 + permissions;PR 跳過 login | PR #1(f9687e2) |
| IL-R04 | Dockerfile `GOARCH=amd64` 寫死,arm64 host 產出跑不動的 image | TARGETOS/TARGETARCH | PR #10 |
| IL-R05 | local image 發布無規則(無 labels、無 arch/smoke gate) | workspace skill `local-image-publish-governance`;首跑即攔下 Go `--help` exit 2 假設錯誤 | PR #12/#14 |
| IL-R10 | DockerHub secrets 未設,push main 的 docker-publish 持續紅(IL-003) | **決策解**:遠端發佈暫緩,workflow 改 manual-only;canonical 通道 = local podman(`local-image-publish-governance` skill)。Re-open 條件:需要對外散佈 image 時,設 secrets + 手動觸發 | 使用者決策(2026-06-07) |
| IL-R07 | UI E2E 正式基線缺失(IL-001) | `ui/e2e/smoke.spec.ts`(7 案例功能斷言)+ CI e2e job;VRT 留 local-only(設計見 SPEC-005) | SPEC-005 |
| IL-R08 | eslint 鏈缺失(IL-002) | eslint 9 flat config + ts-eslint + react-hooks;0 errors(規則調整逐條記理由);CI lint step | SPEC-005 |
| IL-R09 | Metrics 頁無真實驗證(IL-004) | Prometheus(29090)+ exporter;真實圖表截圖入 manual;發現 UI 路由實為 `/q/metrics` | SPEC-005 |
| IL-R06 | Servers/Schedulers/active/retry/completed 頁面從無真實資料佐證(smoke 只有 enqueue-side 狀態) | manual 生成時以 live worker + scheduler seed 補齊 | docs lane(本次) |
| IL-R11 | hosted E2E retry-state assertion 對非同步 worker transition 使用固定延遲而偶發失敗 | 保留 real-data deep-link assertion,改為 bounded Playwright auto-wait;PR #24/#25 E2E 7/7 | CR-2026-07-30-002(`3c0d1ef`) |
| IL-R12 | SPEC-006 registry/operational memo 在 PR #24/#25 完成後仍標示 PR pending,且 generated `.code-review/` 汙染 status | 依 upstream PR/check evidence 單次重生 derived surfaces;`.code-review/` 僅 ignore、不刪除 | CR-2026-07-30-001 |
| IL-R13 | `SplitButton` 在 render 階段讀取 `anchorRef.current`,每次 lint 產生 React correctness warning | 使用 MUI Popper lazy `anchorEl` callback,保留相同 anchor/click-away 行為 | CR-2026-07-30-003 |
| IL-R14 | UI install 後 `go build/vet/test ./...` 與 `govulncheck ./...` 會納入 `ui/node_modules` 內第三方 Go package | 共用 repo-owned package allowlist,排除 `*/node_modules/*`;fixture regression test fail-closed | CR-2026-07-30-004 |
