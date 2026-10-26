"""Bug hunt for the CER-01 site build (site/out/), run before every Pages push.

  python scripts/site_qa.py [out_dir] [--shots DIR]

Loads every page on PC (1366, 1920) and phone (desktop view + compact), opens every window and tab,
and flags: page errors, sideways scroll, text cut off by its box, blank or broken images,
small tap targets, the neural map not filling its card, and the phone view switch losing its zoom.
Exit 1 when any FAIL. Needs Python Playwright; without it, prints SKIP and exits 0.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ['index.html', 'fr.html', 'setup.html', 'setup-fr.html']
PHONE = dict(viewport={'width': 412, 'height': 860}, is_mobile=True, has_touch=True, screen={'width': 412, 'height': 915},
             user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/130 Mobile Safari/537.36')
CONTEXTS = {
    'pc1366': dict(viewport={'width': 1366, 'height': 680}, screen={'width': 1366, 'height': 768}),
    'pc1920': dict(viewport={'width': 1920, 'height': 960}, screen={'width': 1920, 'height': 1080}),
    'phone': PHONE,
    'compact': PHONE,
}

# Text that sticks out of the box that clips it (skips decor, marquees and boxes that scroll sideways on purpose)
CLIP_JS = r"""(scope)=>{const out=[],root=scope?document.querySelector(scope):document.body;if(!root)return out;
const W=document.documentElement.clientWidth;
const skip=e=>e.closest('[aria-hidden="true"],.ticker,[inert],.pcwarn,canvas,svg');
const name=e=>e.tagName.toLowerCase()+(e.id?'#'+e.id:'')+(e.classList.length?'.'+[...e.classList].join('.'):'');
for(const e of root.querySelectorAll('*')){
  if(skip(e))continue;const own=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());if(!own)continue;
  const r=e.getBoundingClientRect(),cs=getComputedStyle(e);if(!r.width||!r.height||cs.visibility==='hidden'||+cs.opacity===0)continue;
  let a=e.parentElement;while(a&&a!==document.body){const s=getComputedStyle(a);
    if(/auto|scroll/.test(s.overflowX))break;
    if(/hidden|clip/.test(s.overflowX)){const b=a.getBoundingClientRect();
      if(r.right>b.right+2||r.left<b.left-2){out.push(name(e)+' "'+e.textContent.trim().slice(0,30)+'" sticks out of '+name(a)+' by '+Math.round(Math.max(r.right-b.right,b.left-r.left))+'px')}break}
    a=a.parentElement}
  if(/hidden|clip/.test(cs.overflowX)&&cs.textOverflow!=='ellipsis'&&e.scrollWidth>e.clientWidth+2)out.push(name(e)+' "'+e.textContent.trim().slice(0,30)+'" cut inside its own box ('+e.scrollWidth+'>'+e.clientWidth+')');
  if(out.length>12)break}
