# NEXT_STEPS (rolling operational memo)

- **Classification**: SPEC-001~006 and closed CRs are complete; no active implementation lane
- **Active spec / lane**: none after CR-2026-07-30-003 promotion
- **Current phase**: `SplitButton` React ref correctness warning resolved; `main` and `dev` synchronized after promotion
- **Next action**: rank the remaining dependency peer mismatch, tooling warnings, and bundle-size posture before opening another CR
- **Operational command**: `make security-refresh`, `make security`, and `make local-ci`
- **Known disposition**: React Router GHSA-qwww-vcr4-c8h2 is limited upstream to unused unstable RSC APIs and remains tracked as not affected in `.security/vex.json`; revisit when a registry-compatible 8.3+ migration is available
- **Blockers**: none
- **Resume hint**: registry [SPECS.md](./SPECS.md); resolved history [ISSUE_LOG.md](./ISSUE_LOG.md); traceability [RTM.md](./RTM.md)
