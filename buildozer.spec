[app]
title = Weight Calculator
package.name = weightcalculator
package.domain = org.weightcalc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = tests,bin,venv,.git,__pycache__,.buildozer,android,lib,.pytest_cache
version = 1.0.0.1

requirements = python3,kivy==2.3.1,numpy,pandas,sqlite3

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

android.permissions = INTERNET
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.api = 33
android.allow_backup = True

# Use p4a stable branch
p4a.branch = master
p4a.bootstrap = sdl2

# Set Python version explicitly
android.python_version = 3.10

[buildozer]
log_level = 2
warn_on_root = 1