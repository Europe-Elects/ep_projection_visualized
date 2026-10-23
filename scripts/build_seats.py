import sys, json, re, collections

SRC, MAP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
L = open(SRC, encoding='utf-8').read().split('\n')
h = L[0].rstrip('\r').split('\t')
R = [l.rstrip('\r').split('\t') for l in L[1:] if l.strip()]

MON = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
cols = []
for i, m in enumerate(h[5:]):
    mm = re.match(r'([A-Za-z]+)-(\d\d)', m.strip())
    mo, yr = MON[mm.group(1)[:3].lower()], 2000 + int(mm.group(2))
    cols.append((yr, mo, 5 + i))
cols.sort()
months = [f"{NAMES[mo-1]} {yr}" for yr, mo, _ in cols]

# one record per party and group (country + name + group). A party whose seats are split across
# two groups in the same month keeps both records, so no seats are lost; the party table merges them again.
parties = collections.OrderedDict()
for r in R:
    r += [''] * (len(h) - len(r))
    country, group = r[1].strip(), r[2].strip()
    name = r[3].strip() or re.sub(r'\s*\([^()]*\)\s*$', '', r[4].strip())
    if not country or not name:
        continue
    key = (country, name, group)
    p = parties.setdefault(key, dict(c=country, n=name, prev=[], s=[[group, 0] for _ in cols]))
    if r[0].strip() and r[0].strip() not in p['prev']: p['prev'].append(r[0].strip())
    for j, (_, _, ci) in enumerate(cols):
        v = r[ci].strip()
        if v:
            try: p['s'][j][1] += int(float(v))
            except ValueError: pass
data = [dict(c=p['c'], n=p['n'], prev=p['prev'], s=[[g, n] if n else 0 for g, n in p['s']]) for p in parties.values()]
M = json.load(open(MAP, encoding='utf-8'))
countries = sorted({p['c'] for p in data})
seats = {c: [sum(x[1] for p in data if p['c'] == c for x in [p['s'][j]] if x) for j in range(len(cols))] for c in countries}
issues = [(c, months[j], seats[c][j]) for c in countries for j in range(len(cols))
          if seats[c][j] != collections.Counter(seats[c]).most_common(1)[0][0]]

# EU-wide totals (rounded at EU level), one row per month
eutot = {}
if len(sys.argv) > 5:
    T = [l.rstrip('\r').split('\t') for l in open(sys.argv[5], encoding='utf-8').read().split('\n') if l.strip()]
    # find each group's column by its header text, so reordering columns in the sheet doesn't matter
    KEYS = [('ESN', 'ESN'), ('PfE', 'PfE'), ('ECR', 'ECR'), ('EPP', 'EPP'), ('RE', 'Renew'), ('NI', 'Non Inscrits'),
            ('unaffiliated', 'unaffiliated'), ('S&D', 'S&D'), ('G/EFA', 'Greens'), ('LEFT', 'Left')]
    cmap = {}
    for i, hd in enumerate(T[0]):
        for k, word in KEYS:
            if word.lower() in hd.lower() and 'EFDD' not in hd and k not in cmap.values():
                cmap[i] = k; break
    missing = [k for k, _ in KEYS if k not in cmap.values()]
    if missing: raise SystemExit("EU-wide seat sheet is missing columns for: " + ", ".join(missing))
    for r in T[1:]:
        mm = re.match(r'(\d{4})-(\d\d)-01$', r[0].strip())
        if not mm: continue
        vals = {k: int(r[i]) for i, k in cmap.items() if i < len(r) and r[i].strip()}
        if not vals: continue
        eutot[f"{NAMES[int(mm.group(2))-1]} {mm.group(1)}"] = vals
    eutot = {m: eutot[m] for m in months if m in eutot}
html = open(sys.argv[4], encoding='utf-8').read()
J = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
shapes = ''.join(
    f'<path class="{"cty" if s["n"] in countries else "bg"}" {"data-c=" + chr(34) + s["n"] + chr(34) if s["n"] in countries else ""} d="{s["d"]}"><title>{s["n"]}</title></path>'
    for s in sorted(M['shapes'], key=lambda s: -s['a']))
for k, v in {'__W__': str(M['W']), '__H__': str(M['H']), '__PATHS__': shapes, '__MONTHS__': J(months),
             '__DATA__': J(data), '__ANCHORS__': J({c: M['anchors'][c] for c in countries}),
             '__ISSUES__': J(issues), '__EUTOT__': J(eutot)}.items():
    html = html.replace(k, v)
# a full standalone page for GitHub Pages, reporting its height to an embedding iframe
RESIZE = '<script>(function(){function s(){try{parent.postMessage({type:"party-timeline-height",height:document.documentElement.scrollHeight},"*")}catch(e){}}addEventListener("load",s);try{new ResizeObserver(s).observe(document.body)}catch(e){}})();</script>'
if not html.lstrip().lower().startswith('<!doctype'):
    i = html.index('<div class="wrap">')
    html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<style>[hidden]{display:none!important}</style>\n'
            + html[:i] + '</head>\n<body>\n' + html[i:] + RESIZE + '\n</body>\n</html>\n')
if len(data) < 20 or len(months) < 2:
    raise SystemExit("Seat sheet looks wrong (too few parties or months); the live page was left unchanged.")
open(OUT, 'w', encoding='utf-8').write(html)
print(len(data), 'parties', len(countries), 'countries', months[0], '→', months[-1], 'issues:', issues)
