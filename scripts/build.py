#!/usr/bin/env python3
"""Builds the whole site into _site/ from data/prompts.csv plus YOUR two original pages in templates/.
  templates/gallery.html  -> used for the home page and every category/subcategory page
  templates/viewer.html   -> used for viewer.html (one page that loads any prompt)
Usage: python3 scripts/build.py [csv] [out_dir] [templates_dir]"""
import csv, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'data', 'prompts.csv')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, '_site')
TPL = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, 'templates')
CATS = ['Men', 'Women', 'Kids', 'Couples', 'Others']
ALIAS = {'man': 'Men', 'male': 'Men', 'woman': 'Women', 'female': 'Women', 'kid': 'Kids',
         'child': 'Kids', 'children': 'Kids', 'couple': 'Couples'}
PAGE, SHARD = 400, 200            # images per gallery page / prompts per detail file
csv.field_size_limit(sys.maxsize)

def fail(msg): sys.exit('\nBUILD ERROR: ' + msg + '\n')
def js(o): return json.dumps(o, ensure_ascii=True, separators=(',', ':')).replace('</', '<\\/')
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-') or 'general'
def thumb(u, n=400):
    return re.sub(r'/s\d+(-c)?/', '/s%d/' % n, u) if re.search(r'googleusercontent|blogger', u) else u
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def patch(s, pat, repl, label, flags=0):
    new, n = re.subn(pat, lambda m: repl, s, count=1, flags=flags)
    if not n: fail("Could not find %s in your template. Paste your ORIGINAL file into templates/ unchanged." % label)
    return new

def tpl(name, must):
    p = os.path.join(TPL, name)
    s = open(p, encoding='utf-8').read() if os.path.exists(p) else ''
    if must not in s: fail("templates/%s is empty or is still the placeholder. Paste your original code into it." % name)
    return s

# ---------- read CSV ----------
def norm(c):
    k = (c or '').strip().lower()
    return next((x for x in CATS if x.lower() == k), ALIAS.get(k))
items = []
with open(CSV, newline='', encoding='utf-8-sig') as f:
    rd = csv.reader(f)
    head = [re.sub(r'[\s-]+', '_', h.strip().lower()) for h in next(rd)]
    for row in rd:
        o = {h: (row[i].strip() if i < len(row) else '') for i, h in enumerate(head)}
        imgs = [u for u in re.split(r'[|\s]+', o.get('image_urls') or o.get('image_url') or o.get('images') or '') if u]
        if not o.get('title') and not imgs: continue
        cat = norm(o.get('category'))
        sub = o.get('subcategory') or (o.get('category', '') if cat is None else '') or 'General'
        items.append({'i': len(items) + 1, 't': o.get('title') or 'Untitled', 'p': o.get('prompt', ''),
                      'c': cat or 'Others', 'sub': sub,
                      'k': [w.strip() for w in re.split(r'[|,]', o.get('keywords', '')) if w.strip()], 'm': imgs})

# ---------- gallery pages ----------
gal = tpl('gallery.html', 'textConfiguration')
READY = r"""
  window.__ready = (function(){
    var P = new URLSearchParams(location.search), raw = (P.get('q') || '').trim(), q = raw.toLowerCase();
    var pg = Math.max(1, +P.get('page') || 1), PS = %d;
    return fetch('data/build/search.json').then(function(r){ return r.json(); }).then(function(rows){
      var hits = rows.filter(function(r){ return (r[1] + ' ' + r[3].split('|').join(' ') + ' ' + r[2]).toLowerCase().indexOf(q) > -1; });
      var pages = Math.max(1, Math.ceil(hits.length / PS));
      hits.slice((pg - 1) * PS, pg * PS).forEach(function(r){
        var u = 'viewer.html?id=' + r[0], t = r[4] || '';
        if (/googleusercontent|blogger/.test(t)) t = t.replace(/\/s\d+(-c)?\//, '/s400/');
        textConfiguration.gridPosts.push({ postUrl: u, category: 'search' });
        postMetaCache.set(u, { imgUrl: t, title: r[1], desc: r[2] });
      });
      var base = 'search.html?q=' + encodeURIComponent(raw), first = 'Results: ' + hits.length;
      var menu = [{ name: first, url: pg === 1 ? '#results' : base }], shown = Math.min(pages, 10);
      for (var n = 2; n <= Math.max(shown, pg <= pages ? pg : 0); n++) { if (n <= shown || n === pg) menu.push({ name: 'Page ' + n, url: base + '&page=' + n }); }
      menu.push({ name: 'Home', url: 'index.html' });
      %s.forEach(function(c){ menu.push({ name: c, url: c.toLowerCase() + '.html' }); });
      textConfiguration.menuLinks.length = 0;
      menu.forEach(function(m){ textConfiguration.menuLinks.push(m); });
      textConfiguration.activeTabName = pg === 1 ? first : 'Page ' + pg;
      document.title = (raw ? raw + ' \u2013 ' : '') + 'Search \u2013 Ai Edits Ram';
    }).catch(function(){});
  })();""" % (PAGE, js(CATS))

