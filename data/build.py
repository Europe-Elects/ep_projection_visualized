import sys, re, json, os, unicodedata, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from load import load

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
h, R = load(SRC)

# Party-family colours (Political Party Database codebook palette, as supplied)
CD, SOC, LIB, CEN, GRN, REG = "#3399FF", "#FF0000", "#FFD700", "#fa8c00", "#009900", "#008080"
EURO, ECO, LEFT, FARL, NATC, CHR = "#502379", "#fb1d79", "#990000", "#7c0000", "#0000FF", "#a16585"
PFE, FARR, PIR, ANI, LIBT, AGR = "#000000", "#70463A", "#9c36b8", "#009076", "#F2C300", "#90ee90"
NIC = "#8a7f99"  # non-attached / not registered (not in the supplied palette)

DIMS = [
 dict(id="europarty", label="Europarty", full="Europarty affiliation", col="Europarty Affiliation",
      f="Europarty Start", t="Europarty End", w="Europarty Interest to Join", keys=collections.OrderedDict([
  ("EPP", (CD, "European People's Party")), ("PES", (SOC, "Party of European Socialists")),
  ("ALDE", (LIB, "ALDE Party")), ("EDP", (CEN, "European Democratic Party")),
  ("EGP", (GRN, "European Green Party")), ("EFA", (REG, "European Free Alliance")),
  ("Volt", (EURO, "Volt Europa")), ("ELA", (ECO, "European Left Alliance for the People and the Planet")),
  ("PEL", (LEFT, "Party of the European Left")), ("DiEM25", (LEFT, "DiEM25 (left-wing family colour)")),
  ("ECL", (FARL, "European Communist Action")),
  ("ECR", (NATC, "European Conservatives and Reformists Party")),
  ("ECPP", (CHR, "European Christian Political Party")),
  ("ECA", (CHR, "European Christian Alliance (Christian family colour)")),
  ("Patriots.eu", (PFE, "Patriots.eu")), ("ESN", (FARR, "Europe of Sovereign Nations")),
  ("APF", (FARR, "Alliance for Peace and Freedom (far-right family colour)")),
  ("PPEU", (PIR, "European Pirate Party")), ("Animal Politics EU", (ANI, "Animal Politics EU"))])),
 dict(id="ep", label="EP group", full="European Parliament group", col="European Parliament Group",
      f="EP Group Start", t="EP Group End", w="EP Interest to Join", keys=collections.OrderedDict([
  ("EPP", (CD, "Group of the European People's Party")), ("S&D", (SOC, "Socialists & Democrats")),
  ("RE", (LIB, "Renew Europe")), ("Greens/EFA", (GRN, "Greens/European Free Alliance")),
  ("LEFT", (LEFT, "The Left")), ("ECR", (NATC, "European Conservatives and Reformists")),
  ("PfE", (PFE, "Patriots for Europe")), ("ESN", (FARR, "Europe of Sovereign Nations")),
  ("NI", (NIC, "Non-attached members"))])),
 dict(id="pace", label="PACE", full="Parliamentary Assembly of the Council of Europe group", col="PACE Group",
      f="PACE Start", t="PACE End", w=None, keys=collections.OrderedDict([
  ("EPP/CD", (CD, "EPP/Christian Democrats")), ("SOC", (SOC, "Socialists, Democrats and Greens")),
  ("ALDE", (LIB, "Alliance of Liberals and Democrats for Europe")),
  ("UEL", (LEFT, "Group of the Unified European Left")),
  ("ECPA", (NATC, "European Conservatives, Patriots & Affiliates")),
  ("NR", (NIC, "Not registered in a group"))])),
 dict(id="intl", label="International", full="International party federation", col="International Party Federation",
      f="International Affiliation Start", t="International Affiliation End", w=None, keys=collections.OrderedDict([
  ("CDI", (CD, "Centrist Democrat International")), ("SI", (SOC, "Socialist International")),
  ("PA", (SOC, "Progressive Alliance")), ("LI", (LIB, "Liberal International")),
  ("GG", (GRN, "Global Greens")), ("PI", (ECO, "Progressive International")),
  ("IMCWP", (FARL, "International Meeting of Communist and Workers' Parties")),
  ("PftAIM", (FARL, "Platform for the Anti-Imperialist Movement")),
  ("WAP", (FARL, "World Anti-imperialist Platform")),
  ("IDU", (NATC, "International Democracy Union")), ("PPI", (PIR, "Pirate Parties International")),
  ("IALP", (LIBT, "International Alliance of Libertarian Parties"))])),
 dict(id="nordic", label="Nordic Council", full="Nordic Council group", col="Nordic Council Group",
      f="Nordic Council Start", t="Nordic Council End", w=None, keys=collections.OrderedDict([
  ("ConG", (CD, "Conservative Group")), ("SDG", (SOC, "Social Democratic Group")),
  ("CG", (LIB, "Centre Group")), ("NGLA", (LEFT, "Nordic Green Left Alliance")),
  ("NF", (PFE, "Nordic Freedom")), ("NI-NC", (NIC, "Non-attached"))])),
 dict(id="benelux", label="Benelux", full="Benelux Parliament group", col="Benelux Affiliation",
      f="Benelux Start", t="Benelux End", w=None, keys=collections.OrderedDict([
  ("CF/GC", (CD, "Christian group")), ("SGD/SVD", (SOC, "Socialist group")),
  ("LF/GL", (LIB, "Liberal group")), ("VB/PVV", (PFE, "VB/PVV group")), ("NI", (NIC, "Non-attached"))])),
 dict(id="clara", label="CLRA", full="Congress of Local and Regional Authorities group", col="CLaRA Membership",
      f="CLaRA Start", t="CLaRA End", w=None, keys=collections.OrderedDict([
  ("EPP", (CD, "European People's Party Group")), ("SGPD", (SOC, "Socialists, Greens and Progressive Democrats")),
  ("ILDG", (LIB, "Independent Liberal and Democratic Group")), ("ECR", (NATC, "European Conservatives and Reformists")),
  ("PfE", (PFE, "Patriots for Europe")), ("NI", (NIC, "Non-attached"))])),
 dict(id="cor", label="CoR", full="European Committee of the Regions group", col="CoR Membership",
      f="CoR Start", t="CoR End", w=None, keys=collections.OrderedDict([
  ("EPP", (CD, "European People's Party")), ("PES", (SOC, "Party of European Socialists")),
  ("RE", (LIB, "Renew Europe")), ("ECR", (NATC, "European Conservatives and Reformists")),
  ("NI", (NIC, "Non-attached"))])),
 dict(id="cis", label="CIS", full="CIS affiliation", col="CIS Affiliation",
      f="CIS Start", t="CIS End", w=None, keys=collections.OrderedDict([
  ("UPC–CPSU", (FARL, "Union of Communist Parties – CPSU"))])),
]

