---
name: local-image-publish-governance
description: 治理「本地發布 container image」的 build → verify → label → tag 規則。當使用者要把專案 build 成 image 留在本機給其他專案/環境使用、提到「發布 image」「打包成 image」「podman build / docker build 給本地用」「tag 到 local namespace」「localhost/local/...」,或要產出可追溯(知道從哪個 commit 建的)的本地 image 時使用——即使使用者只說「幫我 build 一版 image」。不適用於:推送遠端 registry(Docker Hub/GHCR,走專案 CI)、清理舊 images(container-image-janitor)、起容器跑服務(local-infra-registry-governance)。
---

# Local Image Publish Governance

本地發布的 image 是「無人記得來歷的二進位物」高風險區:三個月後沒人知道 `myapp:latest` 是哪個 commit、哪個架構、能不能重建。這個 skill 用固定的 pipeline 把來歷釘進 image 本身(OCI labels + 確定性 tags),並在發布前擋掉最常見的兩種壞品:架構錯誤與起不來的 entrypoint。

## 與相鄰 skills 的邊界

| 需求 | 歸屬 |
|---|---|
| build / tag / 本地發布規則 | **本 skill** |
| 清理舊 images、保留最新 N 版 | `container-image-janitor`(本 skill 永不刪 image) |
| 起容器、port / network / instance 分配 | `local-infra-registry-governance`(本 skill 的 smoke 不映射 port、不長駐) |
| compose / rootless 實作細節 | `devops-container-orchestration` |
| 推送遠端 registry | 專案 CI workflow,不在本 skill 範圍 |

## 命名與 tag 規則

- **Namespace**:本地發布一律落在 `localhost/local/<name>`。`<name>` 用 repo 名(或 local-infra registry 的 canonical project 名,若兩者不同以後者為準)。裸名(`myapp`)只可作為 build 過程的暫時 tag,不可作為發布終態。
- **每次發布雙 tag**:
  - `g<short-sha>`(必有;worktree 髒時為 `g<short-sha>-dirty`)——確定性、不可重用:同名 tag 重 build 必須內容相同,否則用新 sha
  - `latest`(可選 alias,預設給)——僅作便利指標,消費端要可追溯時應改用 sha tag
  - 若 repo 有 release tag(`git describe --exact-match`),額外打 `<version>` tag
- **dirty 發布**是允許的(開發迭代常態),但必須帶 `-dirty` 後綴 + label 註記,不可偽裝成乾淨建置。

## 必要 OCI labels

每次發布必須帶齊(由 script 自動注入,不要手填):

- `org.opencontainers.image.source`(repo URL,取 origin remote)
- `org.opencontainers.image.revision`(full sha,dirty 時加 `-dirty`)
- `org.opencontainers.image.created`(RFC3339 UTC)
- `org.opencontainers.image.title`(`<name>`)
- `org.opencontainers.image.version`(同主 tag)

之後 janitor 盤點或任何人 `inspect` 都能直接回答「這顆是哪裡來的」。

## 發布 pipeline(前一步未過不可進下一步)

優先執行 bundled script(它把以下 gates 做成 fail-closed):

```bash
bash .agents/skills/local-image-publish-governance/scripts/publish_local_image.sh \
  --name <name> [--context <dir>] [--containerfile <path>] \
  [--smoke-arg --help] [--smoke-expect 0] [--no-latest]
```

script 不適用時(特殊 build args、multi-stage 客製),手動依序執行同樣的 gates:

1. **Runtime 選擇**:偏好 podman(rootless);沒有才用 docker。不要混用兩邊的 image store 還以為是同一份。
2. **來歷採集**:git sha / dirty 狀態 / origin URL。不在 git repo 內 → 停下回報,不發布無來歷 image。
3. **Build**:帶上述 labels;Containerfile 應使用 `TARGETOS`/`TARGETARCH` 而非寫死架構。
4. **架構驗證**:`inspect .Architecture` 必須等於 host(或明確指定的 `--platform`)。錯架構是本規則誕生的實際事故(寫死 `GOARCH=amd64` 在 arm64 機器產出跑不動的 image)。
5. **Smoke**:`run --rm <image> <smoke-arg>` 退出碼等於宣告值(預設 0)。注意 **Go flag package 的 `--help` 慣例是 exit 2**——Go binary 請帶 `--smoke-expect 2`;這是本 skill 首次實測就踩到的坑。無害、不開 port、不長駐——所以不需要走 infra registry;若 smoke 需要真實依賴(DB/queue),那已超出發布驗證,改走 `local-infra-registry-governance` 做正式 E2E。
6. **Tag & 發布**:打 `localhost/local/<name>:g<sha>[-dirty]`(+ `latest` / version),移除暫時 build tag。
7. **回報**:image 名、全部 tags、arch、size、revision、smoke 結果。發布後若同名舊版累積,提示使用者可用 `container-image-janitor` 盤點——不要自行動手刪。

## 常見錯誤

- **只打 `latest` 就收工** → 三個月後無法回答「現在跑的是哪版」。sha tag 不是選配。
- **smoke 失敗還是 tag 出去**「反正只是本地」 → 本地 image 正是會被別的專案直接引用的,壞品擴散更快。
- **在 skill 裡順手清舊 image** → 刪除有自己的審核流程(janitor 的 CSV 核准制),發布流程不碰。
- **把 image 清單寫進 SPECS.md / NEXT_STEPS.md** → image store + labels 就是 inventory 的 SSOT,治理文件不存 runtime 狀態。
