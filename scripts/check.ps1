# Lint every skill against CONVENTIONS.md (+ secrets, token cost). -Tokens: per-skill token table. -Pack: zip each skill into dist/ for claude.ai upload. -Drift: compare with ~/.claude/skills.
param([switch]$Pack, [switch]$Drift, [switch]$Tokens)
$root = Split-Path $PSScriptRoot -Parent
$script:fails = 0
function Fail($m) { Write-Output "FAIL $m"; $script:fails++ }
function Warn($m) { Write-Output "warn $m" }

$skills = Get-ChildItem $root -Recurse -Filter SKILL.md | Where-Object { $_.FullName -notmatch '[\\/](\.git|dist|_template)[\\/]' }
$repos = Get-ChildItem (Join-Path $root 'projects') -Recurse -Filter SKILL.md | ForEach-Object {
    if ((Get-Content $_.FullName -Raw) -match 'repo ([\w.-]+/[\w.-]+)') { $Matches[1] } } | Sort-Object -Unique
$nums = @{}
$rows = @()
$tok = { param($n) [math]::Ceiling($n / 4) }  # rough: ~4 chars per token

foreach ($f in $skills) {
    $dir = $f.Directory.Name
    $rel = $f.FullName.Substring($root.Length + 1) -replace '\\', '/'
    $text = Get-Content $f.FullName -Raw
    if ($text -notmatch '(?s)^---\r?\n(.*?)\r?\n---') { Fail "${rel}: no frontmatter"; continue }
    $fm = $Matches[1]
    $name = if ($fm -match '(?m)^name:\s*(.+?)\s*$') { $Matches[1] } else { '' }
    $desc = if ($fm -match '(?m)^description:\s*(.+?)\s*$') { $Matches[1] } else { '' }
    if ($name -ne $dir) { Fail "${rel}: name '$name' != folder '$dir'" }
    if (-not $desc) { Fail "${rel}: no one-line description" }
    elseif ($desc.Length -gt 300) { Warn "${rel}: description is $($desc.Length) chars" }
    $kb = [math]::Round($f.Length / 1KB, 1)
    $rows += [pscustomobject]@{ Skill = $rel; Desc = (& $tok $desc.Length); Body = (& $tok $text.Length) }
    if ($kb -gt 5) { Fail "${rel}: $kb KB > 5 KB cap" } elseif ($kb -gt 2) { Warn "${rel}: $kb KB > 2 KB target" }

    $top, $ctx = ($rel -split '/')[0, 1]
    if ($top -eq 'core') {
        foreach ($r in $repos) { if ($text -match [regex]::Escape($r)) { Fail "${rel}: core names project repo $r" } }
    }
    if ($top -eq 'projects') {
        if (-not $dir.StartsWith("$ctx-")) { Fail "${rel}: project skill must start with '$ctx-'" }
        if ($dir -eq "$ctx-card") {
            if ($desc -notmatch '\(#(\d+)\)') { Fail "${rel}: card description needs its menu number, e.g. (#4)" }
            elseif ($nums[$Matches[1]]) { Fail "${rel}: #$($Matches[1]) already used by $($nums[$Matches[1]])" }
            else { $nums[$Matches[1]] = $ctx }
        }
    }
}
Get-ChildItem (Join-Path $root 'projects') -Directory | Where-Object Name -ne '_template' | ForEach-Object {
    if (-not (Test-Path (Join-Path $_.FullName "$($_.Name)-card/SKILL.md"))) { Fail "projects/$($_.Name): no $($_.Name)-card" }
}
# edged/ is public and loaded every chat: size caps + no private data.
$edged = Join-Path $root 'edged'
if (Test-Path $edged) {
    Get-ChildItem $edged -Recurse -Filter *.md | ForEach-Object {
        $rel = $_.FullName.Substring($root.Length + 1) -replace '\\', '/'
        $cap = if ($_.Name -eq 'CORE.md') { 1.5 } elseif ($_.Directory.Name -eq 'people') { 1 } else { 4 }
        $kb = [math]::Round($_.Length / 1KB, 2)
        if ($kb -gt $cap) { Fail "${rel}: $kb KB > $cap KB edged cap" }
        $text = Get-Content $_.FullName -Raw
        if ($text -match '[\w.+-]+@[\w-]+\.[a-z]{2,}') { Fail "${rel}: looks like an email ($($Matches[0])); edged is public" }
        if ($text -match '(?<![\w.-])(\+\d{1,3}[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?![\w-])' -or $text -match '(?<!\w)\+\d{9,15}(?!\w)') { Fail "${rel}: looks like a phone number; edged is public" }
    }
}
# Secrets/emails anywhere in the (public) repo, not just edged/.
$secretRx = 'ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
Get-ChildItem $root -Recurse -File -Include *.md,*.json,*.ps1,*.py,*.yml,*.txt | Where-Object { $_.FullName -notmatch '[\\/](\.git|dist)[\\/]' } | ForEach-Object {
    $rel = $_.FullName.Substring($root.Length + 1) -replace '\\', '/'
    $text = Get-Content $_.FullName -Raw
    if (-not $text) { return }
    if ($text -match $secretRx) { Fail "${rel}: looks like a secret/token" }
    if ($rel -ne 'scripts/check.ps1' -and $text -match '[\w.+-]+@[\w-]+\.[a-z]{2,}' -and $Matches[0] -notmatch '@(example\.(com|org)|users\.noreply\.github\.com)$|^noreply@') { Fail "${rel}: looks like an email ($($Matches[0])); repo is public" }
}
# Token cost: descriptions are paid in every chat, bodies only when a skill fires.
$descTotal = ($rows | Measure-Object Desc -Sum).Sum
$edgedLoad = 0
foreach ($e in @('edged/CORE.md')) { $ep = Join-Path $root $e; if (Test-Path $ep) { $edgedLoad += (& $tok (Get-Item $ep).Length) } }
Write-Output "tokens: ~$descTotal always-loaded in skill descriptions, ~$edgedLoad for edged CORE, heaviest body ~$(($rows | Measure-Object Body -Maximum).Maximum)"
if ($descTotal -gt 3000) { Fail "skill descriptions cost ~$descTotal tokens/chat > 3000 budget" }
if ($Tokens) { $rows | Sort-Object Body -Descending | Format-Table -AutoSize | Out-String -Width 200 | Write-Output }
Write-Output "$($skills.Count) skills checked, $script:fails failed"

