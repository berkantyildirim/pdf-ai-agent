"""AI motoru - Google Gemini ile PDF ozetleme ve soru-cevap."""

import time

from google import genai
from google.genai import types

from config import DEFAULT_MODEL, MAX_TEXT_CHARS, get_api_key


class AIEngine:
    """Gemini tabanli AI motoru."""

    def __init__(self, model: str = DEFAULT_MODEL):
        self.api_key = get_api_key()
        self.model = model
        self._client = None

    @property
    def is_ready(self) -> bool:
        return bool(self.api_key)

    @property
    def client(self):
        if self._client is None:
            if not self.api_key:
                raise RuntimeError(
                    "API anahtari bulunamadi. Lutfen .env dosyasina "
                    "GEMINI_API_KEY degerini ekleyin."
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def ask(
        self,
        prompt: str,
        context: str = "",
        system_instruction: str = "",
        max_output_tokens: int = 8192,
        temperature: float = 0.3,
    ) -> str:
        """Modeli cagirir ve yaniti dondurur."""
        contents = []
        if context:
            contents.append(
                types.Part.from_text(
                    text=f"Kaynak metin (PDF):\n\n{context[:MAX_TEXT_CHARS]}"
                )
            )
        contents.append(types.Part.from_text(text=prompt))

        config_kwargs = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        return (response.text or "").strip()

    def summarize(
        self,
        context: str,
        detail: str = "orta",
        language: str = "Turkce",
    ) -> str:
        """PDF metnini ozetler.

        detail: 'kisa', 'orta', 'uzun'
        """
        levels = {
            "kisa": "Kisa bir ozet yaz (yaklasik 150-250 kelime).",
            "orta": "Dengeli bir ozet yaz (yaklasik 400-700 kelime).",
            "uzun": (
                "Ayrintili bir ozet yaz (yaklasik 1000-1500 kelime). "
                "Ana bulgulari, yontemleri ve sonuclari ayri basliklarla acikla."
            ),
        }
        instruction = levels.get(detail, levels["orta"])

        prompt = (
            f"Asagidaki kaynak metni {language} olarak ozetle. {instruction}\n\n"
            "Cikti bicimi:\n"
            "1) **Baslik** (calismanin adi/konusu)\n"
            "2) **Ozet**\n"
            "3) **Anahtar Kelimeler**\n"
            "4) **One Cikan Noktalar** (madde isaretleriyle)\n"
            "5) **Sonuc ve Onemi**"
        )

        system = (
            "Sen akademik literatur taramasi yapan bir arastirma asistanisin. "
            "Ciktilari net, duzenli ve {lang} yaz. Metin disina cikma, "
            "sadece verilen kaynaga dayan.".format(lang=language)
        )

        return self.ask(prompt=prompt, context=context, system_instruction=system)

    def question(self, context: str, question: str, language: str = "Turkce") -> str:
        """PDF metnine dayali soru-cevap yapar."""
        prompt = (
            f"Soru: {question}\n\n"
            f"Yukaridaki kaynak metni esas alarak soruyu {language} yanitla. "
            "Eger yanit metinde yoksa 'Bu bilgi metinde bulunmuyor' de. "
            "Mumkunse sayfa numaralarina atif yap."
        )
        system = (
            "Sen dikkatli bir arastirma asistanisin. Yalnizca verilen "
            "kaynak metne dayanarak yanit verirsin."
        )
        return self.ask(prompt=prompt, context=context, system_instruction=system)

    def keywords(self, context: str, language: str = "Turkce") -> str:
        """Anahtar kelime ve konu analizi uretir."""
        prompt = (
            f"Asagidaki metin icin {language} su analizleri uret:\n"
            "1) Ana konu ve alt konular\n"
            "2) Anahtar kelimeler (10-15 adet)\n"
            "3) Kullanicilan yontemler\n"
            "4) Bu metin hangi tur arastirma icin faydali olabilir?\n"
            "5) Literatur taramasinda karsilastirilabilecek benzer alanlar"
        )
        system = "Sen metodoloji uzmani bir arastirma asistanisin."
        return self.ask(prompt=prompt, context=context, system_instruction=system)

    def test_connection(self) -> str:
        """API baglantisini test eder."""
        start = time.time()
        reply = self.ask(prompt="Sadece 'OK' yaz.", max_output_tokens=16)
        elapsed = time.time() - start
        return f"Baglanti basarili ({elapsed:.1f}s): {reply[:50]}"
