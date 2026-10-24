"""crew: free second brains for Claude. One command in, at most 10 short lines out.

  crew.py route "<request>"                  which brains fit (keywords), or skip
  crew.py auto "<request>"                   route + run each matching brain
  crew.py gemini "<scene>" [--fmt 16:9|1:1|9:16] [--style film|anime|gouache|ink]
  crew.py calc "<expr | convert 5 km to mi | sum 1,2,3 | clean <file>>"  [--code "<python>"]
  crew.py gpt "<question>"                   second opinion (optional brain)
  crew.py status | login gemini|gpt | clear  (add --fresh to skip the cache)

No API keys, no paid APIs: Gemini and ChatGPT run in their free web apps through Playwright,
each with its own persistent profile in ~/.crew/profiles (sign in once with `login`).
Exit codes: 0 done or skipped, 3 needs the user to sign in.
"""
import argparse, ast, base64, csv, hashlib, json, math, os, re, shutil, struct, subprocess, sys, tempfile, time
from contextlib import contextmanager
from pathlib import Path

HOME = Path(os.environ.get('CREW_HOME', Path.home() / '.crew'))
CACHE, IMAGES, PROFILES, STATE = HOME / 'cache', HOME / 'images', HOME / 'profiles', HOME / 'state.json'
MAX_LINES, LINE_CAP, REPLY_CAP = 10, 220, 700
OUT = []


def say(*lines):
    for text in lines:
        for line in str(text).splitlines():
            if line.strip() and len(OUT) < MAX_LINES:
                OUT.append(line if len(line) <= LINE_CAP else line[:LINE_CAP - 1] + '…')


def cap(text, limit=REPLY_CAP):
    text = re.sub(r'\n{2,}', '\n', text.strip())
    return text if len(text) <= limit else text[:limit - 1] + '…'


class NeedLogin(Exception): pass   # user must sign in: never retried
class Skip(Exception): pass        # free-tier limit, bot check, refusal: skip the brain


# ---------- triage + cache ----------
ROUTES = [
    ('gemini', r'\b(images?|wallpapers?|draw\w*|render\w*)\b'),
    ('calc', r'\b(calc\w*|convert\w*|conversions?|sum|sums|summing|clean\w*)\b'),
    ('gpt', r'\b(opinions?|second[- ]opinion)\b'),
]


def route(text):
    return [brain for brain, rx in ROUTES if re.search(rx, text, re.I)]


def cache_key(*parts):
    return hashlib.sha256('\n'.join(map(str, parts)).encode()).hexdigest()[:24]


def cache_get(key):
    f = CACHE / f'{key}.json'
    if not f.exists():
        return None
    lines = json.loads(f.read_text('utf-8'))
    paths = [l.split(': ', 1)[1].rsplit(' (', 1)[0] for l in lines if l.startswith('OK gemini image: ')]
    return None if any(not Path(p).exists() for p in paths) else lines


def cache_put(key, lines):
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / f'{key}.json').write_text(json.dumps(lines), 'utf-8')


def cached(key, fresh, fn):
    hit = None if fresh else cache_get(key)
    if hit:
        say(*hit, '(cache: nothing called)')
        return
    start = len(OUT)
    fn()
    new = OUT[start:]
    if new and new[0].startswith('OK'):
        cache_put(key, new)


# ---------- brain 2: local Python ----------
UNITS = {  # unit: (kind, factor to base unit)
    'mm': ('len', .001), 'cm': ('len', .01), 'm': ('len', 1), 'km': ('len', 1000), 'in': ('len', .0254),
    'ft': ('len', .3048), 'yd': ('len', .9144), 'mi': ('len', 1609.344),
    'mg': ('mass', 1e-6), 'g': ('mass', .001), 'kg': ('mass', 1), 'oz': ('mass', .028349523125), 'lb': ('mass', .45359237),
    'ml': ('vol', .001), 'l': ('vol', 1), 'cup': ('vol', .2365882365), 'gal': ('vol', 3.785411784),
    's': ('time', 1), 'min': ('time', 60), 'h': ('time', 3600), 'day': ('time', 86400), 'week': ('time', 604800),
    'm2': ('area', 1), 'ft2': ('area', .09290304), 'km2': ('area', 1e6), 'ha': ('area', 1e4), 'acre': ('area', 4046.8564224),
    'kmh': ('speed', 1 / 3.6), 'mph': ('speed', .44704), 'ms': ('speed', 1),
    'b': ('data', 1), 'kb': ('data', 1e3), 'mb': ('data', 1e6), 'gb': ('data', 1e9), 'tb': ('data', 1e12),
    'c': ('temp', None), 'f': ('temp', None), 'k': ('temp', None),
}
ALIASES = {'mile': 'mi', 'miles': 'mi', 'feet': 'ft', 'foot': 'ft', 'inch': 'in', 'inches': 'in', 'meter': 'm',
           'meters': 'm', 'metre': 'm', 'lbs': 'lb', 'pound': 'lb', 'pounds': 'lb', 'liter': 'l', 'litre': 'l',
           'liters': 'l', 'hr': 'h', 'hour': 'h', 'hours': 'h', 'sec': 's', 'days': 'day', 'km/h': 'kmh',
           'm/s': 'ms', 'sqft': 'ft2', 'sqm': 'm2', '°c': 'c', '°f': 'f', 'celsius': 'c', 'fahrenheit': 'f', 'kelvin': 'k'}


