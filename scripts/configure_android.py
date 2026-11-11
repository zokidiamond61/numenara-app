"""Adjusts the generated Capacitor Android project before the build."""
import os, re, pathlib

ADMOB_APP_ID = "ca-app-pub-3683026843187590~9007009821"
run = int(os.environ.get("GITHUB_RUN_NUMBER", "1"))
version_code = run
version_name = f"1.0.{run}"

# 1. AdMob App ID in the manifest (required by the Google Mobile Ads SDK)
man = pathlib.Path("android/app/src/main/AndroidManifest.xml")
m = man.read_text()
if "com.google.android.gms.ads.APPLICATION_ID" not in m:
    m = re.sub(r"(<application\b[^>]*>)",
               r'\1\n        <meta-data android:name="com.google.android.gms.ads.APPLICATION_ID" android:value="%s"/>' % ADMOB_APP_ID,
               m, count=1)
man.write_text(m)

# 2. Version code / name
gradle = pathlib.Path("android/app/build.gradle")
g = gradle.read_text()
g = re.sub(r"versionCode\s+\d+", f"versionCode {version_code}", g)
g = re.sub(r'versionName\s+"[^"]*"', f'versionName "{version_name}"', g)
gradle.write_text(g)

# 3. Target the latest Android API level required by Google Play
vars_file = pathlib.Path("android/variables.gradle")
v = vars_file.read_text()
v = re.sub(r"compileSdkVersion\s*=\s*\d+", "compileSdkVersion = 36", v)
v = re.sub(r"targetSdkVersion\s*=\s*\d+", "targetSdkVersion = 36", v)
vars_file.write_text(v)

props = pathlib.Path("android/gradle.properties")
p = props.read_text()
if "suppressUnsupportedCompileSdk" not in p:
    p += "\nandroid.suppressUnsupportedCompileSdk=36\n"
props.write_text(p)

print(f"Configured Android project: versionCode={version_code}, versionName={version_name}")
