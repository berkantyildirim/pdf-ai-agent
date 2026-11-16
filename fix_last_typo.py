#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""fix_last_typo.py - kalan son yazim hatasini duzeltir.

Dosya       : fix_last_typo.py
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Gorevi      : fix_typos.py sonucunda olusan "Dosya seçilendi"
              ifadesini dogrusu olan "Dosya Seçilmedi" ile degistirir.
Durum       : TEK SEFERLIK GECMIS BAKIM BETIGI - artik dosyada bu
              metin bulunmadigindan yeniden calistirmak zararsizdir.
Not         : main.py dosyasini duzenler.
"""

# Dosya select etiketini düzeltme

with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# "Dosya seçilendi"ı "Dosya Seçilmedi" yap
new_c = c.replace('text="Dosya seçilendi"', 'text="Dosya Seçilmedi"')

with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'w', encoding='utf-8') as f:
    f.write(new_c)

print("Son yazım hatası düzeltilindi: Dosya Seçilmedi")