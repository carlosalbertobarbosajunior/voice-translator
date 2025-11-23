# PowerShell script to run GUI in Docker (Windows/WSL2)

Write-Host "Voice Translator - Docker GUI Launcher" -ForegroundColor Cyan
Write-Host ""

# Check if running in WSL2
$isWSL2 = Test-Path /proc/version
if ($isWSL2) {
    $wslVersion = Get-Content /proc/version -ErrorAction SilentlyContinue
    if ($wslVersion -match "WSL2" -or $wslVersion -match "microsoft") {
        Write-Host "Detected WSL2" -ForegroundColor Green
        
        # Get Windows host IP for X11
        $nameserver = (Get-Content /etc/resolv.conf | Select-String "nameserver").ToString().Split()[1]
        $env:DISPLAY = "$nameserver`:0.0"
        Write-Host "Setting DISPLAY=$($env:DISPLAY)" -ForegroundColor Yellow
        
        Write-Host ""
        Write-Host "Make sure VcXsrv or X410 is running on Windows!" -ForegroundColor Yellow
        Write-Host "Press Enter to continue..."
        Read-Host
    }
}

# Check if GPU image exists
$gpuImage = docker images --format "{{.Repository}}:{{.Tag}}" | Select-String "voice-translator.*gpu"
if ($gpuImage) {
    $image = "voice-translator:gpu"
    $gpuFlag = "--gpus all"
    Write-Host "Using GPU image" -ForegroundColor Green
} else {
    $image = "voice-translator"
    $gpuFlag = ""
    Write-Host "Using CPU image" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting Docker container..." -ForegroundColor Cyan

# Run Docker container
docker run --rm -it `
  $gpuFlag `
  -e DISPLAY=$env:DISPLAY `
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw `
  -v ${PWD}/input:/app/input `
  -v ${PWD}/output:/app/output `
  -v ${PWD}/cache:/root/.cache `
  $image `
  python runGui.py

