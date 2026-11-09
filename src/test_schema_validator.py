#!/usr/bin/env python3
"""
Hata enjeksiyonu (fault-injection) testi: doğrulayıcının gerçekten hata
yakaladığını kanıtlar. Geçerli bir satır alınır, bilinçli olarak bozulur ve
her bozulmanın beklenen hata mesajını üretmesi kontrol edilir.

    python3 src/test_schema_validator.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema_validator as sv  # noqa: E402

HEADER = ";".join(sv.COLUMNS)
GOOD = ("AIM-120D AMRAAM;USA;Raytheon;Fuze;BVRAAM;2015;161.5;20.5;HE-Frag;3.66;178;0.45;160;4.0;"
        "Solid_Rocket;INS/GPS/Data-Link;ARH;1090000;F-35,F-22;Acik_Kaynak_Dogrulanmis")


def mutate(idx: int, value: str, base: str = GOOD) -> str:
    parts = base.split(";")
    parts[idx] = value
    return ";".join(parts)


CASES = [
    # (açıklama, satırlar, hata mesajında beklenen parça)
    ("geçerli satır", [GOOD], None),
    ("'Mach 2' metni", [mutate(13, "Mach 2")], "float'a dönüştürülemiyor"),
    ("'150+' menzil", [mutate(12, "150+")], "float'a dönüştürülemiyor"),
    ("virgüllü ondalık", [mutate(6, "161,5")], "float'a dönüştürülemiyor"),
    ("eksik sütun", [";".join(GOOD.split(";")[:-1])], "beklenen 20"),
    ("mükerrer ad", [GOOD, mutate(0, "aim-120d  amraam")], "mükerrer kayıt"),
    ("geçersiz ülke", [mutate(1, "Turkey")], "kontrollü sözlükte yok"),
    ("geçersiz kategori", [mutate(3, "Missile")], "kontrollü sözlükte yok"),
    ("yıl formatı", [mutate(5, "2015.0")], "4 haneli yıl"),
    ("boş alan", [mutate(17, "")], "boş alan"),
    ("harp başlığı > toplam", [mutate(7, "500")], "toplam kütleden"),
    ("geçersiz güdüm tokenı", [mutate(16, "ARH+Laser")], "geçersiz terminal"),
    ("GP bomba Mach kuralı",
     ["Mk-82;USA;GD;Gudumsuz_Bomba;GP_Bomb;1955;241;241;HE-Frag;2.22;273;NA;12;1.2;"
      "Free_Fall;Unpowered_Ballistic;Unguided;NA;F-16;Acik_Kaynak_Dogrulanmis"], "Mach 0.9 kuralı"),
]


def run_case(lines):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as fh:
        fh.write(HEADER + "\n" + "\n".join(lines) + "\n")
        path = fh.name
    try:
        rep = sv.Report()
        sv.validate_file(path, rep, {})
        return rep.errors
    finally:
        os.unlink(path)


def main() -> int:
    failed = 0
    for desc, lines, expect in CASES:
        errors = run_case(lines)
        if expect is None:
            ok = not errors
        else:
            ok = any(expect in e for e in errors)
        failed += not ok
        print(f"[{'OK ' if ok else 'FAIL'}] {desc:<26} -> {len(errors)} hata"
              + ("" if ok else f"  (beklenen: '{expect}', bulunan: {errors})"))
    print(f"\n{len(CASES) - failed}/{len(CASES)} test geçti")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
