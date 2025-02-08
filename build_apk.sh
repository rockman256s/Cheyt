#!/bin/bash

# Set environment variables
export PATH=$PATH:$HOME/.local/bin
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PYTHONPATH=$PYTHONPATH:$HOME/.local/lib/python3.11/site-packages
export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk
export ANDROID_NDK_HOME=$HOME/.buildozer/android/platform/android-ndk

# Clean previous build
rm -rf .buildozer
rm -rf bin

# Install build dependencies
pip install --upgrade pip
pip install buildozer==1.5.0 Cython==0.29.36

# Run build with detailed logging
buildozer android debug -v

# Check result
if [ -f "bin/weightcalculator-1.0.0.3-arm64-v8a-debug.apk" ]; then
    echo "APK successfully built!"
    echo "APK location: bin/weightcalculator-1.0.0.3-arm64-v8a-debug.apk"
else
    echo "Build failed. Check the logs for details."
    exit 1
fi