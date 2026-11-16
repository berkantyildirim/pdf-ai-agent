"""Masaüstü simgesi (ikon) ve kisayol olusturur.

Dosya       : create_shortcut.py
Proje       : Doktor Bruce Banner (pdf-ai-agent)
Gorevi      : 1) banner.ico dosyasini kod ile cizer (hulk temali)
              2) Masauste "Doktor Bruce Banner.lnk" kisayolunu olusturur
Kullanim    : python create_shortcut.py
Bagimlilik  : Pillow (ikon cizimi), pywin32 (kisayol; yoksa elle kurulum
              talimati basar)
Cikti       : banner.ico + masaustu kisayolu
"""

import sys
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# Proje klasoru ve uretilecek dosya yollari
BASE = Path(__file__).resolve().parent
ICO_PATH = BASE / "banner.ico"
LNK_NAME = "Doktor Bruce Banner.lnk"


def make_icon_hulk_face() -> bool:
    """Hulk yuzu/karakteri temelli ikon uretir (yeşil/ mor renkler).

    256x256 RGBA olarak cizilir; kaydederken birden fazla boyut
    (16..256) ayni .ico dosyasina yazilir ki Windows her yerde
    net gorunsun.
    """
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))  # seffaf tuval
    d = ImageDraw.Draw(img)

    # 1. Koyu mor/kara arka plan
    d.rectangle([0, 0, S - 1, S - 1], fill=(30, 14, 56, 255))

    # 2. Hulk'in yeşil kozu/kep (yuvarlak)
    # Ana yuvarlak kople
    d.ellipse([40, 56, S - 40, S - 56], fill=(46, 204, 113, 255))  # Hulk yeşili

    # 3. Gorrukler ( iki kirmizi nokta)
    # Sol goruk
    d.ellipse([100 - 14, 130 - 14, 100 + 14, 130 + 14], fill=(231, 76, 60, 255))
    # Sag goruk
    d.ellipse([160 - 14, 130 - 14, 160 + 14, 130 + 14], fill=(231, 76, 60, 255))

    # 4. Buk gibi detay (vertical line)
    d.rectangle([128 - 18, 170, 128 + 18, 210], fill=(52, 73, 94, 255))

    # 5. Kirbiş/nefretli gebe (kirmizi ley similar)
    # Gebe ucu
    d.rectangle([128 - 20, 90, 128 + 20, 130], fill=(231, 76, 60, 255))
    # Gebe kenarligi
    d.ellipse([128 - 24, 90 - 4, 128 + 24, 130 + 4], outline=(231, 76, 60, 255), width=6)

    # 6. Mug neck/region
    d.rectangle([100, 130, 160, 150], fill=(52, 73, 94, 150))

    # 7. Kulak/ear details (muhtemelen yeşil cirkeller)
    d.ellipse([80, 110, 100, 120], outline=(46, 204, 113, 180), width=3)
    d.ellipse([160, 110, 180, 120], outline=(46, 204, 113, 180), width=3)

    # 8. "HULK" yazimi yerine sadece karakter temeli, text yok
    # (Ikon uzerine yazi yazilmaz, simge tekrardan temiz)

    # ICO boyutlari: 16, 24, 32, 48, 64, 128, 256
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ICO_PATH, format="ICO", sizes=sizes)
    return True


def make_default_icon() -> None:
    """Gorsel yoksa varsayilan ikon (eski basit tasarim)."""
    # Hulk ikonu uretilecek, bu fonksiyon calismaz


def create_shortcut() -> Path | None:
    """Windows .lnk kisayolu olusturur.

    Kisayol, mevcut python yorumlayicisini main.py dosyasina
    baglar; boylece "python main.py" komutunu iki tikla calistirir.

    Returns:
        olusturulan .lnk yolu, ya da pywin32 yoksa None
    """
    try:
        import win32com.client  # type: ignore
    except ImportError:
        # pywin32 kurulu degilse programi yikmaya gerek yok:
        # elle kurulum talimati basilir
        print("pywin32 kurulu degil, kisayol otomatik olusturulamadi.")
        return None

    # Masaustu OneDrive altinda da olabilir (Windows vardiya kurulumu)
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path.home() / "OneDrive" / "Desktop"
    lnk_path = desktop / LNK_NAME

    # .lnk alanlarini doldur
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(lnk_path))
    shortcut.TargetPath = sys.executable  # hangi python ile acilsin
    shortcut.Arguments = f'"{BASE / "main.py"}"'  # calistirilacak dosya
    shortcut.WorkingDirectory = str(BASE)  # .env buradan okunur
    shortcut.IconLocation = f"{ICO_PATH},0"  # banner.ico
    shortcut.Description = "Doktor Bruce Banner - PDF Literatur Tarama Asistani"
    shortcut.save()
    return lnk_path


def main():
    """Ikonu uret, sonra kisayolu olustur; eksikse elle talimat ver."""
    # 1) Hulk yuzu ile ikon uret
    print("Hulk ikonu uretiliyor...")
    if not make_icon_hulk_face():
        print("Hulk ikon uretilemedi!")
        return

    print(f"Ikon kaydedildi: {ICO_PATH}")

    # 2) Kisayol olustur
    lnk = create_shortcut()
    if lnk:
        print(f"Kisayol: {lnk}")
    else:
        # pywin32 yoksa kullaniciya adim adim elle kurulum soyle
        print(
            "\nKisayoli elle olustur:\n"
            f'  Masaustune sag tik -> Yeni -> Kisayol\n'
            f'  Hedef: "{sys.executable}" "{BASE / "main.py"}"\n'
            f'  Simge: "{ICO_PATH}"'
        )


if __name__ == "__main__":
    main()