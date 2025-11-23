#!/bin/bash
# Helper script to run web server in Docker

# Check if GPU image exists, otherwise use CPU
if docker images | grep -q "voice-translator.*gpu"; then
    IMAGE="voice-translator:gpu"
    GPU_FLAG="--gpus all"
    echo "Using GPU image"
else
    IMAGE="voice-translator"
    GPU_FLAG=""
    echo "Using CPU image"
fi

echo "Starting web server..."
echo "Open your browser at: http://localhost:5000"
echo ""

# Run Docker container
docker run --rm -it \
  $GPU_FLAG \
  -p 5000:5000 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/cache:/root/.cache \
  $IMAGE \
  python runWeb.py

