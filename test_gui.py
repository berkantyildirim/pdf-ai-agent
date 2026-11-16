"""GUI test scripti - arayuzun hatasiz acildigini dogrular.

Dosya       : test_gui.py
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Gorevi      : App nesnesini mainloop'a girmeden olusturur; pencere
              basligi, olcusu ve busy durumunu yazdirarak arayuz
              kurulumunun (widget baglantilarinin) hata vermedigini
              kontrol eder.
Kullanim    : python test_gui.py
Not         : mainloop() CALISTIRILMAZ; aksi halde betik kilitlenir.
"""
import sys
import os

# Add the project directory to path
project_dir = r"C:\Users\pc\Documents\Varsayılan Proje\pdf-ai-agent"
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Calisma klasorunu de projeye cevir (config.py .env'i oradan okur)
os.chdir(project_dir)

# App'i dogrudan ice aktar: tkinter penceresi burada olusturulur
from main import App

try:
    app = App()
    print("OK - App created successfully")
    print(f"  Window title: {app.title()}")
    print(f"  Window geometry: {app.geometry()}")
    print(f"  Is busy: {app.busy}")
    print("OK - GUI initialization successful!")
    # We don't call mainloop() here - that would block
except Exception as e:
    print("ERROR -", type(e).__name__, ":", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)