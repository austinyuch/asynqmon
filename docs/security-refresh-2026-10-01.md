# Security refresh — 2026-10-01

Historical verification snapshot. Current dependency and integration evidence is in [2026-10-03 refresh](security-refresh-2026-10-03.md); local scanner output paths have since been refreshed.

Dependency upgrades and rebuilt committed UI assets reduce the baseline 42 advisory records (19 HIGH/CRITICAL) to zero detected advisories. No VEX statements were added or broadened.

## Scope

- Go: asynq root/x team.2 → team.3, Redis 9.21.0 → 9.22.0, and compatible Prometheus, atomic, x/sys, x/time and protobuf updates. Go minimum remains 1.26; toolchain directive upgraded to 1.26.8.
- UI: Axios 1.20.0, dayjs 1.11.23, react-window 2.3.3; refresh all lockfile resolutions within existing manifest ranges (including Vite 8.3.2 and Vitest 4.1.11).
- Security resolutions: brace-expansion 5.0.12, js-yaml 4.3.2, postcss 8.5.23, undici 7.29.1, decode-uri-component 0.5.0.
- React 18 and MUI 5 remain the framework baselines. No runtime services or container deployment were started.

## Evidence

`make local-ci` exited 0: Go build/vet/race tests, immutable UI install, lint, 6 unit tests, production bundle and template-token verification, Semgrep, CycloneDX, Trivy, CVE/KEV correlation and govulncheck all passed. Go build/vet/race verification also passed after rebuilding the embedded assets.

Final verified baseline: Go 1.26.8 linux/arm64, Node 24.21.0, Yarn 4.18.0. Full local CI and post-bundle Go build/vet/race checks passed. Browser E2E remains unverified.

The intermediate Go 1.26.5 baseline failed govulncheck with six reachable standard-library advisories: GO-2026-6218, GO-2026-6091, GO-2026-6090, GO-2026-6089, GO-2026-5972 and GO-2026-5026. Upgrading to the official Go 1.26.8 patch release removed all six findings; the downloaded archive was checked against its official SHA-256. Vite, Vitest and Router manifest lower bounds now reflect upgraded versions.

- SBOM: 490 components; zero vulnerabilities and unresolved component references.
- Trivy: zero advisories, zero blocking HIGH/CRITICAL.
- CISA KEV: catalog 2026.09.30, 1730 entries; zero matches. Retrieved 2026-10-01 06:30:56 Asia/Taipei.
- Trivy DB updated at 2026-09-30T19:11:21Z.
- Semgrep: 3 repository rules, 101 scanned targets, zero findings (bounded configured SAST scope).
- govulncheck: zero vulnerabilities across 3 owned Go packages.
- Cross-family review: unavailable; managed xreview doctor reported `policy-not-configured`. No independent-review approval claimed.

Generated evidence is local and ignored under `.local-ci/security/`; this report preserves artifact digests, not copies of the scanner database.

| Artifact | SHA-256 |
|---|---|
| `sbom.cdx.json` | `495258e4c182a3dc935cd1c29acc93ab327a29235d88feb39406ebb34fec74bb` |
| `trivy-vulnerabilities.json` | `5cfd617968e99439c53af0343ba709b34b03fdc79a44b20a02d7d1066efa233b` |
| `cve-kev-correlation.json` | `96df8f99946b7c304f12135473f1e6209d9e7d902932209999b8e3681dc80ec8` |
| `sast-sbom-cve-kev-correlation.json` | `1321f50629fb7d7eab8530f1ec7ff5c261edf9ac5421bf084850cfcd54b94c86` |
| `local-ci-baseline-fixed-2026-10-01.log` | `c71aedc1ad0cd21e60e84912dfaadf0656063d125be6c7ce4da62e6b82f62042` |
| `post-bundle-go-tests-fixed.log` | `f77dfd31b541e226cbacd170ef8fa43ad6ba144a4ee15348d38f85a6fbbe3f3b` |
