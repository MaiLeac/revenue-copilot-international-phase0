$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pythonPath = (Get-Command python -ErrorAction Stop).Source
$scriptPath = Join-Path $PSScriptRoot 'public_demand_scout.py'
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument ('"' + $scriptPath + '"') -WorkingDirectory $repoRoot
$triggers = @(
    New-ScheduledTaskTrigger -Daily -At '08:35'
    New-ScheduledTaskTrigger -Daily -At '14:35'
    New-ScheduledTaskTrigger -Daily -At '20:35'
)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -MultipleInstances IgnoreNew
$userId = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'MoneyHQ-PublicDemandScout' -Action $action -Trigger $triggers -Settings $settings -Principal $principal -Description 'Read public HN/GitHub discussions; no outreach, paid API, or trade' -Force | Out-Null
Get-ScheduledTask -TaskName 'MoneyHQ-PublicDemandScout' | Select-Object TaskName,State
