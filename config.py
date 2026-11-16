"""Yapilandirma modulu - API anahtari ve genel ayarlar.

Dosya       : config.py
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Gorevi      : .env dosyasini yukler, API anahtarini saglar ve tum
              modullerce paylasilan sabitleri (model adi, limitler,
              cikti klasoru) tek yerde toplar.
Kullanan     : ai_engine.py, main.py
Bagimlilik  : python-dotenv
Gizlilik    : GERCEK API ANAHTARI YALNIZCA .env DOSYASINDADIR.
              Bu dosyaya, diger kodlara veya GitHub'a asla yazilmaz;
              repoda yalnizca .env.example (sablon) bulunur.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasini yukle (bu dosyanin bulundugu klasorden okur)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_api_key() -> str:
    """Gemini API anahtarini dondurur.

    Anahtar yoksa ya da sablon degeri (YOUR_API_KEY_HERE) kalmisa
    bos string dondurur; boylece arayuz "API Anahtari Gerekli"
    uyarisi gosterebilir.
    """
    key = os.getenv("GEMINI_API_KEY", "").strip()
    # sablon degeri gercek anahtar sayilmaz
    if not key or key == "YOUR_API_KEY_HERE":
        return ""
    return key


# Varsayilan model - ucretsiz Gemini Flash surumu
DEFAULT_MODEL = "gemini-3.8-flash"

# Maksimum gonderilecek metin uzunlugu (token limiti icin yaklasik)
# Uzun PDF'lerde bu noktadan sonrasi bilerek kesilir ki istek
# modelin token sinirini asmasin ve hata donmesin.
MAX_TEXT_CHARS = 900_000

# Ozet kaydedilecek klasor - yoksa otomatik olusturulur
OUTPUT_DIR = BASE_DIR / "ciktilar"
OUTPUT_DIR.mkdir(exist_ok=True)
