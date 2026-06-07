# Browser Smoke Report — SPEC-003 (MUI v5) + SPEC-004 (React 18 / router 6)

- Date: 2026-06-07 · Stack under test: branch `spec/004-react18-phase-b`(React 18.3.1 + MUI 5.18 + router 6.30 + TS 5.9 + Vite 8)
- Runtime: **full-integration** — real Valkey 9.1.0(registry-governed instance `asynqmon/asynqmon-e2e-smoke`,ports 16382/28090,已 release)+ asynqmon binary(embedded 新 bundle)+ seeded tasks(8 pending/default、5 scheduled/critical、1 pending + 2 archived/low,經 austinyuch/asynq v0.26.0-team.1 client)
- Tool: Playwright 1.60 / Chromium 148(headless),script `temp/smoke/smoke.mjs`(transient,不入版控)

## Results: 12/12 PASS · pageErrors 0 · consoleErrors 0

| # | Case | 驗證點 |
|---|---|---|
| 01 | Dashboard `/` | 渲染 + queues 表 |
| 02 | `/queues/default?status=pending` | deep-link refresh + seeded task payload 顯示 |
| 03 | `/queues/critical?status=scheduled` | scheduled tab + 資料 |
| 04 | `/queues/low?status=archived` | archived tab + 資料 |
| 05-08 | Servers / Schedulers / Redis / Settings | 各頁渲染 |
| 09 | Dark mode(Settings select → Always) | AppBar bg → rgb(18,18,18),MUI5 dark palette 生效 |
| 10 | Client-side nav(dashboard → queue link) | router 6 Link 導航至 /queues/critical |
| 12 | `/metrics`(無 Prometheus) | graceful 渲染不 crash |

截圖:本目錄 `*.png`(12 張)。初跑 3 個 FAIL 均為測試腳本假設錯誤(default tab 是 Active 非 Pending、body bg 不帶 theme 與 v4 架構一致、nav 選錯元素),修正後全綠。

## 結論

SPEC-003 review M-R2 與 SPEC-004 review B-R1/B-R2 的 pending-manual-visual-smoke 已執行完畢,兩份 review verdict 升級為 **PASS**。
