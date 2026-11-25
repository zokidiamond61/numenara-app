"""Version 1.0.9: marketing URL, Croatian localization, attach newest build, submit for review."""
import sys, json, time
sys.path.insert(0, "scripts")
from asc_api import call
APP = "6837479623"; V = "1.0.9"
MKT = "https://zokidiamond61.github.io/numenara/"
SUP = "https://zokidiamond61.github.io/numenara/terms.html"
PRIV = "https://zokidiamond61.github.io/numenara/privacy.html"
def show(s, r, what): print(what, s, "" if s < 300 else json.dumps(r.get("errors", r))[:600])
SUBMIT = len(sys.argv) > 1 and sys.argv[1] == "submit"
EN_DESC = open("store/ios-description.txt").read().strip()
HR_DESC = open("store/ios-description-hr.txt").read().strip()
HR_KW = "numerologija,brojevi,karma,sudbina,horoskop,astrologija,kompatibilnost,ljubav,kristali,ime,rođenje"
EN_KW = "numerology,life path,karma,chaldean,name number,synastry,compatibility,crystals,astrology,horoscope"
assert len(HR_KW) <= 100, len(HR_KW)
WN_EN = "Improved first screen, swipe back gesture and small fixes."
WN_HR = "Poboljšan početni ekran, povratak povlačenjem prsta i manji popravci."

# version
s, r = call("GET", f"/v1/apps/{APP}/appStoreVersions?filter[platform]=IOS&limit=10")
vers = {x["attributes"]["versionString"]: x for x in r["data"]}
print("versions:", {k: v["attributes"]["appStoreState"] for k, v in vers.items()})
if V in vers: vid = vers[V]["id"]
else:
    s, r = call("POST", "/v1/appStoreVersions", {"data": {"type": "appStoreVersions",
        "attributes": {"platform": "IOS", "versionString": V, "releaseType": "AFTER_APPROVAL", "copyright": "2026 Barbara Tot"},
        "relationships": {"app": {"data": {"type": "apps", "id": APP}}}}})
    show(s, r, "create " + V); vid = r["data"]["id"]
s, r = call("PATCH", f"/v1/appStoreVersions/{vid}", {"data": {"type": "appStoreVersions", "id": vid, "attributes": {"releaseType": "AFTER_APPROVAL"}}})
show(s, r, "release after approval")

# version localizations
s, r = call("GET", f"/v1/appStoreVersions/{vid}/appStoreVersionLocalizations")
locs = {x["attributes"]["locale"]: x for x in r["data"]}
print("version locales:", list(locs))
en = locs["en-US"]
s, r = call("PATCH", f"/v1/appStoreVersionLocalizations/{en['id']}", {"data": {"type": "appStoreVersionLocalizations", "id": en["id"], "attributes": {
    "description": en["attributes"].get("description") or EN_DESC, "keywords": en["attributes"].get("keywords") or EN_KW,
    "marketingUrl": MKT, "supportUrl": SUP, "whatsNew": WN_EN}}})
show(s, r, "en-US marketing url + whats new")
hr_attrs = {"description": HR_DESC, "keywords": HR_KW, "marketingUrl": MKT, "supportUrl": SUP, "whatsNew": WN_HR,
    "promotionalText": "Otkrijte svoj numerološki kod s Nan Numero: brojevi imena, karma, kristali, kompatibilnost i nova mudrost, savjet i ritual svaki dan."}
if "hr" in locs:
    s, r = call("PATCH", f"/v1/appStoreVersionLocalizations/{locs['hr']['id']}", {"data": {"type": "appStoreVersionLocalizations", "id": locs["hr"]["id"], "attributes": hr_attrs}})
else:
    s, r = call("POST", "/v1/appStoreVersionLocalizations", {"data": {"type": "appStoreVersionLocalizations",
        "attributes": dict(hr_attrs, locale="hr"), "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": vid}}}}})
show(s, r, "hr version localization")

# app info (name/subtitle) hr
s, r = call("GET", f"/v1/apps/{APP}/appInfos")
infos = [x for x in r["data"] if x["attributes"].get("appStoreState") != "READY_FOR_SALE"] or r["data"]
iid = infos[0]["id"]
s, r = call("GET", f"/v1/appInfos/{iid}/appInfoLocalizations")
il = {x["attributes"]["locale"]: x for x in r["data"]}
hr_info = {"name": "Numenara: Numerologija i karma", "subtitle": "Brojevi, karma i kristali", "privacyPolicyUrl": PRIV}
if "hr" in il:
    s, r = call("PATCH", f"/v1/appInfoLocalizations/{il['hr']['id']}", {"data": {"type": "appInfoLocalizations", "id": il["hr"]["id"], "attributes": hr_info}})
else:
    s, r = call("POST", "/v1/appInfoLocalizations", {"data": {"type": "appInfoLocalizations", "attributes": dict(hr_info, locale="hr"),
        "relationships": {"appInfo": {"data": {"type": "appInfos", "id": iid}}}}})
show(s, r, "hr name/subtitle")

# build
s, r = call("GET", f"/v1/builds?filter[app]={APP}&filter[preReleaseVersion.version]={V}&sort=-uploadedDate&limit=3")
builds = [(b["id"], b["attributes"]["version"], b["attributes"]["processingState"]) for b in r.get("data", [])]
print("builds:", builds)
valid = [b for b in builds if b[2] == "VALID"]
if valid:
    s, r = call("PATCH", f"/v1/appStoreVersions/{vid}/relationships/build", {"data": {"type": "builds", "id": valid[0][0]}})
    show(s, r, "attach build " + valid[0][1])

# review notes
s, r = call("GET", f"/v1/appStoreVersions/{vid}/appStoreReviewDetail")
notes = open("store/review-notes.txt").read().strip()
if r.get("data"):
    rid = r["data"]["id"]
    s, r = call("PATCH", f"/v1/appStoreReviewDetails/{rid}", {"data": {"type": "appStoreReviewDetails", "id": rid, "attributes": {"notes": notes}}})
else:
    s, r = call("POST", "/v1/appStoreReviewDetails", {"data": {"type": "appStoreReviewDetails", "attributes": {
        "contactFirstName": "Barbara", "contactLastName": "Tot", "contactEmail": "nan.numero@gmail.com", "contactPhone": "+381603480311",
        "demoAccountRequired": False, "notes": notes},
        "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": vid}}}}})
show(s, r, "review details")

if SUBMIT and valid:
    s, r = call("POST", "/v1/reviewSubmissions", {"data": {"type": "reviewSubmissions", "attributes": {"platform": "IOS"},
        "relationships": {"app": {"data": {"type": "apps", "id": APP}}}}})
    show(s, r, "review submission")
    if s < 300:
        sid = r["data"]["id"]
        s, r = call("POST", "/v1/reviewSubmissionItems", {"data": {"type": "reviewSubmissionItems",
            "relationships": {"reviewSubmission": {"data": {"type": "reviewSubmissions", "id": sid}},
                              "appStoreVersion": {"data": {"type": "appStoreVersions", "id": vid}}}}})
        show(s, r, "add version")
        s, r = call("PATCH", f"/v1/reviewSubmissions/{sid}", {"data": {"type": "reviewSubmissions", "id": sid, "attributes": {"submitted": True}}})
        show(s, r, "SUBMITTED")
s, r = call("GET", f"/v1/appStoreVersions/{vid}")
print("state:", r["data"]["attributes"]["appStoreState"])
