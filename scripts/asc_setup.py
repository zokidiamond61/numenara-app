"""Registers the iOS bundle ID and reports team / app record status."""
import sys
sys.path.insert(0, "scripts")
from asc_api import call
BID = "com.nannumero.numenara"

s, r = call("GET", f"/v1/bundleIds?filter[identifier]={BID}&limit=5")
print("List bundle IDs:", s)
items = [x for x in r.get("data", []) if x["attributes"]["identifier"] == BID]
if not items:
    s, r = call("POST", "/v1/bundleIds", {"data": {"type": "bundleIds", "attributes": {
        "name": "Numenara", "identifier": BID, "platform": "IOS"}}})
    print("Create bundle ID:", s, r.get("errors", ""))
    if s >= 300: sys.exit(1)
    items = [r["data"]]
b = items[0]
print("Bundle ID:", b["attributes"]["identifier"], "| seedId (Team/App ID prefix):", b["attributes"].get("seedId"))

s, r = call("GET", f"/v1/apps?filter[bundleId]={BID}")
apps = r.get("data", [])
print("App record in App Store Connect:", "YES " + apps[0]["id"] if apps else "NOT YET (create it in App Store Connect)")

s, r = call("GET", "/v1/certificates?limit=50")
print("Certificates:", s, [(c["attributes"]["certificateType"], c["attributes"].get("displayName")) for c in r.get("data", [])])
