# SPEC-006 — Local Supply-Chain Security

## Introduction

This brownfield security change is required by the user request to shift SBOM,
CVE, and CISA Known Exploited Vulnerabilities (KEV) detection into the local
developer loop. The existing pre-push hook only executes `govulncheck` and does
not inventory the UI dependency graph or prioritize known exploitation.

Ponytail Rung 1: a repo-local gate is necessary because the primary artifact is
a Go library with an embedded, committed UI bundle; hosted CI alone cannot
guarantee that the bundle and lockfile were validated before push.

## Dependencies, Impacts, and Change Requests

- [Depends On: SPEC-001 dependency security baseline]
- [Impacts: SPEC-004 React Router 6 baseline]
- [Open Change Requests: none; SPEC-006 owns the new current baseline]
- External contracts: CISA KEV JSON feed, Trivy vulnerability database,
  Go vulnerability database, npm registry, and Go module proxy.

## Adaptive Execution Plan

- Profile: `default`
- Depth: `comprehensive`
- Signals: infrastructure trust boundary, external vulnerability catalogs,
  dependency migrations, committed embedded bundle, fail-closed local hook
- Mandatory gates: TDD, Go/UI regression, CycloneDX token validation,
  CVE/KEV policy, security review, dependency compatibility, traceability

## Repo-side Closure vs External Execution

- **Repo-side closure:** scripts, deterministic KEV correlation, tests, local
  evidence output, dependency/lockfile updates, rebuilt `ui/build`, and hook
  activation.
- **External execution:** hosted CI and PR merge remain owner-operated.
- **External constraint:** `origin/dev` is eight commits behind `origin/main`;
  branch reconciliation must precede a PR to `dev`.

## Security and compliance intake

- Lifecycle posture: material brownfield CI/supply-chain change.
- Repository evidence: lockfiles, CodeQL, `govulncheck` hook, and prior audit
  baselines exist; SBOM and KEV evidence were absent.
- Assumed baseline: ISO/IEC 27002:2022 control 8.9 configuration management and
  8.28 secure coding support local component inventory and vulnerability gates.
- Missing organization evidence: ISMS scope, SoA/equivalent, risk methodology,
  vulnerability SLA, supplier policy, incident process, and named risk owner
  were not supplied. This spec is not an ISO/CNS certification or legal verdict.

## Requirements

### REQ-LSS-001 — Local SBOM and CVE evidence

**User story:** As a developer, I want the full Go and UI dependency graph
scanned locally so that vulnerable embedded components are detected before push.

#### Acceptance Criteria

1. When the security gate runs, it shall create a valid CycloneDX JSON SBOM and
   a machine-readable Trivy vulnerability report under ignored `.local-ci/`.
2. When any HIGH or CRITICAL advisory is present, the gate shall exit non-zero
   and preserve the evidence receipt.
3. If Trivy, `govulncheck`, or required evidence is unavailable, the gate shall
   fail closed rather than report a clean result.

### REQ-LSS-002 — Pinned CISA KEV correlation

**User story:** As a security owner, I want exact CVE IDs matched against a
pinned CISA KEV snapshot so that known exploitation receives priority.

#### Acceptance Criteria

1. When catalogs are refreshed explicitly, the acquisition command shall
   validate the CISA schema, record source/time/SHA-256, and replace files
   atomically.
2. When the ordinary local gate runs, it shall perform no catalog network fetch
   and shall reject missing, tampered, malformed, future-dated, or older-than-7
   day KEV evidence.
3. When any exact CVE ID matches KEV, the gate shall exit non-zero and disclose
   the match; non-CVE advisory IDs shall remain explicitly outside KEV alias
   resolution.

### REQ-LSS-003 — Shift-left activation

**User story:** As a maintainer, I want one canonical local-CI command wired to
pre-push so that build, test, SBOM, CVE, and KEV checks cannot silently drift.

#### Acceptance Criteria

1. When `scripts/local-ci.sh --full` or `--pre-push` runs, it shall execute Go
   build/vet/race tests, UI frozen install/lint/unit/build, and the security gate.
2. When Git invokes `githooks/pre-push`, it shall call that canonical runner.
3. When UI sources or dependencies change, the runner shall rebuild and verify
   the committed `ui/build` Go-template tokens.

### REQ-LSS-004 — Applicable dependency upgrades

**User story:** As a maintainer, I want dependencies upgraded to the newest
applicable compatible releases so that known fixable vulnerabilities are
removed without silently changing externally owned fork contracts.

#### Acceptance Criteria

1. When a current-line patch/minor or compatible major fixes a discovered
   vulnerability, the manifest and lockfile shall be upgraded and regression
   gates shall pass.
2. When a latest major requires a distinct framework migration or changes a
   team-fork contract, it shall be deferred with rationale rather than forced
   into this security slice.
3. After dependency changes, the Trivy HIGH/CRITICAL count and KEV match count
   shall both be zero before a PASS verdict.