def unit(u):
    u = u.lower().replace('²', '2')
    return ALIASES.get(u, u.rstrip('s') if u.rstrip('s') in UNITS and u not in UNITS else u)


def convert(value, a, b):
    a, b = unit(a), unit(b)
    if a not in UNITS or b not in UNITS or UNITS[a][0] != UNITS[b][0]:
        raise ValueError(f'cannot convert {a} to {b}')
    if UNITS[a][0] == 'temp':
        k = {'c': value + 273.15, 'f': (value - 32) * 5 / 9 + 273.15, 'k': value}[a]
        return {'c': k - 273.15, 'f': (k - 273.15) * 9 / 5 + 32, 'k': k}[b]
    return value * UNITS[a][1] / UNITS[b][1]


SAFE = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
SAFE.update(abs=abs, round=round, min=min, max=max, sum=sum, pow=pow)


def safe_eval(expr):
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
        if isinstance(n, ast.BinOp):
            l, r = ev(n.left), ev(n.right)
            ops = {ast.Add: lambda: l + r, ast.Sub: lambda: l - r, ast.Mult: lambda: l * r, ast.Div: lambda: l / r,
                   ast.FloorDiv: lambda: l // r, ast.Mod: lambda: l % r, ast.Pow: lambda: l ** r}
            return ops[type(n.op)]()
        if isinstance(n, ast.UnaryOp): return {ast.USub: -1, ast.UAdd: 1}[type(n.op)] * ev(n.operand)
        if isinstance(n, ast.Name) and n.id in SAFE: return SAFE[n.id]
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in SAFE:
            return SAFE[n.func.id](*[ev(a) for a in n.args])
        if isinstance(n, (ast.List, ast.Tuple)): return [ev(e) for e in n.elts]
        raise ValueError(f'not allowed: {ast.dump(n)[:60]}')
    return ev(ast.parse(expr.replace('^', '**').replace('×', '*').replace(',', '') if ',' in expr and '(' not in expr
                        else expr.replace('^', '**').replace('×', '*'), mode='eval'))


def fmt_num(x):
    return f'{x:,.6g}' if isinstance(x, float) else f'{x:,}'


def clean_file(path):
    src = Path(path.strip('"\''))
    if not src.exists():
        raise ValueError(f'no such file: {src}')
    dst = src.with_name(f'{src.stem}.clean{src.suffix}')
    raw = src.read_text('utf-8-sig', errors='replace').splitlines()
    if src.suffix.lower() in ('.csv', '.tsv'):
        delim = '\t' if src.suffix.lower() == '.tsv' else ','
        rows = [[c.strip() for c in r] for r in csv.reader(raw, delimiter=delim)]
        rows = [r for r in rows if any(r)]
        seen, keep = set(), []
        for r in rows:
            if tuple(r) not in seen: seen.add(tuple(r)); keep.append(r)
        with open(dst, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f, delimiter=delim).writerows(keep)
        n_in, n_out = len(raw), len(keep)
    else:
        lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in raw]
        keep = list(dict.fromkeys(l for l in lines if l))
        dst.write_text('\n'.join(keep) + '\n', 'utf-8')
        n_in, n_out = len(raw), len(keep)
    check = len(dst.read_text('utf-8').splitlines()) == n_out
    say(f'OK calc clean: {dst}', f'{n_in} lines in → {n_out} kept (trimmed, blanks + duplicates removed)',
        'check: row count matches' if check else 'NOT verified: row count differs after write')


