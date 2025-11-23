# PowerShell script to check if NVIDIA Docker runtime is properly configured (for WSL2)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "NVIDIA Docker Runtime Check" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running in WSL2
Write-Host "1. Checking environment..." -ForegroundColor Yellow
if (Test-Path /proc/version) {
    $wslVersion = Get-Content /proc/version
    if ($wslVersion -match "WSL2" -or $wslVersion -match "microsoft") {
        Write-Host "   ✓ Running in WSL2" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Not running in WSL2" -ForegroundColor Yellow
        Write-Host "   Note: Native Windows Docker does not support GPU passthrough" -ForegroundColor Yellow
        Write-Host "   Please use WSL2 or a Linux system" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠ Cannot determine environment" -ForegroundColor Yellow
}

Write-Host ""

# Check if nvidia-smi is available
Write-Host "2. Checking NVIDIA drivers..." -ForegroundColor Yellow
try {
    $nvidiaSmi = wsl nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ nvidia-smi found" -ForegroundColor Green
        Write-Host "   $($nvidiaSmi | Select-Object -First 3 | Out-String)"
    } else {
        Write-Host "   ✗ nvidia-smi not found or not accessible" -ForegroundColor Red
        Write-Host "   Please install NVIDIA drivers in WSL2" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Cannot check NVIDIA drivers" -ForegroundColor Red
    Write-Host "   Make sure you're in WSL2 and NVIDIA drivers are installed" -ForegroundColor Red
}

Write-Host ""

# Check if Docker is installed
Write-Host "3. Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Docker found" -ForegroundColor Green
        Write-Host "   $dockerVersion"
    } else {
        Write-Host "   ✗ Docker not found" -ForegroundColor Red
        Write-Host "   Please install Docker in WSL2" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Docker not found" -ForegroundColor Red
}

Write-Host ""

# Instructions
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open WSL2 (Ubuntu) terminal" -ForegroundColor Yellow
Write-Host "2. Run the Linux check script:" -ForegroundColor Yellow
Write-Host "   bash check-gpu-docker.sh" -ForegroundColor White
Write-Host ""
Write-Host "Or follow the manual setup in DOCKER_GPU_SETUP.md" -ForegroundColor Yellow
Write-Host ""

