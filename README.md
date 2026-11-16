# 🧪 Doktor Bruce Banner

Literatur taraması için **PDF okuyan, özetleyen ve soru-cevap yapan** masaüstü uygulaması.

> Eski adı: PDF AI Agent

## ✨ Özellikler

- 📂 PDF dosyası seçme (tek dosya)
- 📖 Sayfa aralığı seçerek yükleme
- 📝 Kısa / Orta / Uzun özet üretme
- ❓ PDF üzerine soru-cevap (sayfa atıflı)
- 🔑 Anahtar kelime ve yöntem analizi
- 📖 PDF önizleme
- 💾 Sonuçları `.txt` olarak kaydetme

## 🛠 Kurulum

### 1. Bağımlılıklar

```bash
pip install -r requirements.txt
```

### 2. API Anahtarı

1. https://aistudio.google.com/apikey adresinden **ücretsiz** Gemini API anahtarı alın
2. `.env.example` dosyasını `.env` olarak kopyalayın
3. Anahtarı girin:

```
GEMINI_API_KEY=anahtar_buraya
```

### 3. Çalıştırma

```bash
python main.py
```

## 📁 Proje Yapısı

```
pdf-ai-agent/
├── main.py             # Masaüstü arayüzü (CustomTkinter)
├── ai_engine.py        # Gemini bağlantı ve AI komutları
├── pdf_processor.py    # PDF okuma ve metin çıkarma
├── config.py           # Ayarlar ve API anahtarı
├── create_shortcut.py  # Masaüstü ikonu + kısayol oluşturur
├── banner.ico          # Uygulama simgesi
├── requirements.txt    # Bağımlılıklar
├── .env                # API anahtarı
└── ciktilar/           # Kaydedilen sonuçlar
```

## 🖥 Masaüstü Sembolü

Masaüstünde **Doktor Bruce Banner** simgesi oluşturmak için:

```bash
python create_shortcut.py
```

Bu betik:
- `banner.ico` dosyasını üretir (görsel yoksa kod ile çizer)
- Masaüstüne **Doktor Bruce Banner.lnk** kısayolunu ekler

## 🧩 Kullanım

1. **PDF Sec** ile bir makale/kitap seçin
2. İsteğe bağlı **sayfa aralığı** girin (örn. 1-20)
3. Sol paneldeki işlemleri kullanın:
   - **Özet Üret** → Makale özeti
   - **Anahtar Kelime Analizi** → Konu, yöntem, anahtar kelimeler
   - **Soru-Cevap** sekmesi → "Yöntem bölümü ne anlatıyor?"
   - **Sonucu Kaydet** → `ciktilar/` klasörüne `.txt`

## ⚠️ Notlar

- **Taranmış (gorsel) PDF'lerde metin katmanı yoktur** — OCR gerekir, bu sürümde desteklenmiyor.
- Büyük PDF'lerde tüm metni tek seferde göndermek yerine **sayfa aralığı** kullanın.
- Ücretsiz Gemini kotası günlük olarak sınırlıdır.

## 🔌 Alternatif AI Sağlayıcıları

`ai_engine.py` içindeki `AIEngine` sınıfını değiştirerek OpenAI veya Claude'a geçilebilir.
