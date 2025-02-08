[app]
title = Weight Calculator
package.name = weightcalculator
package.domain = org.weightcalc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json
source.exclude_dirs = tests,bin,venv,.git,__pycache__,.buildozer,android,lib,.pytest_cache,.github
version = 1.0.0.1

requirements = python3,kivy==2.3.1,pillow

# Android specific
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.api = 28
android.minapi = 21
android.ndk = 23b
android.sdk = 28
android.accept_sdk_license = True
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Build options
android.release_artifact = apk
android.debug = True

# NDK/SDK paths
android.sdk_path = /opt/android/sdk
android.ndk_path = /opt/android/ndk

# Set Python version explicitly
android.python_version = 3

[buildozer]
log_level = 2
warn_on_root = 1