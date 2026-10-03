# NEXT_STEPS (rolling operational memo)

- **Classification**: security maintenance verified locally; dev → main promotion authorized on 2026-10-03
- **Active spec / lane**: SPEC-006 dependency security maintenance; Node 24 remains production/CI baseline
- **Current phase**: asynq root/x team.3, Go toolchain 1.26.8 / Node 24.21.0; full local CI passed with 488 SBOM components, 10 UI tests, 0 advisories/HIGH/CRITICAL/KEV/SAST, and govulncheck 0
- **Next action**: complete authorized PR promotion from the security lane to dev, then dev to main; hosted build/E2E and remote readback are integration evidence
- **Operational command**: `make security-refresh`, `make security`, and `make local-ci`
- **Known disposition**: React Router GHSA-qwww-vcr4-c8h2 is limited upstream to unused unstable RSC APIs and remains tracked as not affected in `.security/vex.json`; revisit when a registry-compatible 8.3+ migration is available
- **Blockers**: Podman cleanup requires explicit per-item approval. Local real-data E2E still has no registered asynqmon runtime helper, so hosted workflow remains the non-bypassing path.
- **Resume hint**: current evidence [2026-10-03 security refresh](../../docs/security-refresh-2026-10-03.md); prior completed evidence [CR-2026-07-30-005](./004-ui-react16-to-react18-router6-migration/change-requests/CR-2026-07-30-005.md); Node plan [CR-2026-07-30-006](./002-ui-build-migration-cra-to-vite/change-requests/CR-2026-07-30-006.md)
