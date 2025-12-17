# Free port 5173 by terminating the owning process (Windows PowerShell)
# Useful when OAuth redirect requires fixed port 5173

param(
    [int]$Port = 5173
)

Write-Host "[Free-5173] Checking for process using port $Port..."
$tcp = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($null -eq $tcp) {
    Write-Host "[Free-5173] Port $Port is already free."
    exit 0
}

$portPid = $tcp.OwningProcess
try {
    $proc = Get-Process -Id $portPid -ErrorAction Stop
    Write-Host "[Free-5173] Terminating process PID=$portPid ($($proc.Name)) holding port $Port..."
    Stop-Process -Id $portPid -Force
    Start-Sleep -Seconds 1
    $check = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($null -eq $check) {
        Write-Host "[Free-5173] Port $Port freed successfully."
        exit 0
    } else {
        Write-Warning "[Free-5173] Port $Port still in use after termination."
        exit 1
    }
}
catch {
    Write-Warning "[Free-5173] Failed to terminate PID=$portPid. Error: $($_.Exception.Message)"
    exit 1
}
