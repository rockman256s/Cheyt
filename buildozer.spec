[app]
title = Weight Calculator
package.name = weightcalculator
package.domain = org.weightcalc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json
source.exclude_dirs = tests,bin,venv,.git,__pycache__,.buildozer,android,lib,.pytest_cache,.github
version = 1.0.0.1

requirements = python3,kivy==2.3.1,numpy,pandas,sqlite3,plyer

# Android specific
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.gradle_dependencies = com.android.support:support-compat:28.0.0

# Build options
android.release_artifact = apk
android.debug = True

# Set Python version explicitly
android.python_version = 3

[buildozer]
log_level = 2
warn_on_root = 1