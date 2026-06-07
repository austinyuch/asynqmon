.PHONY: api assets build docker

# Container runtime: prefer podman (rootless) when present, fall back to docker.
CONTAINER_RUNTIME ?= $(shell command -v podman >/dev/null 2>&1 && echo podman || echo docker)
# In-container alias for the host: podman uses host.containers.internal.
CONTAINER_HOST_ALIAS := $(if $(findstring podman,$(CONTAINER_RUNTIME)),host.containers.internal,host.docker.internal)

assets:
	cd ./ui && yarn install --frozen-lockfile && yarn build

# This target skips the overhead of building UI assets.
# Intended to be used during development.
api:
	go build -o api ./cmd/asynqmon

# Build a release binary.
build: assets
	go build -o asynqmon ./cmd/asynqmon

# Build image and run Asynqmon server (with default settings).
# Works with both podman (rootless) and docker; override with
#   make docker CONTAINER_RUNTIME=docker
docker:
	$(CONTAINER_RUNTIME) build -t asynqmon .
	$(CONTAINER_RUNTIME) run --rm \
		--name asynqmon \
		-p 8080:8080 \
		asynqmon --redis-addr=$(CONTAINER_HOST_ALIAS):6379
