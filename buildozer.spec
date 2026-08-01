# buildozer.spec
# ==============
# Android packaging configuration for Matrix Hunter Universe.
# Build with: buildozer android debug
# Requires: Linux / WSL with Buildozer installed.
# Install: pip install buildozer

[app]

# Application identity
title        = Matrix Hunter Universe
package.name = matrixhunteruniverse
package.domain = org.matrixhunter
version      = 1.0.0
icon.filename = %(source.dir)s/assets/images/icon.png

# Entry point
source.main = main.py

# Source
source.dir   = .
source.include_exts = py,png,jpg,kv,atlas,json,wav,ogg,ttf

# Python version
# IMPORTANT: Pin to 3.12.x — longintrepr.h was removed in Python 3.13+
# The pygame C extension (src_c/_sdl2/sdl2.c) still includes it → build fails on 3.13/3.14
osx.python_version = 3

# Requirements — both python3 AND hostpython3 must be pinned to the same version.
# hostpython3 = the Python used on the host to cross-compile C extensions
# python3     = the Python shipped inside the APK
# longintrepr.h was removed in 3.13+ → must stay on 3.12.x
requirements = hostpython3==3.12.8,python3==3.12.8,pygame

# Screen / orientation
orientation  = landscape
fullscreen   = 1

# Android specifics
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api         = 33
android.minapi      = 24
android.archs       = arm64-v8a, armeabi-v7a
# Pin build-tools to a stable version (avoids license prompt for brand-new versions)
android.build_tools_version = 34.0.0

# NDK / SDK
android.ndk = 25c

# Build
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
