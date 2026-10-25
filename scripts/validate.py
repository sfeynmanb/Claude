#!/usr/bin/env python3
"""Türk-İslam Atlası veri doğrulama betiği.

Kullanım:  python3 scripts/validate.py [--quiet]
Çıktı:     reports/validation.md  (hata varsa çıkış kodu 1)
"""
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORT = ROOT / "reports" / "validation.md"

TOLERANS = 15  # yaklaşık/tartışmalı tarihlerde yıl toleransı
ILISKI_TURLERI = {"hoca-öğrenci", "himaye", "etkiledi", "çağdaş-tartışma", "tercüme etti", "şerh yazdı", "yayımladı", "iş birliği"}
KESINLIK = {"kesin", "yaklaşık", "tartışmalı"}
YKS = {"yüksek", "orta", "düşük"}
ENLEM = (0, 57)  # Endülüs ve Hicaz’dan İdil-Ural’a (Kazan 55.8)
BOYLAM = (-10, 82)  # Endülüs’ten Kazak bozkırına (Semey 80.2)
KISI_ZORUNLU = ["id", "ad", "tam_ad", "tarih_kesinligi", "koken", "devletler", "alanlar", "ozet", "katkilar", "yks_onemi", "kaynaklar"]
ESER_ZORUNLU = ["id", "ad", "ad_sade", "dil", "tur", "konu", "onemi", "yks_onemi", "kaynaklar"]


def yil_coz(v):
    """int | '~980' | '1069-1070' | '~1020-1030' | None -> (alt, üst, yaklaşık_mı) veya None."""
    if v is None:
        return None
    if isinstance(v, int):
        return (v, v, False)
    s = str(v).strip()
    yaklasik = s.startswith("~")
    s = s.lstrip("~")
    m = re.fullmatch(r"(\d{3,4})(?:-(\d{3,4}))?", s)
    if not m:
        raise ValueError(f"çözülemeyen yıl: {v!r}")
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    return (a, b, yaklasik)


class Rapor:
    def __init__(self):
        self.hatalar = []
        self.uyarilar = []
        self.notlar = []

    def hata(self, kayit, mesaj):
        self.hatalar.append((kayit, mesaj))

    def uyari(self, kayit, mesaj):
        self.uyarilar.append((kayit, mesaj))

    def not_(self, kayit, mesaj):
        self.notlar.append((kayit, mesaj))


def omur(kisi):
    """Kişinin (doğum, ölüm, tolerans) bilgisi; bilinmeyen uçlar None."""
    d = yil_coz(kisi.get("dogum"))
    o = yil_coz(kisi.get("olum"))
    belirsiz = kisi.get("tarih_kesinligi") != "kesin" or (d and d[2]) or (o and o[2])
    tol = TOLERANS if belirsiz else 0
    return (d[0] if d else None, o[1] if o else None, tol)


