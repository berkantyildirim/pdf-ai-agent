"""Yapilandirma modulu - API anahtari ve genel ayarlar."""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasini yukle
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_api_key() -> str:
    """Gemini API anahtarini dondurur."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or key == "YOUR_API_KEY_HERE":
        return ""
    return key


# Varsayilan model
DEFAULT_MODEL = "gemini-3.8-flash"

# Maksimum gonderilecek metin uzunlugu (token limiti icin yaklasik)
MAX_TEXT_CHARS = 900_000

# Ozet kaydedilecek klasor
OUTPUT_DIR = BASE_DIR / "ciktilar"
OUTPUT_DIR.mkdir(exist_ok=True)
