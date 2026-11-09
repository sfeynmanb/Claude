#!/usr/bin/env python3
"""
Hava Mühimmatları Veri Seti — Şema Doğrulayıcı (Schema Validator)
=================================================================

data/raw/*.csv (ve isteğe bağlı olarak data/processed/ master dosyası) için
20 sütunluk şemaya %100 uyumu denetler.

Denetimler
----------
1. Başlık: tam olarak 20 sütun, doğru ad ve doğru sıra, ayraç ';'.
2. Satır yapısı: her satırda 20 alan; baş/son boşluk yok; boş alan yok
   (bilinmeyen değerler için açıkça "NA" yazılmalıdır).
3. Tip denetimi: int / float / kontrollü sözlük (enum) / ISO 3166-1 alpha-3.
   Sayısal sütunlarda "Mach 2", "150+", "~300", "1,5" gibi metin kalıntıları
   hata olarak raporlanır.
4. Fiziksel makullük aralıkları (kütle, çap, uzunluk, menzil, hız...).
5. Çapraz alan kuralları:
     - Harp_Basligi_Kutlesi_kg <= Toplam_Kutle_kg
     - Gudumsuz_Bomba => Free_Fall + Unpowered_Ballistic + Unguided
     - Serbest düşüş GP bombaları için Mach 0.9, sığınak deliciler için 1.1
     - "Unguided" terminal güdümü başka bir modla birleştirilemez
6. Mükerrer kayıt: normalize edilmiş Muhimmat_Adi üzerinden tüm dosyalar
   arasında (dosya içi + dosyalar arası) ve tam satır tekrarları.

Kullanım
--------
    python3 src/schema_validator.py                    # data/raw/*.csv
    python3 src/schema_validator.py --include-processed
    python3 src/schema_validator.py dosya1.csv dosya2.csv

Çıkış kodu: 0 = sıfır hata, 1 = en az bir hata.
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEP = ";"
NA = "NA"

# --------------------------------------------------------------------------
# Kontrollü sözlükler
# --------------------------------------------------------------------------
# ISO 3166-1 alpha-3 + "EUR" (çok uluslu Avrupa konsorsiyumu, ör. MBDA ortak
# programları). Ulusal Avrupa ürünleri kendi ISO kodunu taşır (GBR, FRA...).
COUNTRY_CODES = {
    "USA", "TUR", "RUS", "CHN", "EUR", "ISR", "GBR", "FRA", "DEU", "ITA",
    "SWE", "NOR", "ESP", "IND", "PAK", "ZAF", "BRA", "JPN", "KOR", "TWN",
    "ARE", "IRN", "UKR", "AUS",
}

ANA_KATEGORI = {"Fuze", "Gudumlu_Bomba", "Gudumsuz_Bomba", "Dolanan_Muhimmat"}

# Görev tanımındaki 10 alt kategori + belgelenmiş genişletmeler
ALT_KATEGORI_CORE = {
    "WVRAAM", "BVRAAM", "ALCM", "ARM", "ATGM", "AShM",
    "PGM_Glide", "PGM_Laser_INS", "GP_Bomb", "Bunker_Buster",
}
ALT_KATEGORI_EXT = {
    "ALBM",           # Air-Launched (Aero-)Ballistic Missile (Kinzhal, Rampage...)
    "HGV",            # Hypersonic boost-glide (ARRW)
    "TASM",           # Tactical Air-to-Surface Missile (Maverick, Kh-29...)
    "Guided_Rocket",  # 70-230 mm güdümlü roketler (Cirit, APKWS, TRG-230-İHA)
    "Micro_PGM",      # SİHA mikro/mini güdümlü mühimmat (MAM, Bozok, Kayı...)
    "Loitering",      # Havadan atılan dolanan mühimmat
}
ALT_KATEGORI = ALT_KATEGORI_CORE | ALT_KATEGORI_EXT

HARP_BASLIGI_TIPI = {
    "HE-Frag", "Tandem_HEAT", "Penetrator", "BROACH", "SAPHE", "Thermobaric",
    # genişletmeler
    "HEAT", "Submunition", NA,
}

ITKI_SISTEMI = {
    "Solid_Rocket", "Dual_Pulse_Rocket", "Turbojet", "Ramjet", "Free_Fall",
    "Glide_Unpowered",
    # genişletmeler
    "Turbofan", "Liquid_Rocket", "Electric_Propeller", NA,
}

# Ara safha: "/" ile birleştirilebilen atomik tokenlar (ör. INS/GPS/Data-Link)
MIDCOURSE_TOKENS = {"INS", "GPS", "Data-Link", "TERCOM"}
MIDCOURSE_ATOMIC = {NA, "Unpowered_Ballistic"}

# Terminal safha: "+" ile birleştirilebilen çok-modlu arayıcılar (ör. MMW+SAL)
TERMINAL_TOKENS = {
    "ARH", "SARH", "IIR", "EO", "SAL", "Passive_RF", "INS/GPS_Only",
    # genişletmeler
    "IR", "MMW", "Laser_Beam_Riding", "Command_Guidance",
}
TERMINAL_ATOMIC = {NA, "Unguided"}

GUVENILIRLIK = {"Acik_Kaynak_Dogrulanmis", "Tahmini_Acik_Kaynak"}

# --------------------------------------------------------------------------
# Şema: (sütun adı, tip, ek parametre)
# --------------------------------------------------------------------------
SCHEMA = [
    ("Muhimmat_Adi",            "str",        None),
    ("Mensei_Ulke",             "enum",       COUNTRY_CODES),
    ("Uretici_Firma",           "str_na",     None),
    ("Ana_Kategori",            "enum",       ANA_KATEGORI),
    ("Alt_Kategori",            "enum",       ALT_KATEGORI),
    ("Hizmete_Giris_Yili",      "int_na",     (1940, 2030)),
    ("Toplam_Kutle_kg",         "float_na",   (0.5, 20000.0)),
    ("Harp_Basligi_Kutlesi_kg", "float_na",   (0.1, 15000.0)),
    ("Harp_Basligi_Tipi",       "enum",       HARP_BASLIGI_TIPI),
    ("Uzunluk_m",               "float_na",   (0.3, 13.0)),
    ("Cap_mm",                  "float_na",   (20.0, 1500.0)),
    ("Kanat_Acikligi_m",        "float_na",   (0.1, 10.0)),
    ("Maksimum_Menzil_km",      "float_na",   (0.5, 6000.0)),
    ("Maksimum_Hiz_Mach",       "float_na",   (0.1, 25.0)),
    ("Itki_Sistemi",            "enum",       ITKI_SISTEMI),
    ("Gudum_Sistemi_Midcourse", "midcourse",  None),
    ("Gudum_Sistemi_Terminal",  "terminal",   None),
    ("Birim_Maliyet_USD",       "float_na",   (1000.0, 5.0e7)),
    ("Entegre_Platformlar",     "platforms",  None),
    ("Veri_Guvenilirlik_Notu",  "enum",       GUVENILIRLIK),
]
COLUMNS = [c[0] for c in SCHEMA]
NUMERIC_RE = re.compile(r"^-?\d+(\.\d+)?$")
INT_RE = re.compile(r"^\d{4}$")


def normalize_name(name: str) -> str:
    """Mükerrer tespiti için ad normalizasyonu (büyük/küçük harf, boşluk, tire)."""
    s = name.casefold().replace("ı", "i").replace("İ".casefold(), "i")
    return re.sub(r"[\s\-_/().]+", "", s)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, int] = {}

    def err(self, f: str, line: int, col: str, msg: str) -> None:
        self.errors.append(f"[HATA] {f}:{line} [{col}] {msg}")

    def warn(self, f: str, line: int, col: str, msg: str) -> None:
        self.warnings.append(f"[UYARI] {f}:{line} [{col}] {msg}")


def check_cell(rep: Report, fname: str, ln: int, col: str, kind: str, param, v: str):
    """Tek hücre tip denetimi. Sayısal tipler için float/int ya da None döner."""
    if kind == "str":
        if v == NA:
            rep.err(fname, ln, col, "zorunlu metin alanı NA olamaz")
        return v
    if kind == "str_na":
        return v
    if kind == "enum":
        if v not in param:
            rep.err(fname, ln, col, f"'{v}' kontrollü sözlükte yok")
        return v
    if kind == "int_na":
        if v == NA:
            return None
        if not INT_RE.match(v):
            rep.err(fname, ln, col, f"'{v}' 4 haneli yıl (int) veya NA olmalı")
            return None
        iv = int(v)
        lo, hi = param
        if not lo <= iv <= hi:
            rep.err(fname, ln, col, f"{iv} makul aralık dışında [{lo},{hi}]")
        return iv
    if kind == "float_na":
        if v == NA:
            return None
        if not NUMERIC_RE.match(v):
            rep.err(fname, ln, col,
                    f"'{v}' float'a dönüştürülemiyor (yalnızca '.' ondalıklı saf sayı ya da NA)")
            return None
        fv = float(v)
        lo, hi = param
        if not lo <= fv <= hi:
            rep.err(fname, ln, col, f"{fv} fiziksel makullük aralığı dışında [{lo},{hi}]")
        return fv
    if kind == "midcourse":
        if v in MIDCOURSE_ATOMIC:
            return v
        toks = v.split("/")
        bad = [t for t in toks if t not in MIDCOURSE_TOKENS]
        if bad or len(set(toks)) != len(toks):
            rep.err(fname, ln, col, f"'{v}' geçersiz ara safha güdüm ifadesi (token: {bad or 'tekrar'})")
        return v
    if kind == "terminal":
        if v in TERMINAL_ATOMIC:
            return v
        toks = v.split("+")
        bad = [t for t in toks if t not in TERMINAL_TOKENS]
        if bad or len(set(toks)) != len(toks):
            rep.err(fname, ln, col, f"'{v}' geçersiz terminal güdüm ifadesi (token: {bad or 'tekrar'})")
        return v
    if kind == "platforms":
        if v == NA:
            rep.warn(fname, ln, col, "platform bilgisi NA")
            return v
        toks = v.split(",")
        for t in toks:
            if not t or t != t.strip():
                rep.err(fname, ln, col, f"platform listesinde boş/boşluklu öğe: '{t}'")
        if len(set(toks)) != len(toks):
            rep.err(fname, ln, col, "platform listesinde tekrar eden öğe")
        return v
    raise ValueError(kind)


def validate_file(path: str, rep: Report, seen: dict) -> int:
    fname = os.path.relpath(path, ROOT)
    with open(path, newline="", encoding="utf-8") as fh:
        raw = fh.read()
    if raw.startswith("﻿"):
        rep.err(fname, 1, "-", "UTF-8 BOM bulundu; BOM'suz UTF-8 kullanın")
        raw = raw[1:]
    lines = raw.splitlines()
    if not lines:
        rep.err(fname, 0, "-", "dosya boş")
        return 0
    reader = csv.reader(lines, delimiter=SEP, quotechar='"')
    header = next(reader)
    if header != COLUMNS:
        if len(header) != len(COLUMNS):
            rep.err(fname, 1, "-", f"başlık {len(header)} sütun; beklenen {len(COLUMNS)}")
        for i, (got, exp) in enumerate(zip(header, COLUMNS)):
            if got != exp:
                rep.err(fname, 1, exp, f"başlık sütun {i + 1}: '{got}' != '{exp}'")
        return 0

    n = 0
    full_rows: dict[tuple, int] = {}
    for ln, row in enumerate(reader, start=2):
        if not row or all(not c for c in row):
            rep.err(fname, ln, "-", "boş satır")
            continue
        n += 1
        if len(row) != len(COLUMNS):
            rep.err(fname, ln, "-", f"{len(row)} alan; beklenen {len(COLUMNS)} (ayraç ';' tutarsızlığı?)")
            continue
        vals = {}
        for (col, kind, param), v in zip(SCHEMA, row):
            if v == "":
                rep.err(fname, ln, col, "boş alan (bilinmeyen için 'NA' yazın)")
                continue
            if v != v.strip():
                rep.err(fname, ln, col, f"baş/son boşluk: '{v}'")
            vals[col] = check_cell(rep, fname, ln, col, kind, param, v.strip())

        # --- tam satır tekrarı
        key = tuple(row)
        if key in full_rows:
            rep.err(fname, ln, "-", f"tam satır tekrarı (satır {full_rows[key]})")
        full_rows[key] = ln

        # --- mükerrer ad (tüm dosyalar arası)
        name = vals.get("Muhimmat_Adi")
        if name:
            k = normalize_name(name)
            if k in seen:
                rep.err(fname, ln, "Muhimmat_Adi",
                        f"mükerrer kayıt '{name}' (ilk: {seen[k]})")
            else:
                seen[k] = f"{fname}:{ln}"

        # --- çapraz alan kuralları
        tot, wh = vals.get("Toplam_Kutle_kg"), vals.get("Harp_Basligi_Kutlesi_kg")
        if isinstance(tot, float) and isinstance(wh, float) and wh > tot + 1e-9:
            rep.err(fname, ln, "Harp_Basligi_Kutlesi_kg",
                    f"harp başlığı ({wh}) toplam kütleden ({tot}) büyük")
        ana, alt = vals.get("Ana_Kategori"), vals.get("Alt_Kategori")
        itki = vals.get("Itki_Sistemi")
        mid, term = vals.get("Gudum_Sistemi_Midcourse"), vals.get("Gudum_Sistemi_Terminal")
        mach = vals.get("Maksimum_Hiz_Mach")
        if ana == "Gudumsuz_Bomba":
            if itki != "Free_Fall":
                rep.err(fname, ln, "Itki_Sistemi", "Gudumsuz_Bomba => Free_Fall olmalı")
            if mid != "Unpowered_Ballistic":
                rep.err(fname, ln, "Gudum_Sistemi_Midcourse", "Gudumsuz_Bomba => Unpowered_Ballistic olmalı")
            if term != "Unguided":
                rep.err(fname, ln, "Gudum_Sistemi_Terminal", "Gudumsuz_Bomba => Unguided olmalı")
            if alt not in {"GP_Bomb", "Bunker_Buster"}:
                rep.err(fname, ln, "Alt_Kategori", "Gudumsuz_Bomba => GP_Bomb/Bunker_Buster olmalı")
        elif term == "Unguided":
            rep.err(fname, ln, "Gudum_Sistemi_Terminal", f"'{ana}' kategorisi Unguided olamaz")
        if itki == "Free_Fall" and ana in {"Gudumsuz_Bomba", "Gudumlu_Bomba"}:
            exp = 1.1 if alt == "Bunker_Buster" else 0.9
            if mach is None or abs(mach - exp) > 1e-9:
                rep.err(fname, ln, "Maksimum_Hiz_Mach",
                        f"serbest düşüş {alt} için Mach {exp} kuralı (bulunan: {mach})")
        if mid == "Unpowered_Ballistic" and ana != "Gudumsuz_Bomba":
            rep.err(fname, ln, "Gudum_Sistemi_Midcourse", "Unpowered_Ballistic yalnızca Gudumsuz_Bomba için")
        if ana == "Dolanan_Muhimmat" and alt != "Loitering":
            rep.err(fname, ln, "Alt_Kategori", "Dolanan_Muhimmat => Loitering olmalı")
        if alt == "Loitering" and ana != "Dolanan_Muhimmat":
            rep.err(fname, ln, "Ana_Kategori", "Loitering => Dolanan_Muhimmat olmalı")
        if alt in {"WVRAAM", "BVRAAM", "ARM", "ALCM", "AShM", "ALBM", "HGV", "ATGM"} and ana != "Fuze":
            rep.err(fname, ln, "Ana_Kategori", f"{alt} => Fuze olmalı")
        if alt in {"PGM_Glide", "PGM_Laser_INS", "Micro_PGM"} and ana != "Gudumlu_Bomba":
            rep.err(fname, ln, "Ana_Kategori", f"{alt} => Gudumlu_Bomba olmalı")
        if alt == "GP_Bomb" and ana != "Gudumsuz_Bomba":
            rep.err(fname, ln, "Ana_Kategori", "GP_Bomb => Gudumsuz_Bomba olmalı")

        # --- sayısal kapsam istatistiği
        for col, kind, _ in SCHEMA:
            if kind in ("float_na", "int_na"):
                rep.stats[col] = rep.stats.get(col, 0) + (vals.get(col) is not None)
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="Denetlenecek CSV dosyaları (varsayılan: data/raw/*.csv)")
    ap.add_argument("--include-processed", action="store_true",
                    help="data/processed/master_air_munitions_dataset.csv dosyasını da ayrı olarak denetle")
    ap.add_argument("--report", default=os.path.join(ROOT, "outputs", "validation_report.txt"))
    args = ap.parse_args(argv)

    files = args.files or sorted(glob.glob(os.path.join(ROOT, "data", "raw", "*.csv")))
    if not files:
        print("Denetlenecek CSV bulunamadı.")
        return 1

    rep = Report()
    seen: dict[str, str] = {}
    per_file: dict[str, int] = {}
    for f in files:
        per_file[os.path.relpath(f, ROOT)] = validate_file(f, rep, seen)

    if args.include_processed:
        master = os.path.join(ROOT, "data", "processed", "master_air_munitions_dataset.csv")
        if os.path.exists(master):
            mrep = Report()
            per_file[os.path.relpath(master, ROOT) + " (bağımsız)"] = validate_file(master, mrep, {})
            rep.errors += mrep.errors
            rep.warnings += mrep.warnings

    total = sum(v for k, v in per_file.items() if "bağımsız" not in k)
    out = ["=" * 72, "ŞEMA DOĞRULAMA RAPORU — Hava Mühimmatları Veri Seti", "=" * 72]
    for k, v in per_file.items():
        out.append(f"  {k:<58} {v:>4} satır")
    out.append(f"  {'TOPLAM (raw)':<58} {total:>4} satır")
    out.append("-" * 72)
    if total:
        out.append("Sayısal alan doluluk oranları (NA olmayan):")
        for col, cnt in rep.stats.items():
            out.append(f"  {col:<28} {cnt:>4}/{total:<4} (%{100 * cnt / total:5.1f})")
        out.append("-" * 72)
    out += rep.errors
    out += rep.warnings
    out.append("-" * 72)
    out.append(f"SONUÇ: {len(rep.errors)} hata, {len(rep.warnings)} uyarı")
    out.append("DURUM: " + ("BAŞARILI ✔ (sıfır hata)" if not rep.errors else "BAŞARISIZ ✘"))
    text = "\n".join(out)
    print(text)
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    return 0 if not rep.errors else 1


if __name__ == "__main__":
    sys.exit(main())
