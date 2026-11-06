# Owner only, run it yourself (Claude must not change repo protection): lock main on your repos so every other dev's
# change waits for your approval (CER-01 app → Approvals tab). Owner = admin → you can still merge your own PRs.
#   powershell -ExecutionPolicy Bypass -File scripts\protect.ps1                      (default: Ghostskills, cer01-app)
#   powershell -ExecutionPolicy Bypass -File scripts\protect.ps1 -Repos ghostaiproject/Grocerierun
# Private repos need GitHub Pro (or a team plan) for branch protection; GitHub says so per repo if not.
param([string[]]$Repos = @('ghostaiproject/Ghostskills', 'ghostaiproject/cer01-app'), [string]$Owner = 'ghostaiproject')
$ErrorActionPreference = 'Continue'
$Repos = @($Repos | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$rule = @{ required_status_checks = $null; enforce_admins = $false; restrictions = $null; allow_force_pushes = $false; allow_deletions = $false
           required_pull_request_reviews = @{ require_code_owner_reviews = $true; required_approving_review_count = 1; dismiss_stale_reviews = $true } }
$tmp = Join-Path $env:TEMP 'gs-protect.json'
foreach ($r in $Repos) {
    gh api "repos/$r/contents/.github/CODEOWNERS" --silent 2>$null
    if ($LASTEXITCODE) {   # code owner = you, so "required review" means YOUR review
        $c = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("* @$Owner`n"))
        gh api -X PUT "repos/$r/contents/.github/CODEOWNERS" -f message='CODEOWNERS: owner approves every change' -f content=$c --silent 2>&1 | Out-Null
    }
    $checks = @(gh api "repos/$r/commits/HEAD/check-runs" -q '.check_runs[].name' 2>$null | Sort-Object -Unique)
    $rule.required_status_checks = if ($checks) { @{ strict = $false; contexts = $checks } } else { $null }
    [IO.File]::WriteAllText($tmp, ($rule | ConvertTo-Json -Depth 5))
    $out = gh api -X PUT "repos/$r/branches/main/protection" --input $tmp 2>&1
    if ($LASTEXITCODE) { "$r : NOT protected ($(($out | Out-String).Trim() -replace '\s+', ' '))" } else { "$r : main protected (your review required; checks: $($checks -join ', '))" }
}
Remove-Item $tmp -ErrorAction SilentlyContinue
