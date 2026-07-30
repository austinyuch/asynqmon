# SPEC-006 Readiness Review

## Verdict

PASS. The security baseline was merged to `dev` by PR #24 and promoted to
`main` by PR #25. Later closed CRs preserve the same local/hosted security
baseline.

## Security review

- Reviewed trust boundary: developer working tree → local scanners/catalogs →
  pre-push allow/deny decision.
- Confirmed issues: none remaining.
- Acceptable with rationale: GHSA-qwww-vcr4-c8h2 is present in React Router
  7.18.2 but the upstream advisory limits impact to unstable RSC APIs. This
  client-only Vite SPA uses BrowserRouter and no RSC API. The exact
  advisory/package disposition is tracked in `.security/vex.json`; an exact
  CISA KEV match cannot be waived.
- Closeout verification: local correlated security, pre-push full CI, hosted
  build/E2E, and promotion CodeQL all passed; `main` and `dev` were synchronized.
- Risk-registry handoff: not-required. No target-applicable HIGH/CRITICAL or
  KEV finding remains.

## Evidence

- `./scripts/local-ci.sh --full`: PASS.
- Go build, vet, race tests: PASS.
- UI frozen install, lint, Vitest 3/3, TypeScript, Vite build, Go-template
  token gate: PASS (0 lint errors / 0 rule warnings after CR-2026-07-30-003).
- Semgrep: 3 rules across Go/JS/TS/Python, 0 findings.
- CycloneDX: generated, 486 components.
- Trivy: 1 disclosed advisory, 0 blocking HIGH/CRITICAL.
- CISA KEV: 0 exact matches; snapshot schema, SHA-256, and freshness validated.
- Combined SAST/SBOM/CVE/KEV: 486 components, 1 component advisory fully
  resolved, 0 unresolved references, 0 SAST findings, 0 KEV, 0 blocking.
- `govulncheck` across the module-owned Go package allowlist: no vulnerabilities;
  `*/node_modules/*` generated dependency packages are excluded by
  CR-2026-07-30-004.
- KEV/VEX and evidence-correlation unit suites: 8/8 PASS.

## Dependency and runtime decision

Applicable Go and UI dependencies were upgraded and `ui/build/` rebuilt.
Node 24 is selected for workflows/container builds because it is the current
LTS production line. Node 26 is technically usable with Vite 8 but remains the
Current line until its scheduled LTS transition; this lane does not make a
pre-LTS runtime the production baseline.
