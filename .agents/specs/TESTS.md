# Workspace TESTS Rollup — austinyuch/asynqmon

derived snapshot;row-level authority 在各 folder-level `TESTS.md`。

| Folder | Catalog | Rows | Spec Trace | Freshness |
|---|---|---|---|---|
| `ui/` | [ui/TESTS.md](../../ui/TESTS.md) | UI-BUILD/AUDIT/EMBED/UNIT/BUNDLE/TOKEN/E2E/LINT-001 | SPEC-001~005 + CR-2026-07-30-005 | 2026-07-30(CR UI modernization local gates green;hosted final pending)|
| root(Go) | —(無 folder-level TESTS.md;Go 測試由 CI build.yml + githooks/pre-push govulncheck 治理) | `go test -race ./...`、`govulncheck ./...` | PR #1 baseline / SPEC-001 T-5 | 2026-06-07 |
| `scripts/` | [scripts/TESTS.md](../../scripts/TESTS.md) | SEC-UNIT/SAST/SBOM/CVE/KEV/GO + LOCAL-CI/GO-SCOPE | SPEC-006 | 2026-07-30(CR-2026-07-30-004 owned-package scope) |
