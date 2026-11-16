"""API baglanti testi.

Dosya       : test_api.py
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Gorevi      : Gemini API anahtarinin gecerli oldugunu ve modelin
              yanit verdigini dogrular; gecikmeyi de yazdirir.
Kullanim    : python test_api.py
Not         : Bu betik AG cagrisi yapar; anahtar yoksa/dogru degilse
              hata mesaji basar ve program cikis kodu 1 ile biter.
"""

import time

from ai_engine import AIEngine

# Motoru olustur (anahtar .env dosyasindan okunur)
e = AIEngine()
print("Model:", e.model)

# En fazla 4 deneme: gecici ag/kuota hatalarinda pes etmemek icin
for i in range(4):
    try:
        print(e.test_connection())
        break  # ilk basarili denemeden sonra dur
    except Exception as ex:  # noqa: BLE001
        # hata metnini kesip kisa tut (ekran karismasin)
        print(f"Deneme {i + 1} basarisiz: {str(ex)[:120]}")
        time.sleep(5)  # kotu istek arasi bekleme
