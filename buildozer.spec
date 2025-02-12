[app]
title = Weight Calculator
package.name = weightcalculator
package.domain = org.weightcalc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,toml
source.exclude_dirs = tests, bin, venv, .git
version = 1.0.0.3

requirements = python3,\
    flet==0.19.0,\
    flet-core==0.19.0,\
    numpy==1.26.0,\
    scipy==1.11.3,\
    pillow>=10.0.1

# Android specific
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True

# Build options
android.logcat_filters = *:S python:D
android.copy_libs = 1

# Bootstrap configuration
p4a.bootstrap = webview
p4a.hook = 

# Build settings
android.build_mode = debug
android.accept_sdk_license = True
android.skip_update = True

[buildozer]
log_level = 2
warn_on_root = 1