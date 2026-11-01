$ErrorActionPreference = "Stop"

$program = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
$ruleName = "Ollama for Agent Zero (WSL only)"

Get-NetFirewallApplicationFilter -Program $program -ErrorAction SilentlyContinue |
    Get-NetFirewallRule |
    Where-Object { $_.Direction -eq "Inbound" -and $_.Action -eq "Block" } |
    Disable-NetFirewallRule

Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue |
    Remove-NetFirewallRule

New-NetFirewallRule `
    -DisplayName $ruleName `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 11434 `
    -LocalAddress 172.19.176.1 `
    -RemoteAddress 172.19.176.0/20 `
    -Profile Any `
    -Program $program | Out-Null

"OK" | Set-Content -LiteralPath "$PSScriptRoot\allow-ollama-wsl.result" -Encoding ascii
