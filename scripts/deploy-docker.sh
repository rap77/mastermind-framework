#!/usr/bin/env bash
# Build and deploy Docker image

set -euo pipefail

VERSION="${1:-latest}"
REGISTRY="${REGISTRY:-docker.io/rap77}"
IMAGE_NAME="mastermind-framework"

echo "Building Docker image: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"

# Build image
docker build -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} .

# Tag as latest
docker tag ${REGISTRY}/${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:latest

# Push to registry
echo "Pushing to registry..."
docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
docker push ${REGISTRY}/${IMAGE_NAME}:latest

echo "✅ Deployment complete!"
echo "Image: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo ""
echo "Run with:"
echo "  docker run -p 8000:8000 ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
