# UserPromptSubmit hook: puts the working loop in context on every prompt.
# Chatty prompts get one line; real tasks get the checklist. Never blocks, never fails a turn.
$raw = @($input) -join "`n"
if (-not $raw) { try { $raw = [Console]::In.ReadToEnd() } catch { $raw = '' } }
$p = ''
if ($raw -match '"prompt"\s*:\s*"([^"]*)') { $p = $Matches[1] }

Write-Output "AUTOLOOP: plan -> act -> verify for real -> ship -> wrap up."
$work = ($p.Length -ge 60) -or ($p -match '(?i)\b(build|fix|add|make|change|update|ship|deploy|refactor|improve|test|publish|install|sync|run|write|check|redo|clean)\b')
if ($work) {
  Write-Output "- first tool call carries update_plan with the whole plan; advance as steps finish"
  Write-Output "- batch independent tool calls; grep/sed instead of whole-file reads; no screenshots unless asked"
  Write-Output "- verify in the real app/browser before saying done; name what is unverified"
  Write-Output "- commit + push finished work; bundle every open choice into ONE AskUserQuestion"
}
exit 0
