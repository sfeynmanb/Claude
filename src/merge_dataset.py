#!/usr/bin/env python3
"""
data/raw/*.csv dosyalarını doğrular, birleştirir ve Master veri setini üretir.

Çıktılar
--------
data/processed/master_air_munitions_dataset.csv   (';' ayraçlı, UTF-8, 20 sütun)
data/processed/master_air_munitions_dataset.xlsx  (Master + Veri_Sozlugu + Kaynak_Izleme)

Ham dosyalar sıfır hatayla doğrulanmadan birleştirme yapılmaz.
"""
import glob
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema_validator as sv  # noqa: E402

ROOT = sv.ROOT
RAW = os.path.join(ROOT, "data", "raw")
OUT_DIR = os.path.join(ROOT, "data", "processed")
OUT_CSV = os.path.join(OUT_DIR, "master_air_munitions_dataset.csv")
OUT_XLSX = os.path.join(OUT_DIR, "master_air_munitions_dataset.xlsx")

NUMERIC = [c for c, k, _ in sv.SCHEMA if k in ("float_na", "int_na")]
CAT_ORDER = ["Fuze", "Dolanan_Muhimmat", "Gudumlu_Bomba", "Gudumsuz_Bomba"]

DICTIONARY = [
    ("Muhimmat_Adi", "str", "Mühimmatın resmi/yaygın adı ve varyantı"),
    ("Mensei_Ulke", "ISO 3166-1 alpha-3", "EUR = çok uluslu Avrupa konsorsiyumu"),
    ("Uretici_Firma", "str", "Ana yüklenici / geliştirici; doğrulanamazsa NA"),
    ("Ana_Kategori", "enum", "Fuze | Gudumlu_Bomba | Gudumsuz_Bomba | Dolanan_Muhimmat"),
    ("Alt_Kategori", "enum", "10 temel sınıf + ALBM, HGV, TASM, Guided_Rocket, Micro_PGM, Loitering"),
    ("Hizmete_Giris_Yili", "int | NA", "İlk operasyonel kabiliyet (IOC) yılı"),
    ("Toplam_Kutle_kg", "float | NA", "Havadan atış kütlesi (booster hariç), kg"),
    ("Harp_Basligi_Kutlesi_kg", "float | NA", "Harp başlığı kütlesi; bombalarda gövde (kasa+dolgu)"),
    ("Harp_Basligi_Tipi", "enum", "HE-Frag, Tandem_HEAT, HEAT, Penetrator, BROACH, SAPHE, Thermobaric, Submunition"),
    ("Uzunluk_m", "float | NA", "Toplam uzunluk, m"),
    ("Cap_mm", "float | NA", "Gövde çapı; dairesel olmayan kesitlerde eşdeğer genişlik, mm"),
    ("Kanat_Acikligi_m", "float | NA", "Kanat/kanatçık açıklığı, m"),
    ("Maksimum_Menzil_km", "float | NA", "Optimum yüksek irtifa atış menzili; aralıklarda üst sınır"),
    ("Maksimum_Hiz_Mach", "float | NA", "Serbest düşüş GP bomba = 0.9, sığınak delici = 1.1 (konvansiyon)"),
    ("Itki_Sistemi", "enum", "Solid/Dual_Pulse/Liquid_Rocket, Turbojet, Turbofan, Ramjet, Free_Fall, Glide_Unpowered, Electric_Propeller"),
    ("Gudum_Sistemi_Midcourse", "enum ('/' birleşik)", "INS, GPS(=GNSS), Data-Link, TERCOM; NA; Unpowered_Ballistic"),
    ("Gudum_Sistemi_Terminal", "enum ('+' çok-modlu)", "ARH, SARH, IR, IIR, EO, SAL, MMW, Passive_RF, INS/GPS_Only, ..."),
    ("Birim_Maliyet_USD", "float | NA", "Açık kaynak/bütçe belgesi birim maliyeti (cari USD)"),
    ("Entegre_Platformlar", "str (',' ayraçlı)", "Entegre/sertifikalı platformlar"),
    ("Veri_Guvenilirlik_Notu", "enum", "Acik_Kaynak_Dogrulanmis | Tahmini_Acik_Kaynak"),
]


def main() -> int:
    print(">>> 1/3 Ham dosyalar doğrulanıyor...")
    if sv.main([]) != 0:
        print("Ham veri doğrulamadan geçemedi; birleştirme iptal edildi.")
        return 1

    print("\n>>> 2/3 Birleştiriliyor...")
    frames = []
    for path in sorted(glob.glob(os.path.join(RAW, "*.csv"))):
        df = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
        df["_kaynak"] = os.path.basename(path)
        frames.append(df)
        print(f"    {os.path.basename(path):<34} {len(df):>4} satır")
    master = pd.concat(frames, ignore_index=True)

    # temizlik: boşluk kırpma, tam satır tekrarlarını düşürme
    for c in sv.COLUMNS:
        master[c] = master[c].str.strip()
    before = len(master)
    master = master.drop_duplicates(subset=sv.COLUMNS)
    if len(master) != before:
        print(f"    {before - len(master)} tam-satır tekrarı düşürüldü")

    master["_cat"] = pd.Categorical(master["Ana_Kategori"], CAT_ORDER, ordered=True)
    master = master.sort_values(["_cat", "Alt_Kategori", "Mensei_Ulke", "Muhimmat_Adi"]).reset_index(drop=True)
    trace = master[["Muhimmat_Adi", "_kaynak"]].rename(columns={"_kaynak": "Kaynak_Dosya"})
    master = master[sv.COLUMNS]

    os.makedirs(OUT_DIR, exist_ok=True)
    master.to_csv(OUT_CSV, sep=";", index=False, encoding="utf-8", lineterminator="\n")

    # Excel: sayısal sütunlar gerçek sayı, NA metin olarak korunur
    xl = master.copy()
    for c in NUMERIC:
        xl[c] = xl[c].map(lambda v: v if v == "NA" else (int(v) if c == "Hizmete_Giris_Yili" else float(v)))
    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as w:
        xl.to_excel(w, sheet_name="Master", index=False)
        pd.DataFrame(DICTIONARY, columns=["Sutun", "Tip", "Aciklama"]).to_excel(
            w, sheet_name="Veri_Sozlugu", index=False)
        trace.to_excel(w, sheet_name="Kaynak_Izleme", index=False)
        ws = w.sheets["Master"]
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = ws.dimensions
        for col in ws.columns:
            width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
            ws.column_dimensions[col[0].column_letter].width = min(max(10, width + 2), 45)
    print(f"    -> {os.path.relpath(OUT_CSV, ROOT)} ({len(master)} satır x {master.shape[1]} sütun)")
    print(f"    -> {os.path.relpath(OUT_XLSX, ROOT)}")

    print("\n>>> 3/3 Master dosya bağımsız olarak yeniden doğrulanıyor...")
    rc = sv.main([OUT_CSV, "--report", os.path.join(ROOT, "outputs", "validation_report_master.txt")])
    return rc


if __name__ == "__main__":
    sys.exit(main())
