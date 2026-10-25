"""Live data for the CER-01 Main Control artifact (claude.ai/artifact/MRdTjsGHCoySQxbywYjs2g).

  python scripts/site.py data    -> site/data.json from the working tree (skills, branch, recent commits)
  python scripts/site.py build   -> site/out/ (index, fr, setup, setup-fr) from site/page.html + site/parts/ + data.json
  python scripts/site.py pages   -> build, then push site/out/ to the GitHub Pages repo (PAGES_REPO)
  python scripts/site.py mark V  -> record data.json's rev as pushed to the artifact db (doc site/data, now at version V)
  python scripts/site.py hook    -> Stop hook: asks Claude to push the data when the repo changed

site/ is local only (gitignored): the page carries personal art.
"""
import hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get('GHOST_SITE') or os.path.join(ROOT, 'site')
DATA = os.path.join(SITE, 'data.json')
SYNCED = os.path.join(SITE, '.synced')
URL = 'https://claude.ai/artifact/MRdTjsGHCoySQxbywYjs2g'
# self-hosted copy (GitHub Pages) of site/out/
PAGES_REPO = 'ghostaiproject/cer-01-site'
# top folder -> map cluster (keys of CL in the page)
CLUSTER = {'core': 'core', 'projects': 'projects', 'cer-01': 'edged', 'edged': 'edged',
           'tools': 'tools', 'personal': 'personal', 'skills': 'wiki'}
# the wiki plugin lives on its own branch until merged; read it from there when the tree has none
WIKI_REF = 'docs/neural-map'


def git(*a):
    r = subprocess.run(['git', '-C', ROOT, *a], capture_output=True, text=True, encoding='utf-8')
    return r.stdout.strip()


def front(path, txt=None):
    txt = open(path, encoding='utf-8').read() if txt is None else txt
    m = re.match(r'---\s*\n(.*?)\n---', txt, re.S)
    meta = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(':')
        meta[k.strip()] = v.strip()
    return meta, len(txt.encode('utf-8'))


def skills():
    out = []
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d not in ('dist', 'site', 'node_modules'))
        if 'SKILL.md' not in files:
            continue
        rel = os.path.relpath(dirpath, ROOT).replace('\\', '/')
        meta, size = front(os.path.join(dirpath, 'SKILL.md'))
        desc = meta.get('description', '')
        cmd = re.search(r'(?<![\w/])/[a-z][\w-]*', desc)
        sid = meta.get('name') or rel.rsplit('/', 1)[-1]
        out.append({'id': 'CER-01' if rel == 'cer-01' else sid, 'k': CLUSTER.get(rel.split('/')[0], 'tools'),
                    'dir': rel, 'd': desc, 'cmd': cmd.group(0) if cmd else '(auto)', 'kb': round(size / 1024, 1)})
    py = os.path.join(ROOT, 'scripts', 'ghostskills.py')
    if os.path.exists(py):
        out.append({'id': 'ghostskills.py', 'k': 'wiki', 'dir': 'scripts/ghostskills.py', 'd': '',
                    'cmd': 'python scripts/ghostskills.py', 'kb': round(os.path.getsize(py) / 1024, 1)})
    if not any(s['k'] == 'wiki' for s in out):
        out += branch_wiki()
    return out


def branch_wiki():
    """Wiki plugin skills (skills/*/SKILL.md + scripts/ghostskills.py) from WIKI_REF, tagged with the branch."""
    ref = next((r for r in (WIKI_REF, 'origin/' + WIKI_REF) if git('rev-parse', '--verify', '-q', r)), None)
    if not ref:
        return []
    br = ref.split('origin/')[-1]
    out = []
    for path in git('ls-tree', '-r', '--name-only', ref, '--', 'skills').splitlines():
        if not path.endswith('/SKILL.md'):
            continue
        txt = git('show', f'{ref}:{path}')
        meta, size = front(None, txt)
        rel = path.rsplit('/', 1)[0]
        desc = meta.get('description', '')
        cmd = re.search(r'(?<![\w/])/[a-z][\w-]*', desc)
        out.append({'id': meta.get('name') or rel.rsplit('/', 1)[-1], 'k': 'wiki', 'dir': rel, 'br': br, 'd': desc,
                    'cmd': cmd.group(0) if cmd else '(auto)', 'kb': round(size / 1024, 1)})
    size = git('cat-file', '-s', f'{ref}:scripts/ghostskills.py')
    if size.isdigit():
        out.append({'id': 'ghostskills.py', 'k': 'wiki', 'dir': 'scripts/ghostskills.py', 'br': br, 'd': '',
                    'cmd': 'python scripts/ghostskills.py', 'kb': round(int(size) / 1024, 1)})
    return out


