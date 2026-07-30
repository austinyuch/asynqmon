#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
fixture_dir="${repo_root}/ui/node_modules/local-ci-go-scope-fixture"
invalid_dir="${repo_root}/temp/local-ci-go-scope-invalid"
cleanup() {
  chmod -R u+w "${fixture_dir}" 2>/dev/null || true
  rm -rf "${fixture_dir}"
  rm -rf "${invalid_dir}"
}
trap cleanup EXIT

mkdir -p "${fixture_dir}"
printf 'package fixture\n' >"${fixture_dir}/fixture.go"

module_path="$(cd "${repo_root}" && go list -m -f '{{.Path}}')"
package_output="$("${repo_root}/scripts/go-owned-packages.sh")"

if ! grep -Fxq "${module_path}" <<<"${package_output}"; then
  echo "go package scope test: module root missing" >&2
  exit 1
fi
if grep -Fq '/node_modules/' <<<"${package_output}"; then
  echo "go package scope test: node_modules package leaked into owned scope" >&2
  exit 1
fi

mkdir -p "${invalid_dir}"
printf 'package invalid\nimport _ "example.invalid/missing"\n' >"${invalid_dir}/invalid.go"
if "${repo_root}/scripts/go-owned-packages.sh" >/dev/null 2>&1; then
  echo "go package scope test: partial discovery failure was accepted" >&2
  exit 1
fi

echo "go package scope test: passed"
