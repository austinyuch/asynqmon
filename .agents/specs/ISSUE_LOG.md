# ISSUE_LOG — austinyuch/asynqmon

holding surface:尚未歸屬 spec/CR 的改善項。不是第二份 SPECS.md,也不是 new-spec queue。

## Open

| ID | 描述 | 來源 | 分類傾向 | 狀態 |
|---|---|---|---|---|
| IL-001 | UI E2E 基線:把 smoke script(Playwright)轉正式 suite + CI 整合;@testing-library 已移除待以現役版重引 | SPEC-002/004 review residual | 候選 new spec | open |
| IL-002 | 正式 eslint 鏈(CRA eslintConfig 移除後未補;TS5 已就緒) | SPEC-002 review follow-up | 候選併入 IL-001 spec 或獨立 chore | open |
| IL-003 | Docker Hub 發佈需在 fork repo 設 `DOCKER_USERNAME`/`DOCKER_PASSWORD` secrets | FORK.md 已知未動 | external-blocked(需 repo owner 操作) | open |
| IL-004 | Metrics 頁完整 demo 需 Prometheus 配置;目前 manual/review 僅能呈現 graceful 空態 | manual 生成 gap 盤點 | 候選:demo compose(valkey+prometheus+exporter) | open |

## Resolved(追溯)

| ID | 描述 | 解法 | Resolved by |
|---|---|---|---|
| IL-R01 | `pretty-bytes` 幽靈依賴(靠 react-scripts hoisting,從未宣告) | 補為直接依賴 5.6.0 | SPEC-002(PR #4) |
| IL-R02 | `@types/react` v17 vs React 16 runtime 錯位(upstream 既有) | React 17 對齊,後續 18 + resolutions 統一 | SPEC-004(PR #6/#8) |
| IL-R03 | CodeQL action v1 停服、docker-publish 在 PR 上必失敗 | 升 v3 + permissions;PR 跳過 login | PR #1(f9687e2) |
| IL-R04 | Dockerfile `GOARCH=amd64` 寫死,arm64 host 產出跑不動的 image | TARGETOS/TARGETARCH | PR #10 |
| IL-R05 | local image 發布無規則(無 labels、無 arch/smoke gate) | workspace skill `local-image-publish-governance`;首跑即攔下 Go `--help` exit 2 假設錯誤 | PR #12/#14 |
| IL-R06 | Servers/Schedulers/active/retry/completed 頁面從無真實資料佐證(smoke 只有 enqueue-side 狀態) | manual 生成時以 live worker + scheduler seed 補齊 | docs lane(本次) |
