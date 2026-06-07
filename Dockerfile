#
# First stage: 
# Building a frontend.
#

FROM node:22-alpine AS frontend

# Move to a working directory (/static).
WORKDIR /static

# Copy only ./ui folder to the working directory.
COPY ui .

# Run yarn scripts (install & build) via corepack-managed yarn.
RUN corepack enable && yarn install --frozen-lockfile && yarn build

#
# Second stage: 
# Building a backend.
#

FROM golang:1.26-alpine AS backend

# Move to a working directory (/build).
WORKDIR /build

# Copy and download dependencies.
COPY go.mod go.sum ./
RUN go mod download

# Copy a source code to the container.
COPY . .

# Copy frontend static files from /static to the root folder of the backend container.
COPY --from=frontend ["/static/build", "ui/build"]

# Set necessary environmet variables needed for the image and build the server.
# TARGETOS/TARGETARCH are populated automatically by BuildKit and buildah/podman,
# so the image works on amd64 and arm64 alike (empty values fall back to host).
ARG TARGETOS
ARG TARGETARCH
ENV CGO_ENABLED=0

# Run go build (with ldflags to reduce binary size).
RUN GOOS=${TARGETOS:-linux} GOARCH=${TARGETARCH} go build -ldflags="-s -w" -o asynqmon ./cmd/asynqmon

#
# Third stage: 
# Creating and running a new scratch container with the backend binary.
#

FROM scratch

# Copy binary from /build to the root folder of the scratch container.
COPY --from=backend ["/build/asynqmon", "/"]

# Command to run when starting the container.
ENTRYPOINT ["/asynqmon"]
