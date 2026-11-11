#!/usr/bin/env bash
# Full Android build used by GitHub Actions. All output goes to the build log.
set -euo pipefail
SDKM="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"
[ -x "$SDKM" ] || SDKM="$(command -v sdkmanager)"
yes | "$SDKM" --licenses >/dev/null || true
"$SDKM" "platforms;android-36" "build-tools;36.0.0"

npm install
npx cap add android
npx capacitor-assets generate --android --iconBackgroundColor '#25124a' --splashBackgroundColor '#120a24'
python3 scripts/configure_android.py
npx cap sync android

if [ -z "${KEYSTORE_PASSWORD:-}" ]; then echo "Secret KEYSTORE_PASSWORD is missing"; exit 1; fi
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in keystore/upload.jks.enc -out "$RUNNER_TEMP/upload.jks" -pass env:KEYSTORE_PASSWORD

cd android
chmod +x gradlew
./gradlew bundleRelease assembleRelease --no-daemon --stacktrace \
  -Pandroid.injected.signing.store.file="$RUNNER_TEMP/upload.jks" \
  -Pandroid.injected.signing.store.password="$KEYSTORE_PASSWORD" \
  -Pandroid.injected.signing.key.alias=upload \
  -Pandroid.injected.signing.key.password="$KEYSTORE_PASSWORD"
cd ..
mkdir -p out
cp android/app/build/outputs/bundle/release/app-release.aab "out/Numenara-${GITHUB_RUN_NUMBER}.aab"
cp android/app/build/outputs/apk/release/app-release.apk "out/Numenara-${GITHUB_RUN_NUMBER}.apk"