if ($Pack) {
    $dist = Join-Path $root 'dist'
    New-Item -ItemType Directory -Force $dist | Out-Null
    Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem
    foreach ($f in $skills) {
        # ZipFile by hand: Compress-Archive on Windows PowerShell writes '\' in entry names, which other unzippers mangle.
        $zipPath = Join-Path $dist "$($f.Directory.Name).zip"
        Remove-Item $zipPath -ErrorAction SilentlyContinue
        $zip = [IO.Compression.ZipFile]::Open($zipPath, 'Create')
        try {
            Get-ChildItem $f.Directory.FullName -Recurse -File | ForEach-Object {
                $entry = $f.Directory.Name + '/' + ($_.FullName.Substring($f.Directory.FullName.Length + 1) -replace '\\', '/')
                [void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, $entry)
            }
        } finally { $zip.Dispose() }
    }
    Write-Output "Packed $($skills.Count) zips in dist/ -> upload the changed ones on claude.ai"
}

if ($Drift) {
    $installed = Join-Path $HOME '.claude/skills'
    Get-ChildItem $installed -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $mine = Join-Path $_.FullName 'SKILL.md'; $n = $_.Name
        $repo = $skills | Where-Object { $_.Directory.Name -eq $n } | Select-Object -First 1
        if (-not $repo) { Write-Output "drift $($_.Name): installed, not in repo" }
        elseif ((Get-FileHash $mine).Hash -ne (Get-FileHash $repo.FullName).Hash) { Write-Output "drift $($_.Name): installed copy differs from repo" }
        else { Write-Output "same  $($_.Name)" }
    }
}
if ($script:fails) { exit 1 }
