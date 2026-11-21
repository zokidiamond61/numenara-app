"""Put store/review-notes.txt into App Review notes of the editable iOS version."""
import sys, json
sys.path.insert(0, "scripts")
from asc_api import call
APP = "6837479623"
notes = open("store/review-notes.txt").read().strip()
s, r = call("GET", f"/v1/apps/{APP}/appStoreVersions?filter[platform]=IOS")
v = r["data"][0]; print("version", v["attributes"]["versionString"], v["attributes"]["appStoreState"])
s, r = call("GET", f"/v1/appStoreVersions/{v['id']}/appStoreReviewDetail")
rid = r["data"]["id"]
s, r = call("PATCH", f"/v1/appStoreReviewDetails/{rid}", {"data": {"type": "appStoreReviewDetails", "id": rid, "attributes": {"notes": notes}}})
print("notes", s, len(notes), "" if s < 300 else json.dumps(r.get("errors", r))[:400])
