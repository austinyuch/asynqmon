# Go Package Scope Security Review

- **CR**: CR-2026-07-30-004
- **Verdict**: PASS
- **Blocking findings**: 0

## Review

The shared discovery script obtains package identities from a fully successful `go list`, carries them in a Bash array, excludes only the generated `*/node_modules/*` namespace, and fails closed on discovery error or when no owned package remains. It does not evaluate package names as shell code.

`local-ci.sh` uses the resulting array for build, vet, and race tests. `security-local.sh` independently resolves the same current list for govulncheck, so UI installation cannot widen either gate into JavaScript dependency contents.

## Evidence and residual risk

The regression fixtures create an ignored Go package under `ui/node_modules`, retain the module root, assert no excluded package is emitted, and prove a partial discovery failure is rejected. Full local CI and correlated security evidence remain mandatory.

The policy intentionally does not exclude arbitrary generated directories outside `node_modules`; any future generated Go tree needs an explicit ownership decision rather than a broad heuristic.
