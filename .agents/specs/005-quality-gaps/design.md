# SPEC-005 Design

## E2E(QG-001)
- 拆兩個 spec 檔:`smoke.spec.ts`(功能斷言,CI gate)/ `manual-screenshots.spec.ts`(截圖+VRT,local-only)。CI 跑前者——VRT 在異質 runner 上字型/抗鋸齒差異會假紅(FMEA Q-R1:Prevent=不進 CI)。
- demo/main.go 新增:seed 完成後 `Inspector.PauseQueue("low")` + 補種 5 筆 pending(原手動 curl 步驟收編,guide 同步刪該步)。
- CI e2e job:ubuntu + valkey service(6379)→ build demo+server → 背景啟動 → `npx playwright install chromium --with-deps` → `ASYNQMON_BASE_URL=http://localhost:8080 npx playwright test e2e/smoke.spec.ts`。

## eslint(QG-002)
- flat config:`@eslint/js` recommended + `typescript-eslint` recommended + `react-hooks`。
- legacy 調整(逐條理由):`@typescript-eslint/no-explicit-any` off(API 轉接層大量 any,SPEC-004 已記為日後型別補強)、`no-empty-pattern`/`no-case-declarations` 按實況、`react-hooks/exhaustive-deps` warn(既有程式碼大量刻意省略 deps,先 warn 不 error,避免行為變更)。

## Metrics(QG-003)
- Prometheus 容器(host network 或 -p 29090:9090),config 抓 `localhost:28090/metrics`(server 需 `--enable-metrics-exporter`),scrape_interval 5s;等 ≥3 個樣本點後截圖。
- manual 再生:gen script(docs 化,從 temp 移入 `docs/manual/gen_manual.py`——FMEA Q-R2:再生腳本不可活在 gitignored temp)。

## FMEA
| Risk | Mode | Response |
|---|---|---|
| Q-R1 | VRT 進 CI 假紅 | Prevent:CI 只跑 smoke.spec |
| Q-R2 | 再生腳本在 temp/ 漂失 | Prevent:gen_manual.py 入版控 |
| Q-R3 | eslint 修壞行為(autofix) | Detect:vitest + e2e 全綠後才收;hooks deps 只 warn |
| Q-R4 | CI e2e 不穩(輪詢/時序) | Contain:networkidle+寬鬆 timeout;失敗重試 1 次(playwright retries) |

## Tasks
- [x] Q-T1 demo 收編 pause+pending;smoke.spec.ts;本地對 live env 全綠 [REQ-QG-001]
- [x] Q-T2 eslint flat config + 修至 0 errors;vitest 迴歸 [REQ-QG-002]
- [x] Q-T3 Prometheus 起 + metrics 截圖;manual/review/guide/ISSUE_LOG 更新;gen script 入版控 [REQ-QG-003]
- [x] Q-T4 build.yml lint + e2e jobs;closeout(review.md、SPECS/NEXT_STEPS/TESTS、PR→dev→main) [all]
