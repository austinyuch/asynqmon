# NEXT_STEPS (rolling operational memo)

- **Classification**: completed UI modernization and asynq team.2 dependency security release; separate compatibility and operator-approval follow-ups
- **Active spec / lane**: CR-2026-07-30-006 Node 26 compatibility is planned separately; Node 24 remains production/CI baseline
- **Current phase**: asynq root/x pins advanced to team.2 with Go 1.26 minimum; full local CI passed with 501 SBOM components, 0 HIGH/CRITICAL, 0 KEV, 0 SAST, and govulncheck 0
- **Next action**: open the separate Node 26 compatibility lane when scheduled; review `temp/container-image-inventory-2026-07-30.csv` and explicitly approve individual Podman cleanup rows before any deletion
- **Operational command**: `make security-refresh`, `make security`, and `make local-ci`
- **Known disposition**: React Router GHSA-qwww-vcr4-c8h2 is limited upstream to unused unstable RSC APIs and remains tracked as not affected in `.security/vex.json`; revisit when a registry-compatible 8.3+ migration is available
- **Blockers**: Podman cleanup requires explicit per-item approval. Local real-data E2E still has no registered asynqmon runtime helper, so hosted workflow remains the non-bypassing path.
- **Resume hint**: completed evidence [CR-2026-07-30-005](./004-ui-react16-to-react18-router6-migration/change-requests/CR-2026-07-30-005.md); Node plan [CR-2026-07-30-006](./002-ui-build-migration-cra-to-vite/change-requests/CR-2026-07-30-006.md)
