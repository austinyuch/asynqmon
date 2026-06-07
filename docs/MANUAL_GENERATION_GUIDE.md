# Manual Generation Guide — austinyuch/asynqmon

> 使用手冊(`docs/manual/`)的生成/再生筆記。配合 global `user-manual-skill`;AGENTS.md 的 FORK GOVERNANCE & DOC MEMO 有本檔入口。`docs/manual/MANUAL_GENERATION_GUIDE.md` 為 stub,指向本檔。

## Product Surface Classification

**Web-App Dominant。** Asynqmon 是 Asynq 的監控 Web UI;主要 evidence = **Playwright 截圖(真實 Valkey + 真實 asynq worker/scheduler + seeded demo data)**。次要 surface:Go library 嵌入(`asynqmon.New`)與 CLI flags,以 code/command 範例佐證。

## Canonical Seed / Demo Data

| 項目 | 位置 | 用途 |
|---|---|---|
| Seed + worker + scheduler(真實 API,單一程式) | `docs/manual/demo/main.go` | 唯一權威 demo 來源;產生**全部任務狀態** + live Servers/Schedulers 資料,常駐直到 SIGTERM |
| 任務樣本 | `email:welcome/digest`(completed,Retention 2h)、`report:generate`(scheduled +2h, critical)、`image:resize`(low;2 archived)、`sync:export`(永遠失敗 → retry)、`billing:charge`(MaxRetry 0 → archived)、`video:transcode`(25min 長任務 → active)、`metrics:event`(Group → aggregating) | 覆蓋 8 種狀態 + weighted queues(critical 6 / default 3 / low 1) |
| Paused + pending | 手動步驟:`POST /api/queues/low:pause`(注意是 **`:pause`** 不是 `/pause`——`/pause` 會被 SPA fallback 回 200 騙過)再 enqueue 數筆 low 任務 | paused 佇列 + pending tab 同框 |
| Scheduler entries | demo 內建 `*/5 * * * *` report:generate、`@every 1h` cleanup:tmp | Schedulers 頁 |

## Runtime(registry-governed,不可 ad-hoc 起服務)

依 `local-infra-registry-governance`:project `asynqmon`、instance `asynqmon-e2e-smoke`(Valkey `localhost:16382` + server `:28090` + Prometheus `:29090`)。request → 用 → release。

## 再生手冊的完整命令序列

```bash
# 1. registry request(見上)後:
docker run -d --name asynqmon-e2e-valkey -p 16382:6379 valkey/valkey:9.1.0
go build -o temp/demo-bin ./docs/manual/demo && ./temp/demo-bin -redis_addr=localhost:16382 &   # 等 ~10s 讓狀態就位
go build -o temp/asynqmon ./cmd/asynqmon && \
  ./temp/asynqmon --port=28090 --redis-addr=localhost:16382 \
  --enable-metrics-exporter --prometheus-addr=http://localhost:29090 &
# Prometheus(metrics 頁證據;config 抓 localhost:28090/metrics,5s interval)
docker run -d --name asynqmon-e2e-prom --network host \
  -v $PWD/temp/prometheus.yml:/etc/prometheus/prometheus.yml:ro \
  prom/prometheus --config.file=/etc/prometheus/prometheus.yml --web.listen-address=:29090
# 注意:exporter 佔用 server 的 /metrics;UI Metrics 頁在 /q/metrics(side-nav 進入),
# 截圖腳本需 client-side nav,等 ≥60s 讓圖表有資料點

# 2. paused+pending:demo 程式已內建(Inspector.PauseQueue + 補種)
#    (SPEC-005 起已收編進 demo 程式,本步驟不再需要)

# 3. 截圖(canonical spec;輸出 docs/manual/assets/*.png,含 2 個 VRT baseline)
cd ui && npx playwright test e2e/manual-screenshots.spec.ts
#    VRT baseline 變更時:--update-snapshots

# 4. 更新 docs/manual/{zh-tw,en}/index.{md,html}(引用 assets,逐圖帶 evidence metadata)
# 5. release registry instance + 停 demo/server + 移除容器
```

已知坑(再生時別重踩):
- demo 程式重複啟動會雙重 seed + 雙 worker(ghost server 列);啟動前先確認無殘留程序。
- scheduler enqueue 的任務型別(report:generate/cleanup:tmp)必須有 handler,否則長 session 會堆 handler-not-found retry。
- `pkill -f` 的 pattern 別含進自己命令字串。

## Evidence Metadata 慣例(每張截圖 caption 必帶)

- **Evidence Source**:`live screenshot — real Valkey 9.1 + real asynq worker/scheduler, seeded demo data`
- **Coverage Tier**:`full-integration`;Metrics 頁(無 Prometheus)為 `not_assessed`
- **Readiness State**:沿用 `.agents/specs/00{3,4}-*/review.md` = **PASS**(product-level 來源必須註明 review.md);Metrics 頁 `not_assessed`

## Visual Gap 狀態(隨每次再生更新)

| Gap | 狀態 | Code |
|---|---|---|
| Task actions 互動過程(cancel/archive/run 的 confirm 流) | 截圖為靜態頁;互動結果未逐一截圖 | 文字說明 + API 行為描述 |
| 多 server / cluster 視圖 | demo 僅單 worker | 文字說明 |

### Gaps resolved since last check

- 2026-06-07(SPEC-005):**IL-004 已解**——Prometheus(29090)+ `--enable-metrics-exporter`,Metrics 頁以真實圖表資料截圖(`metrics-live-01/02`),metadata 升 full-integration;發現並記錄 exporter 遮蔽 `/metrics`、UI 實際路由為 `/q/metrics`。
- 2026-06-07(manual 首次生成,基線 = SPEC-003 smoke 12 張):**IL-R06 已解**——Servers(live worker + active payload)、Schedulers(2 entries)、active/retry/completed/aggregating/paused+pending 全部以真實 worker/scheduler 資料截圖;smoke 時這些頁面是空的。aggregating(Group)為**首次**有真實證據的狀態。

## 檔案結構

```
docs/
├── MANUAL_GENERATION_GUIDE.md      ← 本檔(canonical)
└── manual/
    ├── MANUAL_GENERATION_GUIDE.md  ← stub → 本檔
    ├── gen_manual.py               ← HTML 再生腳本(SPEC-005 起入版控)
    ├── demo/main.go                ← canonical seed(go vet 納入 ./...)
    ├── assets/*.png                ← 截圖 evidence(16 張,可再生)
    ├── zh-tw/index.{md,html}
    └── en/index.{md,html}
ui/
├── playwright.config.ts
└── e2e/manual-screenshots.spec.ts  ← canonical 截圖 spec(含 VRT baselines)
```
