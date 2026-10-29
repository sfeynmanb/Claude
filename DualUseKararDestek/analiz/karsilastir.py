#!/usr/bin/env python3
"""Çift kullanımlı karar destek şirketleri için ağırlıklı çok kriterli karşılaştırma.

Puanlar (1-5) skor_matrisi.csv dosyasından, ağırlık setleri agirlik_senaryolari.csv
dosyasından okunur. Sonuç 0-100 ölçeğine normalize edilir.

Kullanım:
    python3 karsilastir.py                       # tüm senaryolar
    python3 karsilastir.py --agirlik "K1=10,K2=20,K3=10,K4=20,K5=10,K6=20,K7=5,K8=5"
    python3 karsilastir.py --duyarlilik K6       # K6 ağırlığını 0-40 arası tarar
"""

import argparse
import csv
import os

KRITERLER = {
    "K1": "Urun olgunlugu / olcek",
    "K2": "Muharebe dogrulamasi",
    "K3": "Veri / entegrasyon katmani derinligi",
    "K4": "Kenar / otonomi ve EH dayanikliligi",
    "K5": "Donanim / efektor entegrasyonu",
    "K6": "Egemenlik uygunlugu (Avrupali alici)",
    "K7": "Finansal saglamlik",
    "K8": "Yonetisim / seffaflik",
}
MAKS_PUAN = 5
DIZIN = os.path.dirname(os.path.abspath(__file__))


def puanlari_oku(yol):
    puanlar = {}
    with open(yol, newline="", encoding="utf-8") as f:
        for satir in csv.DictReader(f):
            puan = int(satir["puan"])
            if not 1 <= puan <= MAKS_PUAN:
                raise ValueError(f"{satir['sirket']} {satir['kriter']}: puan 1-5 olmali")
            puanlar.setdefault(satir["sirket"], {})[satir["kriter"]] = puan
    for sirket, p in puanlar.items():
        eksik = set(KRITERLER) - set(p)
        if eksik:
            raise ValueError(f"{sirket} icin eksik kriter: {sorted(eksik)}")
    return puanlar


def senaryolari_oku(yol):
    senaryolar = []
    with open(yol, newline="", encoding="utf-8") as f:
        for satir in csv.DictReader(f):
            agirlik = {k: float(satir[k]) for k in KRITERLER}
            senaryolar.append((satir["senaryo"], satir["aciklama"], agirlik))
    return senaryolar


def agirlik_ayristir(metin):
    agirlik = {k: 0.0 for k in KRITERLER}
    for parca in metin.split(","):
        anahtar, deger = parca.split("=")
        anahtar = anahtar.strip().upper()
        if anahtar not in KRITERLER:
            raise ValueError(f"Bilinmeyen kriter: {anahtar}")
        agirlik[anahtar] = float(deger)
    return agirlik


def skor(puan, agirlik):
    toplam_agirlik = sum(agirlik.values())
    if toplam_agirlik <= 0:
        raise ValueError("Agirliklarin toplami pozitif olmali")
    ham = sum(puan[k] * agirlik[k] for k in KRITERLER)
    return 100.0 * ham / (MAKS_PUAN * toplam_agirlik)


def siralama_yazdir(baslik, puanlar, agirlik):
    print(f"\n== {baslik} ==")
    print("Agirliklar: " + ", ".join(f"{k}={agirlik[k]:g}" for k in KRITERLER))
    sonuc = sorted(((skor(p, agirlik), s) for s, p in puanlar.items()), reverse=True)
    for sira, (deger, sirket) in enumerate(sonuc, 1):
        cubuk = "#" * int(round(deger / 2))
        print(f"  {sira}. {sirket:<12} {deger:6.1f}  {cubuk}")


def duyarlilik_yazdir(puanlar, temel, kriter, adimlar=(0, 5, 10, 15, 20, 25, 30, 40)):
    print(f"\n== Duyarlilik: {kriter} ({KRITERLER[kriter]}) agirligi degisirken ==")
    sirketler = sorted(puanlar)
    print(f"  {'agirlik':>8} " + " ".join(f"{s:>11}" for s in sirketler) + "   lider")
    for a in adimlar:
        agirlik = dict(temel, **{kriter: float(a)})
        degerler = {s: skor(puanlar[s], agirlik) for s in sirketler}
        lider = max(degerler, key=degerler.get)
        print(f"  {a:>8} " + " ".join(f"{degerler[s]:>11.1f}" for s in sirketler) + f"   {lider}")


def main():
    ayrac = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ayrac.add_argument("--puanlar", default=os.path.join(DIZIN, "skor_matrisi.csv"))
    ayrac.add_argument("--senaryolar", default=os.path.join(DIZIN, "agirlik_senaryolari.csv"))
    ayrac.add_argument("--agirlik", help='Ozel agirlik seti, ornek: "K1=10,K2=20,..."')
    ayrac.add_argument("--duyarlilik", choices=sorted(KRITERLER), help="Senaryo A uzerinde tek kriter taramasi")
    arg = ayrac.parse_args()

    puanlar = puanlari_oku(arg.puanlar)
    senaryolar = senaryolari_oku(arg.senaryolar)

    print("Kriterler:")
    for k, ad in KRITERLER.items():
        print(f"  {k}: {ad}")

    if arg.agirlik:
        siralama_yazdir("Ozel agirlik seti", puanlar, agirlik_ayristir(arg.agirlik))
    else:
        for kod, aciklama, agirlik in senaryolar:
            siralama_yazdir(f"Senaryo {kod}: {aciklama}", puanlar, agirlik)

    if arg.duyarlilik:
        duyarlilik_yazdir(puanlar, senaryolar[0][2], arg.duyarlilik)


if __name__ == "__main__":
    main()
