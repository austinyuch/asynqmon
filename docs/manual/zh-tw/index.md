# Asynqmon 使用手冊(zh-TW)

> Asynqmon 是 [Asynq](https://github.com/austinyuch/asynq) task queue 的監控/管理 Web UI(team fork:`github.com/austinyuch/asynqmon`)。
> 本手冊全部截圖為 **live evidence**:真實 Valkey 9.1 + 真實 asynq worker/scheduler + canonical demo 資料(`docs/manual/demo/main.go`)。
> Product-level readiness:**PASS**(來源:`.agents/specs/003-*/review.md`、`004-*/review.md` + 12/12 browser smoke)。再生方式見 [`docs/MANUAL_GENERATION_GUIDE.md`](../../MANUAL_GENERATION_GUIDE.md)。

每張截圖的 evidence metadata 標準值(個別不同時於該節註明):
**Evidence Source** = live screenshot(seeded demo)· **Coverage Tier** = full-integration · **Readiness State** = PASS(review.md)

## 目標受眾與快速導覽

| 你是誰 | 先看 |
|---|---|
| 維運/值班(看佇列健康、救火) | Dashboard → 任務狀態 → 重試與封存 |
| 後端開發(嵌入自家服務、查任務) | Getting Started(library 模式)→ 任務詳情 |
| 平台管理(worker 容量、排程) | Servers → Schedulers → 佇列操作 |

## Getting Started / Starter Assets

三種啟動方式(擇一):

```bash
# 1) standalone binary
asynqmon --port=8080 --redis-addr=localhost:6379

# 2) container(本地發布規則見 .agents/skills/local-image-publish-governance/)
podman run --rm -p 8080:8080 localhost/local/asynqmon --redis-addr=host.containers.internal:6379

# 3) Go library 嵌入(主要消費型態;UI bundle 已 go:embed)
h := asynqmon.New(asynqmon.Options{
    RootPath:     "/monitoring",
    RedisConnOpt: asynq.RedisClientOpt{Addr: "localhost:6379"},
})
mux.Handle(h.RootPath()+"/", h)
```

Starter assets(git-tracked,可直接下載/執行):

| 檔案 | 用途 |
|---|---|
| [`demo/main.go`](../demo/main.go) | 一鍵種出**全部任務狀態** + live worker/scheduler 的 demo 程式(真實 asynq API) |
| [`../../ui/e2e/manual-screenshots.spec.ts`](../../../ui/e2e/manual-screenshots.spec.ts) | 截圖/VRT spec,可作為自家 E2E 起點 |

## 操作動線(UX Flow)

```mermaid
flowchart LR
    A[Dashboard\n佇列總覽] -->|點佇列| B[Queue 詳情\n8 個狀態 tab]
    B -->|點任務列| C[Task 詳情]
    B -->|批次/單筆操作| D[run / archive / kill / delete]
    A -->|側欄| E[Servers\nworker 與 active 任務]
    A -->|側欄| F[Schedulers\ncron entries]
    A -->|側欄| G[Redis Info]
    A -->|側欄| H[Settings\n輪詢間隔 / Dark mode]
```

## Dashboard(佇列總覽)

![Dashboard](../assets/dashboard-overview-01-queues.png)
*佇列堆疊長條(各狀態着色)、7 日 processed/failed 趨勢、佇列表(state/size/latency/error rate)。注意 `low` 佇列 state 為紅色 **paused**。右側 Actions(⋯)可 pause/resume/delete 佇列。*

![Dashboard dark](../assets/dashboard-overview-02-dark.png)
*Dark mode(Settings → Dark Theme → Always)。*

## 任務狀態(Queue 詳情的 8 個 tabs)

| 狀態 | 含意 | demo 樣本 |
|---|---|---|
| Active | worker 處理中 | `video:transcode`(25 分鐘長任務) |
| Pending | 等待派工 | `image:resize` ×5(於 paused 佇列,故停留) |
| Aggregating | Group 聚合等待中 | `metrics:event` ×5(group `metrics-batch`) |
| Scheduled | 未到 ProcessIn/ProcessAt 時間 | `report:generate` ×5(+2h) |
| Retry | 失敗待重試 | `sync:export`(S3 unreachable,MaxRetry 10) |
| Archived | 重試耗盡/手動封存 | `billing:charge`(MaxRetry 0)、`image:resize` ×2(Inspector 封存) |
| Completed | 成功且在 Retention 期內 | `email:welcome/digest` ×14 |

![Active](../assets/queues-tasks-01-active.png)
*Active tab:可看 payload 與已執行時間;READ_ONLY 模式以外可 cancel。*

![Pending paused](../assets/queues-tasks-02-pending-paused.png)
*Pending tab(佇列 paused 中):任務停留不派工;佇列名旁可見 paused 標記。*

![Scheduled](../assets/queues-tasks-03-scheduled.png)
*Scheduled tab:Process In 倒數;可 Run now / Archive / Delete(單筆或勾選批次)。*

![Retry](../assets/queues-tasks-04-retry.png)
*Retry tab:顯示最後錯誤訊息(此處為 demo 的 "upstream S3 bucket unreachable")、已重試次數/上限、下次重試時間。*

![Archived](../assets/queues-tasks-05-archived.png)
*Archived tab:封存原因(card declined)留在 Last Error;可 Run / Delete。*

![Completed](../assets/queues-tasks-06-completed.png)
*Completed tab:Retention 期內的成功任務,含 Completed 時間。*

![Aggregating](../assets/queues-tasks-07-aggregating.png)
*Aggregating tab:左上 group 下拉(`metrics-batch`)切換群組;等待 GroupGracePeriod/MaxSize 觸發聚合。*

## 任務詳情

![Task detail](../assets/task-detail-01-retry-task.png)
*點任一任務列進入:完整 payload(JSON 高亮)、佇列、狀態、Retry 計數、Last Error、下次重試時間;上方麵包屑可回佇列。*

## Servers(workers)

![Servers](../assets/servers-workers-01-live.png)
*一列 = 一個 asynq server(host:PID、啟動時間、佇列權重 critical 6 / default 3 / low 1)。展開列可見 **Active Workers**:正在執行的 `video:transcode` 與其 payload——這是 live worker 真實在跑的任務。*

## Schedulers(cron entries)

![Schedulers](../assets/schedulers-entries-01-list.png)
*demo scheduler 註冊的兩條 entries:`*/5 * * * *` report:generate(critical)與 `@every 1h` cleanup:tmp(low);含 next/prev enqueue 時間與歷史。*

## Redis Info

![Redis](../assets/redis-info-01-stats.png)
*連線中 Valkey/Redis 的 INFO 摘要(版本、記憶體、連線數等)。*

## Settings

![Settings light](../assets/settings-config-01-light.png)
*輪詢間隔(預設 8s)與 Dark Theme 偏好(System Default / Always / Never)。*

![Settings dark](../assets/settings-config-02-dark.png)

## Metrics(已知 gap)

![Metrics gap](../assets/metrics-gap-01-no-prometheus.png)
*⚠️ **Evidence Source** = live screenshot(graceful 空態)· **Coverage Tier** = `not_assessed` · **Readiness State** = `not_assessed` · Code: `DEMO_NOT_ASSESSED`(ISSUE_LOG IL-004)。本頁需要 server 以 `--enable-metrics-exporter` 啟動且配置 Prometheus(`--prometheus-addr`);demo 環境未配 Prometheus,僅證明該頁 graceful 渲染,不證明圖表功能。*

## CLI flags 速查(server 部署)

| Flag / Env | 說明 |
|---|---|
| `--port` / `PORT` | 監聽埠(預設 8080) |
| `--redis-addr` / `REDIS_ADDR` | Redis/Valkey 位址 |
| `--redis-url` / `REDIS_URL` | redis:// 或 redis-sentinel:// URI(sentinel 密碼語意見 fork 修正) |
| `--redis-cluster-nodes` | cluster 模式節點列表 |
| `--read-only` | 唯讀 UI(隱藏所有寫操作) |
| `--enable-metrics-exporter` + `--prometheus-addr` | 啟用 Metrics 頁 |

完整列表:`asynqmon --help`(Go flag 慣例,exit code 2)。
