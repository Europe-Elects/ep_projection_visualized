"""Reads the seat projection Sheets with the keyless Google login and writes the files the build uses:
  data/seats_party.tsv   per-party seats by month          (PROJECTION_SHEET_ID, first tab)
  data/seats_eu.tsv      EU-wide seats per group by month  (found by its header row, see below)
  site/history/*.csv     projection history for the page  (HISTORY_SHEET_ID)
Needs GOOGLE_TOKEN (google-github-actions/auth) and the three *_SHEET_ID repository secrets.
Every Sheet must be shared with ee-sheets-reader@project-6c08a079-4a01-46eb-aaf.iam.gserviceaccount.com (Viewer).
"""
import csv, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

API = 'https://sheets.googleapis.com/v4/spreadsheets/'
HISTORY_TABS = {'seats': '0', 'coalitions': '1928834079', 'share': '436173681'}   # same gids as before
# Header row of the EU-wide tab as it was last published (used to find the right tab in the Sheets).
EU_HEADER = ["", "Far-right ESN", "Right-wing PfE (prev. ID, ENF, EAPN)", "National-conservative ECR", "Populist EFDD", "Centre-right EPP", "Liberal Renew Europe (prev. ALDE)", "Non Inscrits", "unaffiliated", "Centre-left S&D", "Greens/EFA", "Left Group (prev. GUE/NGL)"]

def get(url):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + os.environ['GOOGLE_TOKEN']})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (400, 403, 404):
                raise RuntimeError(f'Sheets API {e.code} (is the Sheet shared with the service account?) {e.read()[:300]!r}')
            if attempt == 3: raise
        except urllib.error.URLError:
            if attempt == 3: raise
        time.sleep(5 * (attempt + 1))

def tabs(sheet_id):
    return [p['properties'] for p in get(API + sheet_id + '?fields=sheets.properties(sheetId,title,index)')['sheets']]

def values(sheet_id, title):
    rng = urllib.parse.quote("'" + title.replace("'", "''") + "'", safe='')
    rows = get(API + sheet_id + '/values/' + rng + '?valueRenderOption=FORMATTED_VALUE').get('values', [])
    width = max((len(r) for r in rows), default=0)
    return [r + [''] * (width - len(r)) for r in rows]

def by_gid(sheet_id, gid):
    t = next((p for p in tabs(sheet_id) if str(p['sheetId']) == str(gid)), None)
    if not t: raise RuntimeError(f'no tab with gid {gid}')
    return values(sheet_id, t['title'])

clean = lambda c: ' '.join(str(c).replace('\t', ' ').split('\n')).replace('\r', '')
def write_tsv(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(''.join('\t'.join(clean(c) for c in r) + '\n' for r in rows if any(str(c).strip() for c in r)))
    print(f'{path}: {len(rows) - 1} rows')

def find_eu_tab(sheet_ids):
    want = [h.strip() for h in EU_HEADER]
    fuzzy = None
    for sid in sheet_ids:
        for t in sorted(tabs(sid), key=lambda p: p.get('index', 0)):
            rng = urllib.parse.quote("'" + t['title'].replace("'", "''") + "'!1:2", safe='')
            top = get(API + sid + '/values/' + rng).get('values', [])
            head = [h.strip() for h in (top[0] if top else [])]
            if head[:len(want)] == want or [h for h in head if h] == [h for h in want if h]:
                print(f'EU-wide tab: "{t["title"]}"'); return sid, t['title']
            first = top[1][0] if len(top) > 1 and top[1] else ''
            if not fuzzy and any('EPP' in h for h in head) and any('S&D' in h for h in head) and re.match(r'\d{4}-\d{2}', first):
                fuzzy = (sid, t['title'])
    if fuzzy:
        print(f'EU-wide tab (by its columns): "{fuzzy[1]}"'); return fuzzy
    raise RuntimeError('EU-wide seat tab not found (header row with the group names and dates in the first column)')

def main():
    ids = {k: os.environ.get(k, '').strip() for k in ('PROJECTION_SHEET_ID', 'HEADLINE_SHEET_ID', 'HISTORY_SHEET_ID')}
    missing = [k for k, v in ids.items() if not v]
    if missing: sys.exit('Missing secrets: ' + ', '.join(missing))
    os.makedirs('data', exist_ok=True); os.makedirs('site/history', exist_ok=True)
    party = values(ids['PROJECTION_SHEET_ID'], sorted(tabs(ids['PROJECTION_SHEET_ID']), key=lambda p: p.get('index', 0))[0]['title'])
    if not party or 'EU Parliament group' not in party[0]:
        sys.exit('The first tab of the projection Sheet is not the per-party seat sheet')
    write_tsv('data/seats_party.tsv', party)
    sid, title = find_eu_tab([ids['HISTORY_SHEET_ID'], ids['PROJECTION_SHEET_ID'], ids['HEADLINE_SHEET_ID']])
    write_tsv('data/seats_eu.tsv', values(sid, title))
    for name, gid in HISTORY_TABS.items():
        try:
            rows = by_gid(ids['HISTORY_SHEET_ID'], gid)
        except RuntimeError as e:
            if name == 'seats': raise
            print(f'history/{name}.csv skipped: {e}'); continue
        with open(f'site/history/{name}.csv', 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(rows)
        print(f'site/history/{name}.csv: {len(rows) - 1} rows')

if __name__ == '__main__':
    main()
