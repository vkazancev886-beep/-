[app]

title = Отчёт по частотам
package.name = reportfrequencies
version = 1.0

source.dir = .
source.main = main.py

source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = *.png

orientation = portrait,landscape

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Настройки для GitHub Actions
p4a.branch = develop
android.api = 34
android.minapi = 21
android.ndk = 27d

requirements = python3,kivy==2.3.0,matplotlib,pandas,openpyxl,numpy,pillow,setuptools

android.entrypoint = org.kivy.android.PythonActivity
android.bootloader = sdl2

[buildozer]

log_level = 2
warn_on_root = 1
clean = True
build = True
