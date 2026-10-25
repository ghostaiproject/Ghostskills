# Lessons · all
- A scheduled GitHub Action can stall at action_required after commits from another account → check the last run on /load.
- Windows `git clone` fails "Filename too long" → `git -c core.longpaths=true clone`. · ghost 2026-10-23
- Bug seen on phone in a claude.ai link → fix that artifact (read → change → republish same url); repo copies drift from it. · ghost 2026-10-23
- Chrome window won't go under ~550 px → test phone width in a 375×812 iframe of the page. · ghost 2026-10-23
- Edit tool turns `\uXXXX` into the literal char → write escapes with a script; local http.server sends no charset, so garbled text there isn't the page's bug. · ghost 2026-10-23
- Cloud session, Python Playwright: pip version ≠ preinstalled browser → `chromium.launch(executable_path=<glob /opt/pw-browsers/chromium-*/chrome-linux64/chrome>)`, never `playwright install`. · ghost 2026-10-25
