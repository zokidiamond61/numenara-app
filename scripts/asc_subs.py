"""Creates Numenara auto-renewable subscriptions in App Store Connect (idempotent).
Each section is its own subscription group so a user can hold several at once."""
import sys, json
sys.path.insert(0, "scripts")
from asc_api import call
APP = "6837479623"
SUBS = [
 ("sub_karma","Karma","ONE_MONTH","9.99","Karma numbers, lessons and debts"),
 ("sub_chaldean","Chaldean Numerology","ONE_MONTH","9.99","Hidden energy of your name"),
 ("sub_energy","Energy","ONE_MONTH","9.99","Your colours, crystals and films"),
 ("sub_home","Home Numerology","ONE_MONTH","9.99","The energy of your home number"),
 ("sub_calendar","Numerology Calendar","ONE_MONTH","9.99","Your energy code for every day"),
 ("sub_synastry","Synastry","ONE_MONTH","9.99","Compatibility of two people"),
 ("sub_pro","Complete Pro","THREE_MONTHS","59.99","All Pro sections, no ads"),
 ("sub_elements","Four Elements","ONE_MONTH","9.99","Full analysis of your four elements"),
 ("sub_potentials","Potentials","ONE_MONTH","9.99","Your trigons and sextiles in depth"),
]
def ok(s, r, what):
    if s >= 300:
        print("FAIL", what, s, json.dumps(r.get("errors", r))[:600]); return False
    return True

s, r = call("GET", f"/v1/apps/{APP}/subscriptionGroups?include=subscriptions&limit=50")
existing = {x["attributes"]["productId"]: x["id"] for x in r.get("included", []) if x["type"] == "subscriptions"}
print("existing:", list(existing))
s, r = call("GET", "/v1/territories?limit=200"); terr = [t["id"] for t in r["data"]]
print("territories:", len(terr))

for pid, name, period, usd, desc in SUBS:
    if pid in existing:
        sid = existing[pid]; print(pid, "exists", sid)
    else:
        s, r = call("POST", "/v1/subscriptionGroups", {"data": {"type": "subscriptionGroups",
            "attributes": {"referenceName": "Numenara " + name},
            "relationships": {"app": {"data": {"type": "apps", "id": APP}}}}})
        if not ok(s, r, "group " + pid): continue
        gid = r["data"]["id"]
        s, r = call("POST", "/v1/subscriptionGroupLocalizations", {"data": {"type": "subscriptionGroupLocalizations",
            "attributes": {"name": "Numenara " + name if len("Numenara " + name) <= 30 else name, "locale": "en-US"},
            "relationships": {"subscriptionGroup": {"data": {"type": "subscriptionGroups", "id": gid}}}}})
        ok(s, r, "group loc " + pid)
        s, r = call("POST", "/v1/subscriptions", {"data": {"type": "subscriptions",
            "attributes": {"name": name, "productId": pid, "subscriptionPeriod": period, "familySharable": False, "groupLevel": 1,
                           "reviewNote": "Unlocks the " + name + " section of Numenara. Basic numbers are free. Reviewer access: tap the menu footer 7 times and enter the review code given in App Review Information."},
            "relationships": {"group": {"data": {"type": "subscriptionGroups", "id": gid}}}}})
        if not ok(s, r, "sub " + pid): continue
        sid = r["data"]["id"]; print(pid, "created", sid)
        s, r = call("POST", "/v1/subscriptionLocalizations", {"data": {"type": "subscriptionLocalizations",
            "attributes": {"name": name, "locale": "en-US", "description": desc},
            "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}}}}})
        ok(s, r, "loc " + pid)
    # availability
    s, r = call("POST", "/v1/subscriptionAvailabilities", {"data": {"type": "subscriptionAvailabilities",
        "attributes": {"availableInNewTerritories": True},
        "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}},
                          "availableTerritories": {"data": [{"type": "territories", "id": t} for t in terr]}}}})
    ok(s, r, "availability " + pid)
    # prices: USA base, equalized everywhere
    s, r = call("GET", f"/v1/subscriptions/{sid}/prices?limit=1")
    if r.get("data"):
        print(pid, "prices already set"); continue
    s, r = call("GET", f"/v1/subscriptions/{sid}/pricePoints?filter[territory]=USA&limit=800")
    pp = [p for p in r.get("data", []) if p["attributes"]["customerPrice"] in (usd, usd.rstrip("0"))]
    if not pp: print("FAIL no price point", pid, usd); continue
    ppid = pp[0]["id"]
    s, r = call("GET", f"/v1/subscriptionPricePoints/{ppid}/equalizations?limit=200")
    pts = [ppid] + [p["id"] for p in r.get("data", [])]
    n = 0
    for p in pts:
        s, r = call("POST", "/v1/subscriptionPrices", {"data": {"type": "subscriptionPrices",
            "attributes": {"preserveCurrentPrice": False},
            "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}},
                              "subscriptionPricePoint": {"data": {"type": "subscriptionPricePoints", "id": p}}}}})
        if s < 300: n += 1
        elif n == 0: ok(s, r, "price " + pid)
    print(pid, "prices set:", n, "/", len(pts))
# review screenshot for subscriptions that have none
import hashlib, urllib.request
def upload(ops, data):
    for op in ops:
        req = urllib.request.Request(op["url"], data=data[op["offset"]:op["offset"]+op["length"]], method=op["method"],
                                     headers={h["name"]: h["value"] for h in op["requestHeaders"]})
        urllib.request.urlopen(req).read()
data = open("store/review-paywall-v2.png", "rb").read()
s, r = call("GET", f"/v1/apps/{APP}/subscriptionGroups?include=subscriptions&limit=50")
for sub in [x for x in r.get("included", []) if x["type"] == "subscriptions"]:
    sid = sub["id"]; pid = sub["attributes"]["productId"]
    s, r2 = call("GET", f"/v1/subscriptions/{sid}/appStoreReviewScreenshot")
    if s < 300 and r2.get("data"): continue
    s, r2 = call("POST", "/v1/subscriptionAppStoreReviewScreenshots", {"data": {"type": "subscriptionAppStoreReviewScreenshots",
        "attributes": {"fileName": "paywall.png", "fileSize": len(data)},
        "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}}}}})
    if not ok(s, r2, "reserve shot " + pid): continue
    shot = r2["data"]; upload(shot["attributes"]["uploadOperations"], data)
    s, r2 = call("PATCH", f"/v1/subscriptionAppStoreReviewScreenshots/{shot['id']}", {"data": {"type": "subscriptionAppStoreReviewScreenshots", "id": shot["id"],
        "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}})
    print(pid, "screenshot", s)
s, r = call("GET", f"/v1/apps/{APP}/subscriptionGroups?include=subscriptions&limit=50")
for sub in [x for x in r.get("included", []) if x["type"] == "subscriptions"]:
    print("sub", sub["attributes"]["productId"], sub["attributes"].get("state"))
print("done")
