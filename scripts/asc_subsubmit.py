"""Add every READY_TO_SUBMIT subscription to the open review submission."""
import sys, json
sys.path.insert(0, "scripts")
from asc_api import call
APP = "6837479623"
s, r = call("GET", f"/v1/apps/{APP}/subscriptionGroups?include=subscriptions&limit=50")
for sub in [x for x in r.get("included", []) if x["type"] == "subscriptions"]:
    a = sub["attributes"]
    if a.get("state") != "READY_TO_SUBMIT": print(a["productId"], a.get("state")); continue
    s, r2 = call("POST", "/v1/subscriptionSubmissions", {"data": {"type": "subscriptionSubmissions",
        "relationships": {"subscription": {"data": {"type": "subscriptions", "id": sub["id"]}}}}})
    print(a["productId"], s, "" if s < 300 else json.dumps(r2.get("errors", r2))[:3000])
s, r = call("GET", f"/v1/reviewSubmissions?filter[app]={APP}&filter[state]=READY_FOR_REVIEW&include=items")
print("draft submissions:", [(x["id"], x["attributes"]["state"]) for x in r.get("data", [])], "items:", len(r.get("included", [])))
