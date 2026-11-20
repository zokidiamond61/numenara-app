"""Adjusts the generated Capacitor iOS project (Info.plist) before the build."""
import plistlib, pathlib, os
p = pathlib.Path("ios/App/App/Info.plist")
d = plistlib.loads(p.read_bytes())
d["CFBundleDisplayName"] = "Numenara"
# AdMob iOS App ID – Google's sample ID until the iOS app is added in AdMob
d["GADApplicationIdentifier"] = os.environ.get("ADMOB_IOS_APP_ID", "ca-app-pub-3683026843187590~8891716915")
d["NSUserTrackingUsageDescription"] = "This lets us show you more relevant ads. Numenara never shares your names or dates."
d["ITSAppUsesNonExemptEncryption"] = False
d["SKAdNetworkItems"] = [{"SKAdNetworkIdentifier": "cstr6suwn9.skadnetwork"}]
d["UIRequiresFullScreen"] = True
p.write_bytes(plistlib.dumps(d))
# Minimum iOS 15 (Apple requirement from April 2027)
import re
pod = pathlib.Path("ios/App/Podfile")
if pod.exists():
    pod.write_text(re.sub(r"platform :ios, '[0-9.]+'", "platform :ios, '15.0'", pod.read_text()))
pbx = pathlib.Path("ios/App/App.xcodeproj/project.pbxproj")
pbx.write_text(re.sub(r"IPHONEOS_DEPLOYMENT_TARGET = [0-9.]+;", "IPHONEOS_DEPLOYMENT_TARGET = 15.0;", pbx.read_text()))
print("Info.plist configured, iOS 15.0 minimum")
