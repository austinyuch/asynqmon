# NEXT_STEPS (rolling operational memo)

- **Classification**: SPEC-001~006 and closed CRs are complete; no active implementation lane
- **Active spec / lane**: none
- **Current phase**: SPEC-006 merged by PR #24 and promoted by PR #25; `main` and `dev` are synchronized
- **Next action**: run evidence-backed next-gap ranking from completed reviews, test warnings, dependency posture, and current code before opening another spec
- **Operational command**: `make security-refresh`, `make security`, and `make local-ci`
- **Known disposition**: React Router GHSA-qwww-vcr4-c8h2 is limited upstream to unused unstable RSC APIs and remains tracked as not affected in `.security/vex.json`; revisit when a registry-compatible 8.3+ migration is available
- **Blockers**: none
- **Resume hint**: registry [SPECS.md](./SPECS.md); resolved history [ISSUE_LOG.md](./ISSUE_LOG.md); traceability [RTM.md](./RTM.md)
