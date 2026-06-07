# SPEC-001 — ui-runtime-vuln-hardening

## 背景

`yarn audit`(2026-06-07)對 `ui/` 回報 415 findings(16 Low / 147 Moderate / 194 High / 58 Critical)。分類後:

- 大多數 critical/high 屬 **build/test-time only**(react-scripts/jest/babel 鏈),不進產出 bundle。
- **runtime 面(真正進到瀏覽器 bundle)的可修項**即本 spec 範圍。
- EOL 框架(CRA、MUI v4、React 16)升級無解,需遷移 → 分屬 SPEC-002/003/004,不在本 spec 範圍。

注意:`ui/build/` 為 repo 內 committed 的 production bundle(`static.go` 經 `go:embed` 內嵌,module 下游與 release binary 都吃這份)——**僅改 package.json/yarn.lock 不重建 bundle 等於沒修**。

## 需求

### REQ-UIVULN-001:runtime 依賴漏洞收斂

修復下列進入 production bundle 的已知漏洞依賴(升版或 yarn resolutions):

| 依賴 | 現況 | 目標 | Advisory |
|---|---|---|---|
| `axios`(direct) | 0.21.2 | 0.32.0(0.x 最新) | CSRF + 8 條 0.x 系列 advisories(audit-before.txt) |
| `prismjs`(via react-syntax-highlighter) | 1.23.0 | ≥1.30.0 | ReDoS、DOM clobbering(CVE-2024-53382) |
| `d3-color`(via recharts 2.1.4) | 2.0.0 | ≥3.1.0(若 build 相容) | ReDoS |
| `decode-uri-component`(via query-string) | 0.2.0 | ≥0.2.1 | DoS |
| `path-to-regexp`(via react-router `^1.7.0`) | 1.8.0 | ≥1.9.0 | backtracking ReDoS |

#### Acceptance Criteria

1. `yarn audit` 中上表 5 個套件的 runtime advisory 全部消失,或在 `review.md` 記錄不可修原因與 residual risk(僅允許 d3-color 一項,條件見 design FMEA)。
2. express 鏈的 `path-to-regexp@0.1.7`(dev-time)**不被** resolution 波及(`yarn.lock` 中該 entry 維持原樣)。
3. 不引入新的 critical/high advisory。

### REQ-UIVULN-002:bundle 重建與內嵌驗證

#### Acceptance Criteria

1. `NODE_OPTIONS=--openssl-legacy-provider yarn build` 成功,產出新 `ui/build/`,並 commit。
2. `go build ./...` + `go vet ./...` + `go test -race -count=1 ./...` 全綠(驗證 `go:embed` 內嵌新 bundle)。
3. 新 bundle 的 JS 中不再含 axios 0.21.x 指紋(以 bundle 內版本字串/`yarn why` 佐證)。

### REQ-UIVULN-003:Go 端 govulncheck pre-push hook(與 asynq fork 治理對齊)

姊妹 fork austinyuch/asynq 已採 `githooks/pre-push` 跑 `govulncheck`、CI 精簡的模型;本 repo 對齊。

#### Acceptance Criteria

1. 新增 `githooks/pre-push`,對 root module 跑 `govulncheck ./...`,非 0 退出即擋 push。
2. `FORK.md` 記錄啟用方式(`git config core.hooksPath githooks`,per-clone 不入版控)。
3. Hook 在本機實際執行一次並通過(當前 `govulncheck`:No vulnerabilities found)。

## 範圍邊界

- **不動**:react-scripts、MUI v4、React 16、react-router-dom 5 本體(→ SPEC-002/003/004)。
- **不處理**:build/test-time only advisories(nth-check、loader-utils、minimist、@babel/traverse、jest 鏈等)——隨 SPEC-002(CRA→Vite)自然消滅。
- **不動**:Dockerfile frontend stage(alpine:3.17/Node 18)——屬 SPEC-002 範圍。

## Impacts

- [Impacts: FORK.md divergence table](新增 UI resolutions 與 githooks 條目)
- 無既有 completed spec;不涉及 Go contract 變更。