def run_code(code):
    with tempfile.TemporaryDirectory() as tmp:
        try:
            r = subprocess.run([sys.executable, '-I', '-c', code], cwd=tmp, capture_output=True, text=True,
                               timeout=30, encoding='utf-8', errors='replace')
        except subprocess.TimeoutExpired:
            return say('skipped calc: script ran over 30 s')
    body = cap((r.stdout or '') + (('\n' + r.stderr) if r.returncode else ''), 600)
    say(f'OK calc script (exit {r.returncode})' if r.returncode == 0 else f'calc script failed (exit {r.returncode})',
        body or '(no output)', 'NOT verified: script output not cross-checked')


def calc(text, code=None):
    t = text.strip()
    if code or '\n' in t or 'print(' in t:
        return run_code(code or t)
    if m := re.match(r'(?i)clean\s+(.+)$', t):
        return clean_file(m.group(1))
    if m := re.match(r'(?i)(?:convert\s+)?(-?[\d.,]+)\s*([^\s\d][^\s]*)\s+(?:to|in|into|->)\s+(\S+)$', t):
        v, a, b = float(m.group(1).replace(',', '')), m.group(2), m.group(3)
        out = convert(v, a, b)
        back = convert(out, b, a)
        ok = math.isclose(back, v, rel_tol=1e-9, abs_tol=1e-9)
        return say(f'OK calc: {fmt_num(v)} {a} = {fmt_num(round(out, 6))} {b}',
                   'check: round-trip OK' if ok else 'NOT verified: round-trip mismatch')
    if m := re.match(r'(?i)sum\s+(.+)$', t):
        nums = [float(x.replace(',', '')) for x in re.findall(r'-?\d[\d,]*\.?\d*', m.group(1))]
        total = math.fsum(nums)
        return say(f'OK calc: sum of {len(nums)} numbers = {fmt_num(total)}',
                   'check: recount OK' if math.isclose(total, sum(sorted(nums))) else 'NOT verified: recount differs')
    expr = re.sub(r'(?i)^(calc(ulate)?|what is|compute)\s*', '', t).rstrip('?= ')
    expr = re.sub(r'(\d+(?:\.\d+)?)\s*%\s*of\s*', r'\1/100*', expr)
    val = safe_eval(expr)
    say(f'OK calc: {expr} = {fmt_num(val)}', 'check: evaluated locally (exact Python math)')


# ---------- browser plumbing (Gemini + ChatGPT) ----------
URLS = {'gemini': 'https://gemini.google.com/app', 'gpt': 'https://chatgpt.com/'}
LOGIN_URLS = {'gemini': 'https://accounts.google.com/ServiceLogin?continue=https://gemini.google.com/app',
              'gpt': 'https://chatgpt.com/auth/login'}
LIMIT_RX = re.compile(r"(reached (your|the|a) .{0,20}limit|usage (limit|cap)|rate limit|too many requests|"
                      r"try again (later|tomorrow|in)|quota|limite (atteinte|quotidienne)|réessayez plus tard|"
                      r"you'?ve (hit|reached))", re.I)
BOT_RX = re.compile(r'(verify you are human|just a moment|unusual activity|vérifiez que vous êtes|captcha)', re.I)


def browser_exe():
    for p in (r'C:\Program Files\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
              r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'):
        if Path(p).exists():
            return p
    return None


def channels():
    exe = (browser_exe() or '').lower()
    first = ['chrome'] if 'chrome.exe' in exe else ['msedge'] if 'msedge' in exe else []
    return first + [c for c in ('msedge', 'chromium') if c not in first]


def state(brain=None, **update):
    data = json.loads(STATE.read_text('utf-8')) if STATE.exists() else {}
    if update:
        data.setdefault(brain, {}).update(update)
        HOME.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(data, indent=1), 'utf-8')
    return data.get(brain, {}) if brain else data


