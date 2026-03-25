[app]

title = Solar Power Calculator
package.name = solarcalculator
package.domain = org.engineerahmed

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy==2.3.1,kivymd,reportlab,pillow

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# للـ PDF
android.permissions += WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
