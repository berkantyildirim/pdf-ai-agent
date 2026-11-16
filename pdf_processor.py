"""PDF isleme modulu - metin cikarma ve sayfa yonetimi.

Dosya       : pdf_processor.py
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Gorevi      : PDF dosyasini acar, sayfa sayfa metni cikarir ve
              kullaniciyi ilgilendiren sayfa araligini metin olarak dondurur.
Kullanan     : main.py  ->  load_pdf(), get_text(), get_preview()
Bagimlilik  : pymupdf (fitz)
Not         : Bu modulde AI cagrisi YOKTUR; saf dosya okuma/isleme yapar.
              Taranmis (gorsel) PDF'lerde metin katmani bos doner.
"""

from dataclasses import dataclass, field
from pathlib import Path

import pymupdf as fitz  # PyMuPDF - PDF okuma motoru


@dataclass
class PDFDocument:
    """Bir PDF dosyasinin temsili.

    Tum sayfa metinleri tek seferde bellekte tutulur; boylece sonraki
    arama/ozet islemleri dosyayi tekrar acmak zorunda kalmaz.
    """

    path: str
    page_count: int = 0
    title: str = ""  # PDF metadata icindeki baslik (yoksa bos kalir)
    pages: list = field(default_factory=list)  # [{page: int, text: str}, ...]

    @property
    def name(self) -> str:
        """Yolun tamami yerine yalnizca dosya adini dondurur."""
        return Path(self.path).name


def load_pdf(path: str) -> PDFDocument:
    """PDF dosyasini acar ve sayfa metinlerini cikarir.

    Raises:
        FileNotFoundError: dosya yoksa
        ValueError: uzantisi .pdf degilse
    """
    # --- Girdi dogrulama ---
    if not Path(path).exists():
        raise FileNotFoundError(f"Dosya bulunamadi: {path}")

    if not path.lower().endswith(".pdf"):
        raise ValueError("Yalnizca PDF dosyalari desteklenir.")

    # --- Metin cikarma ---
    doc = fitz.open(path)
    try:
        # metadata'da baslik yoksa bos string (None degil)
        metadata_title = (doc.metadata or {}).get("title", "") or ""
        page_count = doc.page_count

        # Her sayfayi ayri ayri oku; "[Sayfa n]" etiketini sonradan ekleriz
        pages = []
        for i in range(page_count):
            page = doc[i]
            # get_text("text") yalnizca metin katmanini verir (OCR degil)
            text = page.get_text("text") or ""
            pages.append({"page": i + 1, "text": text})

        return PDFDocument(
            path=path,
            page_count=page_count,
            title=metadata_title.strip(),
            pages=pages,
        )
    finally:
        # Hata olsa bile dosya tanaci her zaman kapatilir
        doc.close()


def get_text(doc: PDFDocument, start_page: int = 1, end_page: int | None = None) -> tuple[str, int]:
    """Belirli sayfa araliginin metnini dondurur.

    Args:
        start_page: ilk sayfa (1 tabanli)
        end_page: son sayfa; None ise dosyanin sonu

    Returns:
        (metin, karsilasilan_karakter_sayisi)
    """
    # --- Sinirlari guvenli hale getir ---
    if end_page is None or end_page > doc.page_count:
        end_page = doc.page_count

    start_page = max(1, start_page)
    if start_page > end_page:
        raise ValueError("Baslangic sayfasi bitis sayfasindan buyuk olamaz.")

    # --- Secili araligi topla ---
    chunks = []
    for entry in doc.pages[start_page - 1 : end_page]:
        text = entry["text"].strip()
        # bos sayfalari (tarama artefakti vb.) atla ki token harcanmasin
        if text:
            chunks.append(f"[Sayfa {entry['page']}]\n{text}")

    joined = "\n\n".join(chunks)
    # ikinci deger: karakter sayisi (yetersiz metin uyarisi icin kullanilir)
    return joined, len(joined)


def get_preview(doc: PDFDocument, max_chars: int = 3000) -> str:
    """PDF'in kisa bir onizlemesini dondurur.

    En fazla ilk 3 sayfayi okur, uzunsa keser: amac kullaniciya
    "dosya dogru mu" kontrolu sunmak, tam metin degil.
    """
    text, _ = get_text(doc, 1, min(3, doc.page_count))
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n... [onizleme kesildi]"
    return text
