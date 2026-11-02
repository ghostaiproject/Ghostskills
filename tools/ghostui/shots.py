# Render a page at phone/tablet/desktop widths + report spills and text overlaps. Usage: python3 shots.py page.html  (needs playwright + chrome)
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
# text sitting on other text (captions/titles laid over a scene, labels colliding)
OVER="""()=>{const T=[],fx=e=>{for(;e&&e!==document.body;e=e.parentElement)if(getComputedStyle(e).position==='fixed')return 1};for(const e of document.querySelectorAll('body *')){
 const s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden'||+s.opacity===0||fx(e))continue;
 if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;const r=e.getBoundingClientRect();if(r.width&&r.height)T.push([e,r])}
 const out=[],nm=e=>e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+(typeof e.className==='string'&&e.className.trim()?'.'+e.className.trim().split(/\\s+/)[0]:'');
 for(let i=0;i<T.length;i++)for(let j=i+1;j<T.length;j++){const[a,A]=T[i],[b,B]=T[j];if(a.contains(b)||b.contains(a))continue;
  const w=Math.min(A.right,B.right)-Math.max(A.left,B.left),h=Math.min(A.bottom,B.bottom)-Math.max(A.top,B.top);
  if(w>4&&h>4&&w*h>.2*Math.min(A.width*A.height,B.width*B.height)){out.push(nm(a)+' × '+nm(b));if(out.length>=6)return out}}
 return out}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=next((x for x in ['/usr/bin/google-chrome','/usr/bin/chromium'] if os.path.exists(x)),None))
    for w,h in [(390,844),(820,1180),(1440,900)]:
        pg=b.new_page(viewport={'width':w,'height':h});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.set_content(src,wait_until='load');pg.wait_for_timeout(600)
        pg.screenshot(path=f'shot-{w}.png',full_page=w<1000)
        side='sideways-scroll' if pg.evaluate('document.documentElement.scrollWidth')>w else 'ok'
        sp=pg.evaluate(SPILL);ov=pg.evaluate(OVER)
        print(w,side,('spills: '+', '.join(sp)) if sp else 'no spills',('| overlaps: '+', '.join(ov)) if ov else '| no overlaps',errs or '')
    b.close()
