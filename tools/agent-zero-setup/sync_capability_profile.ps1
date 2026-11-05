param(
    [string]$ProfilePath = (Join-Path $env:USERPROFILE 'agent-zero\agent-zero\usr\agents\money-coo\prompts\agent.system.main.specifics.md')
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$catalogPath = Join-Path $repoRoot 'assets\web_capability_library\catalog.json'
if (-not (Test-Path -LiteralPath $ProfilePath -PathType Leaf)) { throw "Agent Zero profile not found: $ProfilePath" }
if (-not (Test-Path -LiteralPath $catalogPath -PathType Leaf)) { throw "Capability catalog not found: $catalogPath" }

$content = Get-Content -LiteralPath $ProfilePath -Raw -Encoding UTF8
$content = [regex]::Replace($content, '(?m)^   - Payment Rails:.*$', '   - Payment rails for the book are not live. The owner may verify transfers manually after a finished product and a tested order path exist.')
$content = [regex]::Replace($content, '(?m)^   - Transaction fee .*$', '   - Do not assume any processing fee; verify actual fees before setting a public price.')
$content = [regex]::Replace($content, '(?m)^   - \*\*Vent\. 1 .*$', '   - **Vent. 1 (Digital Product):** Ban Thao book in progress. The current website shows illustrative free exercises only; no physical goods, price, or live checkout.')
$marker = '## Current Money HQ capability routing (2026-11-05)'
if ($content.Contains($marker)) {
    $fixed = [regex]::Replace($content, '(?m)^- B.* is digital-only\..*$', '- Ban Thao is digital-only. The owner is writing the 28-day book. The seven-page web exercise is illustrative, not approved book content. No tea, physical gift, published price, live checkout or automatic payment confirmation exists. The current catalog is `/a0/usr/projects/money-hq/experiments/exp03-duong-nhan-ai-mvp/products.json`.')
    Set-Content -LiteralPath $ProfilePath -Value $fixed -Encoding UTF8
    Write-Output 'Profile already contains current capability routing.'
    exit 0
}

# Preserve old prompt for local rollback. Do not put it in the repository.
$backup = "$ProfilePath.backup-2026-11-05"
Copy-Item -LiteralPath $ProfilePath -Destination $backup -ErrorAction Stop

$addendum = @'
## Current Money HQ capability routing (2026-11-05)

- This section supersedes older EXP-03 product, payment, and physical-gift descriptions below.
- Before any website, UI, automation, video, or data implementation, read `/a0/usr/projects/money-hq/AGENTS.md`, then run `python /a0/usr/projects/money-hq/tools/capability_lookup.py "task words"` or read `/a0/usr/projects/money-hq/assets/web_capability_library/CAPABILITY_ROUTING.md`. Inspect the candidate's real source, license, installed state and cost before reuse. A GitHub star does not mean installed.
- Ban Thao is digital-only. The owner is writing the 28-day book. The seven-page web exercise is illustrative, not approved book content. No tea, physical gift, published price, live checkout or automatic payment confirmation exists. The current catalog is `/a0/usr/projects/money-hq/experiments/exp03-duong-nhan-ai-mvp/products.json`.
- Do not claim publication, payment or delivery without direct evidence. Do not run third-party code just because it is listed in the catalog.

'@

$updated = $addendum + $content
Set-Content -LiteralPath $ProfilePath -Value $updated -Encoding UTF8
Write-Output 'Agent Zero profile updated. Previous version saved locally beside it.'
