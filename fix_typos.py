#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""fix_typos.py - main.py icindeki yazim hatalarini duzeltir.

Dosya       : fix_typos.py
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Gorevi      : Buton ve etiket metinlerindeki eksik Turkce karakterleri
              (Sec -> Seç, secilmedi -> seçilendi) duzeltir.
Durum       : TEK SEFERLIK GECMIS BAKIM BETIGI - degistirilen metinler
              artik dosyada oldugu icin yeniden calistirmak zararsizdir.
Not         : main.py dosyasini duzenler.
"""

# Türkçe karakter düzeltmesi dosyası
# main.py içindeki "Dosya Sec" ve "Dosya secilmedi" yazılarını düzeltir

with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# "Dosya Sec" buton metnini "Dosya Seç" yap
c = c.replace('text="Dosya Sec"', 'text="Dosya Seç"')

# "Dosya secilmedi" etiket metnini "Dosya seçilmedi" yap
c = c.replace('text="Dosya secilmedi"', 'text="Dosya seçilendi"')

# Düzenlenmiş dosyayı kaydet
with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Yazım hataları düzeltildi.")