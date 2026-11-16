#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""fix_save.py - main.py icindeki _save_output girinti hatasini duzeltir.

Dosya       : fix_save.py
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Gorevi      : "def _save_output" satirinin fazladan girintili
              (indent) haliyle olusan SyntaxError'i duzeltir.
Durum       : TEK SEFERLIK GECMIS BAKIM BETIGI. Sorun giderildigi
              icin yeniden calistirmak "old save not found" basar.
Not         : main.py dosyasini duzenler; yedek almaniz önerilir.
"""

with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# _save_output metodunun tam fix'i
# 617'den başlayan def _save_output satırını düzeltilmiş haliyle değiştir

old_save = """    # ---------- Kaydetme ----------\n        def _save_output(self):\n        \"\"\"Sonucu kaydet.\"\"\"\n        # Butona tıklandığında otomatik kaydet\n        source = self.output_box if self.tabs.get() == \"📄 Sonuç\" else self.qa_output\n        text = source.get(\"1.0\", \"end\").strip()\n        if not text:\n            return  # Kaydetmeyi iptal\n\n        # Dosya adi\n        stamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n        base = (self.doc.name if self.doc else \"bilgi\").replace(\".pdf\", \"\")\n        out_path = OUTPUT_DIR / f\"{base}_{stamp}.txt\"\n        out_path.parent.mkdir(parents=True, exist_ok=True)\n        out_path.write_text(text, encoding=\"utf-8\")"""

new_save = """    # ---------- Kaydetme ----------\n    def _save_output(self):\n        \"\"\"Sonucu kaydet.\"\"\"\n        # Butona tıklandığında otomatik kaydet\n        source = self.output_box if self.tabs.get() == \"📄 Sonuç\" else self.qa_output\n        text = source.get(\"1.0\", \"end\").strip()\n        if not text:\n            return  # Kaydetmeyi iptal\n\n        # Dosya adi\n        stamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n        base = (self.doc.name if self.doc else \"bilgi\").replace(\".pdf\", \"\")\n        out_path = OUTPUT_DIR / f\"{base}_{stamp}.txt\"\n        out_path.parent.mkdir(parents=True, exist_ok=True)\n        out_path.write_text(text, encoding=\"utf-8\")"""

if old_save in c:
    c = c.replace(old_save, new_save)
    with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('save method fixed')
else:
    print('old save not found, trying alternative')
    # Alternatif: sadece text kısmını fixed hale getir
    alt = '        if not text:\\n            return  # Kaydetmeyi iptal'
    if alt in c:
        print('Alt yolu buldu')
    else:
        print('Alternatif de bulamadı')
