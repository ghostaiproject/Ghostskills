# Alexa build + check

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
