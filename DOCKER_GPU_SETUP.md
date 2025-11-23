# NVIDIA Docker Runtime Setup Guide

This guide will help you install and configure the NVIDIA Container Toolkit to enable GPU support in Docker containers.

## Prerequisites

- NVIDIA GPU with CUDA support
- Docker installed
- NVIDIA drivers installed on the host system

## Quick Check: Are you using Docker Desktop?

If you see "Operating System: Docker Desktop" when running `docker info`, you're using **Docker Desktop with WSL2**. 

**Jump to**: [Docker Desktop + WSL2 Setup](#docker-desktop--wsl2-setup) section below.

## Installation Steps

### 1. Verify NVIDIA Drivers

First, verify that NVIDIA drivers are installed and working:

```bash
nvidia-smi
```

You should see information about your GPU. If not, install NVIDIA drivers first.

### 2. Install NVIDIA Container Toolkit

#### Ubuntu/Debian

**Step 1: Check your distribution**

First, verify your distribution and version:

```bash
# Check distribution info
cat /etc/os-release

# Or check Ubuntu version specifically
lsb_release -a
```

**Step 2: Add NVIDIA package repositories**

Try the automatic detection first:

```bash
# Method 1: Automatic detection (try this first)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
echo "Detected distribution: $distribution"

# Add GPG key
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# Add repository (new method)
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

**If the above doesn't work, try manual setup:**

```bash
# Method 2: Manual setup for Ubuntu 22.04
echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/ubuntu22.04/$(ARCH) /" | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Or for Ubuntu 20.04
echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/ubuntu20.04/$(ARCH) /" | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Or for Debian 11
echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/debian11/$(ARCH) /" | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

**Step 3: Install NVIDIA Container Toolkit**

```bash
# Update package list
sudo apt-get update

# Install NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit

# Restart Docker daemon
sudo systemctl restart docker
```

**Alternative: Install from .deb package**

If repository method fails, download and install manually:

```bash
# Download the .deb package (adjust URL for your distribution)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

#### RHEL/CentOS

```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | sudo tee /etc/yum.repos.d/nvidia-docker.repo

# Install NVIDIA Container Toolkit
sudo yum install -y nvidia-container-toolkit

# Restart Docker daemon
sudo systemctl restart docker
```

#### Arch Linux

```bash
# Install from AUR
yay -S nvidia-container-toolkit

# Or using pacman (if available in official repos)
sudo pacman -S nvidia-container-toolkit

# Restart Docker daemon
sudo systemctl restart docker
```

### 3. Configure Docker Runtime

```bash
# Configure the runtime
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker daemon (choose the correct method)
# Run this script first to check your installation:
bash check-docker-install.sh

# Then use the appropriate restart command:
# For systemd: sudo systemctl restart docker
# For snap: sudo snap restart docker
# For service: sudo service docker restart
```

### 4. Verify Installation

Test if GPU is accessible in Docker:

```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

You should see the same GPU information as when running `nvidia-smi` directly.

## Troubleshooting

### Issue: "docker: Error response from daemon: could not select device driver"

**Solution**: Make sure the NVIDIA Container Toolkit is properly installed and Docker daemon is restarted.

```bash
sudo systemctl restart docker
```

### Issue: "nvidia-container-cli: command not found"

**Solution**: The NVIDIA Container Toolkit might not be installed correctly. Reinstall it:

```bash
# For Ubuntu/Debian
sudo apt-get remove --purge nvidia-container-toolkit
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Issue: "Unsupported distribution!" when adding repository

**Solution**: This happens when the automatic distribution detection fails. Try these steps:

1. **Check your distribution manually:**
```bash
cat /etc/os-release
lsb_release -a
```

2. **Use the new repository method (recommended):**
```bash
# Add GPG key
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# For Ubuntu 22.04
echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/ubuntu22.04/$(dpkg --print-architecture) /" | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# For Ubuntu 20.04 (replace ubuntu22.04 with ubuntu20.04)
# For Debian 11 (replace ubuntu22.04 with debian11)

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

3. **Or install from CUDA repository:**
```bash
# Add CUDA repository (works for most Ubuntu/Debian versions)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

4. **Check supported distributions:**
Visit: https://nvidia.github.io/libnvidia-container/

### Issue: Permission denied

**Solution**: Make sure your user is in the docker group:

```bash
sudo usermod -aG docker $USER
# Log out and log back in for changes to take effect
```

### Issue: "Unit docker.service not found" when restarting Docker

**Solution**: Docker might be installed differently (snap, Docker Desktop, etc.). Check how Docker is installed:

```bash
# Check if Docker is running
docker --version
docker ps

# Check if it's a snap package
snap list | grep docker

# Check if it's a systemd service
systemctl list-units | grep docker

# Check if Docker Desktop is running (WSL2)
ps aux | grep -i docker
docker info | grep "Operating System"
```

**Restart methods based on installation:**

1. **If using Docker Desktop (WSL2/Windows) - MOST COMMON:**
   
   The output shows "Operating System: Docker Desktop" - this means Docker Desktop is managing Docker.
   
   **To restart Docker Desktop:**
   - **From Windows**: Right-click Docker Desktop icon in system tray → "Restart Docker Desktop"
   - **From PowerShell (Windows)**: 
     ```powershell
     # Restart Docker Desktop service
     Restart-Service -Name "com.docker.service"
     # Or restart WSL2 entirely
     wsl --shutdown
     # Then restart your WSL2 distro
     ```
   - **From WSL2**: Docker Desktop doesn't need restart in WSL2, it's managed by Windows
   
   **Important for GPU**: Docker Desktop in WSL2 can use GPU, but you need:
   - WSL2 with GPU support enabled
   - NVIDIA drivers installed in WSL2 (not just Windows)
   - Docker Desktop settings: Settings → Resources → WSL Integration → Enable GPU support

2. **If installed via snap:**
```bash
sudo snap restart docker
# Or
sudo systemctl restart snap.docker.dockerd.service
```

3. **If installed via apt (systemd):**
```bash
sudo systemctl restart docker
# Or
sudo service docker restart
```

4. **If Docker is not installed:**
```bash
# Install Docker on Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker

# Or install Docker Engine (official)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Issue: CUDA version mismatch

**Solution**: Make sure the CUDA version in your Dockerfile matches your host CUDA version:

```bash
# Check host CUDA version
nvcc --version

# Or
cat /usr/local/cuda/version.txt
```

Update the `Dockerfile.gpu` if needed to match your CUDA version.

## Testing with Voice Translator

Once installed, test with the voice translator GPU image:

```bash
# Build the GPU image
docker build -f Dockerfile.gpu -t voice-translator:gpu .

# Test with GPU
docker run --rm --gpus all \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  voice-translator:gpu \
  python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

You should see:
```
CUDA available: True
CUDA device: [Your GPU Name]
```

## Windows Users (Docker Desktop + WSL2)

**You're using Docker Desktop with WSL2!** Here's how to set up GPU support:

### Step 1: Enable GPU in WSL2

1. **Install NVIDIA drivers in WSL2** (not just Windows):
   ```bash
   # In WSL2, download and install NVIDIA drivers
   # Download from: https://www.nvidia.com/Download/index.aspx
   # Choose "Linux 64-bit" and your GPU model
   # Or use:
   wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
   sudo dpkg -i cuda-keyring_1.1-1_all.deb
   sudo apt-get update
   sudo apt-get install -y cuda-drivers
   ```

2. **Verify GPU in WSL2**:
   ```bash
   nvidia-smi
   ```

### Step 2: Enable GPU in Docker Desktop

1. **Open Docker Desktop** (from Windows)
2. Go to **Settings** → **Resources** → **WSL Integration**
3. Enable **"Use the WSL 2 based engine"**
4. Enable your WSL2 distribution (Ubuntu-24.04)
5. Go to **Settings** → **Resources** → **Advanced**
6. Enable **"Use GPU"** (if available)

### Step 3: Install NVIDIA Container Toolkit in WSL2

Since you're in WSL2, follow the Linux instructions above, but note:

- Docker Desktop manages Docker, so you don't need to restart with systemctl
- Install NVIDIA Container Toolkit in WSL2:
  ```bash
  # In WSL2 (your current environment)
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  
  # For Ubuntu 24.04 (your version)
  echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/ubuntu24.04/$(dpkg --print-architecture) /" | \
      sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
  
  sudo apt-get update
  sudo apt-get install -y nvidia-container-toolkit
  
  # Configure (this will work even with Docker Desktop)
  sudo nvidia-ctk runtime configure --runtime=docker
  
  # Restart Docker Desktop from Windows (right-click tray icon → Restart)
  ```

### Step 4: Test GPU in Docker

```bash
# Test in WSL2
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

**Note**: If you get "could not select device driver", you may need to:
- Restart Docker Desktop from Windows
- Or restart WSL2: `wsl --shutdown` (from PowerShell), then restart your distro

## Additional Resources

- [NVIDIA Container Toolkit Documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- [Docker GPU Support Documentation](https://docs.docker.com/config/containers/resource_constraints/#gpu)