def data():
    log = [l.split('|', 1) for l in git('log', '-8', '--format=%cs|%s').splitlines() if '|' in l]
    d = {'branch': git('rev-parse', '--abbrev-ref', 'HEAD'), 'sha': git('rev-parse', '--short', 'HEAD'),
         'dirty': bool(git('status', '--porcelain', '--', '.', ':!site', ':!dist')),
         'skills': skills(), 'log': log}
    d['rev'] = hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]
    d['at'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    os.makedirs(SITE, exist_ok=True)
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return d


def fr(page):
    """French copy: ordered (en, fr) pairs from site/parts/fr.json, longest first; a pair that no longer matches is reported."""
    pairs = json.load(open(os.path.join(SITE, 'parts', 'fr.json'), encoding='utf-8'))
    for en, tr in sorted(pairs, key=lambda p: -len(p[0])):
        if en not in page:
            print('fr.json: no match for', en[:70])
        page = page.replace(en, tr)
    return page


LOCK_ITER = 200000


def lock(html, lang):
    """Setup page for devs only: the real page ships encrypted with the access code in site/parts/setup.code.
    Stdlib only, mirrored by WebCrypto in parts/lock.html: PBKDF2-SHA256 key, SHA-256 counter keystream, HMAC-SHA256 tag.
    A 4-digit code keeps casual visitors out; it is not strong secrecy (10k guesses)."""
    import base64, hmac
    code = open(os.path.join(SITE, 'parts', 'setup.code'), encoding='utf-8').read().strip()
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', code.encode(), salt, LOCK_ITER, 64)
    ek, mk = key[:32], key[32:]
    data = html.encode('utf-8')
    stream = b''.join(hashlib.sha256(ek + i.to_bytes(4, 'big')).digest() for i in range((len(data) + 31) // 32))
    ct = bytes(a ^ b for a, b in zip(data, stream))
    tag = hmac.new(mk, ct, 'sha256').digest()
    b64 = lambda b: base64.b64encode(b).decode()
    page = open(os.path.join(SITE, 'parts', 'lock.html'), encoding='utf-8').read()
    return (page.replace('<html lang="en">', f'<html lang="{lang}">', 1)
            .replace('/*@LOCK@*/null', json.dumps({'s': b64(salt), 'i': LOCK_ITER, 't': b64(tag), 'c': b64(ct)})))


def build():
    """site/out/: index.html + fr.html (main control), setup.html + setup-fr.html (first-time PC setup). Also site/index.html for the artifact."""
    d = data()
    page = open(os.path.join(SITE, 'page.html'), encoding='utf-8').read()
    # --setup (setup page header art) is shared: the main page's setup band shows it too
    setup_img = open(os.path.join(SITE, 'parts', 'setup-img.css'), encoding='utf-8').read()
    imgs = open(os.path.join(SITE, 'parts', 'images.css'), encoding='utf-8').read().rstrip('\n') + '\n  ' + setup_img.strip()[len(':root{'):-1] + ';'
    page = page.replace('/*@LIVE@*/null', json.dumps(d, ensure_ascii=False))
    setup = open(os.path.join(SITE, 'parts', 'setup.html'), encoding='utf-8').read().replace('/*@SETUPIMG@*/', setup_img)
    # images go in after translating so the pairs never scan the base64
    pages = {'index.html': page.replace('/*@IMAGES@*/', imgs), 'fr.html': fr(page).replace('/*@IMAGES@*/', imgs),
             'setup.html': lock(setup, 'en'), 'setup-fr.html': lock(setup.replace('<html lang="en">', '<html lang="fr">', 1), 'fr')}
    out = os.path.join(SITE, 'out')
    os.makedirs(out, exist_ok=True)
    for name, html in pages.items():
        with open(os.path.join(out, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
    with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(pages['index.html'])
    print(f"built site/out/ ({', '.join(pages)}) rev {d['rev']} ({len(d['skills'])} skills, {d['branch']}@{d['sha']})")


def pages():
    """Push site/out/ to the self-hosted copy (GitHub Pages repo PAGES_REPO, branch main)."""
    build()
    out = os.path.join(SITE, 'out')
    run = lambda *a: subprocess.run(['git', '-C', out, *a], check=True)
    if not os.path.isdir(os.path.join(out, '.git')):
        run('init', '-q', '-b', 'main')
        run('remote', 'add', 'origin', f'https://github.com/{PAGES_REPO}.git')
    open(os.path.join(out, '.nojekyll'), 'w').close()
    run('add', '-A')
    if subprocess.run(['git', '-C', out, 'diff', '--cached', '--quiet']).returncode:
        run('commit', '-q', '-m', 'Update CER-01 Main Control')
    run('push', '-q', 'origin', 'main')
    print(f'pushed -> https://{PAGES_REPO.split("/")[0]}.github.io/{PAGES_REPO.split("/")[1]}/')


def synced():
    """(rev, db version) last pushed; version pins the next write."""
    try:
        rev, ver = open(SYNCED).read().split()
        return rev, ver
    except (OSError, ValueError):
        return '', ''


def hook():
    try:
        inp = json.load(sys.stdin)
    except ValueError:
        inp = {}
    cwd = os.path.normcase(os.path.abspath(inp.get('cwd') or os.getcwd()))
    if inp.get('stop_hook_active') or not cwd.startswith(os.path.normcase(ROOT)):
        return
    d = data()
    rev, ver = synced()
    if d['rev'] == rev:
        return
    pin = f" if_version={ver}" if ver else ''
    print(json.dumps({'decision': 'block', 'reason':
        f"Ghostskills changed (rev {d['rev']}, {len(d['skills'])} skills, {d['branch']}@{d['sha']}). "
        f"Push the live map data: ArtifactData set url={URL} collection=site doc_id=data file_path={DATA}{pin} "
        f"(version conflict -> get it, retry with its version), then run: python {os.path.join(ROOT, 'scripts', 'site.py')} mark <new version>. "
        f"One line to the user, no republish."}))


def mark():
    with open(DATA, encoding='utf-8') as f:
        rev = json.load(f)['rev']
    with open(SYNCED, 'w') as f:
        f.write(f'{rev} {sys.argv[2]}')
    print('synced', rev, 'version', sys.argv[2])


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'data'
    if cmd == 'data':
        d = data()
        print(f"site/data.json rev {d['rev']} ({len(d['skills'])} skills, {d['branch']}@{d['sha']})")
    else:
        {'build': build, 'pages': pages, 'mark': mark, 'hook': hook}[cmd]()
