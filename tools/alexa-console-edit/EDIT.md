# Alexa edit + verify

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
