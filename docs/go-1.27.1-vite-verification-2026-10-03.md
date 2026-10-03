# Go 1.27.1 / latest Vite verification — 2026-10-03

## Result and changes

Go minimum upgraded to 1.27.1; CI build/E2E/release uses exact 1.27.1 and Docker backend uses golang:1.27.1-alpine. This intentionally raises the minimum version for library consumers. `go mod tidy` removes the redundant equal-version toolchain directive.

npm registry returned latest stable Vite 8.3.2. The existing lockfile already resolved 8.3.2; the manifest lower bound is now ^8.3.2 and the production bundle was rebuilt successfully without asset drift. Node remains 24.21.0. Compatible Go-owned-package/test dependencies and existing-range UI resolutions were refreshed; no further package version changes were required.

Fixed the ESLint Node-globals override to match the real vite.config.mts as well as vite.config.ts. The prior mismatch was configuration drift, not proof that the file was excluded from lint.

## Verification

- Go 1.27.1 linux/arm64, Node 24.21.0, Yarn 4.18.0 full canonical `make local-ci`: pass.
- Go build/vet/race checks; UI immutable install/lint, 10 unit tests, production build and Go template tokens: pass.
- CycloneDX: 488 components, zero vulnerabilities or unresolved references.
- Trivy CVE/advisory and KEV correlation: zero findings.
- Semgrep: zero findings/errors under the three configured repository rules; bounded SAST scope, separate from SCA/SBOM.
- govulncheck: zero reachable vulnerabilities across three owned Go packages.
- GitHub CodeQL open alerts API: zero open alerts at query time. This is an existing-alert inventory, not a new CodeQL analysis of unpushed changes.
- No new suppressions or VEX statements. No runtime service, image publication or container build was performed; the Docker change is source configuration evidence only.
- Same-family read-only inspection covers version surfaces and lint configuration; cross-family approval remains unclaimed (no xreview policy).

Hosted build/E2E and exact-commit promotion evidence are reported separately after PR checks. Local snapshot artifacts are retained under `.local-ci/security/snapshots/go127-2026-10-03/`.

| Artifact | SHA-256 |
|---|---|
| `sbom.cdx.json` | `a23671fd785b881db2cd853db2238293860a47708d738d58603d180c59ff8de3` |
| `trivy-vulnerabilities.json` | `9d5ab2424206d25ab18c12d7fd3c40b6823b2cac6c8795526fd619cff0af1d04` |
| `cve-kev-correlation.json` | `427b01042a7d3d6690b3e1de049c5aba498264f03bcbeeb402e1a0592e148082` |
| `sast-sbom-cve-kev-correlation.json` | `b11c4662545bea8c92c33e343b70a9f9e8cc3687b37efcfff6de4fa2d1796771` |
| `semgrep.json` | `40482deffffd8499cbe533087cf0f96625fe00b961b264bfc0806cdb7c1414c5` |
| `go127-local-ci.log` | `5a8ada12dfb051319311debaff6c6e15e12cafc444af445913017047e0f3664f` |
| `codeql-open-alerts-go127.jsonl` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
