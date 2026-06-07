#!/usr/bin/env bash
# Idempotent:merge upstream 後重新套用 module-path rename。
# 兩條 rename:
#   github.com/hibiken/asynqmon → github.com/austinyuch/asynqmon(本 repo module)
#   github.com/hibiken/asynq    → github.com/austinyuch/asynq(team fork 依賴,含 /x)
# 只改「引用程式碼」的 path,不動指向 upstream 的文件連結(wiki / issues / license / releases)。
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# 1) Go import paths(quoted form,不會誤傷註解中的 upstream issue 連結)。
#    hibiken/asynqmon 與 hibiken/asynq 同字首,先長後短沒有差別——
#    sed 對 "github.com/hibiken/asynq 的單一替換已同時涵蓋兩者。
{ grep -rl '"github.com/hibiken/asynq' --include='*.go' . 2>/dev/null || true; } \
  | xargs -r sed -i 's|"github.com/hibiken/asynq|"github.com/austinyuch/asynq|g'

# 2) go.mod module / require 行(版本由 hotspot 衝突解法決定,這裡只兜底 path)
sed -i 's|^module github.com/hibiken/asynqmon|module github.com/austinyuch/asynqmon|' go.mod
sed -i 's|^	github.com/hibiken/asynq |	github.com/austinyuch/asynq |' go.mod
sed -i 's|^	github.com/hibiken/asynq/x |	github.com/austinyuch/asynq/x |' go.mod

# 3) README 的可執行引用(import 範例、docker image、release/godoc 連結;
#    指向 upstream wiki / issues / license 的純文件連結刻意保留)
sed -i -e 's|"github.com/hibiken/asynqmon"|"github.com/austinyuch/asynqmon"|g' \
       -e 's|"github.com/hibiken/asynq"|"github.com/austinyuch/asynq"|g' \
       -e 's|docker pull hibiken/asynqmon|docker pull austinyuch/asynqmon|g' \
       -e 's|docker run hibiken/asynqmon|docker run austinyuch/asynqmon|g' \
       -e 's|^    hibiken/asynqmon|    austinyuch/asynqmon|' \
       -e 's|godoc.org/github.com/hibiken/asynqmon|godoc.org/github.com/austinyuch/asynqmon|g' \
       -e 's|releases page](https://github.com/hibiken/asynqmon/releases)|releases page](https://github.com/austinyuch/asynqmon/releases)|' \
       README.md

remaining=$({ grep -rn '"github.com/hibiken/asynq' --include='*.go' . 2>/dev/null || true; } | wc -l)
gomod_remaining=$({ grep -n 'github.com/hibiken/asynq' go.mod 2>/dev/null || true; } | wc -l)
echo "remaining hibiken imports in .go files: ${remaining}"
echo "remaining hibiken paths in go.mod: ${gomod_remaining}"
[ "$((remaining + gomod_remaining))" -eq 0 ] || { echo "ERROR: rename incomplete" >&2; exit 1; }

# 資訊性 audit(不擋流程):其他 tracked 檔案中的 hibiken 引用。
# README 指向 upstream repo/wiki/godoc 的連結屬刻意保留;此清單供人工掃一眼
# upstream 是否新增了該改而沒改到的引用(新 workflow、新文件等)。
echo "--- informational audit (intentional upstream links expected) ---"
git grep -n 'hibiken/asynq' -- ':!*.go' ':!go.mod' ':!go.sum' ':!.claude' ':!.agents' ':!CHANGELOG.md' ':!ui/build' || echo "(none)"
