# Numenara – R8 rules (shrink + obfuscate, keep what the WebView bridge needs)
-keepattributes *Annotation*,Signature,InnerClasses,EnclosingMethod,SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Capacitor bridge and plugins (looked up by reflection / annotations)
-keep class com.getcapacitor.** { *; }
-keep @com.getcapacitor.annotation.CapacitorPlugin class * { *; }
-keep class * extends com.getcapacitor.Plugin { *; }
-keepclassmembers class * { @com.getcapacitor.PluginMethod public <methods>; }
-keepclassmembers class * { @android.webkit.JavascriptInterface <methods>; }

# Cordova plugins (cordova-plugin-purchase) – classes are named in config.xml
-keep class org.apache.cordova.** { *; }
-keep class cc.fovea.** { *; }

# AdMob community plugin
-keep class com.getcapacitor.community.** { *; }

# Google Play Billing / Ads ship their own consumer rules; silence optional deps
-dontwarn org.apache.cordova.**
-dontwarn com.google.errorprone.annotations.**
-dontwarn javax.annotation.**
-dontwarn org.checkerframework.**
