"""Attach latest build, exclude China mainland, add review screenshots to subscriptions."""
import sys, os, json, hashlib, urllib.request
sys.path.insert(0, "scripts")
from asc_api import call
APP = "6837479623"
def show(s, r, what): print(what, s, "" if s < 300 else json.dumps(r.get("errors", r))[:400])
def upload(ops, data):
    for op in ops:
        req = urllib.request.Request(op["url"], data=data[op["offset"]:op["offset"]+op["length"]], method=op["method"],
                                     headers={h["name"]: h["value"] for h in op["requestHeaders"]})
        urllib.request.urlopen(req).read()

# 1. build
s, r = call("GET", f"/v1/builds?filter[app]={APP}&filter[preReleaseVersion.version]=1.0.7&sort=-uploadedDate&limit=5")
builds = [(b["id"], b["attributes"]["version"], b["attributes"]["processingState"]) for b in r.get("data", [])]
print("builds:", builds)
valid = [b for b in builds if b[2] == "VALID"]
s, r = call("GET", f"/v1/apps/{APP}/appStoreVersions?filter[platform]=IOS"); vid = r["data"][0]["id"]
if valid:
    s, r = call("PATCH", f"/v1/appStoreVersions/{vid}/relationships/build", {"data": {"type": "builds", "id": valid[0][0]}})
    show(s, r, "attach build " + valid[0][1])

# 2. China mainland off
s, r = call("GET", f"/v1/apps/{APP}/appAvailabilityV2")
if s < 300 and r.get("data"):
    aid = r["data"]["id"]
    s, r = call("GET", f"/v2/appAvailabilities/{aid}/territoryAvailabilities?limit=200&include=territory")
    for t in r.get("data", []):
        if t["relationships"]["territory"]["data"]["id"] == "CHN":
            s, r2 = call("PATCH", f"/v1/territoryAvailabilities/{t['id']}", {"data": {"type": "territoryAvailabilities", "id": t["id"], "attributes": {"available": False}}})
            show(s, r2, "China off")
else:
    s, r = call("GET", "/v1/territories?limit=200"); terr = [t["id"] for t in r["data"]]
    inc = [{"type": "territoryAvailabilities", "id": "${%s}" % t, "attributes": {"available": t != "CHN"},
            "relationships": {"territory": {"data": {"type": "territories", "id": t}}}} for t in terr]
    s, r = call("POST", "/v2/appAvailabilities", {"data": {"type": "appAvailabilities", "attributes": {"availableInNewTerritories": True},
        "relationships": {"app": {"data": {"type": "apps", "id": APP}},
                          "territoryAvailabilities": {"data": [{"type": "territoryAvailabilities", "id": x["id"]} for x in inc]}}}, "included": inc})
    show(s, r, "availability (all except China)")

# 3. review screenshot for each subscription
data = open("store/review-paywall.png", "rb").read()
s, r = call("GET", f"/v1/apps/{APP}/subscriptionGroups?include=subscriptions&limit=50")
for sub in [x for x in r.get("included", []) if x["type"] == "subscriptions"]:
    sid = sub["id"]
    s, r2 = call("GET", f"/v1/subscriptions/{sid}/appStoreReviewScreenshot")
    if s < 300 and r2.get("data"): print(sub["attributes"]["productId"], "has screenshot"); continue
    s, r2 = call("POST", "/v1/subscriptionAppStoreReviewScreenshots", {"data": {"type": "subscriptionAppStoreReviewScreenshots",
        "attributes": {"fileName": "paywall.png", "fileSize": len(data)},
        "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sid}}}}})
    if s >= 300: show(s, r2, "reserve " + sub["attributes"]["productId"]); continue
    shot = r2["data"]; upload(shot["attributes"]["uploadOperations"], data)
    s, r2 = call("PATCH", f"/v1/subscriptionAppStoreReviewScreenshots/{shot['id']}", {"data": {"type": "subscriptionAppStoreReviewScreenshots", "id": shot["id"],
        "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}})
    show(s, r2, "review screenshot " + sub["attributes"]["productId"])
print("done")