@contextmanager
def browser(brain, mode, channel):
    from playwright.sync_api import sync_playwright
    prof = PROFILES / brain
    prof.mkdir(parents=True, exist_ok=True)
    args = ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check']
    if mode == 'offscreen':
        args += ['--window-position=-32000,-32000', '--window-size=1280,900']
    ua = state(brain).get('ua')
    if mode == 'headless' and ua:
        args.append(f'--user-agent={ua}')
    kw = dict(user_data_dir=str(prof), headless=mode == 'headless', args=args, accept_downloads=True,
              ignore_default_args=['--enable-automation'], viewport={'width': 1280, 'height': 900})
    if channel != 'chromium':
        kw['channel'] = channel
    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(**kw)
        except Exception:
            try: (prof / 'lockfile').unlink(missing_ok=True)
            except PermissionError: raise Skip('profile busy: close the sign-in window first')
            for lock in ('SingletonLock', 'SingletonCookie', 'SingletonSocket'):
                try: (prof / lock).unlink()
                except OSError: pass
            ctx = p.chromium.launch_persistent_context(**kw)
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            real = page.evaluate('navigator.userAgent')
            if 'Headless' in real and not ua:  # headless Chrome announces itself; relaunch looking like normal Chrome
                state(brain, ua=real.replace('HeadlessChrome', 'Chrome'))
                raise RuntimeError('headless UA fixed, retrying')
            ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
            yield ctx, page
        finally:
            ctx.close()


def first(page, sels, timeout=8000):
    """First visible match among several selectors (sites change; retry other selectors before failing)."""
    end = time.time() + timeout / 1000
    while time.time() < end:
        for s in sels:
            loc = page.locator(s)
            try:
                if loc.count() and loc.last.is_visible():
                    return loc.last
            except Exception:
                pass
        page.wait_for_timeout(400)
    return None


def open_site(ctx, page, brain, variant):
    slow = variant != 'plain'
    if variant == 'fresh':
        for p in ctx.pages[1:]: p.close()
        page = ctx.new_page()
    page.goto(URLS[brain], wait_until='domcontentloaded', timeout=45000)
    if variant == 'reload':
        page.wait_for_timeout(2000)
        page.reload(wait_until='domcontentloaded')
    page.wait_for_timeout(4000 if slow else 2000)
    return page, slow


def body_text(page):
    try: return page.evaluate('document.body ? document.body.innerText.slice(0, 4000) : ""')
    except Exception: return ''


def last_text(page, sels):
    for s in sels:
        loc = page.locator(s)
        if loc.count():
            return loc.last.inner_text()
    return ''


def count(page, sels):
    return max(page.locator(s).count() for s in sels)


def send(page, inputs, sends, resps, text, slow):
    box = first(page, inputs, 20000 if slow else 12000)
    if not box:
        raise RuntimeError('prompt box not found')
    before = count(page, resps)
    box.click()
    page.keyboard.insert_text(text)
    page.wait_for_timeout(800)
    btn = first(page, sends, 4000)
    if btn and btn.is_enabled():
        btn.click()
    else:
        page.keyboard.press('Enter')
    for _ in range(30):  # make sure it really went out; Enter as a second way
        page.wait_for_timeout(500)
        if count(page, resps) > before:
            return before
        if _ == 12:
            box.click(); page.keyboard.press('Enter')
    raise RuntimeError('prompt did not send')


def run_web(brain, job, budget=420):
    """Retry-first: plain → reload → other window mode → fresh tab → other browser. Stops early on login/limits."""
    st = state(brain)
    modes = ['headless', 'offscreen'] if st.get('mode', 'headless') == 'headless' else ['offscreen', 'headless']
    chans = channels()
    ch = st.get('channel') if st.get('channel') in chans else chans[0]
    steps = [(modes[0], ch, 'plain'), (modes[0], ch, 'plain'), (modes[0], ch, 'reload'),
             (modes[1], ch, 'plain'), (modes[1], ch, 'fresh')] + [(modes[1], c, 'plain') for c in chans if c != ch]
    start, errors, launch_fails = time.time(), [], 0
    for i, (mode, chan, variant) in enumerate(steps):
        if time.time() - start > budget:
            break
        try:
            with browser(brain, mode, chan) as (ctx, page):
                result = job(ctx, page, variant)
            state(brain, mode=mode, channel=chan)
            return result
        except (NeedLogin, Skip):
            raise
        except Exception as e:
            msg = str(e).splitlines()[0][:120] if str(e) else type(e).__name__
            errors.append(msg)
            if os.environ.get('CREW_DEBUG'):
                print(f'[debug] try {i + 1} {mode}/{chan}/{variant}: {msg}', file=sys.stderr)
            if 'launch' in msg.lower() or 'user data directory' in msg.lower():
                launch_fails += 1
    if launch_fails >= 3:  # profile looks broken: keep it as a backup, start clean (needs one sign-in)
        bak = PROFILES / f'{brain}.bak-{int(time.time())}'
        shutil.move(str(PROFILES / brain), str(bak))
        raise NeedLogin(f'profile rebuilt (old one in {bak.name})')
    raise Skip(f'failed after {len(errors)} tries: {errors[-1] if errors else "time budget"}')


