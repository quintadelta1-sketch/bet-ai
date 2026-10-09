[app]

title = BET-AI
package.name = betai
package.domain = org.betai

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = False

[buildozer]

log_level = 2
warn_on_root = 1
