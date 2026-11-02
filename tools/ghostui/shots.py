# Render a page at phone/tablet/desktop widths. Usage: python3 shots.py page.html  (needs playwright + chrome)
import sys
from playwright.sync_api import sync_playwright
src=open(sys.argv[1]).read()
if '<html' not in src.lower(): src='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>'+src+'</body></html>'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=next((x for x in ['/usr/bin/google-chrome','/usr/bin/chromium'] if __import__('os').path.exists(x)),None))
    for w,h in [(390,844),(820,1180),(1440,900)]:
        pg=b.new_page(viewport={'width':w,'height':h});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.set_content(src,wait_until='load');pg.wait_for_timeout(600)
        pg.screenshot(path=f'shot-{w}.png',full_page=w<1000)
        print(w,'sideways-scroll' if pg.evaluate('document.documentElement.scrollWidth')>w else 'ok',errs or '')
    b.close()