def year(v):
    m = re.search(r'\d{4}', v or '')
    return int(m.group()) if m else None

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def clean(v):
    v = (v or '').strip()
    return '' if v.lower() in ('unaffiliated', '*', '') else v

def keys_of(v, dim):
    v = clean(v)
    if not v: return []
    out = []
    for p in re.split(r'[;,]', v):
        p = p.strip()
        if not p or p.lower() == 'unaffiliated': continue
        if p in dim['keys'] or len(p) <= 12:
            if p not in out: out.append(p)
    return out

by_country = collections.OrderedDict()
for r in R:
    by_country.setdefault(r['Country'].strip(), []).append(r)


# Founding year of each affiliation (earliest direct predecessor where one existed); bars never colour before it.
FOUNDED = {
 "europarty": {"EPP":1976,"PES":1974,"ALDE":1976,"EDP":2004,"EGP":1984,"EFA":1981,"Volt":2017,"ELA":2024,"PEL":2004,
               "DiEM25":2016,"ECL":2023,"ECR":2009,"ECPP":2002,"Patriots.eu":2014,"ESN":2024,"APF":2015,"PPEU":2014,
               "Animal Politics EU":2014},
 "ep": {"EPP":1953,"S&D":1953,"RE":1953,"Greens/EFA":1984,"LEFT":1973,"ECR":2009,"PfE":2015,"ESN":2024,"NI":1953},
 "pace": {"EPP/CD":1964,"SOC":1964,"ALDE":1964,"UEL":1991,"ECPA":1970,"NR":1949},
 "intl": {"CDI":1961,"SI":1951,"PA":2013,"LI":1947,"GG":2001,"PI":2020,"IMCWP":1998,"PftAIM":2022,"WAP":2022,
          "IDU":1983,"PPI":2010,"IALP":2015},
 "nordic": {}, "benelux": {}, "clara": {}, "cor": {}, "cis": {"UPC–CPSU":1993},
}
FLOOR = {"europarty":1974,"ep":1953,"pace":1949,"intl":1947,"nordic":1952,"benelux":1955,"clara":1957,"cor":1994,"cis":1991}
# EP group membership is only possible while the country is in the EU (or its predecessors)
EU_JOIN = {"Belgium":1952,"France":1952,"Germany":1952,"Italy":1952,"Luxembourg":1952,"Netherlands":1952,
           "Denmark":1973,"Ireland":1973,"United Kingdom":1973,"Greenland":1973,"Greece":1981,"Portugal":1986,"Spain":1986,
           "Austria":1995,"Finland":1995,"Sweden":1995,"Åland Islands":1995,
           "Cyprus":2004,"Czechia":2004,"Estonia":2004,"Hungary":2004,"Latvia":2004,"Lithuania":2004,"Malta":2004,
           "Poland":2004,"Slovakia":2004,"Slovenia":2004,"Bulgaria":2007,"Romania":2007,"Croatia":2013}