def gallery(title, active, menu, posts, seed, search=False):
    s = patch(gal, r'<title>[^<]*</title>', '<title>%s</title>' % esc(title), '<title>')
    s = patch(s, r'activeTabName:\s*"[^"]*"', 'activeTabName: ' + js(active), 'activeTabName')
    s = patch(s, r'menuLinks:\s*\[.*?\n\s*\],', 'menuLinks: ' + js(menu) + ',', 'menuLinks', re.S)
    s = patch(s, r'gridPosts:\s*\[.*?\n\s*\]\s*\n\s*\};', 'gridPosts: ' + js(posts) + '\n  };', 'gridPosts', re.S)
    s = patch(s, r'if \(query\) runInThemeSearch\(query\);',
              'if (query) window.location.href = "search.html?q=" + encodeURIComponent(query);', 'the search-box submit handler')
    if search:
        s = patch(s, r'document\.addEventListener\("DOMContentLoaded", \(\) => \{',
                  'document.addEventListener("DOMContentLoaded", async () => { try { await window.__ready; } catch (e) {}', 'the DOMContentLoaded handler')
    return patch(s, r'const postMetaCache = new Map\(\);',
                 'const postMetaCache = new Map();\n  ' + js(seed) +
                 '.forEach(function(e){postMetaCache.set(e[0],{imgUrl:e[1],title:e[2],desc:e[3]});});' + (READY if search else ''), 'postMetaCache')

shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
def write(name, s):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f: f.write(s)

# home page: five category cards
cards, seed = [], []
for c in CATS:
    mine = [x for x in items if x['c'] == c]
    cover = thumb(mine[0]['m'][0]) if mine and mine[0]['m'] else ''
    cards.append({'postUrl': c.lower() + '.html', 'category': 'home'})
    seed.append([c.lower() + '.html', cover, c, '%d prompts' % len(mine)])
home_menu = [{'name': 'Home', 'url': '#home'}] + [{'name': c, 'url': c.lower() + '.html'} for c in CATS]
write('index.html', gallery('Ai Edits Ram', 'Home', home_menu, cards, seed))

# search page (keyword links, search box) – results come from the CSV
write('search.html', gallery('Search – Ai Edits Ram', 'Results', [{'name': 'Results', 'url': '#results'}] + home_menu[1:], [], [], True))

