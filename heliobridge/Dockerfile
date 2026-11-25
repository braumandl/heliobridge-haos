# syntax=docker/dockerfile:1
# Heliobridge itself is built with the project's documented Rust 1.97.1,
# cargo-zigbuild and x86_64-unknown-linux-musl recipe.
FROM rust:1.97.1-bookworm AS builder

WORKDIR /build
RUN apt-get update \
    && apt-get install --yes --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && cargo install cargo-zigbuild --version 0.23.0 --locked \
    && pip3 install --break-system-packages --no-cache-dir ziglang==0.16.0

# Unmodified source tree from https://github.com/longsleep/heliobridge tag v0.9.1
COPY heliobridge-source/ /build/
RUN cargo zigbuild --release --locked --target x86_64-unknown-linux-musl \
    && install -D -m 0755 target/x86_64-unknown-linux-musl/release/heliobridge /out/heliobridge

# Explicit base image is required by Home Assistant Supervisor 2026.04 and later.
FROM ghcr.io/home-assistant/amd64-base:latest

LABEL \
    io.hass.version="0.9.1.1" \
    io.hass.type="app" \
    io.hass.arch="amd64"

RUN apk add --no-cache su-exec \
    && adduser -D -H -u 65532 heliobridge

COPY --from=builder /out/heliobridge /usr/local/bin/heliobridge
COPY run.sh /run.sh
RUN chmod 0755 /run.sh

CMD ["/run.sh"]
