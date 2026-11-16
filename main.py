"""Doktor Bruce Banner - Literatur Tarama Asistani.

Literatur taraması için PDF okuyan, ozetleyen ve soru-cevap yapan
modern masaüstü uygulaması (Doctor Bruce Banner).

Dosya       : main.py  (projenin giris noktasi ve GUI sinifi)
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Yazar       : imamaslan46
Kurulum:
--------
1. Gerekli kutuphaneler: pip install -r requirements.txt
2. Gemini API anahtari: .env dosyasina GEMINI_API_KEY ekle
3. Baslat: python main.py

Fonksiyonellik:
--------------
- PDF dosyasi secme ve metin cikarma
- Kisa/Orta/Uzun ozet uretme
- PDF uzerine soru-cevap (sayfa atili)
- Anahtar kelime ve yontem analizi
- PDF onizleme ve sayfa araligi secimi
- Ozetin otomatik kaydedilmesi
- Sonuclari kaydetme ve masaustu kisayolu

Dosya Yapisi (sinif ici bolum sirasi):
--------------------------------------
  1. Tema ve stil ayarlari     : renk/konstant tanimlari
  2. App.__init__              : pencere + durum degiskenleri
  3. _build_*                  : arayuz kurulumu (sol/sag panel, durum cubugu)
  4. Islem akisi               : _check_api_key, _set_status, _run_task
  5. Dosya islemi              : _choose_file, _load_range, onizleme
  6. Islem fonksiyonlari       : ozet / anahtar kelime / soru-cevap
  7. Yardimci fonksiyonlar     : _get_context, _append_output_box
  8. Kaydetme                  : _save_output (ciktilar/*.txt)

Teknik Not:
----------
Tum AI cagrilari _run_task() icinde AYRI THREAD'de calisir; arayuz
kilitlenmesin diye sonuc main thread'e self.after(0, ...) ile geri
gonderilir. Tkinter'da widget'lar yalnizca ana thread'de degistirilebilir.
"""

import threading
import traceback
import time
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from ai_engine import AIEngine
from config import OUTPUT_DIR, get_api_key
from pdf_processor import PDFDocument, get_text, get_preview, load_pdf

# ---------- Tema ve Stil Ayarlari ----------
ctk.set_appearance_mode("dark")  # "dark" | "light" | "system"
ctk.set_default_color_theme("blue")  # "blue" | "green" | "dark-blue"

FONT_BASE = ("Segoe UI", 13)
FONT_BOLD = ("Segoe UI", 15, "bold")
FONT_SMALL = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEADING = ("Segoe UI", 14, "bold")

# Hulk renk paleti (anasayfada vurgulama icin)
COLOR_BG = "#1e1e2f"  # Ana arka plan
COLOR_CARD = "#2c2c3e"  # Kart/frame arka planı
COLOR_ACCENT = "#4ade80"  # Yeşil vuruş (Hulk temalı)
COLOR_ACCENT_HOVER = "#22c55e"
COLOR_WARNING = "#f87171"  # Uyarı/kirmizi
COLOR_INFO = "#60a5fa"  # Bilgi mavidi
COLOR_SUBTLE = "#3f3f4f" # Alt detaylar
COLOR_TEXT = "#f1f5f9" # Ana metin
COLOR_MUTED = "#9ca3af" # Yumuşak/gri

ctk.set_default_color_theme("blue")  # Temanın üzerine eklenecek accent


