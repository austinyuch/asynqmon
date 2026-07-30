# NEXT_STEPS (rolling operational memo)

- **Classification**: completed-baseline CR overlay against SPEC-002/004/005/006
- **Active spec / lane**: CR-2026-07-30-005 UI modernization; CR-2026-07-30-006 Node 26 compatibility is planned separately
- **Current phase**: implementation complete for Yarn 4, dependency migrations, and route splitting; exact-clone local CI, review, hosted E2E, and governance closeout remain
- **Next action**: commit the implementation with CR trace, run canonical full local CI in an exact clone, then dispatch hosted build/E2E without opening a PR
- **Operational command**: `make security-refresh`, `make security`, and `make local-ci`
- **Known disposition**: React Router GHSA-qwww-vcr4-c8h2 is limited upstream to unused unstable RSC APIs and remains tracked as not affected in `.security/vex.json`; revisit when a registry-compatible 8.3+ migration is available
- **Blockers**: linked worktrees cannot preserve normal Go VCS stamping on this host because their `.git` file falls through to an outer Git repository; exact-clone verification is the approved evidence path. Local real-data E2E has no asynqmon registry entry/helper, so hosted workflow dispatch is the non-bypassing runtime path.
- **Resume hint**: CR implementation/tasks [CR-2026-07-30-005](./004-ui-react16-to-react18-router6-migration/change-requests/CR-2026-07-30-005.md); Node plan [CR-2026-07-30-006](./002-ui-build-migration-cra-to-vite/change-requests/CR-2026-07-30-006.md)
