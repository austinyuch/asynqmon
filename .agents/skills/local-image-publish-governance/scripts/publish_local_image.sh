#!/usr/bin/env bash
# Local image publish pipeline (fail-closed):
#   provenance -> build(+OCI labels) -> arch gate -> smoke gate -> tag localhost/local/<name>
# See SKILL.md for the rules this implements.
set -euo pipefail

NAME="" CONTEXT="." CONTAINERFILE="" SMOKE_ARG="--help" SMOKE_EXPECT=0 WITH_LATEST=1 PLATFORM=""
while [ $# -gt 0 ]; do
  case "$1" in
    --name) NAME="$2"; shift 2 ;;
    --context) CONTEXT="$2"; shift 2 ;;
    --containerfile) CONTAINERFILE="$2"; shift 2 ;;
    --smoke-arg) SMOKE_ARG="$2"; shift 2 ;;
    --smoke-expect) SMOKE_EXPECT="$2"; shift 2 ;;
    --no-latest) WITH_LATEST=0; shift ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
[ -n "$NAME" ] || { echo "usage: publish_local_image.sh --name <name> [--context dir] [--containerfile path] [--smoke-arg --help] [--smoke-expect 0] [--no-latest] [--platform os/arch]" >&2; exit 2; }

# 1) runtime: prefer rootless podman
if command -v podman >/dev/null 2>&1; then RT=podman; else RT=docker; fi
command -v "$RT" >/dev/null 2>&1 || { echo "ERROR: no container runtime (podman/docker)" >&2; exit 1; }

# 2) provenance (refuse to publish unidentifiable images)
cd "$CONTEXT"
git rev-parse --git-dir >/dev/null 2>&1 || { echo "ERROR: $CONTEXT is not a git repo; refusing to publish image without provenance" >&2; exit 1; }
SHA=$(git rev-parse HEAD); SHORT=$(git rev-parse --short HEAD)
DIRTY=""; [ -n "$(git status --porcelain)" ] && DIRTY="-dirty"
SRC=$(git remote get-url origin 2>/dev/null || echo "unknown")
CREATED=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MAIN_TAG="g${SHORT}${DIRTY}"
IMG="localhost/local/${NAME}"
TMP_TAG="${NAME}-publish-tmp:${MAIN_TAG}"

# 3) build with OCI labels
BUILD_ARGS=(build -t "$TMP_TAG"
  --label "org.opencontainers.image.source=${SRC}"
  --label "org.opencontainers.image.revision=${SHA}${DIRTY}"
  --label "org.opencontainers.image.created=${CREATED}"
  --label "org.opencontainers.image.title=${NAME}"
  --label "org.opencontainers.image.version=${MAIN_TAG}")
[ -n "$CONTAINERFILE" ] && BUILD_ARGS+=(-f "$CONTAINERFILE")
[ -n "$PLATFORM" ] && BUILD_ARGS+=(--platform "$PLATFORM")
BUILD_ARGS+=(.)
echo ">> ${RT} ${BUILD_ARGS[*]}"
"$RT" "${BUILD_ARGS[@]}"

cleanup_tmp() { "$RT" rmi "$TMP_TAG" >/dev/null 2>&1 || true; }
trap cleanup_tmp EXIT

# 4) arch gate
WANT_ARCH="${PLATFORM##*/}"; [ -n "$WANT_ARCH" ] || WANT_ARCH=$("$RT" info --format '{{.Host.Arch}}' 2>/dev/null || docker version --format '{{.Server.Arch}}' 2>/dev/null || uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')
GOT_ARCH=$("$RT" image inspect "$TMP_TAG" --format '{{.Architecture}}')
[ "$GOT_ARCH" = "$WANT_ARCH" ] || { echo "ERROR: arch gate failed: image=$GOT_ARCH expected=$WANT_ARCH (hardcoded GOARCH in the Containerfile?)" >&2; exit 1; }
echo ">> arch gate OK ($GOT_ARCH)"

# 5) smoke gate (harmless, no ports, not long-running)
# Note: Go flag-package binaries exit 2 on --help; declare it with --smoke-expect 2.
echo ">> smoke: $RT run --rm $TMP_TAG $SMOKE_ARG (expect exit $SMOKE_EXPECT)"
RC=0; "$RT" run --rm "$TMP_TAG" "$SMOKE_ARG" >/dev/null 2>&1 || RC=$?
[ "$RC" = "$SMOKE_EXPECT" ] || { echo "ERROR: smoke gate failed: exit $RC, expected $SMOKE_EXPECT" >&2; exit 1; }
echo ">> smoke gate OK (exit $RC)"

# 6) immutability + publish tags
if "$RT" image inspect "${IMG}:${MAIN_TAG}" >/dev/null 2>&1; then
  OLD_ID=$("$RT" image inspect "${IMG}:${MAIN_TAG}" --format '{{.Id}}')
  NEW_ID=$("$RT" image inspect "$TMP_TAG" --format '{{.Id}}')
  if [ "$OLD_ID" != "$NEW_ID" ] && [ -z "$DIRTY" ]; then
    echo "ERROR: ${IMG}:${MAIN_TAG} already exists with different content; clean-sha tags are immutable" >&2; exit 1
  fi
fi
"$RT" tag "$TMP_TAG" "${IMG}:${MAIN_TAG}"
TAGS=("${IMG}:${MAIN_TAG}")
if VERSION=$(git describe --tags --exact-match 2>/dev/null); then
  "$RT" tag "$TMP_TAG" "${IMG}:${VERSION}"; TAGS+=("${IMG}:${VERSION}")
fi
if [ "$WITH_LATEST" = 1 ]; then
  "$RT" tag "$TMP_TAG" "${IMG}:latest"; TAGS+=("${IMG}:latest")
fi

# 7) report
SIZE=$("$RT" image inspect "$TMP_TAG" --format '{{.Size}}')
echo ""
echo "published: ${IMG}"
printf '  tag: %s\n' "${TAGS[@]}"
echo "  arch: ${GOT_ARCH}  size: $((SIZE/1024/1024))MB  runtime: ${RT}"
echo "  revision: ${SHA}${DIRTY}"
echo "  smoke: '${SMOKE_ARG}' exit ${SMOKE_EXPECT} (as declared)"
[ -n "$DIRTY" ] && echo "  NOTE: built from a dirty worktree (tag carries -dirty)"
echo "  (old versions piling up? inventory them with container-image-janitor — do not delete here)"
