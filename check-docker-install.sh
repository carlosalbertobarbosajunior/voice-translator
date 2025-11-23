#!/bin/bash
# Script to check Docker installation and provide correct restart command

echo "=========================================="
echo "Docker Installation Checker"
echo "=========================================="
echo ""

# Check if Docker command exists
if command -v docker &> /dev/null; then
    echo "✓ Docker command found"
    docker --version
else
    echo "✗ Docker command not found"
    echo "Docker is not installed or not in PATH"
    exit 1
fi

echo ""
echo "Checking Docker installation method..."

# Check if it's a snap package
if snap list 2>/dev/null | grep -q docker; then
    echo "✓ Docker is installed via snap"
    echo ""
    echo "To restart Docker, use:"
    echo "  sudo snap restart docker"
    echo "  OR"
    echo "  sudo systemctl restart snap.docker.dockerd.service"
    SNAP_INSTALLED=true
else
    echo "✗ Docker is NOT installed via snap"
    SNAP_INSTALLED=false
fi

# Check if it's a systemd service
if systemctl list-units --type=service 2>/dev/null | grep -q docker.service; then
    echo "✓ Docker is installed as systemd service"
    echo ""
    echo "To restart Docker, use:"
    echo "  sudo systemctl restart docker"
    echo "  OR"
    echo "  sudo service docker restart"
    SYSTEMD_INSTALLED=true
else
    echo "✗ Docker is NOT installed as systemd service"
    SYSTEMD_INSTALLED=false
fi

# Check if Docker daemon is running
if docker ps &> /dev/null; then
    echo "✓ Docker daemon is running"
    echo ""
    echo "Docker info:"
    docker info 2>/dev/null | grep -E "Server Version|Operating System|Kernel Version" | head -3
    
    # Check if it's Docker Desktop
    if docker info 2>/dev/null | grep -q "Docker Desktop"; then
        echo ""
        echo "⚠ Docker Desktop detected (WSL2)"
        echo "Docker is managed by Windows, not systemd"
        echo ""
        echo "To restart Docker:"
        echo "  1. From Windows: Right-click Docker Desktop tray icon → Restart"
        echo "  2. From PowerShell: wsl --shutdown (then restart WSL2)"
        echo "  3. Or restart Docker Desktop service from Windows"
        DOCKER_DESKTOP=true
    else
        DOCKER_DESKTOP=false
    fi
else
    echo "✗ Docker daemon is NOT running"
    echo ""
    echo "Trying to start Docker..."
    
    if [ "$SNAP_INSTALLED" = true ]; then
        echo "Starting via snap..."
        sudo snap start docker
    elif [ "$SYSTEMD_INSTALLED" = true ]; then
        echo "Starting via systemd..."
        sudo systemctl start docker
    else
        echo "Cannot determine how to start Docker automatically"
        echo "Please check your Docker installation"
    fi
fi

# Check Docker socket
echo ""
echo "Checking Docker socket..."
if [ -S /var/run/docker.sock ]; then
    echo "✓ Docker socket found at /var/run/docker.sock"
    ls -l /var/run/docker.sock
elif [ -S /run/docker.sock ]; then
    echo "✓ Docker socket found at /run/docker.sock"
    ls -l /run/docker.sock
else
    echo "✗ Docker socket not found"
fi

# Check user permissions
echo ""
echo "Checking user permissions..."
if groups | grep -q docker; then
    echo "✓ User is in docker group"
else
    echo "✗ User is NOT in docker group"
    echo ""
    echo "To add user to docker group:"
    echo "  sudo usermod -aG docker $USER"
    echo "  Then log out and log back in"
fi

echo ""
echo "=========================================="
echo "Summary:"
echo "=========================================="

if [ "$DOCKER_DESKTOP" = true ]; then
    echo "Installation: Docker Desktop (WSL2)"
    echo "Restart: Restart Docker Desktop from Windows"
    echo "Or: wsl --shutdown (from PowerShell), then restart WSL2"
elif [ "$SNAP_INSTALLED" = true ]; then
    echo "Installation: Snap"
    echo "Restart command: sudo snap restart docker"
elif [ "$SYSTEMD_INSTALLED" = true ]; then
    echo "Installation: Systemd service"
    echo "Restart command: sudo systemctl restart docker"
else
    echo "Installation: Unknown method"
    echo "Please check your Docker installation"
fi

