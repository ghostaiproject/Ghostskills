# Render a page at phone/tablet/desktop widths + report spills. Usage: python3 shots.py page.html  (needs playwright + chrome)
import sys,os
from playwright.sync_api import sync_playwright
src=open(sys.argv[1]).read()
if '<html' not in src.lower(): src='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>'+src+'</body></html>'
# elements sticking out of their parent box (parent not scrolling/clipping), ignoring positioned decor and svg internals
SPILL="""()=>{const out=[];for(const e of document.querySelectorAll('body *')){
 if(e.closest('svg')&&e.tagName.toLowerCase()!=='svg')continue;const s=getComputedStyle(e);
 if(s.position==='absolute'||s.position==='fixed'||s.display==='none'||s.visibility==='hidden')continue;
 const p=e.parentElement;if(!p||p===document.body)continue;const ps=getComputedStyle(p);
 if(/(auto|scroll|hidden|clip)/.test(ps.overflowX))continue;
 const r=e.getBoundingClientRect(),q=p.getBoundingClientRect();if(!r.width)continue;
 const o=Math.round(Math.max(r.right-q.right,q.left-r.left));
 if(o>2){out.push(e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+(e.className&&typeof e.className==='string'?'.'+e.className.trim().split(/\\s+/)[0]:'')+' +'+o+'px');if(out.length>=6)break}}
 return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=next((x for x in ['/usr/bin/google-chrome','/usr/bin/chromium'] if os.path.exists(x)),None))
    for w,h in [(390,844),(820,1180),(1440,900)]:
        pg=b.new_page(viewport={'width':w,'height':h});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.set_content(src,wait_until='load');pg.wait_for_timeout(600)
        pg.screenshot(path=f'shot-{w}.png',full_page=w<1000)
        side='sideways-scroll' if pg.evaluate('document.documentElement.scrollWidth')>w else 'ok'
        sp=pg.evaluate(SPILL)
        print(w,side,('spills: '+', '.join(sp)) if sp else 'no spills',errs or '')
    b.close()
