#!/usr/bin/env python3
"""
Doktriner hedef matrisi (data/targets/target_vulnerability_matrix.csv) şema doğrulayıcısı.

    python3 src/validate_target_matrix.py [dosya.csv]

Denetimler: sütun adı/sırası, benzersiz Target_ID ve biçimi, kontrollü sözlükler,
sayısal aralıklar ve çapraz alan tutarlılığı. Çıkış kodu: 0 = sıfır hata.
Adım 2'de weaponeering motorunun yükleyicisi bu modülü kullanacaktır.
"""
from __future__ import annotations

import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PATH = os.path.join(ROOT, "data", "targets", "target_vulnerability_matrix.csv")

REQUIRED_COLUMNS = [
    "Target_ID", "Target_Category", "Target_Description", "UFC_Hardness_Rating_psi",
    "Required_Concrete_Penetration_m", "Target_Mobility_Class", "TST_Status",
    "Radar_Cross_Section_m2", "Required_Lethal_Radius_m", "Collateral_Damage_Tier",
]
EXTRA_COLUMNS = ["Passive_Defense_Level", "Thermal_Signature", "Target_Class", "Primary_Damage_Mechanism",
                 "Hardness_Basis", "Data_Confidence"]
COLUMNS = REQUIRED_COLUMNS + EXTRA_COLUMNS

EXTENT = ("Point", "Area")
HARDNESS = ("Hard", "Soft")
MOVEMENT = ("Fixed", "Mobile", "Relocatable")
MOBILITY_CLASSES = ("Fixed", "Slow", "Fast")
CDE_TIERS = ("Low", "Medium", "High")
PASSIVE_LEVELS = ("Low", "Medium", "High", "Extreme")
THERMAL_LEVELS = ("Low", "Medium", "High")
CONFIDENCE_LEVELS = ("Kaynakli", "Turetilmis", "Varsayim")
# Motorun kural tablolarının anahtarı olan hedef sınıfı ve hangi etki modelinin geçerli olduğunu belirleyen mekanizma
TARGET_CLASSES = ("Hardened_Structure", "Soft_Structure", "Infrastructure", "Soft_Vehicle", "Armored_Vehicle",
                  "Radar/Air_Defense", "Naval", "Personnel")
DAMAGE_MECHANISMS = ("Blast", "Fragment", "Direct_Hit", "Penetration", "Crater")
ID_PATTERN = re.compile(r"^TGT-[A-Z0-9]{2,4}-\d{2}$")
NUMERIC_RANGES = {
    "UFC_Hardness_Rating_psi": (0.5, 1000.0),
    "Required_Concrete_Penetration_m": (0.0, 30.0),
    "Radar_Cross_Section_m2": (0.01, 100000.0),
    "Required_Lethal_Radius_m": (0.5, 500.0),
}
MIN_TARGETS = 25


