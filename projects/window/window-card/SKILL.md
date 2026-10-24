---
name: window-card
description: Use only when a core skill (load, save, cmds) picks window (#3): holds the window-alert project's card (Echo says when to open the windows). Never typed by the user.
---
# window card
ctx window · #3 · Echo open-windows alert · repo ghostaiproject/Ouvrelesfnetre · branch main · state HANDOFF.md · also load: — · save extras: —.
Load extras: same batch, one Bash: `gh run list --repo ghostaiproject/Ouvrelesfnetre --workflow window-alert.yml --limit 1 --json conclusion,createdAt,url`. Not success → say it first (alerts are NOT going out) + run link; action_required → user approves it in that link.
Ship: no version; main is live (cron every 15 min + Pages /docs). 1) `pytest -q` (Windows: py -3.12) 2) alert.py or flair.py changed → `python skill/build.py`, then tell the user to redeploy in the Alexa console Code tab 3) commit + push (no [skip ci]) 4) /test main. Alexa model change → alexa-console-edit skill.
List: secret names only (`gh secret list --repo ghostaiproject/Ouvrelesfnetre`), HOME_/PHONE_/GHOME_ = one home each, never values; + docs/*.html pages.
Extra cmds: /test <home|main|all> → `gh workflow run window-alert.yml --repo ghostaiproject/Ouvrelesfnetre -f home=<home>`, then one `gh run list ... --limit 1 --json url` → link. /homes → the List line's homes only.
