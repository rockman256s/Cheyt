[app]
title = Weight Calculator
package.name = weightcalculator
package.domain = org.weightcalc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
version = 1.0.0.3

requirements = python3,\
    kivy==2.3.1,\
    pillow,\
    numpy,\
    scipy,\
    sqlite3

# Android specific
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

# Build options
android.allow_backup = True
android.logcat_filters = *:S python:D
android.copy_libs = 1

# Optimizations
android.enable_androidx = True
android.enable_kiosk = False
android.enable_split_config = true
android.enable_asset_packs = false

[buildozer]
log_level = 2
warn_on_root = 1