# SPEC-002 Design — ui-build-migration-cra-to-vite

## 現況盤點(2026-06-07)

| CRA 接點 | 現況 | 遷移策略 |
|---|---|---|
| `public/index.html` + `%PUBLIC_URL%` | favicon/manifest 連結 + `window.FLAG_ROOT_PATH = "%PUBLIC_URL%"`(CRA homepage=`/[[.RootPath]]` 注入) | 移至 `ui/index.html`,`%PUBLIC_URL%` 全部改寫為字面 `/[[.RootPath]]`;入口 `<script type="module" src="/src/index.tsx">` |
| Go template | `static.go` 用自訂分隔符 **`/[[` `]]`**,`handler.go` `//go:embed ui/build/*`,`staticDirPath: "ui/build"` | Go 端**零改動**;Vite `build.outDir: "build"`、`base: "/[[.RootPath]]/"` |
| SVG as ReactComponent | `App.tsx` 兩處(logo) | `vite-plugin-svgr`,import 改 `?react` 後綴 |
| `process.env.NODE_ENV` | `api.ts` | Vite 內建 define,免改 |
| `serviceWorker.ts` | 只呼叫 `unregister()`(CRA PWA 遺骸,從未 register) | 刪檔 + 移除 `index.tsx` 呼叫 |
| `react-app-env.d.ts` | `/// <reference types="react-scripts" />` | 改 `vite/client` + `vite-plugin-svgr/client` |
| `App.test.tsx` | CRA boilerplate「learn react link」——**現狀即失敗**(App 無此文案,CI 從未跑) | 汰除;以 `parseFlags.test.ts`(真實 util,jsdom)取代,跑 Vitest |
| `eslintConfig: react-app` / `browserslist` / `homepage` | package.json | 移除(base 改由 vite.config 承載;esbuild target 取代 browserslist) |
| React 16.14.0(lockfile) | 支援 automatic JSX runtime | `@vitejs/plugin-react` 預設即可 |

## 關鍵風險:Go template token 的 URL-safe 性

CRA/webpack 把 `homepage` 原樣寫進 asset URL(`/[[.RootPath]]/static/js/...`)。Vite 的 `base` 處理可能把 `[` `]` encode 成 `%5B%5D`,會讓 Go template(分隔符 `/[[`)找不到 action → RootPath 不被替換 → **整個 UI 在子路徑部署下 404**。

**Mitigation(FMEA R-1)**:
- Prevent:自訂 Vite plugin `goTemplateBaseGuard`(`transformIndexHtml` 階段把 `%5B%5B`→`[[`、`%5D%5D`→`]]` 還原,idempotent)
- Detect:post-build 驗證 gate——比對 `build/index.html` 必含 `"/[[.RootPath]]"`(FLAG 行)與 `/[[.RootPath]]/assets/`(asset 前綴),且不含 `%5B`;Go 端 `go test`(embed 重編)
- 驗證 gate 寫入 `package.json` `build` script 鏈(`yarn build` 即跑)

## Lightweight FMEA

| Risk ID | Failure Mode | Effect | Control / Response | Sev | Occ | Det | Task Trace |
|---|---|---|---|---|---|---|---|
| R-1 | Vite encode `[[ ]]` | RootPath 不替換,子路徑部署全壞 | 如上(plugin + post-build gate) | 高 | 中 | 低→高(gate 後) | T-2, T-4 |
| R-2 | SPA fallback 失效:Vite hash 資產路徑改變(`static/` → `assets/`) | 深層路由 refresh 404 | `serveFile` 對任意 path 走 embed FS,目錄名無 hardcode(已盤點);Go test + 指紋驗證 | 中 | 低 | 高 | T-4 |
| R-3 | React 16 + 最新 plugin-react 不相容 | build 失敗 | spike 先行(T-1);若 Vite 7 不可行,允許降至相容 major 並記錄 | 中 | 低 | 高 | T-1 |
| R-4 | audit 殘餘不降反升(vite 鏈自身 advisory) | AC4 不達標 | post-audit 比對;Vite 鏈是活的(有 patch 出路),逐條列 review.md | 低 | 低 | 高 | T-5 |
| R-5 | dev server(`yarn start`→`vite`)proxy 行為差異 | 開發流程中斷 | `server.proxy` 把 `/api` 轉 `localhost:8080`(對齊 api.ts dev 分支行為);煙測非 gate(dev-only) | 低 | 中 | 中 | T-3 |

## 新依賴(devDependencies)

`vite`、`@vitejs/plugin-react`、`vite-plugin-svgr`、`vitest`、`jsdom`;移除 `react-scripts`、`@types/jest`。
`@testing-library/*` 保留(後續 SPEC-003/004 回歸用)。

## Scripts

```json
"start": "vite",
"build": "tsc --noEmit && vite build && node scripts/verify-go-template-tokens.mjs",
"test": "vitest run",
"preview": "vite preview"
```