# ---------- Ana Uygulama Sınıfi ----------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere ayarlari
        self.title("Doktor Bruce Banner - AI Literatur Tarama")
        self.geometry("1200x800")
        self.minsize(960, 640)

        # Durum takibi
        self.doc: PDFDocument | None = None
        self.engine = AIEngine()
        self.busy = False
        self.history: list[dict] = []  # Onceki sorular/cevaplar

        # UI'yi build et
        self._build_ui()

        # API kontrolü
        self._check_api_key()

    # ---------- Arayüz Kurulumu ----------
    def _build_ui(self):
        # --- Ana frame ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sol panel (kontroller) ---
        self.left_panel = ctk.CTkFrame(self, width=320, corner_radius=12, fg_color=COLOR_CARD)
        self.left_panel.grid(row=0, column=0, sticky="ns", padx=(12, 8), pady=12)
        self.left_panel.grid_rowconfigure(0, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)

        # --- Sag panel (çikti) ---
        self.right_panel = ctk.CTkFrame(self, corner_radius=12, fg_color=COLOR_BG)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        # --- Sol panel iceriği ---
        self._build_left_panel()

        # --- Sag panel iceriği ---
        self._build_right_panel()

        # --- Alt durum çubuğu ---
        self._build_status_bar()

    def _build_left_panel(self):
        """Sol panel: Dosya secimi, ayarlar, islemler."""
        # Başlik
        ctk.CTkLabel(
            self.left_panel,
            text="Doktor Bruce Banner",
            font=FONT_TITLE,
            text_color=COLOR_ACCENT,
        ).pack(anchor="w", padx=20, pady=(20, 8))

        # Dosya secme
        ctk.CTkLabel(
            self.left_panel,
            text="📄 PDF Dosyası",
            font=FONT_BOLD,
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # Dosya baslik
        self.file_label = ctk.CTkLabel(
            self.left_panel,
            text="Dosya seçilmedi",
            font=FONT_SMALL,
            text_color=COLOR_MUTED,
            anchor="w",
            justify="left",
        )
        self.file_label.pack(anchor="w", padx=16, pady=(0, 8))

        # Dosya yolu (gizli)
        self._file_path_var = ctk.StringVar(value="")
        self._file_btn = ctk.CTkButton(
            self.left_panel,
            text="Dosya Seç",
            command=self._choose_file,
            height=38,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
        )
        self._file_btn.pack(anchor="w", padx=16, pady=4)

        # Sayfa araligi
        ctk.CTkLabel(
            self.left_panel,
            text="📑 Sayfa Aralığı (İsteğe Bağlı)",
            font=FONT_BOLD,
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=16, pady=(16, 4))

        # Aralik entries
        self.page_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.page_frame.pack(anchor="w", padx=16, pady=4)

        self.page_from = ctk.CTkEntry(
            self.page_frame, placeholder_text="Başlangıç", width=80
        )
        self.page_from.pack(side="left", padx=(0, 6))
        ctk.CTkLabel(self.page_frame, text="-", font=FONT_BASE).pack(side="left")
        self.page_to = ctk.CTkEntry(
            self.page_frame, placeholder_text="Bitiş", width=80
        )
        self.page_to.pack(side="left", padx=(6, 0))

        # Yukle araligi butonu
        ctk.CTkButton(
            self.left_panel,
            text="Aralıgi Yükle",
            command=self._load_range,
            height=32,
            fg_color="#2b7a4b",
            hover_color="#245f3d",
        ).pack(anchor="w", padx=16, pady=(6, 12))

        # Ozet detayi
        ctk.CTkLabel(
            self.left_panel,
            text="📝 Özet Detayı",
            font=FONT_BOLD,
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=16, pady=(0, 4))

        self.detail_var = ctk.StringVar(value="orta")
        for val, label in (("kisa", "Kısa"), ("orta", "Orta"), ("uzun", "Uzun")):
            ctk.CTkRadioButton(
                self.left_panel,
                text=label,
                variable=self.detail_var,
                value=val,
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_ACCENT_HOVER,
            ).pack(anchor="w", padx=20, pady=1)

        # Hizli islemler
        ctk.CTkLabel(
            self.left_panel,
            text="⚡ Hızlı İşlemler",
            font=FONT_BOLD,
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        # Butonlar
        btn_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=3)

        self.btn_summarize = ctk.CTkButton(
            btn_frame,
            text="📝 Özet Üret",
            command=lambda: self._run_task(self._do_summarize),
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_ACCENT,
            text_color=COLOR_ACCENT,
        )
        self.btn_summarize.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_keywords = ctk.CTkButton(
            btn_frame,
            text="🔑 Anahtar Kelime",
            command=lambda: self._run_task(self._do_keywords),
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_INFO,
            text_color=COLOR_INFO,
        )
        self.btn_keywords.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Soru-cevap sekmesi gecis butonu
        ctk.CTkButton(
            self.left_panel,
            text="❓ Soru-Cevap",
            command=self._toggle_qa_view,
            height=32,
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_SUBTLE,
            text_color=COLOR_SUBTLE,
        ).pack(anchor="w", padx=16, pady=(10, 4))

        # Kaydet butonu - otomatik kaydetmeyi destekler
        ctk.CTkButton(
            self.left_panel,
            text="💾 Sonuç Kaydet",
            command=self._save_output,
            height=36,
            fg_color="#8a6d1f",
            hover_color="#6f5718",
        ).pack(anchor="w", padx=16, pady=4)

        # Bilgi etiketi
        self.info_label = ctk.CTkLabel(
            self.left_panel,
            text="",
            font=FONT_SMALL,
            text_color=COLOR_MUTED,
            anchor="w",
            justify="left",
        )
        self.info_label.pack(anchor="w", padx=16, pady=(8, 0))

    def _build_right_panel(self):
        """Sag panel: Sekmelerle output display."""
        # Sekmeler (tabview)
        self.tabs = ctk.CTkTabview(self.right_panel, corner_radius=10)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)

        # Sekmeler ekle
        self.tabs.add("📄 Sonuç")
        self.tabs.add("❓ Soru-Cevap")
        self.tabs.add("📖 PDF Önizleme")

        # --- Sekme 1: Sonuc ---
        self.output_box = ctk.CTkTextbox(
            self.tabs.tab("📄 Sonuç"),
            font=FONT_BASE,
            wrap="word",
            state="disabled",
        )
        self.output_box.pack(fill="both", expand=True, padx=8, pady=8)

        # --- Sekme 2: Soru-Cevap ---
        qa = self.tabs.tab("❓ Soru-Cevap")

        # Soru girişi
        self.question_entry = ctk.CTkEntry(
            qa,
            placeholder_text="PDF ile ilgili bir soru yazın... (Enter'a basin)",
            height=42,
            font=FONT_BASE,
        )
        self.question_entry.pack(fill="x", padx=12, pady=(12, 6))
        self.question_entry.bind("<Return>", lambda e: self._run_task(self._do_ask))

        # Soru butonu
        ctk.CTkButton(
            qa,
            text="Soruyu Yanıtla",
            command=lambda: self._run_task(self._do_ask),
            height=34,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
        ).pack(anchor="e", padx=12, pady=(0, 12))

        # Cikti alani
        self.qa_output = ctk.CTkTextbox(
            qa,
            font=FONT_BASE,
            wrap="word",
            state="disabled",
        )
        self.qa_output.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # --- Sekme 3: PDF Onizleme ---
        self.preview_box = ctk.CTkTextbox(
            self.tabs.tab("📖 PDF Önizleme"),
            font=FONT_BASE,
            wrap="word",
            state="disabled",
        )
        self.preview_box.pack(fill="both", expand=True, padx=12, pady=12)

    def _build_status_bar(self):
        """Alt durum çubuğu."""
        self.status_bar = ctk.CTkFrame(self, corner_radius=0, height=32)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
        self.status_bar.grid_columnconfigure(1, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_bar, text="Hazır", font=FONT_SMALL, anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        # Belirsiz modda donen ilerleme cubugu (calisirken hareket eder)
        self.progress_bar = ctk.CTkProgressBar(
            self.status_bar, width=150, mode="indeterminate"
        )
        self.progress_bar.grid(row=0, column=1, padx=(0, 8))
        self.progress_bar.set(0)

        # Zaman damgasi
        self.time_label = ctk.CTkLabel(
            self.status_bar, text="", font=FONT_SMALL, anchor="e"
        )
        self.time_label.grid(row=0, column=2, sticky="e", padx=(0, 0))

        # Zamanı güncelle (ilk cagri burada yapilir)
        self._update_time()

    def _update_time(self):
        """Saat'i güncelle.

        Her saniye kendini yeniden planlayarak durum cubugundaki
        saati tazeler (after() bloklayici degildir).
        """
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=now)
        self.after(1000, self._update_time)

    # ---------- Islem Akisi ----------
    def _check_api_key(self):
        """API anahtari kontrol ve baslat."""
        if get_api_key():
            self.status_label.configure(text="✅ API Hazır", text_color=COLOR_ACCENT)
        else:
            self.status_label.configure(
                text="⚠️ API Anahtarı Gerekli", text_color=COLOR_WARNING
            )
            # uyarı kutusu
            messagebox.showinfo(
                "API Anahtarı Gerekli",
                "Gemini API anahtarınızı ekleyin.\n\n"
                "1) https://aistudio.google.com/apikey adresinden ücretsiz alın\n"
                "2) Bu klasördeki .env dosyasına:\n"
                "   GEMINI_API_KEY=anahtar_buraya",
            )

    def _set_status(self, text: str, busy: bool = False):
        """Durum çubuğunu guncelle.

        busy=True iken yaziyi kirmiziya cevirir ve ilerleme cubugunu
        baslatir; is bitince normale doner. busy ayni zamanda yeni
        islem baslatmayi engelleyen kilit olarak kullanilir.
        """
        self.status_label.configure(text=text, text_color=COLOR_ACCENT if not busy else COLOR_WARNING)
        if busy:
            self.progress_bar.start(12)  # 12ms adimla don
        else:
            self.progress_bar.stop()
            self.progress_bar.set(0)
        self.busy = busy
        self.update_idletasks()  # degisiklik aninda ekrana yansisin

    def _run_task(self, func):
        """Gorevi arka planda calistir (thread).

        GUI donmasin diye AI cagrisi ayri thread'de yapilir;
        sonuclar self.after(0, ...) ile ana thread'e tasinir.
        """
        if self.busy:
            messagebox.showwarning("Bekleyin", "Bir islem zaten devam ediyor.")
            return
        if not self.engine.is_ready:
            messagebox.showerror("Hata", "API anahtarı bulunamadı.")
            return

        self.busy = True
        self._set_status("Çalışıyor...", busy=True)
        self.progress_bar.start(12)

        def worker():
            """Thread govdesi: hatalari yakalar, durumu geri bildirir."""
            try:
                func()
                # Basarili sonucta history kaydet
                self.after(
                    0,
                    lambda: self._set_status("Tamamlandı", busy=False),
                )
            except Exception as exc:  # noqa: BLE001
                traceback.print_exc()
                self.after(
                    0,
                    lambda: messagebox.showerror("Hata", str(exc)),
                )
                self.after(0, lambda: self._set_status("Hata", busy=False))
            finally:
                # Kilidi her durumda birak ki uygulama kilitlenmesin
                self.after(0, lambda: self.progress_bar.stop())
                self.after(0, lambda: self.progress_bar.set(0))
                self.busy = False

        # daemon=True: pencere kapaninca thread zorla bitsin
        threading.Thread(target=worker, daemon=True).start()

    # ---------- Dosya Islemi ----------
    def _choose_file(self):
        """PDF dosyasi sec."""
        path = filedialog.askopenfilename(
            title="PDF Sec",
            filetypes=[("PDF Dosyalari", "*.pdf"), ("Tümü", "*.*")],
        )
        if not path:
            return

        try:
            self._set_status("PDF yukleniyor...")
            self.doc = load_pdf(path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Hata", str(exc))
            return

        # Bilgileri guncelle
        name = self.doc.title or self.doc.name
        self.file_label.configure(text=name, text_color=COLOR_TEXT)
        size_mb = Path(path).stat().st_size / 1_048_576
        self.info_label.configure(
            text=f"Sayfa sayısı: {self.doc.page_count}\nBoyut: {size_mb:.1f} MB"
        )

        # Sayfa entries doldur
        self.page_from.delete(0, "end")
        self.page_to.delete(0, "end")
        self.page_to.insert(0, str(self.doc.page_count))

        # Onizlemeyi guncelle
        self._update_preview()

        # Output'lari temizle
        self._clear_output()
        self._set_status(f"Yüklendi: {self.doc.name}")

    def _load_range(self):
        """Secilen sayfa araligini yukle."""
        if self.doc is None:
            messagebox.showwarning("Uyarı", "Önce PDF secin.")
            return
        try:
            # Kullanicinin girisinden sayfa numaralarini al
            raw_from = self.page_from.get().strip()
            raw_to = self.page_to.get().strip()
            start = int(raw_from) if raw_from else 1
            end = int(raw_to) if raw_to else self.doc.page_count
            start = max(1, start)
            end = min(self.doc.page_count, end)
            if start > end:
                messagebox.showerror("Hata", "Başlangıç sayfası bitisden büyük.")
                return

            text, nchars = get_text(self.doc, start, end)
            if nchars < 50:
                messagebox.showwarning(
                    "Uyarı",
                    "Seçili aralıkta yeterli metin bulunamadı. "
                    "PDF taranmış (görsel) olabilir.",
                )
                return

            # Onizlemeyi guncelle
            preview = (
                f"[Sayfa {start}-{end}] ({nchars:,} karakter)\n\n"
                + (text[:2000] + "\n\n... [kesildi]" if len(text) > 2000 else text)
            )
            self._update_preview_box(preview)
            self._set_status(f"Aralık yüklendi: {start}-{end} ({nchars:,} karakter)")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Hata", str(exc))

    def _update_preview(self):
        """PDF onizleme başlığını güncelle."""
        if self.doc is None:
            return
        preview = get_preview(self.doc, max_chars=2000)
        self._update_preview_box(preview)

    def _update_preview_box(self, text: str):
        """Onizleme metnini update et."""
        self.preview_box.configure(state="normal")
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("1.0", text)
        self.preview_box.configure(state="disabled")

    def _toggle_qa_view(self):
        """Soru-cevap sekmesinin aktif/pasif olmasını toggle eder.

        Sol paneldeki buton tek tikla "Sonuç" ve "Soru-Cevap"
        sekmeleri arasinda gecis yapar.
        """
        # Tabview current index'i değiştir
        current = self.tabs.get()
        if current == "❓ Soru-Cevap":
            self.tabs.set("📄 Sonuç")
        else:
            self.tabs.set("❓ Soru-Cevap")
        # Soru giriş alanını temizle
        self.question_entry.delete(0, "end")

    def _clear_output(self):
        """Output'lari temizle.

        Yeni PDF acildiginda onceki belgenin sonuclari karismasin
        diye tum kutular ve soru alani sifirlanir.
        """
        self._append_output_box("", self.output_box)
        self._append_output_box("", self.qa_output)
        self.question_entry.delete(0, "end")

    # ---------- Islem Fonksiyonlari ----------
    def _do_summarize(self):
        """Özetiüretil ve kaydet.

        Once guncel sayfa araliginin metnini alir, sonra
        _summarize_worker'i arka planda calistirir.
        """
        context = self._get_context()
        if not context:
            return  # metin yoksa sessizce dur (uyariyi _get_context verdi)
        detail = self.detail_var.get()  # kisa / orta / uzun
        self._run_task(lambda: self._summarize_worker(context, detail))

    def _summarize_worker(self, context: str, detail: str):
        """Özet çalışan (arka planda)."""
        result = self.engine.summarize(context, detail=detail)
        # sonucu ana thread'e tas (Tkinter kurali)
        self.after(0, lambda: self._append_output_box(result, self.output_box))
        # Özeti otomatik kaydet
        self._save_output_internal(result)

    def _save_output_internal(self, text: str):
        """İçeriği otomatik kaydet.

        Kullaniciya sormadan ciktilar/ klasorune yazar;
        dosya adi: <pdf_adi>_<yilaygun>_saat.txt
        """
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = (self.doc.name if self.doc else "bilgi").replace(".pdf", "")
        out_path = OUTPUT_DIR / f"{base}_{stamp}.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        # Kullanıcıya bilgi ver (gerekirse)
        # messagebox.showinfo("Kaydedildi", f"Özet kaydedildi:\\n{out_path}")

    def _do_keywords(self):
        """Anahtar kelime analiz."""
        context = self._get_context()
        if not context:
            return
        self._run_task(lambda: self._keywords_worker(context))

    def _keywords_worker(self, context: str):
        """Anahtar kelime worker (arka planda)."""
        result = self.engine.keywords(context)
        self.after(0, lambda: self._append_output_box(result, self.output_box))

    def _do_ask(self):
        """Soru-cevap."""
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("Uyarı", "Sorunuzu yazın.")
            return
        context = self._get_context()
        if not context:
            return
        self._run_task(lambda: self._ask_worker(context, question))

    def _ask_worker(self, context: str, question: str):
        """Soruyu cevapla (arka planda)."""
        answer = self.engine.question(context, question)
        # History'e ekle
        self.history.append({"q": question, "a": answer})
        self.after(
            0, lambda: self._append_output_box(answer, self.qa_output)
        )
        # Soru girdisini temizle
        self.after(0, lambda: self.question_entry.delete(0, "end"))

    # ---------- Yardimci Fonksiyonlar ----------
    def _get_context(self) -> str:
        """Aktif metin aralığını dondur.

        Kullanicinin girdigi sayfa araligini guvenli bicime cevirir
        (sinirlar sicrar, ters giris olursa takas eder) ve o araligin
        metnini AI'a gonderilmek uzere dondurur.
        Metin cok kisaysa bos doner; boylece bos yere istek atilmaz.
        """
        if self.doc is None:
            messagebox.showwarning("Uyarı", "Önce bir PDF dosyası secin.")
            return ""
        try:
            # --- Sayfa araligini oku ve temizle ---
            raw_from = self.page_from.get().strip()
            raw_to = self.page_to.get().strip()
            start = int(raw_from) if raw_from else 1
            end = int(raw_to) if raw_to else self.doc.page_count
            # sinirlari dosya uzunluguna sikistir
            start = max(1, min(start, self.doc.page_count))
            end = max(1, min(end, self.doc.page_count))
            if start > end:
                start, end = end, start  # ters girilmissa takas et

            # --- Metni al ---
            text, _ = get_text(self.doc, start, end)
            if len(text) < 50:
                # bos/taranmis PDF: istek atmadan uyar
                messagebox.showwarning(
                    "Uyarı",
                    "Seçili aralıkta metin yok. Tüm PDF mi yüklünüz?",
                )
                return ""
            return text
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Hata", str(exc))
            return ""

    def _append_output_box(self, text: str, box: ctk.CTkTextbox):
        """Output butuncesine metin ekle (thread-safe).

        Kutu normalde 'disabled' (yazilamaz) tutulur; yazmak icin
        kisa sureligine acilir, sonra tekrar kilitlenir. Boylece
        kullanici ciktinin uzerine elle yazamaz.
        """
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")
        # Kaydedilecek sonucu göster
        # (Kaydet butonu bu metni alacak)

    # ---------- Kaydetme ----------
    def _save_output(self):
        """Sonucu kaydet (manuel).

        Hangi sekme aciksa o kutunun icerigini ciktilar/ altina yazar;
        dosya adi PDF adi + zaman damgasi ile cakismayi onler.
        """
        # Hangi sekmede focus olduguna bagli
        source = self.output_box if self.tabs.get() == "📄 Sonuç" else self.qa_output
        text = source.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Uyarı", "Kaydedilecek metin yok.")
            return

        # Dosya adi
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = (self.doc.name if self.doc else "bilgi").replace(".pdf", "")
        out_path = OUTPUT_DIR / f"{base}_{stamp}.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        messagebox.showinfo("Kaydedildi", f"Sonuç kaydedildi:\\n{out_path}")


# ---------- Uygulama Başlatma ----------
if __name__ == "__main__":
    # Dogrudan calistirilmissa pencereyi ac
    # (import edilirse calismaz - test_gui.py icin bu onemli)
    App().mainloop()