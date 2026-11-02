#!/usr/bin/env python3
"""Splits big CSVs into small files so the gallery loads fast, then builds _site/ (one index.html + data files).
data/<category>/<subcategory>.csv   e.g. data/men/portrait.csv
Columns: title, prompt, keywords, image_urls   (optional: subcategory)

Output per category (all tiny, loaded only when needed):
  data/<cat>/index.json            tabs + counts
  data/<cat>/<tab>-<page>.json     listing pages, 60 images each (id, title, thumbnail)
  data/<cat>/items/<n>.json        prompt details, 200 per file (opened by the viewer)
  data/<cat>/search.json           loaded only when someone types in the search box"""
import csv, json, os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, OUT, TPL = (os.path.join(ROOT, d) for d in ('data', '_site', 'templates'))
CATS = [('men', 'Men'), ('women', 'Women'), ('kids', 'Kids'), ('couples', 'Couples'), ('other', 'Other')]
PAGE, SHARD = 60, 200
csv.field_size_limit(sys.maxsize)

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-') or 'general'
def thumb(u): return re.sub(r'/s\d+(-c)?/', '/s400/', u) if re.search(r'googleusercontent|blogger', u) else u
def jsn(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
def render(tpl, **kw):
    s = open(os.path.join(TPL, tpl), encoding='utf-8').read()
    for k, v in kw.items(): s = s.replace('__%s__' % k.upper(), v)
    return s

shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(os.path.join(OUT, 'data'))
shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
def write(path, s):
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f: f.write(s)

summary, total = [], 0
for key, label in CATS:
    folder, items = os.path.join(DATA, key), []
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith('.csv')) if os.path.isdir(folder) else []
    for fn in files:
        default_sub = re.sub(r'[-_]+', ' ', fn[:-4]).strip().title()
        with open(os.path.join(folder, fn), newline='', encoding='utf-8-sig') as f:
            rd = csv.reader(f)
            head = [re.sub(r'[\s-]+', '_', h.strip().lower()) for h in next(rd, [])]
            for row in rd:
                o = {h: (row[i].strip() if i < len(row) else '') for i, h in enumerate(head)}
                imgs = [u for u in re.split(r'[|\s]+', o.get('image_urls') or o.get('image_url') or o.get('image') or '') if u]
                if not imgs: continue
                sub = o.get('subcategory') or default_sub
                items.append({'id': len(items) + 1, 't': o.get('title') or 'Untitled', 'p': o.get('prompt', ''), 's': sub,
                              'sl': slug(sub), 'm': imgs, 'k': [w.strip() for w in re.split(r'[|,]', o.get('keywords', '')) if w.strip()]})
    groups = {}
    for x in items: groups.setdefault(x['sl'], []).append(x)
    for lst in groups.values():                      # neighbours + listing page of each item inside its tab
        for i, x in enumerate(lst):
            x['pv'] = lst[i - 1]['id'] if i else 0
            x['nx'] = lst[i + 1]['id'] if i + 1 < len(lst) else 0
            x['pg'] = i // PAGE + 1
    def listing(sl, lst):
        pages = max(1, -(-len(lst) // PAGE))
        for n in range(pages):
            write('data/%s/%s-%d.json' % (key, sl, n + 1), jsn([[x['id'], x['t'], thumb(x['m'][0])] for x in lst[n * PAGE:(n + 1) * PAGE]]))
        return pages
    tabs = [{'sl': 'all', 'name': 'All', 'count': len(items), 'pages': listing('all', items)}]
    for sl, lst in groups.items():
        tabs.append({'sl': sl, 'name': lst[0]['s'], 'count': len(lst), 'pages': listing(sl, lst)})
    write('data/%s/index.json' % key, jsn({'key': key, 'name': label, 'tabs': tabs}))
    shards = {}
    for x in items: shards.setdefault(x['id'] // SHARD, {})[x['id']] = {k: x[k] for k in ('t', 'p', 'k', 'm', 's', 'sl', 'pv', 'nx', 'pg')}
    for n, d in shards.items(): write('data/%s/items/%d.json' % (key, n), jsn(d))
    write('data/%s/search.json' % key, jsn([[x['id'], x['t'], '|'.join(x['k']), x['s'], thumb(x['m'][0])] for x in items]))
    summary.append({'key': key, 'name': label, 'count': len(items), 'cover': thumb(items[0]['m'][0]) if items else ''})
    total += len(items)
    print('  %-8s %6d prompts, %d tabs' % (label, len(items), len(groups)))
write('index.html', render('app.html', data=jsn(summary), shard=str(SHARD)))   # the whole site is this one page
print('Built %d prompts into %s' % (total, OUT))
