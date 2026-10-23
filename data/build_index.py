import json, sys, os, html as H
OUT = sys.argv[1]
d = json.load(open(os.path.join(OUT, '_index.json')))
EPS = d['eps']

used = []
for c in d['index']:
    for k, _ in c['mix']:
        if k not in used: used.append(k)
used.sort(key=lambda k: list(EPS).index(k))
light = "".join(f"{EPS[k][0]}:{EPS[k][2]};" for k in used)
dark = "".join(f"{EPS[k][0]}:{EPS[k][3]};" for k in used)

cards = []
for c in d['index']:
    segs = "".join(f'<i style="flex:{n};background:var({EPS[k][0]})" title="{H.escape(k)}: {n}"></i>' for k, n in c['mix'])
    rest = c['n'] - c['mem']
    if rest: segs += f'<i style="flex:{rest};background:var(--bar)" title="No Europarty: {rest}"></i>'
    cards.append(f'''<a class="card" href="{c['file']}" data-name="{H.escape(c['country'].lower())}">
  <span class="cn">{H.escape(c['country'])}</span>
  <span class="meta"><span><b>{c['n']}</b> parties</span><span><b>{c['active']}</b> active</span><span><b>{c['mem']}</b> Europarty</span></span>
  <span class="mix">{segs}</span>
</a>''')

legend = "".join(f'<span><span class="sw" style="background:var({EPS[k][0]})"></span>{H.escape(k)}</span>' for k in used)

body = f'''<title>European Party Timelines</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Advent+Pro:wght@400;500;600;700;800&display=swap">
<style>
/* Layout: index of country ledgers — search + responsive card grid, Europarty mix strip per country */
:root{{--bg:#f8f8f6;--surface:#fff;--land:#ededea;--land-in:#dfe1e6;--land-hover:#cfd3db;--nodata:#b4b8c0;--fg:#14213d;--muted:#5b616e;--rule:#e3e3de;--bar:#9aa1ad;--link:#003399;--navy:#003399;--yellow:#ffcc00;--edge:transparent;{light}
  --display:"Advent Pro","Arial Narrow",system-ui,sans-serif;--body:"Advent Pro","Arial Narrow",system-ui,sans-serif;--mono:"Advent Pro","Arial Narrow",system-ui,sans-serif}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;font-weight:500;line-height:1.4}}
.band{{background:transparent;color:var(--fg);border-bottom:1px solid var(--rule)}}
.band h1{{color:var(--navy)}}
.band h1::after{{content:"";display:block;width:56px;height:4px;background:var(--yellow);margin-top:10px}}
.band-in{{max-width:1240px;margin:0 auto;padding-block:22px 26px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:8px}}
.band .lede{{color:var(--muted)}}
.wrap{{max-width:1240px;margin:0 auto;padding-block:22px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:20px}}
h1{{font-family:var(--display);font-weight:800;font-size:clamp(32px,4.8vw,50px);line-height:1;margin:0;text-transform:uppercase;letter-spacing:.02em;text-wrap:balance}}
.lede{{color:var(--muted);margin:0}}
input{{font:inherit;padding:8px 12px;border:1px solid var(--rule);border-bottom:3px solid var(--navy);border-radius:2px;background:var(--surface);color:var(--fg);width:100%;max-width:320px}}
input:focus-visible,.card:focus-visible{{outline:2px solid var(--link);outline-offset:2px}}
.legend{{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:14px;color:var(--muted)}}
.legend span{{display:inline-flex;align-items:center;gap:6px}}
.sw{{width:14px;height:8px;border-radius:2px;display:inline-block}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}}
.card{{display:flex;flex-direction:column;gap:8px;padding:14px;background:var(--surface);border:1px solid var(--rule);border-top:3px solid var(--navy);border-radius:2px;color:var(--fg);text-decoration:none;min-width:0}}
.card:hover{{border-top-color:var(--yellow)}}
.cn{{font-family:var(--display);font-weight:700;font-size:21px;text-transform:uppercase;letter-spacing:.02em}}
.meta{{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:14px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted)}}
.meta b{{color:var(--fg);font-variant-numeric:tabular-nums;font-weight:600}}
.mix{{display:flex;height:6px;border-radius:3px;overflow:hidden;gap:1px}}
.mix i{{display:block;box-shadow:inset 0 0 0 1px var(--edge)}}
.sw{{box-shadow:inset 0 0 0 1px var(--edge)}}
.empty{{color:var(--muted)}}
.wip{{margin:4px 0 0;padding:10px 14px;background:#fff8d6;border-left:4px solid var(--yellow);color:var(--fg);font-size:15px;line-height:1.4;border-radius:2px}}
.wip b{{text-transform:uppercase;letter-spacing:.04em;color:var(--navy)}}
</style>
<header class="band"><div class="band-in">
    <h1>European Party Timelines</h1>
    <p class="lede">One timeline page per country, showing when each party began political activity, when it was registered or deregistered as a legal entity, and when it changed its name. On the map, each dot is one party, coloured by its affiliation in the selected year; the strip on each card shows how that country's parties currently split across Europarties; grey is no Europarty or no data yet; the database is still being completed.</p>
    <p class="wip" role="note"><b>Work in progress.</b> Our database does not list every party yet, and some records are still incomplete. Counts, maps and timelines only show the parties recorded so far.</p>
  </div></header>
<div class="wrap">
  __MAPSECTION__
  <label for="q" style="display:flex;flex-direction:column;gap:6px;font:700 13px var(--body);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)">Find a country<input id="q" type="search" placeholder="e.g. Serbia" autocomplete="off"></label>
  <div class="legend">{legend}<span><span class="sw" style="background:var(--bar)"></span>None / no data</span></div>
  <div class="cards" id="cards">
{chr(10).join(cards)}
  </div>
  <p class="empty" id="none" hidden>No country matches that search.</p>
</div>
<script>
const q=document.getElementById("q"),cards=[...document.querySelectorAll(".card")],none=document.getElementById("none");
q.addEventListener("input",()=>{{const v=q.value.trim().toLowerCase();let n=0;cards.forEach(c=>{{const m=!v||c.dataset.name.includes(v);c.hidden=!m;n+=m}});none.hidden=n>0}});
</script>
<script>(function(){{function s(){{try{{parent.postMessage({{type:"party-timeline-height",height:document.documentElement.scrollHeight}},"*")}}catch(e){{}}}}addEventListener("load",s);try{{new ResizeObserver(s).observe(document.body)}}catch(e){{}}}})();</script>
'''

