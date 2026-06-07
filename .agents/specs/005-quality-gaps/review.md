# SPEC-005 Review — quality-gaps

## Verdict: PASS

### REQ-QG-001(E2E 基線)
✅ `ui/e2e/smoke.spec.ts` 7 案例(states 全集含 paused/aggregating group 流、task 詳情 client-nav、servers live worker、schedulers、dark mode、0 console errors)本地對 live env **7/7**;demo 程式收編 pause+pending(canonical scenario 單一來源);build.yml 新增 `e2e` job(valkey service + demo + chromium);VRT 留 local-only(Q-R1)。

### REQ-QG-002(eslint)
✅ eslint 9 flat config,`yarn lint` **0 errors**(1 documented warning:react-hooks/refs in SplitButton)。規則調整逐條記理由(config 註解 + design.md):no-explicit-any off(API 轉接層)、exhaustive-deps/refs warn(行為保留)、no-case-declarations/no-useless-assignment off(legacy reducer 模式)。真修:prototype-builtins、未用 imports/params/catch(含誤刪有用 catch binding 一次,vitest+tsc 攔回——Q-R3 防線生效)。CI lint+vitest step 入 build job。

### REQ-QG-003(Metrics)
✅ Prometheus(29090,registry 管轄)+ `--enable-metrics-exporter`:Metrics 頁渲染**真實資料圖表**(61 條 SVG data paths;Tasks Processed/Failed/Error Rate + per-queue 序列)。截圖 `metrics-live-01/02` 入 manual assets;manual(md+html×2)、review、兩份 guide、ISSUE_LOG(IL-004→R09)全部同步。**發現**:exporter 佔用 `/metrics`,UI Metrics 路由實為 `/q/metrics`(已記入 guide 與 manual)。

### 驗證
yarn lint 0 ✓ · vitest 3/3 ✓ · yarn build+token gate ✓ · playwright smoke 7/7 ✓ · go build/vet/test -race ✓ · manual HTML 再生 render-check ✓

### Residual
- IL-003(DockerHub secrets)仍 external-blocked——唯一剩餘 open gap,需 repo owner 在 GitHub settings 設定。
- CI e2e job 首跑於本 PR 驗證(Q-R4 retries 未啟用,若見不穩再加 retries=1)。
