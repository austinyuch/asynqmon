#!/usr/bin/env bash
# Canonical repo-local CI. Hooks call the same entrypoint developers run manually.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
mode="${1:---full}"
if [[ "${mode}" != "--full" && "${mode}" != "--pre-push" ]]; then
  echo "usage: scripts/local-ci.sh [--full|--pre-push]" >&2
  exit 2
fi

for tool in go corepack; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "local CI: required tool unavailable: ${tool}" >&2
    exit 2
  fi
done

export GOMODCACHE="${GOMODCACHE:-${repo_root}/.local-ci/go-mod-cache}"
export GOCACHE="${GOCACHE:-${repo_root}/.local-ci/go-build-cache}"
export COREPACK_HOME="${COREPACK_HOME:-${repo_root}/.local-ci/corepack}"
export YARN_CACHE_FOLDER="${YARN_CACHE_FOLDER:-${repo_root}/.local-ci/yarn-cache}"
mkdir -p "${GOMODCACHE}" "${GOCACHE}" "${COREPACK_HOME}" "${YARN_CACHE_FOLDER}"

echo "local CI: Go build, vet, and race tests"
(cd "${repo_root}" && go build ./...)
(cd "${repo_root}" && go vet ./...)
(cd "${repo_root}" && go test -race -count=1 ./...)

echo "local CI: UI install, lint, unit tests, and embedded bundle build"
(
  cd "${repo_root}/ui"
  corepack yarn install --frozen-lockfile
  corepack yarn lint
  corepack yarn test
  corepack yarn build
)

"${repo_root}/scripts/security-local.sh"
echo "local CI: passed (${mode})"