def check_wall(page, brain, box_sels, signin_sels):
    url = page.url
    if 'accounts.google.' in url or '/auth/' in url or 'auth.openai' in url:
        raise NeedLogin('login wall')
    has_box = first(page, box_sels, 6000) is not None
    if brain == 'gemini' and first(page, signin_sels, 1500):
        raise NeedLogin('not signed in (images need an account)')
    if not has_box:
        if BOT_RX.search(body_text(page)):
            raise Skip('bot check on the page')  # never solved by script; next attempt tries another window mode
        if first(page, signin_sels, 1500):
            raise NeedLogin('login wall')
        raise RuntimeError('prompt box not found')


# ---------- brain 1: Gemini images (ceig rules) ----------
G_IN = ['rich-textarea div[contenteditable="true"]', 'div.ql-editor[contenteditable="true"]',
        'div[contenteditable="true"][role="textbox"]', 'textarea']
G_SEND = ['button[aria-label*="Send" i]', 'button[aria-label*="Envoyer" i]', 'button.send-button']
G_RESP = ['model-response', '[id^="model-response"]', 'message-content']
G_SIGNIN = ['a[href*="ServiceLogin"]', 'a[aria-label*="Sign in" i]', 'a[aria-label*="Connexion" i]',
            'button:has-text("Sign in")', 'a:has-text("Se connecter")']
G_DL = ['button[data-test-id*="download" i]', 'button[aria-label*="ownload" i]', 'button[aria-label*="léchar" i]']
STYLES = {'film': 'shot on 35mm film, Kodak Portra 400, 50mm lens, natural light, shallow depth of field',
          'anime': 'cinematic anime painting, hand-drawn line work',
          'gouache': 'gouache painting, visible brush strokes, matte paper texture',
          'ink': 'ink and watercolor, loose hand-drawn lines'}
FORMATS = {'16:9': ('16:9 landscape', 1280), '1:1': ('1:1 square', 1000), '9:16': ('9:16 portrait', 1280)}
BANNED = re.compile(r',?\s*\b(masterpiece|8k|4k|ultra[- ]detailed|hyper-?realistic|trending on artstation|'
                    r'best quality|highly detailed)\b', re.I)
MEDIUM = re.compile(r'\b(film|photo|painting|anime|gouache|ink|watercolou?r|pencil|oil|illustration|3d)\b', re.I)
PEOPLE = re.compile(r'\b(person|people|man|woman|child|kid|figure|portrait|crowd)\b', re.I)


def build_prompt(scene, fmt, style):
    scene = BANNED.sub('', scene).strip().rstrip('.')
    parts = [f'Generate an image: {FORMATS[fmt][0]}.', scene + '.']
    if not MEDIUM.search(scene):
        parts.append(STYLES[style] + '.')
    parts.append('film grain, chromatic aberration, haze, dust, uneven light, wet reflections, asymmetric composition.')
    if re.search(r'\bwallpaper', scene, re.I):
        parts.append('negative space on the left for desktop icons.')
    parts.append('no text, no letters, no logos, no watermarks' + ('' if PEOPLE.search(scene) else ', no characters') + '.')
    return ' '.join(parts)


