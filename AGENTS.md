# PROJECT KNOWLEDGE BASE

**Updated:** 2026-06-07
**Branch model:** `main`(穩定/default)← `dev`(整合)← `spec/* | chore/* | docs/*` lanes;`master` = upstream 純鏡像

## OVERVIEW
Asynqmon 是 Asynq task queue 的 Web UI。本 repo 是 hibiken/asynqmon 的 team fork(module path = `github.com/austinyuch/asynqmon`),**主要消費型態是 Go library**:`asynqmon.New(Options)` 回傳 `http.Handler`,UI bundle 經 `go:embed` 隨 module 出貨。standalone binary(`cmd/asynqmon`)與 container image 為次要部署型態。

## STRUCTURE
```text
asynqmon/
├── *.go                  # library:handler.go(New/Options)、各 API handlers、conversion_helpers
├── cmd/asynqmon/         # standalone binary(flags/env 解析)
├── ui/                   # React 18 + MUI 5 + router 6 + TS 5,Vite 8 建置
│   ├── build/            # committed production bundle(go:embed 的來源!)
│   └── src/
├── docs/                 # manual / review 生成物與 guides
├── .agents/{skills,specs}/  # canonical agent workspace(.claude/.kiro/.codex 下為 symlink)
└── githooks/pre-push     # govulncheck gate(git config core.hooksPath githooks)
```

## WHERE TO LOOK
| Task | Location | Notes |
|---|---|---|
| Library 入口 / Options | `handler.go` | `//go:embed ui/build/*` 在此 |
| Go template 注入(RootPath 等) | `static.go` | 自訂分隔符 **`/[[` `]]`**;index.html 的 token 不可被 encode |
| API handlers | `*_handlers.go` + `conversion_helpers.go` | 對 austinyuch/asynq Inspector 的轉接層 |
| UI 路由 / 頁面 | `ui/src/App.tsx`、`ui/src/views/` | router 6,paths 帶 `window.ROOT_PATH` 前綴 |
| UI build 設定 | `ui/vite.config.ts` | base=`/[[.RootPath]]/` + goTemplateBaseGuard plugin |
| Build token 驗證 gate | `ui/scripts/verify-go-template-tokens.mjs` | `yarn build` 內建,fail-closed |

## CONVENTIONS / ANTI-PATTERNS
- **改了 ui 依賴或源碼,必須 `cd ui && yarn build` 重建並 commit `ui/build/`**——僅改 package.json/lock 等於沒修(embed 出貨的是 committed bundle)。
- 不可破壞 index.html 中的 `/[[.RootPath]]` 等 Go template tokens(build gate 會擋,但別繞過 gate)。
- Go module path 以 `go.mod` 的 `module` 行為準(austinyuch),不要從 import 長相猜。
- UI dev server:`cd ui && yarn start`(proxy `/api` → localhost:8080)。
- 測試:`go test -race ./...`(無 Redis 依賴)+ `cd ui && yarn test`(Vitest)。

## COMMANDS
```bash
go build ./... && go vet ./... && go test -race -count=1 ./...
cd ui && yarn install --frozen-lockfile && yarn build   # tsc + vite + token gate
cd ui && yarn test && yarn lint
cd ui && npx playwright test e2e/smoke.spec.ts   # 需 demo env(見 docs/MANUAL_GENERATION_GUIDE.md);CI 自帶
make build        # UI assets + binary
make docker       # podman/docker 自動偵測
bash .agents/skills/local-image-publish-governance/scripts/publish_local_image.sh \
  --name asynqmon --smoke-expect 2    # 本地發布 image(Go --help exits 2)
```

## FORK GOVERNANCE & DOC MEMO
動 git / release / sync / 文件前先看:

| 文件 | 用途 |
|---|---|
| `FORK.md` | branch model、divergence 清單、sync log |
| `.agents/specs/SPECS.md` | spec registry(SPEC-001~005,全 Completed) |
| `.agents/specs/NEXT_STEPS.md` | rolling operational memo / 唯一權威 handoff path |
| `.agents/specs/ISSUE_LOG.md` | 未歸屬問題 + resolved 追溯 |
| `.agents/specs/RTM.md` | 需求 → spec → 驗證證據 矩陣 |
| `.agents/skills/upstream-sync/` | upstream 同步 pipeline(canonical) |
| `.agents/skills/local-image-publish-governance/` | 本地 image 發布規則(namespace/tags/labels/gates) |
| `docs/MANUAL_GENERATION_GUIDE.md` | 使用手冊(`docs/manual/{lang}/index.html`)生成/再生筆記 |
| `docs/REVIEW_GENERATION_GUIDE.md` | review 文件(`docs/review/index.html`)生成/再生筆記 |

**PR 鐵則**:fork 上 `gh pr create` 預設指向 upstream——一律帶 `--repo austinyuch/asynqmon`。PR base=`dev`,merge 一律人工(或經使用者明確授權)。

**Runtime 鐵則**:起 Valkey / server / E2E 必須走 `local-infra-registry-governance`(registry 在 `~/.config/opencode/local-infra/`),不可 ad-hoc `docker run`。

## NOTES
- 安全基線:yarn audit **0**、govulncheck **0**(pre-push gate);UI stack 全在現役 supported 線(React 18.3 / MUI 5.18 / router 6.30 / TS 5.9 / Vite 8)。
- 容器發佈:**local podman 為 canonical**(遠端 DockerHub 暫緩,IL-R10);docker-image-publish workflow 為手動觸發。
- Metrics 頁需要 `--enable-metrics-exporter` + Prometheus;exporter 佔用 server 的 `/metrics` 路徑,**UI 的 Metrics 視圖在 `/q/metrics`**(側欄進入)。
- asynq 依賴指向 team fork(`austinyuch/asynq v0.26.0-team.1`);upstream bump 時先回 asynq fork 做 sync + tag。
