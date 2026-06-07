# SPEC-002 — ui-build-migration-cra-to-vite

**Status: Pending Implementation(authoring only)**

## 背景

`react-scripts`(Create React App)已於 2025 正式 sunset,**永遠不會再有 security patch**——這是「升級也救不了」的第一類依賴。SPEC-001 後殘餘的 376 個 yarn audit findings(含全部 58 critical)幾乎全數來自 CRA 的 build/test 鏈(webpack4、jest、babel loaders);最終版 react-scripts 5.0.1 仍 pin 有漏洞的 webpack-dev-server 4。唯一出路是遷移 build 工具鏈,本 spec 選 **Vite**。

連帶可移除的技術債:
- `NODE_OPTIONS=--openssl-legacy-provider` workaround(Dockerfile、release.yml、本機 build)
- Dockerfile frontend stage 的 `alpine:3.17`/Node 18 EOL pin(可升現代 Node LTS)

## 需求

### REQ-VITE-001:build 工具鏈遷移

#### Acceptance Criteria

1. `ui/` 以 Vite(最新 stable)+ `@vitejs/plugin-react` 完成 production build,移除 `react-scripts` 依賴。
2. 產出目錄維持 `ui/build/`(`vite.config.ts` 設 `build.outDir: "build"`),`static.go` 的 `go:embed` 與 `index.html` 服務路徑**不需改動**;Go 端 `go build && go test -race ./...` 綠。
3. CRA 慣例完成轉換:`public/index.html` → root `index.html`(`%PUBLIC_URL%` → Vite base);`REACT_APP_*` env → `import.meta.env.VITE_*`;CRA `homepage: "/[[.RootPath]]"`(Go template 注入的 base path)等價遷移為 Vite `base` 設定,並驗證子路徑部署情境。
4. `yarn audit`(或 npm audit)critical/high 較 SPEC-001 後基準(58 critical / 174 high)下降 ≥90%;殘餘項逐條列入 review.md。
5. 不再需要 `--openssl-legacy-provider`;Dockerfile frontend stage 與 release.yml 改用現役 Node LTS。

### REQ-VITE-002:test runner 遷移

#### Acceptance Criteria

1. jest(react-scripts 內建)→ Vitest;既有測試(如有)全數通過或明確記錄汰除原因。
2. `ui/TESTS.md` 更新 canonical commands。

### REQ-VITE-003:TypeScript 與 lint 鏈

#### Acceptance Criteria

1. TS 4.9 在 Vite 下可過;eslint 由 `eslint-config-react-app` 改為 Vite 生態等價配置。

## 範圍邊界

- **不動** React 16 / MUI v4 / react-router 5 本體(SPEC-003/004);Vite 4.x 對 React 16 相容性需在 design 階段驗證(spike),若 Vite 最新版要求更高,允許先落在相容版本並記錄。
- 遷移後建立 E2E smoke(Playwright 對 real backend)為 stretch goal,供 SPEC-003/004 回歸使用。

## Impacts

- [Impacts: Dockerfile frontend stage]、[Impacts: .github/workflows/release.yml]、[Impacts: FORK.md divergence table]、[Impacts: ui/TESTS.md]
- 建議執行順序:**SPEC-002 最先**(獨立於框架升級,且為 003/004 提供現代化驗證環境)。
