---
name: next
description: Use after any action Claude takes on the user's computer (Chrome, built-in browser, desktop apps, its files): end the reply with one short next-step question; after page/app/project changes, first a visual review (before vs after, + Gemini critique).
---
# Next-step question (computer work)
After any action on the user's computer → last thing in the reply is one next-step choice.

## Visual review (end of a task that changed a page, app or project look)
1. Open the result where the user sees it (Chrome; built-in browser if no Chrome): before = previous version/other tab, after = new. Cover every state, not just the landing view: popups/modals, windows, subpages, tabs, hover/open states, phone width. Screenshot each before/after pair at `scale` 0.5.
2. Same time: paste the after screenshot in Gemini (Chrome, `gemini.google.com/app`, clipboard + ctrl+v) → "Art-director critique of this page: top 5 concrete visual fixes, 1 line each."
3. Merge own + Gemini findings → keep max 4 that are concrete and doable now; drop generic ones.
4. Close tabs you opened.

## Choice
- AskUserQuestion picker (terminal-style), never a prose question: 2–4 options, short labels, 1-line description each; first = recommended.
- Options = concrete actions on what's open now (fixes from the review), not generic help.
- Picked → do it. "Stop"/no → stop, ask nothing more.
- Findings text: 1 line per point, no recap.
