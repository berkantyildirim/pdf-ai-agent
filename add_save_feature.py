#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""add_save_feature.py - Ozet sonucunun otomatik kaydedilmesini ekler.

Dosya       : add_save_feature.py
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Gorevi      : main.py icindeki _summarize_worker ve _save_output
              metodlarini metin bazli arama/degistirme ile gunceller;
              boylece ozet uretildiginde sonuc otomatik .txt dosyasina
              yazilir.
Durum       : TEK SEFERLIK GECMIS BAKIM BETIGI. main.py artik bu
              ozelligi icerdigi icin yeniden calistirmak bir sey
              degistirmez ("pattern bulunamadi" mesaji basar).
Not         : Betik main.py dosyasini duzenler; calistirmeden once
              yedek almaniz önerilir.
"""

with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# _do_summarize metodunun sonuna kaydet ekle
# Önceki definisionun sonundaki }'i bul ve üzerine kaydet ekle
old_pattern = '''    def _summarize_worker(self, context: str, detail: str):
        \"\"\"Özet çalışan (arka planda).\"\"\"\n        result = self.engine.summarize(context, detail=detail)\n        self.after(0, lambda: self._append_output_box(result, self.output_box))'''

new_pattern = '''    def _summarize_worker(self, context: str, detail: str):
        \"\"\"Özet çalışan (arka planda).\"\"\"\n        result = self.engine.summarize(context, detail=detail)\n        self.after(0, lambda: self._append_output_box(result, self.output_box))\n        # Özeti kaydet\n        self._save_output_internal(result)'''

# --- 1. Adim: ozet calisani sonuna kaydet komutu ekle ---
if old_pattern in c:
    c = c.replace(old_pattern, new_pattern)
    with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('Özet kaydet özelliği eklendi')
else:
    print('Önpattern bulunamadı, dosya yapısı değişmiş olabilir')
    # Alternatif: sadece butona tıklandığında kaydet ekle
    print('Dosya içeriği kontrol ediliyor...')
    
# Ayrıca _save_output metodunu de değiştirelim - kullanıcıya soru sorarak kaydet veya otomatik kaydet
# Kullanıcının seçimine göre: butona tıklandığında otomatik kaydet
save_button_code = '''    def _save_output(self):
        \"\"\"Sonucu kaydet.\"\"\"\n        # Hangi sekmede focus olduguna bagli\n        source = self.output_box if self.tabs.get() == \"📄 Sonuç\" else self.qa_output\n        text = source.get(\"1.0\", \"end\").strip()\n        if not text:\n            messagebox.showwarning(\"Uyarı\", \"Kaydedilecek metin yok.\")\n            return\n\n        # Dosya adi\n        stamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n        base = (self.doc.name if self.doc else \"bilgi\").replace(\".pdf\", \"\")\n        out_path = OUTPUT_DIR / f\"{base}_{stamp}.txt\"\n        out_path.parent.mkdir(parents=True, exist_ok=True)\n        out_path.write_text(text, encoding=\"utf-8\")\n        messagebox.showinfo(\"Kaydedildi\", f\"Sonuç kaydedildi:\\n{out_path}\")'''

# --- 2. Adim: _save_output metodunu bul ve guncelle ---
if 'def _save_output(self):' in c:
    # Mevcut _save_output'u bul: baslangicindan siradaki bolum ayiricisina kadar
    start = c.find('def _save_output(self):')
    end = c.find('\\n\\n# ----------', start)
    if end == -1:
        end = c.find('\\n\\n# ---------- Uygulama', start)
    if end == -1:
        end = len(c)
    
    # Mevcut metodun yerine yeni versiyonu koy
    current_method = c[start:end]
    new_method = '''    def _save_output(self):
        \"\"\"Sonucu kaydet.\"\"\"\n        # Butona tıklandığında otomatik kaydet\n        source = self.output_box if self.tabs.get() == \"📄 Sonuç\" else self.qa_output\n        text = source.get(\"1.0\", \"end\").strip()\n        if not text:\n            return  # Kaydetmeyi iptal\n\n        # Dosya adi\n        stamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n        base = (self.doc.name if self.doc else \"bilgi\").replace(\".pdf\", \"\")\n        out_path = OUTPUT_DIR / f\"{base}_{stamp}.txt\"\n        out_path.parent.mkdir(parents=True, exist_ok=True)\n        out_path.write_text(text, encoding=\"utf-8\")'''

    # Yalnizca henuz guncellenmemis ise uygula (ikinci calistirma guvenli)
    if 'def _save_output(self):' in c and 'Butona tıklandığında otomatik kaydet' not in c:
        c = c.replace(current_method, new_method)
        with open('C:\\Users\\pc\\Documents\\Varsayılan Proje\\pdf-ai-agent\\main.py', 'w', encoding='utf-8') as f:
            f.write(c)
        print('_save_output yöntemi güncellendi')
    else:
        print('_save_output zaten güncellemeli veya farklı')
else:
    print('_save_output bulunamadı')