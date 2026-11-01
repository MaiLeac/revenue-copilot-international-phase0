param([ValidateSet('Start','Login','Check','Backtest','Stop')][string]$Action='Start')
$ErrorActionPreference='Stop'
$base=Join-Path $env:LOCALAPPDATA 'MaiVibeTrading'
$source=Join-Path $base 'Vibe-Trading'
$python=Join-Path $base '.venv\Scripts\python.exe'
$env:VIRTUAL_ENV=Join-Path $base '.venv'
$env:PATH=(Join-Path $env:VIRTUAL_ENV 'Scripts')+';'+$env:PATH
$env:VIBE_TRADING_HOME=Join-Path $env:USERPROFILE '.vibe-trading'
$env:PYTHONUTF8='1'
$logs=Join-Path $base 'logs'
New-Item -ItemType Directory -Force $logs | Out-Null
Set-Location -LiteralPath $source
function Invoke-Cli([string[]]$CliArgs) {
    & $python -m cli @CliArgs
    if($LASTEXITCODE -ne 0){throw "Vibe-Trading exited with code $LASTEXITCODE"}
}
function Get-Listener { @(Get-NetTCPConnection -LocalPort 8899 -State Listen -ErrorAction SilentlyContinue) }
function Assert-OurServer($listener) {
    if($listener.LocalAddress -ne '127.0.0.1'){throw 'Port 8899 is not restricted to localhost.'}
    $proc=Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    $owned=$proc -and $proc.ExecutablePath -ieq $python
    if($proc -and -not $owned){
        $parent=Get-CimInstance Win32_Process -Filter "ProcessId=$($proc.ParentProcessId)"
        $owned=$parent -and $parent.ExecutablePath -ieq $python -and $parent.CreationDate -le $proc.CreationDate -and $parent.CommandLine -match '-m\s+cli\s+serve\s' -and $parent.CommandLine -match '--port\s+8899(?:\s|$)'
    }
    if(-not $owned -or $proc.CommandLine -notmatch '-m\s+cli\s+serve\s' -or $proc.CommandLine -notmatch '--host\s+127\.0\.0\.1(?:\s|$)' -or $proc.CommandLine -notmatch '--port\s+8899(?:\s|$)') {
        throw 'Port 8899 belongs to an unrecognized process. No process was stopped.'
    }
    return $proc
}
try {
    switch($Action) {
        'Login' { Invoke-Cli @('provider','login','openai-codex'); Invoke-Cli @('provider','doctor') }
        'Check' {
            Invoke-Cli @('--version')
            & $python -m pip check
            if($LASTEXITCODE -ne 0){throw 'Dependency check failed'}
            Invoke-Cli @('provider','doctor')
            if(-not(Test-Path (Join-Path $source 'frontend\dist\index.html'))){throw 'Frontend missing'}
            $listeners=Get-Listener
            foreach($listener in $listeners){$null=Assert-OurServer $listener}
            Write-Host "Frontend exists. Localhost listeners: $($listeners.Count)"
            Write-Host "Live HALT present: $(Test-Path (Join-Path $env:VIBE_TRADING_HOME 'live\HALT'))"
        }
        'Backtest' {
            $end=(Get-Date).AddDays(-1).ToString('yyyy-MM-dd')
            $prompt="Research/backtest only. No broker connections, no real orders, no leverage. Backtest SOL-USDT spot daily from 2021-01-01 through $end. Compare buy-and-hold with EMA50/EMA200 long-only (long when EMA50 > EMA200, otherwise cash). Use leverage=1 and funding_rate=0 for spot; never use perpetual funding defaults. Fees 0.1% each side; slippage 0.05% each side. Signals use completed bars and execute at the next bar open. Use warmup history without future data. Report actual data source, coverage, max drawdown, CAGR, Sharpe, trade count and a chronological out-of-sample period 2025-01-01 onward with fixed parameters. Do not mistake slicing an equity curve for parameter-selection walk-forward. If data fails, try supported public fallbacks; never fabricate results. Explain all limitations."
            $promptPath=Join-Path $logs 'sol-backtest-prompt.txt'
            $prompt+=' Use the built-in backtest tool with config.json and code/signal_engine.py so performance artifacts pass the grounding gate. Do not rely only on a standalone custom script. Use completed UTC daily candles, report missing warmup honestly, include initial capital and first-day returns in metrics, and distinguish order count from completed round trips. Read the strategy-generate skill without inventing section names.'
            [IO.File]::WriteAllText($promptPath,$prompt,(New-Object Text.UTF8Encoding($false)))
            Invoke-Cli @('--version')
            & $python (Join-Path $PSScriptRoot 'Run-SOL-Backtest.py')
            if($LASTEXITCODE -ne 0){throw "SOL backtest failed with code $LASTEXITCODE"}
        }
        'Start' {
            $listeners=Get-Listener
            if($listeners.Count -eq 0){
                $stamp=Get-Date -Format 'yyyyMMdd-HHmmss'
                $p=Start-Process -FilePath $python -ArgumentList @('-m','cli','serve','--host','127.0.0.1','--port','8899') -WorkingDirectory $source -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs "server-$stamp.out.log") -RedirectStandardError (Join-Path $logs "server-$stamp.err.log") -PassThru
                $p.Id | Set-Content (Join-Path $logs 'server.pid')
            }
            $ready=$false
            for($i=0;$i -lt 180;$i++){
                try {
                    $response=Invoke-WebRequest 'http://127.0.0.1:8899/' -UseBasicParsing -TimeoutSec 2
                    if($response.StatusCode -eq 200 -and $response.Content -match '<html' -and $response.Content -match '<script'){$ready=$true;break}
                } catch {}
                Start-Sleep -Seconds 2
            }
            if(-not $ready){throw "Server not ready. Inspect $logs"}
            foreach($listener in (Get-Listener)){$null=Assert-OurServer $listener}
            Start-Process 'http://127.0.0.1:8899/'
            Write-Host 'Vibe-Trading ready at http://127.0.0.1:8899/'
        }
        'Stop' {
            Invoke-Cli @('--version')
            foreach($listener in (Get-Listener)){
                $proc=Assert-OurServer $listener
                Stop-Process -Id $proc.ProcessId -ErrorAction Stop
                Write-Host "Stopped Vibe-Trading server PID $($proc.ProcessId) only."
            }
        }
    }
} catch { Write-Host $_ -ForegroundColor Red; exit 1 }
