[app]
title = Weight Calculator
package.name = weightcalculator
package.domain = org.weightcalc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,db
source.include_patterns = assets/*,*.py
source.exclude_dirs = tests,bin,venv,.git,__pycache__
version = 1.0.0.1

requirements = python3,kivy==2.3.1,numpy,pandas,scipy,kivy_garden.graph

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a

# Android specific
android.permissions = INTERNET
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.gradle_dependencies = com.android.support:support-v4:27.1.1
android.allow_backup = True

# Garden requirements
garden_requirements = graph

[buildozer]
log_level = 2
warn_on_root = 1