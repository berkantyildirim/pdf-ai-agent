"""API baglanti testi."""

import time

from ai_engine import AIEngine

e = AIEngine()
print("Model:", e.model)

for i in range(4):
    try:
        print(e.test_connection())
        break
    except Exception as ex:  # noqa: BLE001
        print(f"Deneme {i + 1} basarisiz: {str(ex)[:120]}")
        time.sleep(5)
