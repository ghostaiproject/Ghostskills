---
name: next
description: Use at the end of EVERY reply to a user prompt: if a next step is possible, end with one multiple-choice picker of next implementations (works on phone/Remote Control too); after page/app/project changes, first a visual review (before vs after, + Gemini critique).
---
# Next-step question (every prompt)
After every user prompt → check for a next step. Possible → last thing in the reply is one multiple-choice question. None (pure fact answer, user said stop) → skip.

## Visual review (end of a task that changed a page, app or project look)
1. Open the result where the user sees it (Chrome; built-in browser if no Chrome): before = previous version/other tab, after = new. Cover every state, not just the landing view: popups/modals, windows, subpages, tabs, hover/open states, phone width. Screenshot each before/after pair at `scale` 0.5.
2. Same time: paste the after screenshot in Gemini (Chrome, `gemini.google.com/app`, clipboard + ctrl+v) → "Art-director critique of this page: top 5 concrete visual fixes, 1 line each."
3. Merge own + Gemini findings → keep max 4 that are concrete and doable now; drop generic ones.
4. Close tabs you opened.

## Choice
- AskUserQuestion picker, never a prose question (it shows on phone/Remote Control too). Picker not available → in-chat `show_widget` card with 2–4 `sendPrompt` buttons, plus the same options as a numbered line.
- 2–4 options, short labels, 1-line description each; first = recommended.
- Options = next implementations on what was just built/found (review fixes, follow-up features, new elements, look/function ideas), not generic help.
- Picked → do it. "Stop"/no → stop, ask nothing more.
- Findings text: 1 line per point, no recap.
