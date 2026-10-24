---
name: alexa-console-edit
description: Edit an Alexa skill's interaction model (invocation name, intents, samples, slots) in the Alexa developer console via Claude in Chrome, script-first. Use for any Alexa console model change or build-error fix.
---

# Alexa console edit (token-lean)

Use Claude in Chrome (`mcp__claude-in-chrome__*`). Load in ONE ToolSearch:
`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__find`

**Rule: work through `javascript_tool`, not screenshots.** Take a screenshot only when a script result is unclear. Never dump the whole model; return only the fields you need.

## 1. Find the skill ID (skip if known)

Open `https://developer.amazon.com/alexa/console/ask`, then run:
```js
await new Promise(r=>setTimeout(r,3000));
[...document.querySelectorAll('a[href*="amzn1.ask.skill"]')].map(a=>[a.textContent.trim(), a.href.match(/amzn1\.ask\.skill\.[\w-]+/)[0]])
```

## 2. Open a locale's JSON editor directly

`https://developer.amazon.com/alexa/console/ask/build/custom/<SKILL_ID>/development/<LOCALE>/json-editor`
LOCALE uses an underscore: `en_CA`, `fr_CA`, `en_US`, …

Popups like "global build update" can be ignored. Scripts work behind them.

## 3. Read only what you need

```js
await new Promise(r=>setTimeout(r,4000));
const lm = JSON.parse(ace.edit(document.querySelector('.ace_editor')).getValue()).interactionModel.languageModel;
({inv: lm.invocationName, intents: lm.intents.map(i=>[i.name, (i.samples||[]).length])})
```

## 4-7. Only when needed
- Change + save + reload-check → read EDIT.md (next to this file).
- Build once after all locales saved, then check the result → read BUILD.md.

## Report
One line per locale (what changed) + build result. Close the tab you opened unless the user wants it.
