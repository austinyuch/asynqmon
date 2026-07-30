# SPEC-006 Design

## Architecture and trust boundary

The new boundary is local developer execution before Git transport:

`explicit KEV refresh → pinned local bytes → fresh Trivy DB → local scan → evidence
receipts → pre-push decision`.

Catalog acquisition and correlation are separate. The refresh script is the
only network-enabled catalog path. The pre-push path consumes pinned bytes and
checks SHA-256 plus freshness. Every ordinary scan refreshes the Trivy
vulnerability DB and fails closed if refresh is unavailable. Trivy owns package discovery and advisory
matching; a small standard-library Python correlator owns exact CVE-to-KEV
matching and policy output. `govulncheck` remains the call-graph-aware Go check.
Tracked VEX statements may mark a precisely identified non-KEV advisory and
package as not affected with a concrete reachability rationale. Exact KEV
matches are never waivable.

## Contract authority

| Contract | Authority | Local representation |
|---|---|---|
| CycloneDX SBOM | OWASP CycloneDX / Trivy output | `.local-ci/security/sbom.cdx.json` |
| CVE/advisory evidence | Trivy DB + Go vuln DB | ignored JSON receipts |
| KEV catalog | CISA JSON feed | catalog bytes + SHA-256 receipt |
| Gate policy | This repository | `security_kev_gate.py` |
| Applicability disposition | This repository | `.security/vex.json` |

No live catalog, clock-selected source, or shell-evaluated finding content is
allowed in the deterministic matching step. A missing catalog is unavailable
evidence, never an empty set.

## Dependency decision

Ponytail Rungs 2–4: use existing Trivy, `govulncheck`, Python stdlib, Git hooks,
and lockfiles. No scanner service or new application dependency is introduced.
Direct upgrades are limited to compatible releases and security-remediation
migrations proven by the existing Go/UI tests and build. React/MUI major
migrations and team-owned `austinyuch/asynq` tags stay outside this spec unless
required to clear a blocking finding.

## Failure and recovery

- Network/catalog failure: preserve the previous known-good snapshot.
- Hash/schema/freshness failure: exit 2 as evidence unavailable.
- HIGH/CRITICAL or KEV match: preserve receipts and exit 1.
- Invalid or over-broad VEX statement: exit 2; KEV remains blocking.
- Tool unavailable: exit 2 with the exact missing tool.
- Bad dependency upgrade: revert only that manifest/lockfile change and retain
  the prior committed embedded bundle; do not bypass the gate.

## FMEA

| Risk | Failure mode | Control | Response | Task |
|---|---|---|---|---|
| LSS-R1 | Missing catalog interpreted as clean | required catalog+receipt | Prevent / fail closed | LSS-T2 |
| LSS-R2 | Catalog tampering or stale bytes | SHA-256 and 7-day age | Detect / exit 2 | LSS-T2 |
| LSS-R3 | GHSA mistaken for KEV-negative CVE | explicit ignored boundary | Contain / disclose | LSS-T2 |
| LSS-R4 | Hook and manual CI drift | one canonical runner | Prevent | LSS-T3 |
| LSS-R5 | UI manifest updated but embedded bundle stale | `yarn build` token gate | Detect | LSS-T4 |
| LSS-R6 | Latest-major migration breaks behavior | compatibility regression suite | Contain / defer | LSS-T4 |
| LSS-R7 | Non-applicable advisory silently ignored | tracked narrow VEX + tests; KEV non-waivable | Contain / disclose | LSS-T4 |

Residual organization-process risks (SLA, ownership, exception approval, and
production operation) remain `missing-evidence`; they do not become implemented
controls merely because this repository gate exists.
