#!/bin/bash
# Automated NVIDIA Container Toolkit installation script
# This script handles various Linux distributions and common issues

set -e

echo "=========================================="
echo "NVIDIA Container Toolkit Installer"
echo "=========================================="
echo ""

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
    echo "Detected OS: $OS"
    echo "Detected Version: $VERSION"
else
    echo "Error: Cannot detect OS distribution"
    exit 1
fi

# Function to install for Ubuntu/Debian
install_ubuntu_debian() {
    echo ""
    echo "Installing for Ubuntu/Debian..."
    
    # Detect architecture
    ARCH=$(dpkg --print-architecture)
    echo "Architecture: $ARCH"
    
    # Add GPG key
    echo "Adding GPG key..."
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    
    # Determine repository URL based on OS version
    if [ "$OS" = "ubuntu" ]; then
        if [ "$VERSION" = "22.04" ] || [ "$VERSION" = "22.10" ]; then
            REPO_URL="https://nvidia.github.io/libnvidia-container/stable/ubuntu22.04/$ARCH"
        elif [ "$VERSION" = "20.04" ] || [ "$VERSION" = "20.10" ]; then
            REPO_URL="https://nvidia.github.io/libnvidia-container/stable/ubuntu20.04/$ARCH"
        elif [ "$VERSION" = "18.04" ]; then
            REPO_URL="https://nvidia.github.io/libnvidia-container/stable/ubuntu18.04/$ARCH"
        else
            echo "Warning: Ubuntu version $VERSION might not be officially supported"
            echo "Trying Ubuntu 22.04 repository..."
            REPO_URL="https://nvidia.github.io/libnvidia-container/stable/ubuntu22.04/$ARCH"
        fi
    elif [ "$OS" = "debian" ]; then
        if [ "$VERSION" = "12" ] || [ "$VERSION" = "bookworm" ]; then
            REPO_URL="https://nvidia.github.io/libnvidia-container/stable/debian12/$ARCH"
        elif [ "$VERSION" = "11" ] || [ "$VERSION" = "bullseye" ]; then
            REPO_URL="https://nvidia.github.io/libnvidia-container/stable/debian11/$ARCH"
        elif [ "$VERSION" = "10" ] || [ "$VERSION" = "buster" ]; then
            REPO_URL="https://nvidia.github.io/libnvidia-container/stable/debian10/$ARCH"
        else
            echo "Warning: Debian version $VERSION might not be officially supported"
            echo "Trying Debian 11 repository..."
            REPO_URL="https://nvidia.github.io/libnvidia-container/stable/debian11/$ARCH"
        fi
    else
        echo "Error: Unsupported distribution: $OS"
        exit 1
    fi
    
    echo "Using repository: $REPO_URL"
    
    # Add repository
    echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] $REPO_URL /" | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    # Update and install
    echo "Updating package list..."
    sudo apt-get update
    
    echo "Installing NVIDIA Container Toolkit..."
    sudo apt-get install -y nvidia-container-toolkit
    
    # Configure runtime
    echo "Configuring Docker runtime..."
    sudo nvidia-ctk runtime configure --runtime=docker
    
    # Restart Docker
    echo "Restarting Docker..."
    sudo systemctl restart docker
    
    echo ""
    echo "✓ Installation complete!"
}

# Function to install for RHEL/CentOS
install_rhel_centos() {
    echo ""
    echo "Installing for RHEL/CentOS..."
    
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | sudo tee /etc/yum.repos.d/nvidia-docker.repo
    
    sudo yum install -y nvidia-container-toolkit
    sudo systemctl restart docker
    
    echo ""
    echo "✓ Installation complete!"
}

# Main installation logic
case $OS in
    ubuntu|debian)
        install_ubuntu_debian
        ;;
    rhel|centos|fedora)
        install_rhel_centos
        ;;
    *)
        echo "Error: Unsupported OS: $OS"
        echo "Please install manually following instructions in DOCKER_GPU_SETUP.md"
        exit 1
        ;;
esac

# Verify installation
echo ""
echo "Verifying installation..."
if command -v nvidia-container-cli &> /dev/null; then
    echo "✓ nvidia-container-cli found"
    nvidia-container-cli --version
else
    echo "✗ nvidia-container-cli not found"
    exit 1
fi

# Test GPU access
echo ""
echo "Testing GPU access in Docker..."
if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "✓ GPU accessible in Docker!"
    echo ""
    echo "Test output:"
    docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi --query-gpu=name --format=csv,noheader | head -1
else
    echo "✗ GPU not accessible in Docker"
    echo "Please check your configuration"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ All done! NVIDIA Docker is ready to use."
echo "=========================================="

