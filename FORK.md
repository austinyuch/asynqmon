# Fork Maintenance — github.com/austinyuch/asynqmon

Team-maintained fork of [hibiken/asynqmon](https://github.com/hibiken/asynqmon).
姊妹 fork:[austinyuch/asynq](https://github.com/austinyuch/asynq)(本 repo 的 asynq 依賴來源,治理模型相同)。

## Branch model

| Branch | 角色 | 規則 |
|---|---|---|
| `main`(default) | 下游消費 + 團隊 PR 目標 | PR-merge only;never rebase / force-push |
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
| 其他 | `FORK.md`、`.agents/skills/upstream-sync/` | 團隊維運工具 |

已知未動(follow-up 候選):
- `Dockerfile` frontend stage 仍是 `alpine:3.17`(Node 18 EOL);UI 是 CRA/webpack4 + React 16,升 Node/依賴需要另開 spec 驗證 UI build
- `ui/` npm 依賴鏈未做 security bump(同上,牽動大)
- docker-image-publish 需要在 fork repo 設定 `DOCKER_USERNAME` / `DOCKER_PASSWORD` secrets 才會真的發佈

## Sync log

| 日期 | Upstream base | 衝突 | 測試 |
|---|---|---|---|
| 2026-06-07 | `d1b8894`(與 upstream/master 同步,0 behind) | —(初始 rename + hardening,非 merge) | `go build` / `go vet` / `go test -race ./...` 全綠(Go 1.26.4) |

## Release tags

單一 module,tag 格式:`vX.Y.Z-team.N`(對應 upstream 最近 release 加 team 序號)。
