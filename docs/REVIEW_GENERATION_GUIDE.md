# Review Generation Guide — austinyuch/asynqmon

> 高階 review 文件(`docs/review/index.html`)的生成/再生筆記。配合 global `project-review-skill`;AGENTS.md 的 FORK GOVERNANCE & DOC MEMO 有本檔入口。

## 受眾與語言

管理層 / 外部 stakeholder;繁體中文(README 為英文,但決策受眾為中文)。

## 數據來源(claim 與 authority 對應)

| Claim | Authority / Source |
|---|---|
| 安全 415→0、govulncheck 0 | `.agents/specs/001~002/reports/audit-*.txt`、githooks/pre-push 實跑 |
| smoke 12/12、UI readiness PASS | `.agents/specs/003-*/reports/smoke/SMOKE_REPORT.md`、`003,004/review.md` |
| build 13.6s→0.33s、stack 版本 | SPEC-002/004 review.md、FORK.md divergence 表 |
| Gap(open/resolved) | `.agents/specs/ISSUE_LOG.md`(唯一來源;NEXT_STEPS 只是 hint) |
| Roadmap | ISSUE_LOG open 項 + FORK.md 已知未動 |

**Claim cap 規則**:Metrics 頁一律 `not_assessed` + `DEMO_NOT_ASSESSED`(IL-004 未解前);任何 readiness 措辭不得超出對應 review.md 裁決。

## Evidence(canonical,不另起 runtime)

Review 截圖**複用** manual 的 canonical assets(同一 seeded 情境,見 `docs/MANUAL_GENERATION_GUIDE.md`):

```bash
for s in dashboard-overview-01-queues queues-tasks-04-retry servers-workers-01-live dashboard-overview-02-dark; do
  cp docs/manual/assets/$s.png docs/review/assets/screenshot-$s.png
done
```

manual assets 過期時,先依 manual guide 再生,再執行上述複製——**不要**為 review 另建第二套 demo 流程(evidence 漂移風險)。

## 再生步驟

1. 確認 manual assets 新鮮(或先再生 manual)。
2. 複製 4 張關鍵截圖(上方命令)。
3. 更新 `docs/review/index.html`:hero 三數字、Gap 表(對照 ISSUE_LOG 現況)、Roadmap。
4. 渲染防呆:headless 開啟 index.html,確認 16:0 破圖、mermaid SVG 渲染、chips 顯示。
5. commit(PR base=dev)。

## Gap 狀態(隨每次再生更新)

- 2026-06-07(首次生成,基線):4 張 live 截圖、claim 全數對應 authority;Metrics 維持 not_assessed(IL-004)。
