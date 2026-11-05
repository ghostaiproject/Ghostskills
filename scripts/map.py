"""Neural map data (docs/neural-map/nodes.json) kept in step with the repo's skills.

python scripts/map.py         -> report skills missing from the map / map nodes whose folder is gone
python scripts/map.py --fix   -> add missing skills (description from SKILL.md; fill cmd/ad by hand later), drop gone ones

Then push it live (no page read, no republish): ArtifactData set, artifact = the map's url (cer-01/lessons/skills.md),
collection "map", doc_id "nodes", file_path docs/neural-map/nodes.json.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'docs', 'neural-map', 'nodes.json')
KIND = {'core': 'core', 'projects': 'projects', 'tools': 'tools', 'personal': 'personal', 'cer-01': 'edged', 'skills': 'wiki'}
TOK = {'core': 'core', 'projects': 'project', 'tools': 'tool', 'personal': 'personal', 'edged': 'core', 'wiki': 'on trigger'}


def repo_skills():
    out = {}
    for top in KIND:
        for dp, dirs, files in os.walk(os.path.join(ROOT, top)):
            dirs[:] = [d for d in dirs if not d.startswith(('_', '.')) and d != '__pycache__']
            if 'SKILL.md' in files:
                txt = open(os.path.join(dp, 'SKILL.md'), encoding='utf-8').read()
                m = re.search(r'^description:\s*(.+)$', txt, re.M)
                rel = os.path.relpath(dp, ROOT).replace('\\', '/')
                out[rel] = (KIND[top], m.group(1).strip() if m else '')
    return out


def main():
    data = json.load(open(DATA, encoding='utf-8'))
    nodes = data['nodes']
    have = {n.get('dir') for n in nodes}
    skills = repo_skills()
    missing = [d for d in skills if d not in have]
    gone = [n['id'] for n in nodes if n.get('dir', '').count('/') and not os.path.exists(os.path.join(ROOT, n['dir']))]
    print('missing from map:', ', '.join(missing) or 'none')
    print('gone from repo:', ', '.join(gone) or 'none')
    if '--fix' in sys.argv and (missing or gone):
        nodes[:] = [n for n in nodes if n['id'] not in gone]
        for d in missing:
            k, desc = skills[d]
            nodes.append({'id': d.rsplit('/', 1)[-1], 'k': k, 'cmd': '(auto)', 'd': desc, 'tok': TOK[k], 'dir': d,
                          'ad': 'TODO art-director line'})
        json.dump(data, open(DATA, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
        open(DATA, 'a', encoding='utf-8').write('\n')
        print('nodes.json updated:', len(nodes), 'nodes')
    return 1 if (missing or gone) and '--fix' not in sys.argv else 0


if __name__ == '__main__':
    sys.exit(main())
