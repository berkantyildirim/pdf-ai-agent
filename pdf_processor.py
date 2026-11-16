"""PDF isleme modulu - metin cikarma ve sayfa yonetimi."""

from dataclasses import dataclass, field
from pathlib import Path

import pymupdf as fitz  # PyMuPDF


@dataclass
class PDFDocument:
    """Bir PDF dosyasinin temsili."""

    path: str
    page_count: int = 0
    title: str = ""
    pages: list = field(default_factory=list)

    @property
    def name(self) -> str:
        return Path(self.path).name


def load_pdf(path: str) -> PDFDocument:
    """PDF dosyasini acar ve sayfa metinlerini cikarir."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Dosya bulunamadi: {path}")

    if not path.lower().endswith(".pdf"):
        raise ValueError("Yalnizca PDF dosyalari desteklenir.")

    doc = fitz.open(path)
    try:
        metadata_title = (doc.metadata or {}).get("title", "") or ""
        page_count = doc.page_count

        pages = []
        for i in range(page_count):
            page = doc[i]
            text = page.get_text("text") or ""
            pages.append({"page": i + 1, "text": text})

        return PDFDocument(
            path=path,
            page_count=page_count,
            title=metadata_title.strip(),
            pages=pages,
        )
    finally:
        doc.close()


def get_text(doc: PDFDocument, start_page: int = 1, end_page: int | None = None) -> tuple[str, int]:
    """Belirli sayfa araliginin metnini dondurur.

    Returns:
        (metin, karsilasilan_karakter_sayisi)
    """
    if end_page is None or end_page > doc.page_count:
        end_page = doc.page_count

    start_page = max(1, start_page)
    if start_page > end_page:
        raise ValueError("Baslangic sayfasi bitis sayfasindan buyuk olamaz.")

    chunks = []
    for entry in doc.pages[start_page - 1 : end_page]:
        text = entry["text"].strip()
        if text:
            chunks.append(f"[Sayfa {entry['page']}]\n{text}")

    joined = "\n\n".join(chunks)
    return joined, len(joined)


def get_preview(doc: PDFDocument, max_chars: int = 3000) -> str:
    """PDF'in kisa bir onizlemesini dondurur."""
    text, _ = get_text(doc, 1, min(3, doc.page_count))
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n... [onizleme kesildi]"
    return text
