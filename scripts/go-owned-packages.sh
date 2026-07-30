#!/usr/bin/env bash
# List Go packages owned by this module while excluding generated dependency trees.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
# Package-name discovery produces no artifact, so VCS build stamping is neither
# useful nor reliable in linked worktrees. The actual build keeps its default
# VCS stamping behavior.
if ! package_output="$(cd "${repo_root}" && go list -buildvcs=false ./...)"; then
  echo "go package scope: discovery failed" >&2
  exit 2
fi
mapfile -t discovered_packages <<<"${package_output}"

owned_count=0
for package in "${discovered_packages[@]}"; do
  case "${package}" in
    */node_modules/*) continue ;;
  esac
  printf '%s\n' "${package}"
  owned_count=$((owned_count + 1))
done

if [[ "${owned_count}" -eq 0 ]]; then
  echo "go package scope: no owned packages discovered" >&2
  exit 2
fi
