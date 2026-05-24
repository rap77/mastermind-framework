# Rust Control Plane — Multi-stage build for minimal image
FROM rust:latest as builder

WORKDIR /app

# Copy Cargo manifests
COPY Cargo.toml Cargo.lock ./

# Copy source code
COPY build.rs ./build.rs
COPY proto ./proto
COPY migrations ./migrations
COPY src ./src

# Build release binary
RUN cargo build --release

# Runtime stage — minimal Debian image
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy binary from builder
COPY --from=builder /app/target/release/rust_control_plane /usr/local/bin/

# Expose Control Plane port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run the Control Plane
CMD ["rust_control_plane"]
