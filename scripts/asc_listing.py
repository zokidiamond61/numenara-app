"""Fills the App Store listing for Numenara (texts, categories, version, price, screenshots)."""
import sys, os, json, hashlib, glob, urllib.request
sys.path.insert(0, "scripts")
from asc_api import call
APP = "6837479623"
def show(s, r, what):
    print(what, s, "" if s < 300 else json.dumps(r.get("errors", r))[:500])

DESC = open("store/ios-description.txt").read().strip()

# 1. App info: categories + localization (name, subtitle, privacy URL)
s, r = call("GET", f"/v1/apps/{APP}/appInfos")
info = [x for x in r["data"] if x["attributes"].get("appStoreState") not in ("READY_FOR_SALE",)][0]
iid = info["id"]
s, r = call("PATCH", f"/v1/appInfos/{iid}", {"data": {"type": "appInfos", "id": iid, "relationships": {
    "primaryCategory": {"data": {"type": "appCategories", "id": "LIFESTYLE"}},
    "secondaryCategory": {"data": {"type": "appCategories", "id": "ENTERTAINMENT"}}}}})
show(s, r, "categories")
s, r = call("GET", f"/v1/appInfos/{iid}/appInfoLocalizations")
loc = [x for x in r["data"] if x["attributes"]["locale"] == "en-US"][0]
s, r = call("PATCH", f"/v1/appInfoLocalizations/{loc['id']}", {"data": {"type": "appInfoLocalizations", "id": loc["id"], "attributes": {
    "name": "Numenara: Numerology & Karma", "subtitle": "Your numbers, crystals & path",
    "privacyPolicyUrl": "https://zokidiamond61.github.io/numenara/privacy.html"}}})
show(s, r, "app info localization")

# 2. Version 1.0.7
s, r = call("GET", f"/v1/apps/{APP}/appStoreVersions?filter[platform]=IOS")
ver = r["data"][0]; vid = ver["id"]
s, r = call("PATCH", f"/v1/appStoreVersions/{vid}", {"data": {"type": "appStoreVersions", "id": vid, "attributes": {
    "versionString": "1.0.7", "copyright": "2026 Barbara Tot", "releaseType": "MANUAL"}}})
show(s, r, "version 1.0.7 (manual release)")
s, r = call("GET", f"/v1/appStoreVersions/{vid}/appStoreVersionLocalizations")
vl = [x for x in r["data"] if x["attributes"]["locale"] == "en-US"][0]
s, r = call("PATCH", f"/v1/appStoreVersionLocalizations/{vl['id']}", {"data": {"type": "appStoreVersionLocalizations", "id": vl["id"], "attributes": {
    "description": DESC,
    "keywords": "numerology,life path,karma,chaldean,name number,synastry,compatibility,crystals,astrology,horoscope",
    "promotionalText": "Discover your numerology code with Nan Numero: name numbers, karma, crystals, compatibility and new daily wisdom, advice and rituals every day.",
    "supportUrl": "https://zokidiamond61.github.io/numenara/terms.html"}}})
show(s, r, "version texts")

# 3. Price: free
s, r = call("GET", f"/v1/apps/{APP}/appPricePoints?filter[territory]=USA&limit=5")
free = [p for p in r.get("data", []) if p["attributes"]["customerPrice"] in ("0", "0.0", "0.00")]
if free:
    body = {"data": {"type": "appPriceSchedules", "relationships": {
        "app": {"data": {"type": "apps", "id": APP}},
        "baseTerritory": {"data": {"type": "territories", "id": "USA"}},
        "manualPrices": {"data": [{"type": "appPrices", "id": "${p0}"}]}}},
        "included": [{"type": "appPrices", "id": "${p0}", "attributes": {"startDate": None},
                      "relationships": {"appPricePoint": {"data": {"type": "appPricePoints", "id": free[0]["id"]}}}}]}
    s, r = call("POST", "/v1/appPriceSchedules", body); show(s, r, "price free")

# 4. Screenshots (6.9" iPhone)
s, r = call("GET", f"/v1/appStoreVersionLocalizations/{vl['id']}/appScreenshotSets")
sets = {x["attributes"]["screenshotDisplayType"]: x["id"] for x in r.get("data", [])}
if "APP_IPHONE_67" in sets:
    ssid = sets["APP_IPHONE_67"]
    s, r = call("GET", f"/v1/appScreenshotSets/{ssid}/appScreenshots")
    for x in r.get("data", []): call("DELETE", f"/v1/appScreenshots/{x['id']}")
else:
    s, r = call("POST", "/v1/appScreenshotSets", {"data": {"type": "appScreenshotSets", "attributes": {"screenshotDisplayType": "APP_IPHONE_67"},
        "relationships": {"appStoreVersionLocalization": {"data": {"type": "appStoreVersionLocalizations", "id": vl["id"]}}}}})
    show(s, r, "screenshot set"); ssid = r["data"]["id"]
for f in sorted(glob.glob("store/ios-shots/*.png"), key=lambda p: int(p.split("-")[-1].split(".")[0])):
    data = open(f, "rb").read()
    s, r = call("POST", "/v1/appScreenshots", {"data": {"type": "appScreenshots", "attributes": {"fileName": os.path.basename(f), "fileSize": len(data)},
        "relationships": {"appScreenshotSet": {"data": {"type": "appScreenshotSets", "id": ssid}}}}})
    if s >= 300: show(s, r, "reserve " + f); continue
    shot = r["data"]
    for op in shot["attributes"]["uploadOperations"]:
        chunk = data[op["offset"]:op["offset"] + op["length"]]
        req = urllib.request.Request(op["url"], data=chunk, method=op["method"], headers={h["name"]: h["value"] for h in op["requestHeaders"]})
        urllib.request.urlopen(req).read()
    s, r = call("PATCH", f"/v1/appScreenshots/{shot['id']}", {"data": {"type": "appScreenshots", "id": shot["id"],
        "attributes": {"uploaded": True, "sourceFileChecksum": hashlib.md5(data).hexdigest()}}})
    show(s, r, "screenshot " + os.path.basename(f))
print("done")
