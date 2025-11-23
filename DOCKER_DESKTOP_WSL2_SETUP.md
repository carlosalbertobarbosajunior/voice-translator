# Docker Desktop + WSL2 GPU Setup Guide

**Quick Guide for Docker Desktop users in WSL2**

## Step-by-Step Setup

### Step 1: Verify GPU in WSL2

```bash
# Check if GPU is accessible in WSL2
nvidia-smi
```

**If `nvidia-smi` doesn't work**, you need to install NVIDIA drivers in WSL2:

```bash
# Install NVIDIA drivers in WSL2
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-drivers

# Verify
nvidia-smi
```

### Step 2: Install NVIDIA Container Toolkit in WSL2

```bash
# Add GPG key
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# Add repository for Ubuntu 24.04
echo "deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://nvidia.github.io/libnvidia-container/stable/ubuntu24.04/$(dpkg --print-architecture) /" | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update and install
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure runtime
sudo nvidia-ctk runtime configure --runtime=docker
```

### Step 3: Restart Docker Desktop

**From Windows** (not WSL2):
1. Right-click Docker Desktop icon in system tray
2. Click "Restart Docker Desktop"

**OR from PowerShell (Windows)**:
```powershell
Restart-Service -Name "com.docker.service"
```

**OR restart WSL2 entirely**:
```powershell
# From PowerShell (Windows)
wsl --shutdown
# Then restart your WSL2 distro
```

### Step 4: Test GPU in Docker

```bash
# Test GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

You should see your GPU information.

### Step 5: Build and Test Voice Translator GPU Image

```bash
# Build the GPU image (this may take a while, especially downloading PyTorch)
docker build -f Dockerfile.gpu -t voice-translator:gpu .

# Test PyTorch with CUDA
docker run --rm --gpus all voice-translator:gpu \
  python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

**Note**: The first build will take longer as it downloads PyTorch with CUDA support (~2-3GB).

## Troubleshooting

### Issue: "could not select device driver" after installing toolkit

**Solution**: Restart Docker Desktop from Windows (right-click tray icon → Restart)

### Issue: nvidia-smi doesn't work in WSL2

**Solution**: Install NVIDIA drivers in WSL2 (see Step 1 above)

### Issue: GPU not detected in Docker

**Solution**: 
1. Make sure `nvidia-smi` works in WSL2 first
2. Restart Docker Desktop from Windows
3. Verify with: `docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi`

### Issue: "Unit docker.service not found"

**This is NORMAL for Docker Desktop!** Docker Desktop doesn't use systemd. 
- To restart: Restart Docker Desktop from Windows
- Or use: `wsl --shutdown` (from PowerShell), then restart WSL2

