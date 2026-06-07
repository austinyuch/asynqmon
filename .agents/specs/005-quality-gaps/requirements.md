# SPEC-005 — quality-gaps(E2E 基線 + eslint + Metrics demo)

來源:ISSUE_LOG IL-001 / IL-002 / IL-004(spec-master 分類:三項同屬「品質防線補齊」,併一 spec)。IL-003 為 external-blocked,不在範圍。

## REQ-QG-001:UI E2E 正式基線(IL-001)

#### Acceptance Criteria
1. `ui/e2e/smoke.spec.ts`:功能性 E2E(非 VRT)——dashboard、8 狀態 tab(含 paused/pending)、task 詳情、servers live worker、schedulers、dark mode、0 console errors;對 seeded demo 資料斷言。
2. demo 程式內建 pause-low + 補種 pending(取代手動 curl 步驟),CI 與本地同一套 canonical scenario。
3. CI:build.yml 新增 `e2e` job(valkey service + demo + server + Playwright chromium),PR gate。
4. VRT(manual-screenshots.spec.ts)維持 local-only(CI 字型渲染差異風險,design 記載)。

## REQ-QG-002:eslint 鏈(IL-002)

#### Acceptance Criteria
1. eslint 9 flat config(typescript-eslint + react-hooks),`yarn lint` 0 errors。
2. 對 legacy 碼的規則調整需在 design.md 記錄理由(不可無聲關閉)。
3. CI build job 加 lint step。

## REQ-QG-003:Metrics 頁真實驗證(IL-004)

#### Acceptance Criteria
1. demo 環境補 Prometheus(registry 管轄 port 29090),server 以 `--enable-metrics-exporter --prometheus-addr` 啟動;Metrics 頁渲染**真實圖表資料**(非空殼)。
2. 截圖納入 manual assets;manual(md/html×2 語)與 review 的 `DEMO_NOT_ASSESSED` 標記升級為 full-integration。
3. MANUAL_GENERATION_GUIDE 補 Prometheus 步驟;ISSUE_LOG IL-004 → resolved。

## Impacts
[Impacts: build.yml]、[Impacts: docs/manual/*, docs/review/*]、[Impacts: ISSUE_LOG]
