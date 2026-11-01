<#
.SYNOPSIS
    Automated System & Docker Cleanup Script for Money HQ.
    Runs periodically to keep C: drive clean and prevent disk exhaustion.
#>

$ErrorActionPreference = "SilentlyContinue"

Write-Host "=== [1/4] Cleaning Docker Unused Objects & Build Cache ==="
wsl -- docker builder prune -af | Out-Null
wsl -- docker system prune -f | Out-Null

Write-Host "=== [2/4] Cleaning User Temp Files ==="
$userTemp = $env:TEMP
if (Test-Path $userTemp) {
    Get-ChildItem -Path $userTemp -Recurse -Force -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-1) } |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

Write-Host "=== [3/4] Cleaning Pip & NPM Package Caches ==="
pip cache purge | Out-Null
npm cache clean --force | Out-Null

Write-Host "=== [4/4] Emptying Recycle Bin ==="
Clear-RecycleBin -DriveLetter C -Force -ErrorAction SilentlyContinue

$cDrive = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -eq "C" }
$freeGB = [math]::Round($cDrive.Free / 1GB, 2)
Write-Host ">>> Cleanup Complete. C: Drive Free Space: $freeGB GB"
