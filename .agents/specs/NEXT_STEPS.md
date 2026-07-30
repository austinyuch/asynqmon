# NEXT_STEPS (rolling operational memo)

- **Classification**: completed UI modernization CR; separate compatibility and operator-approval follow-ups
- **Active spec / lane**: CR-2026-07-30-006 Node 26 compatibility is planned separately; Node 24 remains production/CI baseline
- **Current phase**: CR-2026-07-30-005 completed; exact-clone full local CI, correlated security, semantic review, hosted build, and real-data E2E 7/7 are green
- **Next action**: open the separate Node 26 compatibility lane when scheduled; review `temp/container-image-inventory-2026-07-30.csv` and explicitly approve individual Podman cleanup rows before any deletion
- **Operational command**: `make security-refresh`, `make security`, and `make local-ci`
- **Known disposition**: React Router GHSA-qwww-vcr4-c8h2 is limited upstream to unused unstable RSC APIs and remains tracked as not affected in `.security/vex.json`; revisit when a registry-compatible 8.3+ migration is available
- **Blockers**: Podman cleanup requires explicit per-item approval. Local real-data E2E still has no registered asynqmon runtime helper, so hosted workflow remains the non-bypassing path.
- **Resume hint**: completed evidence [CR-2026-07-30-005](./004-ui-react16-to-react18-router6-migration/change-requests/CR-2026-07-30-005.md); Node plan [CR-2026-07-30-006](./002-ui-build-migration-cra-to-vite/change-requests/CR-2026-07-30-006.md)
