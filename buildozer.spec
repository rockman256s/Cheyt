[app]
title = Weight Calculator
package.name = weightcalculator
package.domain = org.weightcalc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json
source.include_patterns = main_android.py
source.exclude_dirs = tests,bin,venv,.git,__pycache__,.buildozer,android,lib,.pytest_cache,.github
version = 1.0.0.6

requirements = python3==3.9.18,kivy==2.2.1,pillow==9.5.0,plyer==2.1.0,android

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
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Build options
android.release_artifact = apk
android.debug = True
android.logcat_filters = *:S python:D
android.copy_libs = 1

# Build optimization
android.enable_androidx = True
android.gradle_dependencies = androidx.core:core:1.6.0
p4a.hook = gradle

# Python-for-android specific
p4a.branch = develop
p4a.bootstrap = sdl2
p4a.local_recipes = ./p4a-recipes
p4a.extra_args = --color=always --debug

[buildozer]
log_level = 2
warn_on_root = 1