def read_matrix(path: str = DEFAULT_PATH) -> pd.DataFrame:
    """Matrisi metin olarak okur (doğrulama için); tip dönüşümü load_matrix'te yapılır."""
    return pd.read_csv(path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")


def validate(df: pd.DataFrame, min_rows: int = MIN_TARGETS) -> tuple[list[str], list[str]]:
    """(hatalar, uyarılar) döndürür."""
    errors: list[str] = []
    warnings: list[str] = []
    if list(df.columns) != COLUMNS:
        return [f"Sütunlar beklenenle aynı değil.\n  beklenen: {COLUMNS}\n  bulunan : {list(df.columns)}"], warnings
    if len(df) < min_rows:
        errors.append(f"En az {min_rows} hedef gerekli; bulunan {len(df)}")
    duplicated = df["Target_ID"][df["Target_ID"].duplicated()].tolist()
    if duplicated:
        errors.append(f"Mükerrer Target_ID: {duplicated}")

    enums = {
        "Target_Mobility_Class": MOBILITY_CLASSES, "TST_Status": ("True", "False"),
        "Collateral_Damage_Tier": CDE_TIERS, "Passive_Defense_Level": PASSIVE_LEVELS,
        "Thermal_Signature": THERMAL_LEVELS, "Data_Confidence": CONFIDENCE_LEVELS,
        "Target_Class": TARGET_CLASSES, "Primary_Damage_Mechanism": DAMAGE_MECHANISMS,
    }
    for line, row in enumerate(df.to_dict("records"), start=2):
        tid = row["Target_ID"]
        where = f"satır {line} ({tid})"
        if not ID_PATTERN.match(tid):
            errors.append(f"{where}: Target_ID biçimi TGT-XXX-NN olmalı")
        for col in ("Target_Description", "Hardness_Basis"):
            if not row[col].strip():
                errors.append(f"{where} [{col}]: boş olamaz")
        for col, allowed in enums.items():
            if row[col] not in allowed:
                errors.append(f"{where} [{col}]: '{row[col]}' geçersiz; seçenekler: {list(allowed)}")

        parts = row["Target_Category"].split("/")
        category_ok = (len(parts) == 3 and parts[0] in EXTENT and parts[1] in HARDNESS
                       and parts[2] in MOVEMENT)
        if not category_ok:
            errors.append(f"{where} [Target_Category]: '{row['Target_Category']}' "
                          f"{'|'.join(EXTENT)} / {'|'.join(HARDNESS)} / {'|'.join(MOVEMENT)} biçiminde olmalı")

        values: dict[str, float] = {}
        for col, (low, high) in NUMERIC_RANGES.items():
            try:
                values[col] = float(row[col])
            except ValueError:
                errors.append(f"{where} [{col}]: '{row[col]}' sayısal değil")
                continue
            if not low <= values[col] <= high:
                errors.append(f"{where} [{col}]: {values[col]} aralık dışında [{low}, {high}]")

        # çapraz alan tutarlılığı
        if category_ok:
            _, hardness, movement = parts
            penetration = values.get("Required_Concrete_Penetration_m")
            mobility = row["Target_Mobility_Class"]
            if hardness == "Soft" and penetration:
                errors.append(f"{where}: Soft hedefte beton delme gereksinimi 0 olmalı")
            if movement == "Fixed" and mobility != "Fixed":
                errors.append(f"{where}: kategori Fixed iken Target_Mobility_Class '{mobility}' olamaz")
            if movement == "Mobile" and mobility == "Fixed":
                errors.append(f"{where}: kategori Mobile iken Target_Mobility_Class Fixed olamaz")
            if penetration and movement != "Fixed":
                errors.append(f"{where}: beton delme gereksinimi yalnız sabit yapılar için anlamlı")
            if row["Target_Class"] == "Hardened_Structure" and not penetration:
                warnings.append(f"{where}: Hardened_Structure sınıfında beton delme gereksinimi 0")
            if row["TST_Status"] == "True" and movement == "Fixed":
                warnings.append(f"{where}: sabit tesis TST olarak işaretlenmiş - gerekçesini doğrulayın")
            if movement == "Mobile" and mobility == "Fast" and row["TST_Status"] == "False":
                warnings.append(f"{where}: hızlı hareketli hedef TST değil - doğrulayın")
    return errors, warnings


def load_matrix(path: str = DEFAULT_PATH) -> pd.DataFrame:
    """Doğrular ve tipleri dönüştürür (sayısal → float, TST_Status → bool)."""
    df = read_matrix(path)
    errors, _ = validate(df)
    if errors:
        raise ValueError("Hedef matrisi geçersiz:\n  " + "\n  ".join(errors))
    for col in NUMERIC_RANGES:
        df[col] = df[col].astype(float)
    df["TST_Status"] = df["TST_Status"] == "True"
    return df


def main(argv=None) -> int:
    path = (argv or sys.argv[1:] or [DEFAULT_PATH])[0]
    df = read_matrix(path)
    errors, warnings = validate(df)
    print(f"Hedef matrisi: {os.path.relpath(path, ROOT)} - {len(df)} hedef x {df.shape[1]} sütun")
    if not errors:
        print("Güven dağılımı:", df["Data_Confidence"].value_counts().to_dict())
        print("TST:", int((df["TST_Status"] == "True").sum()), "| Hard:",
              int(df["Target_Category"].str.contains("/Hard/").sum()), "| Soft:",
              int(df["Target_Category"].str.contains("/Soft/").sum()))
    for msg in errors:
        print("[HATA]", msg)
    for msg in warnings:
        print("[UYARI]", msg)
    print(f"SONUÇ: {len(errors)} hata, {len(warnings)} uyarı")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
