"""Adjusts the generated Capacitor iOS project (Info.plist) before the build."""
import plistlib, pathlib, os
p = pathlib.Path("ios/App/App/Info.plist")
d = plistlib.loads(p.read_bytes())
d["CFBundleDisplayName"] = "Numenara"
# AdMob iOS App ID – Google's sample ID until the iOS app is added in AdMob
d["GADApplicationIdentifier"] = os.environ.get("ADMOB_IOS_APP_ID", "ca-app-pub-3940256099942544~1458002511")
d["NSUserTrackingUsageDescription"] = "This lets us show you more relevant ads. Numenara never shares your names or dates."
d["ITSAppUsesNonExemptEncryption"] = False
d["SKAdNetworkItems"] = [{"SKAdNetworkIdentifier": "cstr6suwn9.skadnetwork"}]
d["UIRequiresFullScreen"] = True
p.write_bytes(plistlib.dumps(d))
print("Info.plist configured")
