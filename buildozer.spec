[app]

# (str) Title of your application
title = Weight Calculator

# (str) Package name
package.name = weightcalculator

# (str) Package domain (needed for android/ios packaging)
package.domain = org.weightcalculator

# (str) Source code where the main.py live
source.dir = .

# (str) Application versioning
version = 1.0.0

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,db

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, .github, __pycache__, .buildozer

# (list) List of exclusions using pattern matching
source.exclude_patterns = license,images/*/*.jpg,.gitignore,README.md,.gcloudignore,cloudbuild.yaml

# (str) Application requirements
requirements = python3==3.11,\
    kivy==2.3.0,\
    kivymd==1.1.1,\
    pillow,\
    numpy

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# Android specific
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True
android.arch = armeabi-v7a

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) The Android app theme, default is ok for Kivy-based app
android.apptheme = @android:style/Theme.NoTitleBar

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) Android additional adb arguments
android.adb_args = -H host.docker.internal

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin