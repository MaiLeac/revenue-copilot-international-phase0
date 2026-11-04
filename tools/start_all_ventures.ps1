<#
.SYNOPSIS
  WINK Ecosystem Multi-Ventures Master Launcher & Health Monitor.
#>

param(
  [ValidateSet("Status", "Start", "Stop")]
  [string]$Action = "Status"
)

$Ventures = @(
  @{ Name = "Wink Master Hub (:8000)"; Port = 8000; Url = "http://127.0.0.1:8000/" },
  @{ Name = "Bản Thảo Thấu Thể 3D (:8000)"; Port = 8000; Url = "http://127.0.0.1:8000/experiments/exp03-duong-nhan-ai-mvp/" },
  @{ Name = "CatalogueQA Enterprise (:8000)"; Port = 8000; Url = "http://127.0.0.1:8000/experiments/exp02-catalogue-qa-pilot/" },
  @{ Name = "Vibe-Trading UI (:8899)"; Port = 8899; Url = "http://127.0.0.1:8899/" },
  @{ Name = "Loser Kingdom (:8888)"; Port = 8888; Url = "http://127.0.0.1:8888/" },
  @{ Name = "Little Loop Factory (:3210)"; Port = 3210; Url = "http://127.0.0.1:3210/" },
  @{ Name = "Wink Living Production"; Port = 443; Url = "https://winkhere.com/" }
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       WINK ECOSYSTEM MULTI-VENTURE ORCHESTRATOR           " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

function Test-PortAlive([string]$hostStr, [int]$port) {
  try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $iar = $tcp.BeginConnect($hostStr, $port, $null, $null)
    $success = $iar.AsyncWaitHandle.WaitOne(400, $false)
    if ($success) {
      $tcp.EndConnect($iar)
      $tcp.Close()
      return $true
    }
    $tcp.Close()
    return $false
  } catch {
    return $false
  }
}

if ($Action -eq "Start") {
  Write-Host "[ORCHESTRATOR] Starting offline venture services..." -ForegroundColor Yellow

  # 1. Local Hub (:8000 & :8899)
  if (-not (Test-PortAlive "127.0.0.1" 8000)) {
    Write-Host " -> Launching Local Hub & Vibe Trading (:8000, :8899)..." -ForegroundColor White
    Start-Process -FilePath "python" -ArgumentList "tools/serve_local_hub.py" -WorkingDirectory "C:\Users\ACER\Documents\Codex\revenue-copilot-international-phase0" -WindowStyle Hidden
    Start-Sleep -Milliseconds 800
  }

  # 2. Loser Kingdom (:8888)
  if (-not (Test-PortAlive "127.0.0.1" 8888)) {
    $loserDir = "C:\Users\ACER\.codex\worktrees\focus-back-restore\Loser Kingdom"
    if (Test-Path "$loserDir\server.py") {
      Write-Host " -> Launching Loser Kingdom (:8888)..." -ForegroundColor White
      Start-Process -FilePath "python" -ArgumentList "server.py" -WorkingDirectory $loserDir -WindowStyle Hidden
      Start-Sleep -Milliseconds 800
    }
  }

  # 3. Little Loop Factory (:3210)
  if (-not (Test-PortAlive "127.0.0.1" 3210)) {
    $videoDir = "C:\Users\ACER\OneDrive\Tài liệu\ChatGPT\Youtube\video-factory"
    if (Test-Path "$videoDir\package.json") {
      Write-Host " -> Launching Little Loop Factory (:3210)..." -ForegroundColor White
      Start-Process -FilePath "npm.cmd" -ArgumentList "start" -WorkingDirectory $videoDir -WindowStyle Hidden
      Start-Sleep -Milliseconds 1200
    }
  }
}

foreach ($v in $Ventures) {
  $isOpen = $false
  if ($v.Port -eq 443) {
    try {
      $res = Invoke-WebRequest -Uri $v.Url -Method Head -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
      if ($res.StatusCode -eq 200) { $isOpen = $true }
    } catch {}
  } else {
    $isOpen = Test-PortAlive "127.0.0.1" $v.Port
  }

  if ($isOpen) {
    Write-Host " [ONLINE] " -ForegroundColor Green -NoNewline
    Write-Host "$($v.Name) -> $($v.Url)" -ForegroundColor White
  } else {
    Write-Host " [OFFLINE] " -ForegroundColor Yellow -NoNewline
    Write-Host "$($v.Name) (Port $($v.Port))" -ForegroundColor Gray
  }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Open Master Hub at: http://127.0.0.1:8000/" -ForegroundColor Cyan
