# Running GUI in Docker

This guide explains how to run the graphical user interface (GUI) inside Docker containers.

## Prerequisites

The GUI uses tkinter which requires X11 display server. You need to set up X11 forwarding.

### For WSL2 (Windows)

1. **Install X Server on Windows:**
   - Option 1: [VcXsrv](https://sourceforge.net/projects/vcxsrv/) (Free, recommended)
   - Option 2: [X410](https://www.x410.dev/) (Paid, better performance)

2. **Configure VcXsrv:**
   - Download and install VcXsrv
   - Launch "XLaunch"
   - Select "Multiple windows" → Next
   - Select "Start no client" → Next
   - **IMPORTANT**: Check "Disable access control" → Next
   - Click "Finish"
   - VcXsrv will run in system tray

3. **Set DISPLAY in WSL2:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc for permanent setup
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
   
   # Or run once per session:
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
   ```

4. **Test X11 connection:**
   ```bash
   # Test if X11 is working
   xeyes  # Should open a window with eyes following mouse
   # Or
   xclock  # Should open a clock window
   ```

### For Linux (Native)

X11 forwarding should work automatically if you have a display server running.

## Running GUI with Docker

### Method 1: Using Docker Run (CPU)

```bash
# Set DISPLAY (if not already set)
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0

# Run with X11 forwarding
docker run --rm -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd):/app \
  voice-translator \
  python runGui.py
```

### Method 2: Using Docker Run (GPU)

```bash
# Set DISPLAY (if not already set)
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0

# Run with X11 forwarding and GPU
docker run --rm -it \
  --gpus all \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd):/app \
  voice-translator:gpu \
  python runGui.py
```

### Method 3: Using Docker Compose

Add to your `docker-compose.yml`:

```yaml
services:
  voice-translator-gui:
    build:
      context: .
      dockerfile: Dockerfile.gpu
    container_name: voice-translator-gui
    environment:
      - DISPLAY=${DISPLAY}
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ./input:/app/input
      - ./output:/app/output
      - ./cache:/root/.cache
    network_mode: host
    # For GPU support, uncomment:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]
    stdin_open: true
    tty: true
    command: python runGui.py
```

Then run:
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
docker-compose up voice-translator-gui
```

## Helper Scripts

### For WSL2/Windows

Create `run-gui-docker.sh`:

```bash
#!/bin/bash
# Helper script to run GUI in Docker (WSL2)

# Get Windows host IP for X11
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0

# Allow X11 connections
xhost +local:docker

# Run Docker container
docker run --rm -it \
  --gpus all \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/cache:/root/.cache \
  voice-translator:gpu \
  python runGui.py
```

### For Linux

Create `run-gui-docker.sh`:

```bash
#!/bin/bash
# Helper script to run GUI in Docker (Linux)

# Allow X11 connections
xhost +local:docker

# Run Docker container
docker run --rm -it \
  --gpus all \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/cache:/root/.cache \
  voice-translator:gpu \
  python runGui.py
```

## Troubleshooting

### Issue: "cannot connect to X server"

**Solution**: 
1. Make sure X server is running (VcXsrv/X410 on Windows)
2. Check DISPLAY variable: `echo $DISPLAY`
3. Allow X11 connections: `xhost +local:docker` (Linux) or enable in VcXsrv settings

### Issue: "No display name and no $DISPLAY environment variable"

**Solution**: Set DISPLAY variable:
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```

### Issue: GUI appears but is slow

**Solution**: 
- Use X410 instead of VcXsrv (better performance)
- Or run natively instead of Docker for better performance

### Issue: Permission denied for X11

**Solution**: 
```bash
xhost +local:docker
# Or in VcXsrv: Enable "Disable access control"
```

## Alternative: Run Natively (Recommended for GUI)

For best GUI performance, consider running the GUI natively instead of in Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI
python runGui.py
```

The GUI will have better performance and easier setup when run natively.