# ---- map of Europe (shapes pre-projected in europe_map.json) ----
HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, 'europe_map.json'), encoding='utf-8'))
files = {c['country']: c['file'] for c in d['index']}
parts, dots = [], []
for s in sorted(M['shapes'], key=lambda s: -s['a']):
    nm = s['n']
    if nm in files:
        t = H.escape(nm)
        parts.append(f'<a href="{files[nm]}" aria-label="{t}"><path class="cty" data-c="{t}" d="{s["d"]}"><title>{t}</title></path></a>')
        if False:
            dots.append(f'<a href="{files[nm]}" aria-label="{t}"><circle class="dot" data-c="{t}" cx="{s["c"][0]}" cy="{s["c"][1]}" r="5"><title>{t}</title></circle></a>')
    else:
        parts.append(f'<path class="bg" d="{s["d"]}"><title>{H.escape(nm)}</title></path>')
mapc = [dict(country=c['country'], file=c['file'], tl=c.get('tl', {}), life=c.get('life', [])) for c in d['index'] if c['country'] in {s['n'] for s in M['shapes']}]
jj = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
sec = open(os.path.join(HERE, 'map_section.html'), encoding='utf-8').read()
sec = sec.replace('__W__', str(M['W'])).replace('__H__', str(M['H'])).replace('__PATHS__', ''.join(parts + dots))
sec = sec.replace('__COUNTRIES__', jj(mapc)).replace('__DIMS__', jj(d['dims'])).replace('__ANCHORS__', jj(M['anchors']))
body = body.replace('__MAPSECTION__', sec)
open(os.path.join(OUT, '_index_body.html'), 'w', encoding='utf-8').write(body)
full = '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<style>[hidden]{display:none!important}</style>\n' + body.replace('<header class="band">', '</head>\n<body>\n<header class="band">', 1) + '</body>\n</html>\n'
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(full)
print('ok')
