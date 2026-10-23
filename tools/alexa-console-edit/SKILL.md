---
name: alexa-console-edit
description: Edit an Alexa skill's interaction model (invocation name, intents, samples, slots) in the Alexa developer console through Claude in Chrome with few tokens — script the Ace JSON editor, save, check by reloading, build. Use for any Alexa console model change or build-error fix (e.g. "invocation name empty", per-locale fixes).
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

## 4. Edit + save in one call

```js
const ed = ace.edit(document.querySelector('.ace_editor'));
const m = JSON.parse(ed.getValue()); const lm = m.interactionModel.languageModel;
// --- edits ---
lm.invocationName = "my invocation";             // lowercase letters, spaces, apostrophes, periods; 2–50 chars
lm.intents = lm.intents.filter(i=>i.name!=="MyIntent");
lm.intents.unshift({name:"MyIntent", slots:[], samples:["..."]});   // keep the AMAZON.* intents
// --------------
ed.setValue(JSON.stringify(m, null, 4), -1);
await new Promise(r=>setTimeout(r,1000));        // let the page register the change BEFORE saving
[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Save').click();
await new Promise(r=>setTimeout(r,4000)); 'saved?'
```

## 5. Check by reloading (always required)

A save can fail without any error; this happened once when Save was clicked right after `setValue`. Navigate to the same URL again and run step 3. If the value didn't change, repeat step 4.

## 6. Build once, after every locale is saved and checked

"Build skill" builds **all locales**, so run it once at the end:
```js
[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Build skill').click();
await new Promise(r=>setTimeout(r,1500));
const b=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Build' && b.offsetParent); b&&b.click(); 'build started'
```
(A confirm dialog appears only if "Don't show this message again" was never ticked.)

## 7. Check the build result

Builds take about 30–90 s. **Don't loop inside one JS call.** The tool times out after 45 s and the page can freeze. Instead, use `computer` `wait` (10 s each, several in one `browser_batch`), then:
```js
document.querySelector('[class*="toolbar"], body').innerText.match(/Build (in progress|Failed|Successful|Completed)[^\n]*|Last successful build[^\n]*|\d+\s*errors?/gi)
```
If the result is unclear, take ONE screenshot at `scale: 0.6` and look at the bottom "Errors and Warnings" bar (error count, plus a red line for each locale).

## Report

Give one line per locale saying what changed, plus the build result. Close the tab you opened unless the user wants it.
