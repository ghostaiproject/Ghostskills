"""Live data for the CER-01 Main Control artifact (claude.ai/artifact/MRdTjsGHCoySQxbywYjs2g).

  python scripts/site.py data    -> site/data.json from the working tree (skills, branch, recent commits)
  python scripts/site.py build   -> site/index.html from site/page.html + site/parts/images.css + data.json
  python scripts/site.py mark V  -> record data.json's rev as pushed to the artifact db (doc site/data, now at version V)
  python scripts/site.py hook    -> Stop hook: asks Claude to push the data when the repo changed

site/ is local only (gitignored): the page carries personal art.
"""
import hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
DATA = os.path.join(SITE, 'data.json')
SYNCED = os.path.join(SITE, '.synced')
URL = 'https://claude.ai/artifact/MRdTjsGHCoySQxbywYjs2g'
# top folder -> map cluster (keys of CL in the page)
CLUSTER = {'core': 'core', 'projects': 'projects', 'cer-01': 'edged', 'edged': 'edged',
           'tools': 'tools', 'personal': 'personal', 'skills': 'wiki'}


def git(*a):
    r = subprocess.run(['git', '-C', ROOT, *a], capture_output=True, text=True, encoding='utf-8')
    return r.stdout.strip()


def front(path):
    txt = open(path, encoding='utf-8').read()
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


def build():
    d = data()
    page = open(os.path.join(SITE, 'page.html'), encoding='utf-8').read()
    imgs = open(os.path.join(SITE, 'parts', 'images.css'), encoding='utf-8').read().rstrip('\n')
    page = page.replace('/*@IMAGES@*/', imgs).replace('/*@LIVE@*/null', json.dumps(d, ensure_ascii=False))
    with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(page)
    print(f"built site/index.html rev {d['rev']} ({len(d['skills'])} skills, {d['branch']}@{d['sha']})")


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
        {'build': build, 'mark': mark, 'hook': hook}[cmd]()
