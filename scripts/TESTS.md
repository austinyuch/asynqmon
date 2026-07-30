# scripts TESTS — Local Security and CI

| Test | Command / Evidence | Expected | Spec |
|---|---|---|---|
| SEC-UNIT-001 | `PYTHONPATH=scripts python3 -m unittest -v scripts/test_security_kev_gate.py` | 6/6: exact KEV block, KEV non-waivable, HIGH block, narrow VEX, tamper/stale rejection | SPEC-006 |
| SEC-UNIT-002 | `PYTHONPATH=scripts python3 -m unittest -v scripts/test_security_evidence_correlate.py` | 2/2: SBOM component resolution and KEV/unresolved-ref blocking | SPEC-006 |
| SEC-SAST-001 | `semgrep scan --config .semgrep.yml --error` (via security runner) | 3 rules, 0 blocking findings | SPEC-006 |
| SEC-SBOM-001 | `.local-ci/security/sbom.cdx.json` | CycloneDX JSON generated from Go and Yarn locks | SPEC-006 |
| SEC-CVE-001 | `.local-ci/security/trivy-vulnerabilities.json` + correlation receipt | 1 disclosed RSC-only advisory, 0 blocking HIGH/CRITICAL | SPEC-006 |
| SEC-KEV-001 | `.local-ci/security/cve-kev-correlation.json` | 0 exact CISA KEV matches; catalog hash/schema/freshness valid | SPEC-006 |
| SEC-CORR-001 | `.local-ci/security/sast-sbom-cve-kev-correlation.json` | SAST→SBOM→CVE→KEV links resolve; unresolved refs block | SPEC-006 |
| SEC-GO-001 | `govulncheck $(scripts/go-owned-packages.sh)` via `security-local.sh` | 0 vulnerabilities across module-owned packages; generated dependency trees excluded | SPEC-006 CR-2026-07-30-004 |
| LOCAL-CI-001 | `./scripts/local-ci.sh --full` | Go build/vet/race + UI install/lint/test/build + all security gates pass | SPEC-006 |
| LOCAL-CI-GO-SCOPE-001 | `./scripts/test-go-owned-packages.sh` | module-owned packages retained; `*/node_modules/*` excluded; partial discovery failure rejected | SPEC-006 CR-2026-07-30-004 |

Evidence snapshot: 2026-07-30. Generated `.local-ci/` evidence is deliberately
ignored and must be regenerated; the policy, tests, and VEX disposition are
tracked.
