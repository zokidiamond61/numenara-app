"""Adjusts the generated Capacitor Android project before the build."""
import os, re, pathlib

ADMOB_APP_ID = "ca-app-pub-3683026843187590~9007009821"
run = int(os.environ.get("GITHUB_RUN_NUMBER", "1"))
version_code = run
version_name = os.environ.get("VERSION_NAME", "1.0.7")  # visible version; versionCode still grows every build

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
v = re.sub(r"minSdkVersion\s*=\s*\d+", "minSdkVersion = 24", v)
vars_file.write_text(v)

props = pathlib.Path("android/gradle.properties")
p = props.read_text()
if "suppressUnsupportedCompileSdk" not in p:
    p += "\nandroid.suppressUnsupportedCompileSdk=36\n"
props.write_text(p)

# 4. Release build: R8 shrinking + obfuscation (Play "DEX code optimisation")
g = gradle.read_text()
g = re.sub(r"(release\s*\{[^}]*?)minifyEnabled\s+false", r"\1minifyEnabled true\n            shrinkResources true", g, count=1, flags=re.S)
g = g.replace("getDefaultProguardFile('proguard-android.txt')", "getDefaultProguardFile('proguard-android-optimize.txt')")
gradle.write_text(g)
assert "minifyEnabled true" in g, "could not enable minify"
rules = pathlib.Path("android/app/proguard-rules.pro")
rules.write_text(rules.read_text() + "\n" + pathlib.Path("scripts/proguard-rules.pro").read_text())

# 5. Edge-to-edge (Android 15+): dark window behind the system bars
styles = pathlib.Path("android/app/src/main/res/values/styles.xml")
st = styles.read_text()
pathlib.Path("android/app/src/main/res/values/numenara_colors.xml").write_text('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="numenara_bg">#FF120A24</color>\n</resources>\n')
if "numenara_bg" not in st:
    st = re.sub(r'(<style name="AppTheme\.NoActionBar"[^>]*>)',
                r'\1\n        <item name="android:windowBackground">@color/numenara_bg</item>\n        <item name="android:statusBarColor">@color/numenara_bg</item>\n        <item name="android:navigationBarColor">@color/numenara_bg</item>\n        <item name="android:windowLightStatusBar">false</item>',
                st, count=1)
styles.write_text(st)

print(f"Configured Android project: versionCode={version_code}, versionName={version_name}")
