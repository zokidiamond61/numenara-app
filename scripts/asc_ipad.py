"""Content rights declaration + 13-inch iPad screenshots (all version localizations)."""
import sys, os, glob, json, hashlib, urllib.request
sys.path.insert(0, "scripts")
from asc_api import call
APP = "6837479623"
def show(s, r, what): print(what, s, "" if s < 300 else json.dumps(r.get("errors", r))[:400])
s, r = call("PATCH", f"/v1/apps/{APP}", {"data": {"type": "apps", "id": APP, "attributes": {"contentRightsDeclaration": "DOES_NOT_USE_THIRD_PARTY_CONTENT"}}})
show(s, r, "content rights")
s, r = call("GET", f"/v1/apps/{APP}/appStoreVersions?filter[platform]=IOS"); vid = r["data"][0]["id"]
s, r = call("GET", f"/v1/appStoreVersions/{vid}/appStoreVersionLocalizations")
files = sorted(glob.glob("store/ipad-shots/*.png"), key=lambda p: int(p.split("-")[-1].split(".")[0]))
for vl in r["data"]:
    loc = vl["attributes"]["locale"]
    s, r2 = call("GET", f"/v1/appStoreVersionLocalizations/{vl['id']}/appScreenshotSets")
    sets = {x["attributes"]["screenshotDisplayType"]: x["id"] for x in r2.get("data", [])}
    print(loc, "sets:", list(sets))
    if "APP_IPHONE_67" not in sets: continue  # only where iPhone shots exist
    if "APP_IPAD_PRO_3GEN_129" in sets:
        ssid = sets["APP_IPAD_PRO_3GEN_129"]
        s, r3 = call("GET", f"/v1/appScreenshotSets/{ssid}/appScreenshots")
        for x in r3.get("data", []): call("DELETE", f"/v1/appScreenshots/{x['id']}")
    else:
        s, r3 = call("POST", "/v1/appScreenshotSets", {"data": {"type": "appScreenshotSets", "attributes": {"screenshotDisplayType": "APP_IPAD_PRO_3GEN_129"},
            "relationships": {"appStoreVersionLocalization": {"data": {"type": "appStoreVersionLocalizations", "id": vl["id"]}}}}})
        show(s, r3, loc + " ipad set"); ssid = r3["data"]["id"]
    for f in files:
        data = open(f, "rb").read()
        s, r3 = call("POST", "/v1/appScreenshots", {"data": {"type": "appScreenshots", "attributes": {"fileName": "ipad-" + os.path.basename(f), "fileSize": len(data)},
            "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": ssid}}}}})
        if s >= 300: show(s, r3, "reserve " + f); continue
        shot = r3["data"]
        for op in shot["attributes"]["uploadOperations"]:
            req = urllib.request.Request(op["url"], data=data[op["offset"]:op["offset"] + op["length"]], method=op["method"], headers={h["name"]: h["value"] for h in op["requestHeaders"]})
            urllib.request.urlopen(req).read()
        s, r3 = call("PATCH", f"/v1/appScreenshots/{shot['id']}", {"data": {"type": "appScreenshots", "id": shot["id"],
            "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}})
        show(s, r3, loc + " ipad " + os.path.basename(f))
print("done")
