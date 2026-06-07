---
name: upstream-sync
description: 同步 upstream hibiken/asynqmon 到這個 team fork(module path 已改名為 github.com/austinyuch/asynqmon,asynq 依賴指向 team fork austinyuch/asynq)。當使用者提到「sync upstream」「同步上游」「upstream 有沒有更新」「merge hibiken」「更新 fork」「拉 upstream 的新 commit / release / tag」,或詢問 fork 與 upstream 的差異與衝突處理時使用。即使使用者只說「看一下上游有什麼新東西」也應觸發。
---

# Upstream Sync(hibiken/asynqmon → austinyuch/asynqmon)

這個 repo 是 team-maintained fork,branch 模型:
- module path 已改名:`github.com/hibiken/asynqmon` → `github.com/austinyuch/asynqmon`
- asynq 依賴指向 team fork:`github.com/austinyuch/asynq`(+ `/x`),用 `-team.N` tags
- **`main`**(default):下游專案直接消費的穩定線。只接受由 `dev` promote 的 PR;**永遠不可 rebase 或 force-push**
- **`dev`**:整合分支,sync / spec / chore lane 的 PR 目標;**merge 一律人工執行**(agent 只開 PR)
- **`master`**:upstream 的**純鏡像**,只能 `--ff-only` 從 `upstream/master` 更新,永不放團隊 commit——這條線是與 upstream 的對照基準
- 與 upstream 的差異清單記錄在 `FORK.md`,每次 sync 後必須更新

## Pipeline(前一步未通過不可進入下一步)

### 1. 前置檢查

```bash
git status --porcelain        # 必須是 clean worktree
git checkout main && git pull --ff-only origin main
git remote get-url upstream || git remote add upstream https://github.com/hibiken/asynqmon.git
```

`--ff-only` 是必要的:預設 pull 在 divergence 時會報錯或(若使用者設了 `pull.rebase=true`)默默 rebase——後者直接違反本 skill 的「永不 rebase main」。

### 2. 偵測 upstream 更新,並更新鏡像分支

```bash
git fetch upstream --tags
git rev-list --count --first-parent master..upstream/master
```

(`--first-parent` 讓計數符合人類直覺;寫進 PR body / FORK.md 的數字以 first-parent 為準。)

- 為 `0` → 回報「已與 upstream 同步」,**流程到此結束**
- 大於 0 → 先更新鏡像,再列出這次 sync 的內容:

```bash
git checkout master && git merge --ff-only upstream/master && git push origin master
git log --oneline main..master        # 這次要合入 main 的 upstream commits
```

`--ff-only` 失敗代表 master 被污染(混入了非 upstream commit)——停下來回報,不可硬 merge。

### 3. 建立 sync branch 並 merge

```bash
SYNC_BRANCH=sync/upstream-$(date +%Y%m%d)   # 只算一次,後續步驟都用變數(跨午夜不會分岔)
git checkout -b "$SYNC_BRANCH" main
git merge master
```

只用 merge,不用 rebase——保留 fork commit 的 hash,衝突一次解完,歷史可追溯。

### 4. 解衝突(已知 divergence hotspots)

| 檔案 | 解法 |
|---|---|
| `go.mod` / `go.sum` | **保留 fork 的** `module github.com/austinyuch/asynqmon` 行、`github.com/austinyuch/asynq...-team.N` requires、較新的 Go/toolchain 版本;**採用 upstream 的**新增依賴。upstream 若 bump 了 `hibiken/asynq` 版本,改成對應(或更新)的 fork `-team.N` tag——fork tag 落後時先回 austinyuch/asynq repo 做 sync + tag。之後跑 `go mod tidy` 收斂 `go.sum` |
| `README.md` | **保留 fork 的** import path(austinyuch)、docker image `austinyuch/asynqmon`;**採用 upstream 的**新內容段落 |
| `.github/workflows/*.yml` | **保留 fork 的** `main` branch targets、`build.yml`(valkey)、image `austinyuch/asynqmon`、Go/Node 版本;**採用 upstream 的**新 job/step |
| `Dockerfile` | **保留 fork 的** `golang:1.26-alpine`(或更新);**採用 upstream 的**其他變更 |
| `cmd/asynqmon/main_test.go` | **保留 fork 的** sentinel URI 期望(`SentinelPassword`,asynq c08f142 行為);**採用 upstream 的**新測試 |
| 任何 `*.go` 的 import 區塊 | 直接**採 upstream 側**(hibiken path 也沒關係)——step 5 的 rename script 會兜底改成 austinyuch,這是最機械、最不易出錯的解法 |

不在表內的衝突:優先理解 upstream 意圖,必要時對照 `FORK.md` 判斷哪邊是 intentional divergence。

衝突解完後 `git commit`(完成 merge commit)再進下一步。

### 5. 重新套用 module-path rename

upstream 新增的檔案 import 的是 `github.com/hibiken/asynqmon` / `github.com/hibiken/asynq`,merge 後必須重套 rename。執行 idempotent script:

```bash
bash .agents/skills/upstream-sync/scripts/reapply-module-path.sh
```

script 結束時會輸出殘留的 hibiken import 數量,必須為 0 才能繼續。若 script 有改動檔案,連同 step 6 `go mod tidy` 產生的變更一起 `git commit -m "Re-apply module path rename after upstream sync"`——不可留 uncommitted 變更進 step 9,否則 push 出去的是不完整的 branch。

### 6. 建置驗證

```bash
go mod tidy && go build ./... && go vet ./...
```

### 7. 測試

asynqmon 的 Go 測試不需要 Redis instance:

```bash
go test -race -count=1 ./...
```

若這次 sync 動到 `ui/`(package.json / yarn.lock / src),需另外驗證 UI build
(CRA/webpack4 在 Node ≥ 17 要 `NODE_OPTIONS=--openssl-legacy-provider`):

```bash
(cd ui && yarn install && NODE_OPTIONS=--openssl-legacy-provider yarn build)
```

若需要 live smoke(跑 binary 對真實 Valkey),**必須走 `local-infra-registry-governance` skill 的流程**,不可直接 `docker run` 繞過 registry。

### 8. 更新 FORK.md

在 sync log 加一列:日期、合入的 upstream commit(short hash)、解掉的衝突、測試結果,然後 `git commit`。若這次 sync 改變了 divergence 清單(fork-only 修改被 upstream 收編、或新增了 fork-only 改動),同步更新差異表。

### 9. PR → main

確認 `git status --porcelain` 乾淨(所有步驟的變更都已 commit)後:

```bash
git push -u origin "$(git branch --show-current)"
gh pr create --repo austinyuch/asynqmon --base dev --title "Sync upstream $(date +%Y%m%d)" --body "<upstream commits 摘要 + 測試結果>"
```

(`gh` 在 fork 上預設指向 upstream repo,`--repo` 不可省。)

CI(build.yml)綠了之後**由人工 merge**(agent 不執行 merge)。merge 後視需要打 tag:

```bash
git tag v<upstream-version>-team.<N>
git push origin --tags
```

## 絕對不做

- force-push 或 rebase `main`(下游 go.sum 記著 commit hash,改寫歷史會弄壞所有消費者)
- 把團隊 commit 放進 `master`(它是 upstream 鏡像;污染後 `--ff-only` 會永久失敗)
- 在測試未全綠時 merge sync PR
- 繞過 local-infra registry 直接起容器
