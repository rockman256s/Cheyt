[app]
title = Weight Calculator
package.name = weightcalculator
package.domain = org.weightcalc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = assets/*
version = 1.0

requirements = python3,kivy,numpy,scipy,pandas

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# Android specific
android.permissions = INTERNET
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1