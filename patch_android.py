#!/usr/bin/env python3
"""يعدّل مجلد android الذي ينشئه `flutter create` ليناسب هذا التطبيق.

يُشغَّل من جذر المشروع. آمن إذا شُغّل أكثر من مرة.
  - صلاحية الإنترنت وصلاحية تثبيت الحزم
  - السماح بفتح روابط https (url_launcher)
  - اسم التطبيق الظاهر
  - رفع minSdk إلى 24 (مطلوب لتخزين التوكن المشفّر)
"""
import pathlib
import re
import sys

APP_LABEL = "بنّاء APK"
MIN_SDK = "24"

root = pathlib.Path("android")
manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
if not manifest.exists():
    sys.exit("android/app/src/main/AndroidManifest.xml not found - run `flutter create` first")

text = manifest.read_text(encoding="utf-8")

# 1) الصلاحيات
perms = ""
for name in ("android.permission.INTERNET", "android.permission.REQUEST_INSTALL_PACKAGES"):
    if name not in text:
        perms += f'    <uses-permission android:name="{name}"/>\n'

# 2) السماح بفتح روابط https
view_intent = (
    "<intent>\n"
    '            <action android:name="android.intent.action.VIEW"/>\n'
    '            <data android:scheme="https"/>\n'
    "        </intent>"
)
has_view = 'android:scheme="https"' in text
queries = ""
if not has_view:
    if "<queries>" in text:
        text = text.replace("<queries>", "<queries>\n        " + view_intent, 1)
    else:
        queries = "    <queries>\n        " + view_intent + "\n    </queries>\n"

if perms or queries:
    if "    <application" in text:
        text = text.replace("    <application", perms + queries + "    <application", 1)
    else:
        text = text.replace("<application", perms + queries + "<application", 1)

# 3) اسم التطبيق
text = re.sub(r'android:label="[^"]*"', f'android:label="{APP_LABEL}"', text, count=1)

manifest.write_text(text, encoding="utf-8")

# 4) minSdk
for rel in ("app/build.gradle", "app/build.gradle.kts"):
    f = root / rel
    if f.exists():
        s = f.read_text(encoding="utf-8")
        s2 = s.replace("flutter.minSdkVersion", MIN_SDK)
        if s2 != s:
            f.write_text(s2, encoding="utf-8")
            print(f"patched minSdk in {rel}")

print("android project patched")
