$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pythonPath = (Get-Command python -ErrorAction Stop).Source
$scriptPath = Join-Path $PSScriptRoot 'auto_update_family_assets.py'
$tr = "`"$pythonPath`" `"$scriptPath`" --telegram-prices-only"

schtasks /Create /TN "FamilyAssets_AutoPriceUpdater" /TR $tr /SC DAILY /ST 20:00 /F
schtasks /Query /TN "FamilyAssets_AutoPriceUpdater" /FO LIST
