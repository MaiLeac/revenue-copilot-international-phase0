$ErrorActionPreference = 'Stop'
$logPath = (Join-Path $PSScriptRoot 'recover-wsl.log')

try {
    Get-Process -Name 'vmmemWSL' -ErrorAction SilentlyContinue | ForEach-Object {
        & taskkill.exe /PID $_.Id /T /F | Out-File -FilePath $logPath -Encoding utf8 -Append
    }
    $service = Get-CimInstance Win32_Service -Filter "Name='WslService'"
    if ($service.ProcessId -gt 0) {
        & taskkill.exe /PID $service.ProcessId /T /F | Out-File -FilePath $logPath -Encoding utf8
    }
    Start-Sleep -Seconds 2
    & sc.exe start WslService | Out-File -FilePath $logPath -Encoding utf8 -Append
    'RECOVERY_COMPLETE' | Out-File -FilePath $logPath -Encoding utf8 -Append
}
catch {
    $_ | Out-File -FilePath $logPath -Encoding utf8 -Append
    exit 1
}