return [...new Set(out)]}"""

PAGE_JS = r"""()=>{const d=document.documentElement,W=d.clientWidth,o=[];
if(d.scrollWidth>W+1)o.push('FAIL sideways scroll: page '+d.scrollWidth+'px wide in a '+W+'px view');
for(const i of document.images){const r=i.getBoundingClientRect();if(r.width&&i.complete&&!i.naturalWidth)o.push('FAIL broken image '+(i.getAttribute('src')||'').slice(0,60))}
const small=[];for(const e of document.querySelectorAll('a[href],button,input,select,[role=tab]')){if(e.closest('[inert],[aria-hidden="true"],label'))continue;
  const r=e.getBoundingClientRect(),cs=getComputedStyle(e);if(!r.width||cs.visibility==='hidden')continue;
  if(r.height<24||r.width<24)small.push((e.textContent.trim()||e.getAttribute('aria-label')||e.tagName).slice(0,24)+' '+Math.round(r.width)+'x'+Math.round(r.height))}
if(small.length)o.push('WARN tap targets under 24px: '+small.slice(0,6).join(', ')+(small.length>6?' +'+(small.length-6):''));
return o}"""


def main():
    args = sys.argv[1:]
    shots = None
    if '--shots' in args:
        i = args.index('--shots'); shots = args[i + 1]; del args[i:i + 2]
        os.makedirs(shots, exist_ok=True)
    out = os.path.abspath(args[0] if args else os.path.join(ROOT, 'site', 'out'))
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('SKIP site_qa: Python Playwright not installed'); return 0
    found = []

    def note(where, msgs):
        for m in msgs:
            m = m if m.startswith(('FAIL', 'WARN')) else 'FAIL ' + m
            found.append(f'{where} | {m}')

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for cname, opts in CONTEXTS.items():
            ctx = b.new_context(**opts)
            ctx.add_init_script("try{localStorage.setItem('cer-view','%s')}catch(e){}" % ('compact' if cname == 'compact' else 'wide'))
            for page in PAGES:
                if not os.path.exists(os.path.join(out, page)):
                    continue
                p = ctx.new_page(); errs = []
                p.on('pageerror', lambda e: errs.append(str(e)[:120]))
                p.on('console', lambda m: m.type == 'error' and 'fonts.g' not in m.text and errs.append(m.text[:120]))
                p.goto('file:///' + os.path.join(out, page).replace('\\', '/')); p.wait_for_timeout(900)
                w = f'{cname} {page}'
                note(w, p.evaluate(PAGE_JS)); note(w, p.evaluate(CLIP_JS, None))
                if cname.startswith('pc') and p.evaluate("()=>document.documentElement.classList.contains('small')||document.documentElement.classList.contains('scaled')||document.documentElement.clientWidth!==innerWidth"):
                    note(w, ['FAIL PC treated as a phone (phone view or Compact button on a computer)'])
                if page in ('index.html', 'fr.html'):
                    check_windows(p, w, note, shots and page == 'index.html' and os.path.join(shots, cname))
                    if cname == 'phone':
                        check_switch(p, w, note)
                note(w, ['page error: ' + e for e in errs])
                p.close()
            ctx.close()
        b.close()
    fails = [f for f in found if '| FAIL' in f]
    for f in found:
        print(f)
    print(f'site_qa: {len(fails)} FAIL, {len(found) - len(fails)} WARN')
    return 1 if fails else 0


def check_windows(p, w, note, shot):
    if shot:
        p.screenshot(path=shot + '-home.jpg', type='jpeg', quality=55)
    if p.locator('button.skband.qsk').count():
        p.click('button.skband.qsk'); p.wait_for_timeout(700)
        for tab in ('#t-map', '#t-dirs', '#t-build'):
            p.click(tab); p.wait_for_timeout(400)
            note(f'{w} skills{tab}', p.evaluate(CLIP_JS, '#win-sk'))
            if tab == '#t-map':
                gap = p.evaluate("()=>{const b=document.querySelector('.mapbox').getBoundingClientRect(),l=document.querySelector('#legend').getBoundingClientRect();return Math.round(b.bottom-l.bottom)}")
                if gap > 3:
                    note(w, [f'FAIL neural map leaves {gap}px empty under the legend'])
                if shot:
                    p.screenshot(path=shot + '-map.jpg', type='jpeg', quality=55)
        p.click('#win-sk .x'); p.wait_for_timeout(400)
    for i in range(p.locator('#projects .proj').count()):
        p.locator('#projects .proj .go').nth(i).click(); p.wait_for_timeout(500)
        note(f'{w} unit{i + 1}', p.evaluate(CLIP_JS, '.win:not([inert])'))
        if p.locator('.win:not([inert]) .x').count():
            p.locator('.win:not([inert]) .x').click(); p.wait_for_timeout(300)


def check_switch(p, w, note):
    if not p.locator('.vmode').count():
        return note(w, ['FAIL no Compact button on a phone'])
    for want in ('compact', 'wide', 'compact', 'wide'):
        p.locator('.vmode').click(); p.wait_for_timeout(700)
        view, width, scale, meta = p.evaluate("()=>[document.documentElement.dataset.view,document.documentElement.clientWidth,visualViewport.scale,document.querySelector('meta[name=viewport]').content]")
        # real phones keep the old zoom unless the viewport names its scale, so both views must set initial-scale
        ok = view == want and 'initial-scale' in meta and ((want == 'wide' and width == 980 and scale < .6) or (want == 'compact' and width < 500 and scale > .95))
        if not ok:
            return note(w, [f'FAIL view switch to {want}: got {view}, {width}px wide, zoom {scale:.2f}, viewport "{meta}"'])


if __name__ == '__main__':
    sys.exit(main())