# category pages: tabs = subcategories (split every PAGE images)
pages = 0
for c in CATS:
    mine = [x for x in items if x['c'] == c]
    subs = {}
    for x in mine: subs.setdefault(x['sub'].lower(), []).append(x)
    tabs = []                                  # (tab name, file, items)
    for lst in subs.values():
        label, base = lst[0]['sub'], c.lower() + '-' + slug(lst[0]['sub'])
        for n in range(0, max(1, -(-len(lst) // PAGE))):
            tabs.append((label if n == 0 else '%s %d' % (label, n + 1), base + ('' if n == 0 else '-%d' % (n + 1)) + '.html', lst[n * PAGE:(n + 1) * PAGE]))
    menu = [{'name': 'Home', 'url': 'index.html'}] + [{'name': t[0], 'url': t[1]} for t in tabs]
    def page(name, active, lst):
        global pages
        posts = [{'postUrl': 'viewer.html?id=%d' % x['i'], 'category': c.lower()} for x in lst]
        sd = [['viewer.html?id=%d' % x['i'], thumb(x['m'][0]) if x['m'] else '', x['t'], x['p'][:110]] for x in lst]
        write(name, gallery('%s – %s – Ai Edits Ram' % (c, active), active, menu, posts, sd)); pages += 1
    for t in tabs: page(t[1], t[0], t[2])
    page(c.lower() + '.html', tabs[0][0] if tabs else 'Home', tabs[0][2] if tabs else [])

# ---------- viewer page ----------
v = tpl('viewer.html', 'PR_CONFIG').lstrip()
v = re.sub(r'^<a\b.*?</a>\s*', '', v, count=1, flags=re.S)     # drop the Blogger thumbnail helper link
wrap = """window.__prItem.then(function(it){
  if(it){
    var big=function(u){return /googleusercontent|blogger/.test(u)?u.replace(/\\/s\\d+(-c)?\\//,'/s1600/'):u;};
    PR_CONFIG.slides=it.m.map(function(u){return {image:big(u),title:it.t,prompt:it.p};});
    PR_CONFIG.keywords=it.k;
    PR_CONFIG.search.baseUrl='search.html?q=';
    PR_CONFIG.search.openInNewTab=false;
    PR_CONFIG.links.categories=it.c.toLowerCase()+'.html';
    document.title=it.t+' \\u2013 Ai Edits Ram';
  }
}).catch(function(){}).then(function(){
  prInitConfig();
  prRender();
  prRenderKeywords();
  prPromoLoad();
});"""
v = patch(v, r'prInitConfig\(\);\s*prRender\(\);\s*prRenderKeywords\(\);\s*prPromoLoad\(\);', wrap, 'the viewer start-up calls (prInitConfig / prRender / prRenderKeywords / prPromoLoad)')
REL = r"""function prLoadRelatedPosts(){
  var kws = (PR_CONFIG.keywords || []).map(function(k){ return k.toLowerCase(); });
  var me = +new URLSearchParams(location.search).get('id');
  if(!kws.length){ prRenderSideList('empty', []); return; }
  prRenderSideList('loading');
  fetch('data/build/search.json').then(function(r){ return r.json(); }).then(function(rows){
    var scored = [];
    rows.forEach(function(r){
      if(r[0] === me || !r[3]) return;
      var n = 0;
      r[3].toLowerCase().split('|').forEach(function(k){ if(kws.indexOf(k) > -1) n++; });
      if(n) scored.push([n, r]);
    });
    scored.sort(function(a, b){ return b[0] - a[0] || b[1][0] - a[1][0]; });
    var items = scored.slice(0, 60).map(function(x){
      var r = x[1], t = r[4] || '';
      if(/googleusercontent|blogger/.test(t)) t = t.replace(/\/s\d+(-c)?\//, '/s500-c/');
      return { title: r[1], link: 'viewer.html?id=' + r[0], thumb: t };
    });
    prRenderSideList(items.length ? 'ok' : 'empty', items);
  }).catch(function(){ prRenderSideList('error'); });
}
"""
v = patch(v, r'function prLoadRelatedPosts\(\)\{.*?\n\}\n', REL, 'the prLoadRelatedPosts function', re.S)
head = ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ai Edits Ram</title>'
        "<script>window.__prItem=(function(){var id=+new URLSearchParams(location.search).get('id');"
        "return fetch('data/build/items/'+Math.floor(id/%d)+'.json').then(function(r){return r.json()}).then(function(s){return s[id]})})();</script>"
        '</head><body>\n' % SHARD)
write('viewer.html', head + v + '\n</body></html>\n')

# ---------- prompt detail files (one per 200 prompts) ----------
shards = {}
for x in items:
    shards.setdefault(x['i'] // SHARD, {})[x['i']] = {k: x[k] for k in ('t', 'p', 'c', 'sub', 'k', 'm')}
os.makedirs(os.path.join(OUT, 'data', 'build', 'items'))
for n, d in shards.items():
    with open(os.path.join(OUT, 'data', 'build', 'items', '%d.json' % n), 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
with open(os.path.join(OUT, 'data', 'build', 'search.json'), 'w', encoding='utf-8') as f:
    json.dump([[x['i'], x['t'], x['c'], '|'.join(x['k']), x['m'][0] if x['m'] else ''] for x in items], f, ensure_ascii=False, separators=(',', ':'))
print('Built %d prompts, %d gallery pages in %s' % (len(items), pages + 1, OUT))
