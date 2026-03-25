[app]

title = Solar Power Calculator
package.name = solarcalculator
package.domain = org.engineerahmed

source.dir = .
source.include_exts = py

version = 1.0

requirements = python3,kivy==2.3.1,kivymd,reportlab,pillow

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
