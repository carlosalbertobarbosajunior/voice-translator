#!/bin/bash
# Helper script to run GUI in Docker

# Detect if running in WSL2
if grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null ; then
    echo "Detected WSL2 - using Windows host IP for X11"
    # Get Windows host IP for X11 forwarding
    export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
else
    echo "Detected Linux - using local DISPLAY"
    # Use local DISPLAY if not set
    if [ -z "$DISPLAY" ]; then
        export DISPLAY=:0.0
    fi
fi

echo "DISPLAY=$DISPLAY"

# Allow X11 connections (Linux only, WSL2 uses VcXsrv settings)
if ! grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null ; then
    xhost +local:docker 2>/dev/null
fi

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

# Run Docker container
docker run --rm -it \
  $GPU_FLAG \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/cache:/root/.cache \
  $IMAGE \
  python runGui.py

