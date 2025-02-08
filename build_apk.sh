#!/bin/bash

echo "Starting APK build process..."

# Проверка наличия необходимых инструментов
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python 3.11"
    exit 1
fi

# Установка зависимостей
echo "Installing dependencies..."
pip install buildozer==1.5.0 Cython==0.29.36

# Очистка предыдущей сборки
echo "Cleaning previous build..."
rm -rf .buildozer
rm -rf bin

# Проверка наличия buildozer.spec
if [ ! -f "buildozer.spec" ]; then
    echo "buildozer.spec not found. Creating default configuration..."
    buildozer init
fi

# Сборка APK
echo "Building APK..."
buildozer android debug

# Проверка результата
if [ -f "bin/weightcalculator-1.0.0.3-arm64-v8a-debug.apk" ]; then
    echo "APK built successfully!"
    echo "APK location: bin/weightcalculator-1.0.0.3-arm64-v8a-debug.apk"
else
    echo "Build failed. Check logs for details."
    exit 1
fi