def img_size(b):
    if b[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', b[16:24])
    if b[:2] == b'\xff\xd8':
        i = 2
        while i < len(b) - 9:
            if b[i] != 0xFF: i += 1; continue
            m, ln = b[i + 1], struct.unpack('>H', b[i + 2:i + 4])[0]
            if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack('>HH', b[i + 5:i + 9]); return w, h
            i += 2 + ln
    if b[:4] == b'RIFF' and b[8:12] == b'WEBP':
        if b[12:16] == b'VP8X':
            return 1 + int.from_bytes(b[24:27], 'little'), 1 + int.from_bytes(b[27:30], 'little')
        if b[12:16] == b'VP8 ':
            return struct.unpack('<H', b[26:28])[0] & 0x3FFF, struct.unpack('<H', b[28:30])[0] & 0x3FFF
    return 0, 0


IMG_JS = """(sels) => { let r = []; for (const s of sels) { const q = [...document.querySelectorAll(s)]; if (q.length) { r = q; break; } }
  const last = r[r.length - 1]; if (!last) return {n: 0};
  const imgs = [...last.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth >= 400);
  const im = imgs[imgs.length - 1];
  const busy = !!document.querySelector('button[aria-label*="Stop" i], button[aria-label*="Arrêter" i]');
  return {n: r.length, src: im ? im.src : null, w: im ? im.naturalWidth : 0, h: im ? im.naturalHeight : 0,
          text: last.innerText.slice(0, 1500), busy}; }"""

CANVAS_JS = """(sels) => { let r = []; for (const s of sels) { const q = [...document.querySelectorAll(s)]; if (q.length) { r = q; break; } }
  const imgs = [...r[r.length - 1].querySelectorAll('img')].filter(i => i.naturalWidth >= 400); const im = imgs[imgs.length - 1];
  const c = document.createElement('canvas'); c.width = im.naturalWidth; c.height = im.naturalHeight;
  c.getContext('2d').drawImage(im, 0, 0); return c.toDataURL('image/png').split(',')[1]; }"""


def wait_reply(page, before, slow, want_image):
    end, last, stable = time.time() + (210 if slow else 150), None, 0
    while time.time() < end:
        page.wait_for_timeout(2000)
        info = page.evaluate(IMG_JS, G_RESP)
        if info['n'] <= before:
            continue
        if want_image and info['src']:
            page.wait_for_timeout(1500)
            return page.evaluate(IMG_JS, G_RESP)
        if LIMIT_RX.search(info['text']):
            raise Skip('free-tier limit: ' + cap(info['text'], 90).replace('\n', ' '))
        stable = stable + 1 if info['text'] == last and info['text'] and not info['busy'] else 0
        last = info['text']
        if stable >= (15 if want_image else 2):
            if want_image:
                raise Skip('no image made: ' + cap(info['text'], 100).replace('\n', ' '))
            return info
    raise RuntimeError('reply timed out')


def save_image(ctx, page, info, stem):
    data = None
    try:  # 1) Gemini's own full-size download button
        resp = page.locator(G_RESP[0]).last
        resp.locator('img').last.hover()
        btn = first(page, [f'{G_RESP[0]} >> nth=-1 >> {s}' for s in G_DL], 4000)
        if btn:
            with page.expect_download(timeout=60000) as dl:
                btn.click()
            tmp = HOME / 'dl.tmp'
            dl.value.save_as(tmp)
            data = tmp.read_bytes(); tmp.unlink()
    except Exception:
        data = None
    if not data and info['src'].startswith('http'):  # 2) fetch the src with the signed-in cookies
        try:
            r = ctx.request.get(info['src'])
            data = r.body() if r.ok else None
        except Exception:
            data = None
    if not data:  # 3) redraw it from the page
        data = base64.b64decode(page.evaluate(CANVAS_JS, G_RESP))
    ext = '.png' if data[:4] == b'\x89PNG' else '.webp' if data[:4] == b'RIFF' else '.jpg'
    w, h = img_size(data)
    w, h = (w, h) if w else (info['w'], info['h'])
    path = IMAGES / 'rejected' / f'{stem}{ext}'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path, w, h


def art_check(page, brief, slow):
    before = count(page, G_RESP)
    ask = ('Act as a strict art director. Judge only the last image you made against this brief: ' + brief +
           ' Check: right format, subject and palette; no artifacts, warped objects or extra limbs; no text, letters, '
           'logos or watermarks; nothing generic or AI-looking. Do not make a new image. Reply with one line only: '
           'PASS, or FAIL: <the single most important fix>.')
    send(page, G_IN, G_SEND, G_RESP, ask, slow)
    text = wait_reply(page, before, slow, want_image=False)['text']
    m = re.search(r'\b(PASS|FAIL)\b\s*[:\-–]?\s*(.*)', text)
    return (m.group(1), m.group(2).strip()[:160]) if m else (None, '')


def gemini(scene, fmt='16:9', style='film', fresh=False):
    prompt = build_prompt(scene, fmt, style)
    stem = re.sub(r'[^a-z0-9]+', '-', scene.lower())[:40].strip('-') + '-' + cache_key(prompt)[:8]
    min_side = FORMATS[fmt][1]

    def job(ctx, page, variant):
        page, slow = open_site(ctx, page, 'gemini', variant)
        check_wall(page, 'gemini', G_IN, G_SIGNIN)
        ask, verdict = prompt, None
        for rnd in range(4):  # first gen + max 3 reprompts
            before = send(page, G_IN, G_SEND, G_RESP, ask, slow)
            info = wait_reply(page, before, slow, want_image=True)
            path, w, h = save_image(ctx, page, info, f'{stem}-r{rnd + 1}')
            if max(w, h) < min_side:
                verdict, fix = 'FAIL', f'too small ({w}x{h}); regenerate at a higher resolution'
            else:
                verdict, fix = art_check(page, prompt, slow)
            if verdict in ('PASS', None):
                final = IMAGES / f'{stem}{path.suffix}'
                shutil.move(str(path), final)
                return final, w, h, rnd, verdict, fix
            ask = f'Regenerate the image. Keep the rest, change: {fix}'
        return path, w, h, rnd, verdict, fix

    def go():
        try:
            path, w, h, rnd, verdict, fix = run_web('gemini', job)
        except NeedLogin as e:
            say(f'skipped gemini: {e} → sign in: python crew.py login gemini'); sys.exit(3)
        except Skip as e:
            return say(f'skipped gemini: {e}')
        if verdict == 'FAIL':
            return say(f'weak image after 3 reprompts, not saved as final: {fix}', f'best try (rejected): {path}')
        say(f'OK gemini image: {path} ({w}x{h})', f'round {rnd + 1}/4 · size OK (≥{min_side}px long side)',
            'check: PASS (Gemini art-director critique)' if verdict else 'NOT verified: art check unreadable, Read the image once')
    cached(cache_key('gemini', prompt), fresh, go)


# ---------- brain 3: ChatGPT second opinion (optional) ----------
C_IN = ['#prompt-textarea', '#mobile-composer-prompt', 'textarea[aria-label*="ChatGPT" i]', 'div[contenteditable="true"][id*="prompt"]', 'textarea']
C_SEND = ['button[data-testid="send-button"]', 'button[aria-label*="Send" i]', 'button[aria-label*="Envoyer" i]']
C_RESP = ['[data-message-role="assistant"]', '[data-message-author-role="assistant"]', '[data-assistant-markdown-root]']
C_SIGNIN = ['button[data-testid="login-button"]', 'a[href*="/auth/login"]', 'button:text-is("Log in")', 'a:text-is("Log in")']
C_DISMISS = ['a:has-text("Stay logged out")', 'button:has-text("Stay logged out")', 'a:has-text("Rester déconnecté")',
             'button:has-text("Reject non-essential")', 'button:has-text("Refuser")']


def gpt_reply(page, before, slow):
    end, last, stable = time.time() + (180 if slow else 120), None, 0
    while time.time() < end:
        page.wait_for_timeout(1500)
        if count(page, C_RESP) <= before:
            if LIMIT_RX.search(last_text(page, ['[role="alert"]', '.toast-root'])):
                raise Skip('free-tier limit')
            continue
        text = last_text(page, C_RESP)
        busy = page.locator('[data-testid="stop-button"], button[aria-label*="Stop" i]').count() > 0
        stable = stable + 1 if text == last and text and not busy else 0
        last = text
        if stable >= 2:
            if LIMIT_RX.search(text):
                raise Skip('free-tier limit: ' + cap(text, 90).replace('\n', ' '))
            return re.sub(r'^\s*ChatGPT (said|a dit)\s*:\s*', '', text)
    raise RuntimeError('reply timed out')


def gpt(question, fresh=False):
    ask = f'Second opinion, answer in at most 5 short lines, no preamble: {question}'

    def job(ctx, page, variant):
        page, slow = open_site(ctx, page, 'gpt', variant)
        btn = first(page, C_DISMISS, 2500)
        if btn: btn.click(); page.wait_for_timeout(800)
        check_wall(page, 'gpt', C_IN, C_SIGNIN)
        before = send(page, C_IN, C_SEND, C_RESP, ask, slow)
        return gpt_reply(page, before, slow)

    def go():
        try:
            text = run_web('gpt', job, budget=300)
        except NeedLogin as e:
            return say(f'skipped gpt: {e} → optional; sign in: python crew.py login gpt')
        except Skip as e:
            return say(f'skipped gpt: {e}')
        say('OK gpt opinion:', *cap(text).splitlines()[:6], 'NOT verified: second opinion only, Claude decides')
    cached(cache_key('gpt', ask), fresh, go)


# ---------- menu commands ----------
def login(brain):
    exe = browser_exe()
    prof = PROFILES / brain
    prof.mkdir(parents=True, exist_ok=True)
    if not exe:
        say('skipped login: no Chrome or Edge found'); return
    # Plain browser, no automation attached, so Google/OpenAI sign-in pages behave normally. The user types, never Claude.
    proc = subprocess.Popen([exe, f'--user-data-dir={prof}', '--no-first-run', '--no-default-browser-check',
                             LOGIN_URLS[brain]])
    print(f'Sign in to {brain} in the window that just opened, then close that window (waiting up to 15 min).', flush=True)
    try:
        proc.wait(timeout=900)
    except subprocess.TimeoutExpired:
        proc.terminate()
        say(f'login {brain}: timed out after 15 min, window closed'); return
    status([brain])


def probe(brain):
    def job(ctx, page, variant):
        page, _ = open_site(ctx, page, brain, variant)
        if brain == 'gpt':
            btn = first(page, C_DISMISS, 2000)
            if btn: btn.click()
        check_wall(page, brain, G_IN if brain == 'gemini' else C_IN, G_SIGNIN if brain == 'gemini' else C_SIGNIN)
        signed = brain == 'gemini' or not first(page, C_SIGNIN, 1500)
        return 'ready' + (' (signed in)' if signed else ' (logged-out free mode)')
    try:
        return run_web(brain, job, budget=120)
    except NeedLogin as e:
        return f'sign-in needed ({e})'
    except Skip as e:
        return f'down: {e}'


def status(brains=('gemini', 'calc', 'gpt')):
    for i, b in enumerate(brains, 1):
        st = state(b)
        how = f" · {st.get('mode')}/{st.get('channel')}" if st.get('mode') else ''
        say(f'{i} {b}: ' + (f'ready (local Python {sys.version.split()[0]})' if b == 'calc' else probe(b) + how))
    n = len(list(CACHE.glob('*.json'))) if CACHE.exists() else 0
    say(f'cache: {n} saved results · images: {IMAGES}')


def clear():
    n = 0
    for f in CACHE.glob('*.json') if CACHE.exists() else []:
        f.unlink(); n += 1
    say(f'OK cache cleared: {n} results removed (images and sign-ins kept)')


def main():
    for s in (sys.stdout, sys.stderr):
        try: s.reconfigure(encoding='utf-8', errors='replace')
        except Exception: pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('cmd', choices=['route', 'auto', 'gemini', 'calc', 'gpt', 'status', 'login', 'clear'])
    ap.add_argument('text', nargs='?', default='')
    ap.add_argument('--fmt', choices=list(FORMATS), default=None)
    ap.add_argument('--style', choices=list(STYLES), default='film')
    ap.add_argument('--code', default=None)
    ap.add_argument('--fresh', action='store_true')
    a = ap.parse_args()
    fmt = a.fmt or '16:9'
    try:
        if a.cmd == 'route':
            say(' '.join(route(a.text)) or 'skip (no crew needed, 0 cost)')
        elif a.cmd == 'auto':
            brains = route(a.text)
            if not brains: say('skip (no crew needed, 0 cost)')
            for b in brains:
                if b == 'gemini': gemini(a.text, fmt, a.style, a.fresh)
                elif b == 'calc':
                    try: calc(a.text)
                    except Exception as e: say(f'skipped calc: {str(e)[:100]} (pass an expression)')
                else: gpt(a.text, a.fresh)
        elif a.cmd == 'gemini': gemini(a.text, fmt, a.style, a.fresh)
        elif a.cmd == 'calc': cached(cache_key('calc', a.text, a.code), a.fresh or 'clean' in a.text.lower(),
                                     lambda: calc(a.text, a.code))
        elif a.cmd == 'gpt': gpt(a.text, a.fresh)
        elif a.cmd == 'status': status()
        elif a.cmd == 'login':
            if a.text not in URLS: say('login needs: gemini or gpt')
            else: login(a.text)
        elif a.cmd == 'clear': clear()
    except SystemExit:
        raise
    except Exception as e:
        say(f'skipped {a.cmd}: {type(e).__name__}: {str(e)[:140]}')
    finally:
        print('\n'.join(OUT[:MAX_LINES]))


if __name__ == '__main__':
    main()
