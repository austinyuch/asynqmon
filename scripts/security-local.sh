#!/usr/bin/env bash
# Offline-by-default local supply-chain gate: SBOM, CVE scan, and CISA KEV match.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
evidence_dir="${repo_root}/.local-ci/security"
catalog_dir="${evidence_dir}/catalogs"
trivy_cache="${TRIVY_CACHE_DIR:-${evidence_dir}/trivy-cache}"
export SEMGREP_SETTINGS_FILE="${SEMGREP_SETTINGS_FILE:-${evidence_dir}/semgrep-settings.yml}"
export SEMGREP_LOG_FILE="${SEMGREP_LOG_FILE:-${evidence_dir}/semgrep.log}"
export SEMGREP_SEND_METRICS=off
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-${repo_root}/.local-ci/cache}"
refresh_catalogs=false

if [[ "${1:-}" == "--refresh-catalogs" ]]; then
  refresh_catalogs=true
elif [[ "$#" -ne 0 ]]; then
  echo "usage: scripts/security-local.sh [--refresh-catalogs]" >&2
  exit 2
fi

for tool in trivy govulncheck python3 semgrep; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "security local: required tool unavailable: ${tool}" >&2
    exit 2
  fi
done

mkdir -p "${evidence_dir}" "${trivy_cache}"
if "${refresh_catalogs}"; then
  "${repo_root}/scripts/security-update-catalogs.sh"
fi

catalog="${catalog_dir}/known_exploited_vulnerabilities.json"
receipt="${catalog_dir}/known_exploited_vulnerabilities.receipt.json"
if [[ ! -s "${catalog}" || ! -s "${receipt}" ]]; then
  echo "security local: KEV snapshot unavailable; run:" >&2
  echo "  scripts/security-local.sh --refresh-catalogs" >&2
  exit 2
fi

echo "security local: refreshing Trivy vulnerability database (fail closed)"
trivy image --download-db-only --no-progress --cache-dir "${trivy_cache}"

echo "security local: Semgrep SAST"
(cd "${repo_root}" && semgrep scan --config .semgrep.yml --error --json \
  --output "${evidence_dir}/semgrep.json")

echo "security local: generating CycloneDX SBOM"
trivy fs \
  --scanners vuln \
  --include-dev-deps \
  --skip-db-update \
  --skip-version-check \
  --skip-dirs "${repo_root}/.local-ci" \
  --skip-dirs "${repo_root}/ui/node_modules" \
  --no-progress \
  --cache-dir "${trivy_cache}" \
  --format cyclonedx \
  --output "${evidence_dir}/sbom.cdx.json" \
  "${repo_root}"

echo "security local: scanning CVEs and advisories"
trivy fs \
  --scanners vuln \
  --include-dev-deps \
  --skip-db-update \
  --skip-version-check \
  --skip-dirs "${repo_root}/.local-ci" \
  --skip-dirs "${repo_root}/ui/node_modules" \
  --no-progress \
  --cache-dir "${trivy_cache}" \
  --format json \
  --output "${evidence_dir}/trivy-vulnerabilities.json" \
  "${repo_root}"

python3 "${repo_root}/scripts/security_kev_gate.py" \
  --trivy-report "${evidence_dir}/trivy-vulnerabilities.json" \
  --kev-catalog "${catalog}" \
  --kev-receipt "${receipt}" \
  --vex "${repo_root}/.security/vex.json" \
  --output "${evidence_dir}/cve-kev-correlation.json"

python3 "${repo_root}/scripts/security_evidence_correlate.py" \
  --sbom "${evidence_dir}/sbom.cdx.json" \
  --sast "${evidence_dir}/semgrep.json" \
  --kev-catalog "${catalog}" \
  --kev-receipt "${receipt}" \
  --vex "${repo_root}/.security/vex.json" \
  --output "${evidence_dir}/sast-sbom-cve-kev-correlation.json"

mapfile -t go_packages < <("${repo_root}/scripts/go-owned-packages.sh")
echo "security local: govulncheck owned Go packages=${#go_packages[@]}"
(cd "${repo_root}" && govulncheck "${go_packages[@]}")

echo "security local: passed; evidence in .local-ci/security/"
