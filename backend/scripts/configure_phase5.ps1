# Configure Phase 5B - MedSAM Integration
# This script helps validate your environment and configure MedSAM.

param(
    [string]$CheckpointPath = "",
    [string]$Device = "cpu",
    [string]$Model = "vit_b"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Phase 5B - MedSAM Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$backendRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$envPath = Join-Path $backendRoot ".env"

if (-not (Test-Path $envPath)) {
    Write-Host "[ERROR] backend/.env not found. Create it before running this script." -ForegroundColor Red
    exit 1
}

if ($CheckpointPath -eq "") {
    Write-Host "[INFO] You can pass -CheckpointPath C:\\models\\medsam\\sam_vit_b_medsam.pth"
}

# Update or append entries in .env
function Set-EnvVar($path, $key, $value) {
    $content = Get-Content $path
    $pattern = "^$key=.*$"
    if ($content -match $pattern) {
        $new = ($content -replace $pattern, "$key=$value")
        Set-Content -Path $path -Value $new -NoNewline
    } else {
        Add-Content -Path $path -Value "`r`n$key=$value"
    }
}

if ($CheckpointPath -ne "") { Set-EnvVar $envPath "PHASE5_MEDSAM_CHECKPOINT" $CheckpointPath }
if ($Device -ne "") { Set-EnvVar $envPath "PHASE5_DEVICE" $Device }
if ($Model -ne "") { Set-EnvVar $envPath "PHASE5_MEDSAM_MODEL" $Model }

Write-Host "[OK] Updated backend/.env with Phase 5B variables" -ForegroundColor Green

Write-Host "[INFO] Verifying Python environment..." -ForegroundColor Yellow
Push-Location $backendRoot
. .\venv\Scripts\Activate.ps1 2>$null
try {
    python - << 'PY'
import os
import sys
print("Python:", sys.version)
ckpt = os.getenv('PHASE5_MEDSAM_CHECKPOINT')
print("PHASE5_MEDSAM_CHECKPOINT:", ckpt)
try:
    import torch
    print("torch:", torch.__version__, "cuda:", torch.cuda.is_available())
except Exception as e:
    print("[WARN] torch not available:", e)
try:
    import segment_anything
    print("segment_anything available")
except Exception as e:
    print("[WARN] segment_anything not available (install optional):", e)
PY
} finally {
    Pop-Location
}

Write-Host "[DONE] You can now switch model via: POST /api/phase-5/models/switch?model_id=medsam_v1" -ForegroundColor Green