EU_LEAVE = {"Greenland":1985,"United Kingdom":2020}
EU_DROPPED = []
def eu_window(country):
    if country == "European Union": return (None, None)
    if country not in EU_JOIN: return False
    return (EU_JOIN[country], EU_LEAVE.get(country))

def founded(dim, keys):
    ys = [FOUNDED[dim].get(k, FLOOR[dim]) for k in keys]
    y = min(ys) if ys else FLOOR[dim]
    # Europarties only exist as a formal category from Regulation 2004/2003
    return max(y, 2004) if dim == "europarty" else y

index = []
LINKS = []
def vnum(r):
    try: return int(r['Europe Elects Entity Version'])
    except: return 0

for country, rs in sorted(by_country.items(), key=lambda kv: kv[0].replace('Å', 'A')):
    ents = collections.OrderedDict()
    for r in rs: ents.setdefault(r['Europe Elects Entity ID'].strip() or r['Entity Version ID'], []).append(r)
    for vs_ in ents.values(): vs_.sort(key=lambda r: (vnum(r), year(r['Name Registration']) or 0))
    # link renamed/realigned entities to their continuation under another entity ID
    def lscore(a, o):
        s = 0
        if a['National Legal ID'].strip() and a['National Legal ID'].strip() == o['National Legal ID'].strip(): s += 4
        for c in ('Political Activity Started', 'Legal Entity Registration'):
            if year(a[c]) and year(a[c]) == year(o[c]): s += 1
        if year(a['Name Deregistration']) and year(a['Name Deregistration']) == year(o['Name Registration']): s += 2
        if a['Abbreviation'].strip() == o['Abbreviation'].strip(): s += 1
        return s
    succ = {}
    for eid, vs_ in ents.items():
        t = vs_[-1]
        if t['Status'].strip() not in ('renamed', 'realigned'): continue
        best = None
        for oid, ovs in ents.items():
            if oid == eid or oid in succ.values(): continue
            o = ovs[0]
            s = lscore(t, o)
            ok = s >= 4 or (t['Status'].strip() == 'realigned' and t['Abbreviation'].strip() == o['Abbreviation'].strip() and s >= 3)
            if ok and (best is None or s > best[0]): best = (s, oid)
        if best: succ[eid] = best[1]
    for a, b in succ.items(): LINKS.append((country, a, b, ents[a][-1]['Abbreviation'].strip(), ents[b][0]['Abbreviation'].strip()))
    # fold chains: predecessors' versions go before the successor's
    def root(e):
        seen = set()
        while e in succ and e not in seen: seen.add(e); e = succ[e]
        return e
    merged = collections.OrderedDict()
    order = {}
    for eid in ents:
        rt = root(eid)
        merged.setdefault(rt, [])
    for eid, vs_ in ents.items():
        rt = root(eid); n = 0; e = eid
        while e != rt: n += 1; e = succ[e]
        for r in vs_: order[id(r)] = -n
        merged[rt].extend(vs_)
    ents = collections.OrderedDict((k, v) for k, v in merged.items() if v)
    rows, und = [], []
    for ei, (eid, vs) in enumerate(ents.items()):
        vs.sort(key=lambda r: (order[id(r)], vnum(r), year(r['Name Registration']) or year(r['Political Activity Started']) or 0))
        V = []
        for r in vs:
            a = {}
            for d in DIMS:
                k = keys_of(r[d['col']], d)
                a[d['id']] = dict(k=k, f=year(r[d['f']]) if k else None, t=year(r[d['t']]) if k else None,
                                  w=clean(r[d['w']]) if d['w'] else '')
            V.append(dict(r=r, a=a, act=year(r['Political Activity Started']), lr=year(r['Legal Entity Registration']),
                          ld=year(r['Legal Entity Deregistration']), nr=year(r['Name Registration']),
                          nd=year(r['Name Deregistration'])))
        starts = [x for v in V for x in (v['act'], v['lr'], v['nr']) if x]
        e_start = min(starts) if starts else None
        # version windows
        for n, v in enumerate(V):
            if n == 0: v['s'] = e_start
            else: v['s'] = V[n-1]['e']
            if n == len(V) - 1:
                v['e'] = None
            else:
                ends = [x for x in [v['nd'], v['ld']] + [v['a'][d['id']]['t'] for d in DIMS] if x]
                nxt = V[n+1]
                nstarts = [x for x in [nxt['nr']] + [nxt['a'][d['id']]['f'] for d in DIMS] if x and (v['s'] is None or x >= v['s'])]
                v['e'] = max(ends) if ends else (max(nstarts) if nstarts else v['s'])
                if v['s'] is not None and v['e'] is not None and v['e'] < v['s']: v['e'] = v['s']
        last = V[-1]
        aff, want = {}, {}
        for d in DIMS:
            iv = []
            for n, v in enumerate(V):
                a = v['a'][d['id']]
                if a['k']:
                    f = a['f'] if a['f'] is not None else v['s']
                    t = a['t'] if a['t'] is not None else (None if n == len(V) - 1 else v['e'])
                    fy = founded(d['id'], a['k'])
                    # start unknown: no start year recorded and not a continuation of the same affiliation
                    unk = a['f'] is None and not (iv and iv[-1]['k'] == a['k'])
                    if f is None or f < fy: f = fy
                    if d['id'] == 'ep':
                        win = eu_window(country)
                        if win is False:
                            EU_DROPPED.append((country, v['r']['Abbreviation'].strip(), a['k'])); continue
                        if win[0] is not None and f < win[0]: f = win[0]
                        if win[1] is not None: t = win[1] if t is None else min(t, win[1])
                    if t is not None and t < f: continue
                    rec_ = dict(k=a['k'], f=f, t=t, v=n)
                    if unk: rec_['u'] = 1
                    iv.append(rec_)
            if iv: aff[d['id']] = iv
        # name history: merge consecutive identical names
        names = []
        for n, v in enumerate(V):
            ab, nm = v['r']['Abbreviation'].strip(), v['r']['Name (English)'].split(' / ')[0].strip()
            s = v['nr'] if v['nr'] is not None else v['s']
            if names and names[-1]['abbr'] == ab and names[-1]['name'] == nm:
                names[-1]['e'] = v['nd']
                continue
            if names and names[-1]['e'] is None and s is not None: names[-1]['e'] = s - 1 if s - 1 >= (names[-1]['s'] or 0) else s
            names.append(dict(abbr=ab, name=nm, s=s, e=v['nd']))
        ld = last['ld']
        lr = min([v['lr'] for v in V if v['lr']] or [None]) if any(v['lr'] for v in V) else None
        act = min([v['act'] for v in V if v['act']]) if any(v['act'] for v in V) else None
        lr0 = last['r']
        cur = {d['id']: last['a'][d['id']]['k'] for d in DIMS if last['a'][d['id']]['k']}
        rec = dict(i=ei, eid=eid, abbr=lr0['Abbreviation'].strip(), name=lr0['Name (English)'].split(' / ')[0].strip(),
                   native=lr0['Name (Native)'].strip(), status=lr0['Status'].strip(),
                   act=act, lr=lr, ld=ld, nd=last['nd'], aff=aff, cur=cur, want=want,
                   names=[x for x in names if x['s'] is not None] if any(x['s'] is not None for x in names) else [],
                   vers=[dict(vid=v['r']['Entity Version ID'].strip(), status=v['r']['Status'].strip(), s=v['s'], e=v['e'],
                              abbr=v['r']['Abbreviation'].strip(), name=v['r']['Name (English)'].split(' / ')[0].strip(),
                              a={d['id']: v['a'][d['id']]['k'] for d in DIMS if v['a'][d['id']]['k']}) for v in V],
                   former=[x['abbr'] for x in names[:-1] if x['abbr'] != lr0['Abbreviation'].strip()],
                   reg=lr0['National Legal ID'].strip(), ideo=lr0['Ideological Orientation'].strip())
        (und if e_start is None else rows).append(rec)
    allr = rows + und
    dims_here = [dict(id=d['id'], label=d['label'], full=d['full'], keys={k: list(v) for k, v in d['keys'].items()})
                 for d in DIMS if any(d['id'] in x['aff'] or d['id'] in x['want'] for x in allr)]
    if not dims_here or dims_here[0]['id'] != 'europarty':
        d0 = DIMS[0]
        dims_here = [dict(id=d0['id'], label=d0['label'], full=d0['full'], keys={k: list(v) for k, v in d0['keys'].items()})] + \
                    [d for d in dims_here if d['id'] != 'europarty']
    ys = [x['act'] or x['lr'] for x in rows if x['act'] or x['lr']] + [n['s'] for x in rows for n in x['names'] if n['s']]
    lo = min(ys) if ys else 2000
    span = 2027 - lo
    step = 25 if span > 120 else 20 if span > 80 else 10 if span > 45 else 5
    y0 = ((lo - max(3, span // 18)) // step) * step
    span = 2027 - y0
    minw = int(max(860, min(1100, 270 + span * 9)))
    minws = int(max(700, min(950, 170 + span * 8)))
    html = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
    j = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
    for k, v in {"__TITLE__": f"{country} Party Timeline", "__COUNTRY__": country,
                 "__EPLIGHT__": "", "__EPDARK__": "", "__MINWS__": str(minws), "__MINW__": str(minw),
                 "__Y0__": str(y0), "__STEP__": str(step), "__DIMS__": j(dims_here),
                 "__DATA__": j(rows), "__UNDATED__": j(und)}.items():
        html = html.replace(k, v)
    fn = slug(country) + '.html'
    open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(html)
    mix = collections.Counter(x['cur']['europarty'][0] for x in allr if x['cur'].get('europarty'))
    # per-affiliation membership spans for the map: [key, from, to or None]
    tl = {}
    life = []
    for pi, x in enumerate(allr):
        s0 = min([y for y in [x['act'], x['lr']] + [nm['s'] for nm in x['names']] if y is not None] or [None]) if (x['act'] or x['lr'] or x['names']) else None
        pend = x['ld'] if x['ld'] is not None else (x['nd'] if x['status'] == 'inactive' else None)
        life.append([s0, pend])
        for did, ivl in x['aff'].items():
            for v in ivl:
                f = v['f'] if v['f'] is not None else s0
                if f is None: continue
                if s0 is not None and f < s0: f = s0
                t = v['t']
                if pend is not None: t = pend if t is None else min(t, pend)
                if t is not None and t < f: continue
                for k in v['k']:
                    tl.setdefault(did, []).append([k, f, t, pi])
    index.append(dict(country=country, file=fn, n=len(allr),
                      active=sum(x['status'] == 'active' for x in allr),
                      mem=sum(mix.values()), mix=[[k, mix[k]] for k in DIMS[0]['keys'] if mix[k]], tl=tl, life=life))

eps = {k: ["--ep-" + slug(k), v[1], v[0], v[0]] for k, v in DIMS[0]['keys'].items()}
dims_all = [dict(id=d['id'], label=d['label'], full=d['full'], keys={k: list(v) for k, v in d['keys'].items()}) for d in DIMS]
json.dump(dict(index=index, eps=eps, dims=dims_all), open(os.path.join(OUT, '_index.json'), 'w'), ensure_ascii=False)
print(len(index), 'countries')
for x in EU_DROPPED: print('EP group ignored (country not in the EU):', *x)
for l in LINKS: print('linked', *l)
