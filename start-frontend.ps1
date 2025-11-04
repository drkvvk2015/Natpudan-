# Start Frontend Development Server
Set-Location "$PSScriptRoot\frontend"
Write-Host "Starting Vite dev server from: $(Get-Location)" -ForegroundColor Green
npm run dev
