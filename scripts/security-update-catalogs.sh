#!/usr/bin/env bash
# Explicit network acquisition for the local CISA KEV snapshot.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
catalog_dir="${repo_root}/.local-ci/security/catalogs"
catalog="${catalog_dir}/known_exploited_vulnerabilities.json"
receipt="${catalog_dir}/known_exploited_vulnerabilities.receipt.json"
source_url="${CISA_KEV_URL:-https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json}"

for tool in curl jq sha256sum; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "security catalog refresh: required tool unavailable: ${tool}" >&2
    exit 2
  fi
done

mkdir -p "${catalog_dir}"
tmp_catalog="$(mktemp "${catalog_dir}/.kev.XXXXXX.json")"
tmp_receipt="$(mktemp "${catalog_dir}/.kev-receipt.XXXXXX.json")"
cleanup() {
  rm -f "${tmp_catalog}" "${tmp_receipt}"
}
trap cleanup EXIT

curl --fail --location --silent --show-error \
  --connect-timeout 15 --max-time 120 \
  "${source_url}" -o "${tmp_catalog}"

jq -e '
  (.catalogVersion | type == "string") and
  (.dateReleased | type == "string") and
  (.count | type == "number") and
  (.vulnerabilities | type == "array") and
  (.count == (.vulnerabilities | length)) and
  (all(.vulnerabilities[];
    (.cveID | test("^CVE-[0-9]{4}-[0-9]{4,}$")) and
    (.vendorProject | type == "string") and
    (.product | type == "string")
  ))
' "${tmp_catalog}" >/dev/null

catalog_sha256="$(sha256sum "${tmp_catalog}" | awk '{print $1}')"
retrieved_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
jq -n \
  --arg source_url "${source_url}" \
  --arg retrieved_at "${retrieved_at}" \
  --arg sha256 "${catalog_sha256}" \
  --arg catalog_version "$(jq -r '.catalogVersion' "${tmp_catalog}")" \
  --arg date_released "$(jq -r '.dateReleased' "${tmp_catalog}")" \
  --argjson count "$(jq '.count' "${tmp_catalog}")" \
  '{
    schema: "asynqmon-security-catalog-receipt/v1",
    source_url: $source_url,
    retrieved_at: $retrieved_at,
    sha256: $sha256,
    catalog_version: $catalog_version,
    date_released: $date_released,
    count: $count
  }' >"${tmp_receipt}"

chmod 0600 "${tmp_catalog}" "${tmp_receipt}"
mv "${tmp_catalog}" "${catalog}"
mv "${tmp_receipt}" "${receipt}"
trap - EXIT

echo "security catalog refresh: CISA KEV ${catalog_sha256} (${retrieved_at})"
