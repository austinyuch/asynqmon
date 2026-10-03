# Security refresh — 2026-10-03

## Result

Go 1.26.8 / Node 24.21.0 full local CI passed after dependency upgrades and rebuilding committed embed assets. Ten UI tests passed. CycloneDX contains 488 components; Trivy advisories, blocking HIGH/CRITICAL, CISA KEV matches, Semgrep findings and reachable Go vulnerabilities are all zero. Go build/vet/race tests passed again against the final embedded UI.

## Change and compatibility

- Go toolchain 1.26.4 → 1.26.8; minimum module version remains 1.26.0. An intermediate 1.26.5 check found six reachable standard-library advisories, eliminated by 1.26.8.
- asynq root/x team.2 → team.3, go-redis 9.21.0 → 9.22.0, plus compatible Prometheus, atomic, x/sys, x/time and protobuf updates.
- Axios 1.20.0, dayjs 1.11.23, react-window 2.3.3; existing-range UI lockfile refresh includes Vite 8.3.2, Vitest 4.1.11 and Router 7.18.4. React 18 / MUI 5 remain the framework baselines.
- Security overrides: brace-expansion 5.0.12, js-yaml 4.3.2, postcss 8.5.23, undici 7.29.1, decode-uri-component 0.5.0.
- query-string 7.0.1 → 9.5.1 fixes CommonJS/ESM decoder incompatibility introduced by the secure decoder upgrade. Existing code only stringifies, so the old parse mismatch was a latent risk. Four new tests verify API pagination, metrics escaping/omission and decoder loading.
- No VEX statement was added or broadened; final zero-advisory result does not depend on VEX exceptions.

## Evidence and limits

Canonical gate: `make local-ci`, with Go 1.26.8 linux/arm64, Node 24.21.0 and Yarn 4.18.0. Template-token gate passed. Semgrep uses three configured repository rules; it is bounded SAST evidence. Same-family independent read-only inspection confirmed decoder compatibility and test scope. Cross-family xreview remains unavailable (`policy-not-configured`); no cross-family approval is claimed. No local runtime service or container deployment was started. Hosted PR E2E is the integration check, with completion reported separately.

CISA KEV catalog `2026.10.02` contains 1733 entries, fetched `2026-10-03T01:42:27Z`; SHA-256 `d2c8c6cb23291b46ff2b086197641a6b1fa35e6b746bba714cc280a1778f9e48`. Trivy DB updated `2026-10-02T19:00:34Z`.

Snapshot artifacts are ignored under `.local-ci/security/snapshots/2026-10-03/`; SHA-256 receipts below bind the pre-commit verification snapshot. Exact-commit pre-push verification and hosted runs are separate integration evidence.

| Artifact | SHA-256 |
|---|---|
| `sbom.cdx.json` | `b38b7c7f6f0e14cbbd5a71950e020454a788fe8c2334851b399eefb674c6c0d6` |
| `trivy-vulnerabilities.json` | `e2abf8373981f12528dfe3c6de9bb416cef62db45c03a817a1a28329eeee34df` |
| `cve-kev-correlation.json` | `427b01042a7d3d6690b3e1de049c5aba498264f03bcbeeb402e1a0592e148082` |
| `sast-sbom-cve-kev-correlation.json` | `b11c4662545bea8c92c33e343b70a9f9e8cc3687b37efcfff6de4fa2d1796771` |
| `local-ci-final-2026-10-03.log` | `a59cabe94f1d2e0ca8b68423104b938a66acee65c5cebeccd0c7e62bdd40b4fa` |
| `post-bundle-go-tests-2026-10-03.log` | `9ab73ffaf919d1b0d56c56860a88b03ed7dea0bd0dda04c794eabcd92b68156f` |
