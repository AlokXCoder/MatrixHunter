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

# Source
source.dir   = .
source.include_exts = py,png,jpg,kv,atlas,json,wav,ogg,ttf

# Python version
osx.python_version = 3

# Requirements (pygame-ce + numpy for procedural audio)
requirements = python3,pygame-ce,numpy

# Screen / orientation
orientation  = landscape
fullscreen   = 1

# Android specifics
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api         = 33
android.minapi      = 24
android.archs       = arm64-v8a, armeabi-v7a

# NDK / SDK
android.ndk         = 25b
android.sdk         = 33

# Build
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
