# Fork Maintenance — github.com/austinyuch/asynqmon

Team-maintained fork of [hibiken/asynqmon](https://github.com/hibiken/asynqmon).
姊妹 fork:[austinyuch/asynq](https://github.com/austinyuch/asynq)(本 repo 的 asynq 依賴來源,治理模型相同)。

## Branch model

| Branch | 角色 | 規則 |
|---|---|---|
| `main`(default) | 下游消費(穩定線) | 只接受由 `dev` promote 的 PR;**merge 一律人工執行**;never rebase / force-push |
| `dev` | 整合分支:spec / chore lane 的 PR 目標 | PR-merge only,**merge 一律人工執行**(agent 只開 PR,不 merge) |
| `master` | upstream 純鏡像 | 只能 `--ff-only` from `upstream/master`;永不放團隊 commit |

下游消費方式(module path 已改名):

```bash
go get github.com/austinyuch/asynqmon
docker pull austinyuch/asynqmon
```

Upstream sync 流程見 repo-local skill:`.agents/skills/upstream-sync/`。

Agent 工作目錄採 `.agents/` 為 canonical source:`.claude/.kiro/.codex` 下的 `skills/`、`specs/` 是 symlink(gitignored),各 agent 的設定/權限檔維持實體檔案。fresh clone 後用 `cross-agents-symlink-bridge` skill 重建,或手動:

```bash
for a in .claude .kiro .codex; do mkdir -p $a && ln -sfn ../.agents/skills $a/skills && ln -sfn ../.agents/specs $a/specs; done
git config core.hooksPath githooks   # 啟用 pre-push govulncheck
```

## Intentional divergence from upstream

| 範圍 | 內容 | 原因 |
|---|---|---|
| Module path | `github.com/hibiken/asynqmon` → `github.com/austinyuch/asynqmon`(go.mod + 全部 import + README 範例) | 下游直接 require,免 `replace` |
| asynq 依賴 | `hibiken/asynq v0.24.1` → `austinyuch/asynq v0.26.0-team.1`;`hibiken/asynq/x`(pseudo-version)→ `austinyuch/asynq/x v0.1.0-team.1` | 吃到團隊 fork 的 security hardening(go-redis v9.20.0、protobuf v1.36.11 等皆隨之收斂) |
| Dependencies | gorilla/mux v1.8.1、rs/cors v1.11.1(DoS fix)、prometheus/client_golang v1.23.2、go-redis v9.20.0(經 asynq fork 傳遞) | security hardening / CVE 面收斂 |
| Go toolchain | `go 1.16` → `go 1.25.0` + `toolchain go1.26.4`;CI 用 1.26.x | 跟上 supported releases,與 asynq fork 一致 |
| `cmd/asynqmon/main_test.go` | sentinel URI 測試期望改為 `SentinelPassword`(原註解即標 FIXME) | asynq `c08f142`(v0.25+)修正 sentinel URI 解析行為 |
| CI | 新增 `build.yml`(PR → main;Go 1.26.x;valkey/valkey:9.1.0 service);codeql / docker-publish 改 target `main`;docker image 改 `austinyuch/asynqmon`;release.yml 改 Go 1.26.x + Node 18(`NODE_OPTIONS=--openssl-legacy-provider`);actions 升級(codeql-action v1→v3 + `security-events: write`、checkout v4、setup-go v5、docker metadata/login/build-push 現行版,PR 不跑 DockerHub login) | 配合 branch model 與 fork 發佈通道;v1 codeql-action 已停服 |
| `Dockerfile` | backend stage `golang:1.18-alpine` → `golang:1.26-alpine` | go 1.25.0 module 需要新 toolchain |
| Docs | README 的 import 範例 / docker image / godoc / releases 連結改 fork path;指向 upstream wiki、issues、license 的連結刻意保留 | 反映 fork 現況 |
| UI runtime deps | axios 0.32.0(direct);resolutions:prismjs 1.30.0、decode-uri-component 0.2.2、d3-color 3.1.0、lodash 4.18.1、@babel/runtime(-corejs3) 7.29.7、@types/react(-dom) 18(path-to-regexp pin 已隨 router 6 移除);`ui/build/` 以修復後依賴重建 | SPEC-001/002 vuln 收斂(yarn audit 415 → 0) |
| UI frameworks | React 16.14 → **18.3.1**(SPEC-004);@material-ui v4 → **@mui v5** + emotion + tss-react(SPEC-003);react-router 5 → **6.30**;react-redux 9 + RTK 2;TS 4.9 → **5.9**;recharts 2.15;@testing-library/redux-devtools 等未使用件移除 | EOL majors 清零 |
| UI build toolchain | CRA/react-scripts → **Vite 8** + vite-plugin-svgr + Vitest;`pretty-bytes` 補為直接依賴(原為幽靈依賴);`index.html` 移至 ui/ 根、Go template token 由 `goTemplateBaseGuard` plugin + post-build gate 保護;Dockerfile frontend `alpine:3.17`→`node:22-alpine`(移除 openssl-legacy hack);Makefile/release.yml 同步 | SPEC-002:CRA 已 EOL,build 鏈 58 critical 無修復出路(`.agents/specs/002-ui-build-migration-cra-to-vite/`) |
| Git hooks | `githooks/pre-push` 跑 `govulncheck ./...`;啟用:`git config core.hooksPath githooks`(per-clone,不入版控) | 與 asynq fork 治理對齊 |
| 其他 | `FORK.md`、`.agents/skills/upstream-sync/`、`.agents/specs/` | 團隊維運工具 |

已知未動(follow-up 候選):
- UI 元件測試 / E2E(Playwright)基線——SPEC-003/004 的視覺/行為 smoke 目前 pending-manual
- docker-image-publish 需要在 fork repo 設定 `DOCKER_USERNAME` / `DOCKER_PASSWORD` secrets 才會真的發佈

## Sync log

| 日期 | Upstream base | 衝突 | 測試 |
|---|---|---|---|
| 2026-06-07 | `d1b8894`(與 upstream/master 同步,0 behind) | —(初始 rename + hardening,非 merge) | `go build` / `go vet` / `go test -race ./...` 全綠(Go 1.26.4) |

## Release tags

單一 module,tag 格式:`vX.Y.Z-team.N`(對應 upstream 最近 release 加 team 序號)。
