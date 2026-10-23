import sys
def load(path):
    L=[l.rstrip('\r') for l in open(path,encoding='utf-8').read().split('\n')]
    out=[];buf=None
    for l in L:
        if not l.strip() and buf is None: continue
        if buf is None: buf=l
        else: buf=buf+' '+l
        if len(buf.split('\t'))>=59:
            out.append(buf.split('\t')); buf=None
    if buf: out.append(buf.split('\t'))
    h=out[0]
    return h,[dict(zip(h,r)) for r in out[1:]]


REQUIRED = ["Status", "Country", "Name (Native)", "Name (English)", "Europe Elects Entity ID",
            "Europe Elects Entity Version", "Entity Version ID", "National Legal ID", "Abbreviation",
            "Ideological Orientation", "Political Activity Started", "Legal Entity Registration",
            "Legal Entity Deregistration", "Name Registration", "Name Deregistration",
            "European Parliament Group", "EP Group Start", "EP Group End", "Europarty Affiliation",
            "Europarty Start", "Europarty End", "PACE Group", "PACE Start", "PACE End",
            "International Party Federation", "International Affiliation Start", "International Affiliation End",
            "Nordic Council Group", "Nordic Council Start", "Nordic Council End", "CIS Affiliation", "CIS Start",
            "CIS End", "Benelux Affiliation", "Benelux Start", "Benelux End", "CLaRA Membership", "CLaRA Start",
            "CLaRA End", "CoR Membership", "CoR Start", "CoR End", "Europarty Interest to Join", "EP Interest to Join"]

_load = load
def load(path):
    h, R = _load(path)
    missing = [c for c in REQUIRED if c not in h]
    if missing:
        raise SystemExit("Sheet is missing expected columns: " + ", ".join(missing) + ". Fix the header row; the live site was left unchanged.")
    if len(R) < 50:
        raise SystemExit(f"Sheet has only {len(R)} rows; refusing to publish a near-empty build.")
    return h, R
