# CR-2026-07-30-005 Review Evidence

## Verdict

PASS for local implementation and security controls; final hosted build/E2E evidence is required before closure.

## Dependency and warning evidence

- Yarn is project-pinned at 4.18.0 with `nodeLinker: node-modules`; `yarn install --immutable` completes without Yarn Classic `DEP0169`, React peer, or Prism resolution warnings.
- `react-window` is 2.3.0 with its built-in declarations; the obsolete `@types/react-window` package is absent.
- `react-syntax-highlighter` is 16.1.1 and its refractor chain requests the security-pinned PrismJS range.
- GitHub Actions hosted validation exposed Node 20 action-runtime deprecations. Checkout, setup-go, and setup-node were refreshed to their Node 24-backed v6 majors across build, E2E, release, CodeQL, and image workflows.

## Behavior and bundle evidence

- Focused TDD: the new GroupSelect tests failed before the v2 adapter existed, then passed after implementation.
- Vitest: 2 files, 6 tests passed.
- ESLint: 0 errors, 0 warnings.
- TypeScript, Vite build, and Go-template token guard passed.
- Baseline entry JavaScript: 1,244,238 bytes.
- New entry/largest JavaScript chunk: 415,980 bytes (66.6% smaller).
- New aggregate JavaScript: 1,260,924 bytes. This is intentionally disclosed because route splitting improves initial delivery while adding a small chunking overhead.
- Generated `ui/build/` route chunks are committed for the `go:embed` library contract.

## Security and integration evidence

- Correlated local security: 501 CycloneDX components; 1 disclosed RSC-only advisory; 0 HIGH/CRITICAL; 0 KEV; 0 unresolved references; 0 SAST; 0 blocking findings.
- `govulncheck`: no vulnerabilities.
- Exact-clone `scripts/local-ci.sh --full`: passed Go build/vet/race, UI lint/unit/build/token, and correlated security with normal VCS stamping.
- Pre-push full local CI: passed.
- Semantic changed-file review: no new actionable findings. Remaining low-complexity findings in `App` and `Dashboard` predate this CR.
- New-test quality review: 0 findings.
- Full-history gitleaks check: no leaks. A directory scan found only two generated viewer-asset false positives outside tracked source.

## Bounded follow-ups

- Node 26 remains a separate compatibility-only CR (`CR-2026-07-30-006`); Node 24 remains the production and hosted CI baseline.
- The repository has no registered local asynqmon runtime helper, so real-data E2E uses the existing hosted workflow rather than an ad-hoc container.
- Secret scanning is not yet part of the canonical correlated local gate. The one-off full-history proof is recorded here without silently changing the established security contract.

## Hosted failure-driven corrections

- Run `30542886625` failed all seven E2E cases because Vite embedded the Go-only `RootPath` template token inside JavaScript preload URLs. The build now uses relative chunk URLs plus an HTML-only templated `<base>`, and the token gate rejects any future RootPath token in JavaScript.
- Run `30543778947` proved the MIME/chunk failure was gone but exposed React #130 from MUI icons. Package-wide `"type": "module"` had changed CommonJS default interop; ESM is now scoped to `.mjs`/`.mts` config files instead.
- A production-bundle browser probe after the interop correction rendered the application shell and Dashboard without React errors. Only expected API 404s were observed because that diagnostic intentionally did not start a backend.
