#!/usr/bin/env python
# Dosya select etiketini düzeltme

with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# "Dosya seçilendi"ı "Dosya Seçilmedi" yap
new_c = c.replace('text="Dosya seçilendi"', 'text="Dosya Seçilmedi"')

with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'w', encoding='utf-8') as f:
    f.write(new_c)

print("Son yazım hatası düzeltilindi: Dosya Seçilmedi")