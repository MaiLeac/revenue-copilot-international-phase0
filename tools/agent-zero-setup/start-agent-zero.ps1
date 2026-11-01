$ErrorActionPreference = 'SilentlyContinue'

$workspaceRoot = 'C:\Users\ACER\Documents\Codex\2026-09-30\stop-rebuilding-the-agent-from-scratch-2'
$moneyHqRepo = 'C:\Users\ACER\Documents\Codex\revenue-copilot-international-phase0'
$a0Path = Join-Path $env:USERPROFILE '.local\bin\a0.exe'
$stdoutLog = Join-Path $workspaceRoot 'work\a0-connector.log'
$stderrLog = Join-Path $workspaceRoot 'work\a0-connector.err.log'

$wslKeepalive = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'wsl.exe' -and (
        $_.CommandLine -like '*agent-zero-keepalive*' -or
        $_.CommandLine -like '*sleep 2147483647*'
    )
}
if (-not $wslKeepalive) {
    $wslArgs = @(
        '-d', 'Ubuntu-24.04', '-u', 'root', '--', 'sh', '-lc',
        'systemctl start docker; docker start agent-zero >/dev/null 2>&1 || true; exec -a agent-zero-keepalive sleep infinity'
    )
    Start-Process -FilePath 'wsl.exe' -ArgumentList $wslArgs -WindowStyle Hidden | Out-Null
}

$transportPatch = '/mnt/c/Users/ACER/Documents/Codex/2026-09-30/stop-rebuilding-the-agent-from-scratch-2/agent-zero/helpers/litellm_transport.py'
& wsl.exe -d Ubuntu-24.04 -u root -- docker cp $transportPatch agent-zero:/a0/helpers/litellm_transport.py | Out-Null

for ($attempt = 0; $attempt -lt 60; $attempt++) {
    try {
        if ((Invoke-WebRequest -UseBasicParsing 'http://localhost:5080' -TimeoutSec 2).StatusCode -eq 200) {
            break
        }
    }
    catch {}
    Start-Sleep -Seconds 2
}

$connector = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'a0.exe' -and $_.CommandLine -like '*headless*localhost:5080*'
}
if (-not $connector -and (Test-Path -LiteralPath $a0Path) -and (Test-Path -LiteralPath $moneyHqRepo)) {
    $a0Args = @(
        'headless', '--host', 'http://localhost:5080', '--new-chat',
        "--workspace=`"$moneyHqRepo`"", '--output', 'jsonl'
    )
    Start-Process -FilePath $a0Path -ArgumentList $a0Args -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog | Out-Null
}
