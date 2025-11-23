#!/bin/bash
# Script to check if NVIDIA Docker runtime is properly configured

echo "=========================================="
echo "NVIDIA Docker Runtime Check"
echo "=========================================="
echo ""

# Check if nvidia-smi is available
echo "1. Checking NVIDIA drivers..."
if command -v nvidia-smi &> /dev/null; then
    echo "   ✓ nvidia-smi found"
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | head -1 | while IFS=, read -r name version; do
        echo "   GPU: $name"
        echo "   Driver: $version"
    done
else
    echo "   ✗ nvidia-smi not found"
    echo "   Please install NVIDIA drivers first"
    exit 1
fi

echo ""

# Check if Docker is installed
echo "2. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "   ✓ Docker found"
    docker --version
else
    echo "   ✗ Docker not found"
    echo "   Please install Docker first"
    exit 1
fi

echo ""

# Check if nvidia-container-toolkit is installed
echo "3. Checking NVIDIA Container Toolkit..."
if command -v nvidia-container-cli &> /dev/null; then
    echo "   ✓ NVIDIA Container Toolkit found"
    nvidia-container-cli --version
else
    echo "   ✗ NVIDIA Container Toolkit not found"
    echo "   Please install it following instructions in DOCKER_GPU_SETUP.md"
    exit 1
fi

echo ""

# Check Docker daemon configuration
echo "4. Checking Docker daemon configuration..."
if docker info 2>/dev/null | grep -q "nvidia"; then
    echo "   ✓ NVIDIA runtime configured in Docker"
else
    echo "   ⚠ NVIDIA runtime might not be configured"
    echo "   Run: sudo nvidia-ctk runtime configure --runtime=docker"
    echo "   Then: sudo systemctl restart docker"
fi

echo ""

# Test GPU access in Docker
echo "5. Testing GPU access in Docker..."
if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "   ✓ GPU accessible in Docker containers"
    echo ""
    echo "   GPU test output:"
    docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi --query-gpu=name --format=csv,noheader | head -1
else
    echo "   ✗ GPU not accessible in Docker containers"
    echo "   Please check your NVIDIA Container Toolkit installation"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ All checks passed! GPU Docker is ready."
echo "=========================================="