def main():
    quiet = "--quiet" in sys.argv
    r = Rapor()
    people = json.loads((DATA / "people.json").read_text(encoding="utf-8"))
    works = json.loads((DATA / "works.json").read_text(encoding="utf-8"))
    rels = json.loads((DATA / "relations.json").read_text(encoding="utf-8"))
    meta = json.loads((DATA / "meta.json").read_text(encoding="utf-8"))

    pid = {p["id"]: p for p in people}
    wid = {w["id"]: w for w in works}
    for ad, coll in (("kişi", people), ("eser", works)):
        for i, n in Counter(x["id"] for x in coll).items():
            if n > 1:
                r.hata(i, f"{ad} kimliği {n} kez tekrarlanıyor")
    for i in set(pid) & set(wid):
        r.hata(i, "aynı kimlik hem kişi hem eser için kullanılmış")

    bilinen_devlet = {d["ad"] for d in meta["devletler"]} | set(meta["grup_eslemesi"])

    # --- Kişiler ---
    for p in people:
        k = f"kişi:{p['id']}"
        for alan in KISI_ZORUNLU:
            if p.get(alan) in (None, "", []):
                r.hata(k, f"zorunlu alan boş: {alan}")
        if p.get("tarih_kesinligi") not in KESINLIK:
            r.hata(k, f"geçersiz tarih_kesinligi: {p.get('tarih_kesinligi')!r}")
        if p.get("yks_onemi") not in YKS:
            r.hata(k, f"geçersiz yks_onemi: {p.get('yks_onemi')!r}")
        try:
            d, o, tol = omur(p)
        except ValueError as e:
            r.hata(k, str(e))
            continue
        if d and o and d > o:
            r.hata(k, f"doğum ({d}) ölümden ({o}) sonra")
        if d is None and o is None:
            r.not_(k, "doğum ve ölüm yılları bilinmiyor")
        for dev in p.get("devletler", []):
            if dev not in bilinen_devlet:
                r.uyari(k, f"meta.json'da tanımsız devlet: {dev}")
        for durak in p.get("duraklar", []):
            lat, lon = durak.get("enlem"), durak.get("boylam")
            yer = durak.get("sehir")
            if lat is None or lon is None:
                r.hata(k, f"{yer}: koordinat eksik")
                continue
            if durak.get("bolge_disi"):
                r.not_(k, f"{yer} ({lat}, {lon}) çalışma bölgesi dışında; bilerek 'bolge_disi' işaretli")
            elif not (ENLEM[0] <= lat <= ENLEM[1] and BOYLAM[0] <= lon <= BOYLAM[1]):
                r.hata(k, f"{yer} ({lat}, {lon}) makul bölge dışında (enlem {ENLEM}, boylam {BOYLAM})")
            for uc in ("yil_baslangic", "yil_bitis"):
                y = durak.get(uc)
                if y is None:
                    continue
                if d and y < d - tol:
                    r.uyari(k, f"{yer}: {uc}={y} doğumdan ({d}) önce")
                if o and y > o + tol:
                    r.uyari(k, f"{yer}: {uc}={y} ölümden ({o}) sonra")
            if durak.get("yil_baslangic") and durak.get("yil_bitis") and durak["yil_baslangic"] > durak["yil_bitis"]:
                r.hata(k, f"{yer}: başlangıç yılı bitişten büyük")
        for kay in p.get("kaynaklar", []):
            if not str(kay.get("url", "")).startswith("https://"):
                r.hata(k, f"geçersiz kaynak URL'si: {kay}")

    # --- Eserler ---
    for w in works:
        k = f"eser:{w['id']}"
        for alan in ESER_ZORUNLU:
            if w.get(alan) in (None, "", []):
                r.hata(k, f"zorunlu alan boş: {alan}")
        if w.get("yks_onemi") not in YKS:
            r.hata(k, f"geçersiz yks_onemi: {w.get('yks_onemi')!r}")
        yazar = w.get("yazar_id")
        if yazar is None:
            if not w.get("anonim"):
                r.hata(k, "yazar_id boş ama 'anonim' işaretli değil")
            else:
                r.not_(k, "anonim eser (yazar_id yok)")
        elif yazar not in pid:
            r.hata(k, f"yazar_id people.json'da yok: {yazar}")
        try:
            y = yil_coz(w.get("yil"))
        except ValueError as e:
            r.hata(k, str(e))
            y = None
        if y and yazar in pid:
            d, o, tol = omur(pid[yazar])
            if y[2]:
                tol = max(tol, TOLERANS)
            bas, bit = y[0], y[1]
            # Bir uç bilinmiyorsa makul en uzun ömür (100 yıl) varsayılır.
            if o is None and d:
                o, tol = d + 100, max(tol, TOLERANS)
            if d is None and o:
                d, tol = o - 100, max(tol, TOLERANS)
            if d and bas < d - tol:
                r.hata(k, f"eser yılı {w['yil']} yazarın doğumundan ({d}) önce (tolerans ±{tol})")
            elif d and bas - d < 12 and not w.get("anonim"):
                r.uyari(k, f"eser yılı {w['yil']} yazarın {bas - d} yaşına denk geliyor")
            if o and bas > o + tol:
                r.hata(k, f"eser yılı {w['yil']} yazarın ölümünden ({o}) sonra (tolerans ±{tol})")
            elif o and bit > o + tol and not w.get("olum_sonrasi_tamamlandi"):
                r.hata(k, f"eserin bitiş yılı {bit} yazarın ölümünden ({o}) sonra; 'olum_sonrasi_tamamlandi' işaretlenmeli")
        elif w.get("yil") is None:
            r.not_(k, "eser yılı belirtilmemiş")
        for kay in w.get("kaynaklar", []):
            if not str(kay.get("url", "")).startswith("https://"):
                r.hata(k, f"geçersiz kaynak URL'si: {kay}")

    # --- İlişkiler ---
    seen = Counter()
    for i, rel in enumerate(rels):
        k = f"ilişki#{i}:{rel.get('kaynak')}→{rel.get('hedef')}"
        if rel.get("tur") not in ILISKI_TURLERI:
            r.hata(k, f"geçersiz ilişki türü: {rel.get('tur')!r}")
        for uc in ("kaynak", "hedef"):
            if rel.get(uc) not in pid and rel.get(uc) not in wid:
                r.hata(k, f"{uc} kimliği bulunamadı: {rel.get(uc)}")
        if rel.get("kaynak") == rel.get("hedef"):
            r.hata(k, "kaynak ve hedef aynı")
        seen[(rel.get("kaynak"), rel.get("hedef"), rel.get("tur"))] += 1
        if rel.get("tur") == "hoca-öğrenci":
            a, b = pid.get(rel.get("kaynak")), pid.get(rel.get("hedef"))
            if not (a and b):
                r.hata(k, "hoca-öğrenci ilişkisinin iki ucu da kişi olmalı")
                continue
            da, oa, ta = omur(a)
            db, ob, tb = omur(b)
            tol = max(ta, tb)
            ust_a = oa if oa is not None else (da + 90 if da else None)
            alt_b = db if db is not None else (ob - 90 if ob else None)
            ust_b = ob if ob is not None else (db + 90 if db else None)
            alt_a = da if da is not None else (oa - 90 if oa else None)
            if None in (ust_a, alt_b, ust_b, alt_a):
                r.uyari(k, "ömür bilgisi eksik; çakışma kontrol edilemedi")
            elif ust_a + tol < alt_b or ust_b + tol < alt_a:
                r.hata(k, f"hoca ({alt_a}–{ust_a}) ile öğrencinin ({alt_b}–{ust_b}) ömürleri çakışmıyor")
    for key, n in seen.items():
        if n > 1:
            r.hata(f"ilişki:{key[0]}→{key[1]}", f"aynı ilişki {n} kez tanımlanmış")

    # --- Karıştırılanlar ---
    for c in meta.get("karistirilanlar", []):
        for uc in ("a", "b"):
            if c[uc] not in wid:
                r.hata(f"karıştırılan:{c['a']}/{c['b']}", f"eser bulunamadı: {c[uc]}")

    # --- Kaynak / teyit raporları ---
    kaynaksiz = [x["id"] for x in people + works if not x.get("kaynaklar")]
    dogrulanamadi = [("kişi", x["id"]) for x in people if x.get("dogrulanamadi")] + \
                    [("eser", x["id"]) for x in works if x.get("dogrulanamadi")] + \
                    [("ilişki", f"{x['kaynak']}→{x['hedef']} ({x['tur']})") for x in rels if x.get("dogrulanamadi")]
    teyitsiz = [("kişi", x["id"], x["teyitsiz_alanlar"]) for x in people if x.get("teyitsiz_alanlar")] + \
               [("eser", x["id"], x["teyitsiz_alanlar"]) for x in works if x.get("teyitsiz_alanlar")]
    alan_sayaci = Counter(a for _, _, alanlar in teyitsiz for a in alanlar)

    # --- Rapor yaz ---
    lines = [
        "# Doğrulama Raporu",
        "",
        f"_Oluşturma: {date.today().isoformat()} · `python3 scripts/validate.py`_",
        "",
        "## Özet",
        "",
        "| | Sayı |", "|---|---:|",
        f"| Kişi | {len(people)} |", f"| Eser | {len(works)} |", f"| İlişki | {len(rels)} |",
        f"| Karıştırılan çift | {len(meta.get('karistirilanlar', []))} |",
        f"| **Hata** | **{len(r.hatalar)}** |", f"| Uyarı | {len(r.uyarilar)} |", f"| Not | {len(r.notlar)} |",
        f"| Kaynaksız kayıt | {len(kaynaksiz)} |",
        f"| `dogrulanamadi` işaretli kayıt | {len(dogrulanamadi)} |",
        f"| Kendi bilgimize dayanan alan içeren kayıt | {len(teyitsiz)} |",
        "",
        "Kontroller: yazar kimlikleri, eser yılının yazarın ömrüyle uyumu (yaklaşık/tartışmalı tarihlerde ±15 yıl), "
        "ilişki kimlikleri ve türleri, hoca-öğrenci ömür çakışması, koordinatların bölge içinde olması "
        f"(enlem {ENLEM[0]}–{ENLEM[1]}, boylam {BOYLAM[0]}–{BOYLAM[1]}), zorunlu alanlar, kaynak URL'leri, karıştırılan çiftler.",
        "",
    ]

    def bolum(baslik, kayitlar):
        lines.append(f"## {baslik} ({len(kayitlar)})")
        lines.append("")
        if not kayitlar:
            lines.append("_Yok._")
        for kayit, mesaj in kayitlar:
            lines.append(f"- `{kayit}` — {mesaj}")
        lines.append("")

    bolum("Hatalar", r.hatalar)
    bolum("Uyarılar", r.uyarilar)
    bolum("Notlar", r.notlar)

    lines.append(f"## Kaynağı olmayan kayıtlar ({len(kaynaksiz)})")
    lines.append("")
    lines.extend([f"- `{i}`" for i in kaynaksiz] or ["_Yok; her kayıtta en az bir kaynak URL'si var._"])
    lines.append("")
    lines.append(f"## `dogrulanamadi` işaretli kayıtlar ({len(dogrulanamadi)})")
    lines.append("")
    lines.append("Bu kayıtlar tutuldu ama dayandıkları bilgi kaynakla teyit edilemedi; arayüzde uyarı etiketiyle gösterilir.")
    lines.append("")
    lines.extend([f"- {t}: `{i}`" for t, i in dogrulanamadi] or ["_Yok._"])
    lines.append("")
    lines.append(f"## Kendi bilgimize dayanan, kaynakla teyit edilmemiş alanlar ({len(teyitsiz)} kayıt)")
    lines.append("")
    lines.append("TDV İslâm Ansiklopedisi sitesine bu ortamdan doğrudan erişilemedi. Her kayıttaki TDV URL'si ve temel tarihler "
                 "web aramasıyla dönen TDV madde özetlerinden teyit edildi. Aşağıdaki alanlar ise bu özetlerde görülmedi; "
                 "genel bilgiye dayanır ve TDV maddesinin tam metniyle karşılaştırılmalıdır.")
    lines.append("")
    lines.append("Alan bazında: " + ", ".join(f"`{a}` ({n})" for a, n in alan_sayaci.most_common()))
    lines.append("")
    lines.append("| Tür | Kimlik | Teyitsiz alanlar |")
    lines.append("|---|---|---|")
    for t, i, alanlar in teyitsiz:
        lines.append(f"| {t} | `{i}` | {', '.join(alanlar)} |")
    lines.append("")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    if not quiet:
        print(f"{len(people)} kişi, {len(works)} eser, {len(rels)} ilişki")
        print(f"Hata: {len(r.hatalar)}  Uyarı: {len(r.uyarilar)}  Not: {len(r.notlar)}")
        for kayit, mesaj in r.hatalar:
            print(f"  HATA  {kayit}: {mesaj}")
        for kayit, mesaj in r.uyarilar:
            print(f"  uyarı {kayit}: {mesaj}")
        print(f"Rapor: {REPORT.relative_to(ROOT)}")
    return 1 if r.hatalar else 0


if __name__ == "__main__":
    sys.exit(main())
