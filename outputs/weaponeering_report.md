# Weaponeering Motoru - Toplu Sonuç Raporu

*Oluşturulma: 2026-11-13 · Üretici: `src/weaponeering_engine.py --report`*

> Sözde-PK değerleri temsilî katsayılı, kalibre edilmemiş bir sezgisel modelden gelir; JMEM/JAWS verisi değildir ve operasyonel planlama için kullanılamaz.

## TGT-HAS-01 - Hardened Aircraft Shelter (HAS) - betonarme kemer ve çelik iç kaplama

`Point/Hard/Fixed` · `Hardened_Structure` · sertlik 30 psi (Varsayim) · delme 0.9 m · gerekli yarıçap 8 m · Fixed · pasif savunma High · RCS 800 m² · termal Low · TST False · mekanizma Penetration · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 17 uygun / 198 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | AGM-154C JSOW | Uçak | 71.7 | 0.72 | 2 | IIR | 130 |
| 2 | SOM-B2 | Uçak | 71.7 | 0.72 | 2 | IIR | 250 |
| 3 | Storm Shadow (SCALP-EG) | Uçak | 71.7 | 0.72 | 2 | IIR | 560 |
| 4 | Taurus KEPD 350 | Uçak | 71.7 | 0.72 | 2 | IIR | 500 |
| 5 | AGM-84H SLAM-ER | Uçak | 67.9 | 0.68 | 3 | IIR | 270 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 10 uygun / 218 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | SOM-B2 | Uçak | 71.7 | 0.72 | 2 | IIR | 250 |
| 2 | Storm Shadow (SCALP-EG) | Uçak | 71.7 | 0.72 | 2 | IIR | 560 |
| 3 | Taurus KEPD 350 | Uçak | 71.7 | 0.72 | 2 | IIR | 500 |
| 4 | AGM-84H SLAM-ER | Uçak | 67.9 | 0.68 | 3 | IIR | 270 |
| 5 | AGM-158A JASSM | Uçak | 67.9 | 0.68 | 3 | IIR | 370 |

## TGT-C2B-02 - Underground Command and Control Bunker - kalın betonarme tavan ve toprak örtü

`Point/Hard/Fixed` · `Hardened_Structure` · sertlik 100 psi (Varsayim) · delme 3 m · gerekli yarıçap 12 m · Fixed · pasif savunma High · RCS 50 m² · termal Low · TST False · mekanizma Penetration · CDE Medium

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 9 uygun / 206 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | GBU-57A/B MOP | Uçak | 68.7 | 0.75 | 2 | INS/GPS | - |
| 2 | GBU-28 | Uçak | 67.9 | 0.68 | 3 | SAL | 9 |
| 3 | GBU-24 Paveway III | Uçak | 36.5 | 0.37 | 6 | SAL | 18.5 |
| 4 | GBU-31(V)3/B JDAM | Uçak | 33.1 | 0.33 | 6 | INS/GPS | 28 |
| 5 | Taurus KEPD 350 | Uçak | 26.2 | 0.26 | 8 | IIR | 500 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 5 uygun / 223 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Taurus KEPD 350 | Uçak | 26.2 | 0.26 | 8 | IIR | 500 |
| 2 | Storm Shadow (SCALP-EG) | Uçak | 13.4 | 0.13 | 16 | IIR | 560 |
| 3 | SOM-B2 | Uçak | 6.5 | 0.06 | 35 | IIR | 250 |
| 4 | AGM-154C JSOW | Uçak | 6.3 | 0.08 | 29 | IIR | 130 |
| 5 | AGM-84H SLAM-ER | Uçak | 5.2 | 0.05 | 43 | IIR | 270 |

## TGT-DUF-03 - Deeply Buried Facility - tünel/dağ içi, çok katmanlı koruma

`Point/Hard/Fixed` · `Hardened_Structure` · sertlik 300 psi (Varsayim) · delme 5 m · gerekli yarıçap 15 m · Fixed · pasif savunma Extreme · RCS 10 m² · termal Low · TST False · mekanizma Penetration · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 2 uygun / 213 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | GBU-57A/B MOP | Uçak | 69.1 | 0.69 | 2 | INS/GPS | - |
| 2 | GBU-28 | Uçak | 26.9 | 0.27 | 8 | SAL | 9 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 0 uygun / 228 elenen / 8 verisi yetersiz

_Bu koşullarda envanterde uygun mühimmat yok._

## TGT-PBX-04 - Concrete Pillbox - mazgallı betonarme ateş mevzii

`Point/Hard/Fixed` · `Hardened_Structure` · sertlik 30 psi (Turetilmis) · delme 0.6 m · gerekli yarıçap 3 m · Fixed · pasif savunma Medium · RCS 5 m² · termal Low · TST False · mekanizma Penetration · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 33 uygun / 182 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | AGM-65E Maverick | Uçak | 65.8 | 0.76 | 2 | SAL | 22 |
| 2 | AGM-65G Maverick | Uçak | 65.8 | 0.76 | 2 | IIR | 27 |
| 3 | AGM-154C JSOW | Uçak | 63.6 | 0.80 | 2 | IIR | 130 |
| 4 | SOM-B2 | Uçak | 63.4 | 0.80 | 2 | IIR | 250 |
| 5 | Kh-69 | Uçak | 56.2 | 0.76 | 2 | EO | 290 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 10 uygun / 218 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | SOM-B2 | Uçak | 63.4 | 0.80 | 2 | IIR | 250 |
| 2 | Kh-69 | Uçak | 56.2 | 0.76 | 2 | EO | 290 |
| 3 | Kh-59MK2 | Uçak | 55.7 | 0.76 | 2 | EO | 290 |
| 4 | AGM-84H SLAM-ER | Uçak | 54.1 | 0.76 | 2 | IIR | 270 |
| 5 | Storm Shadow (SCALP-EG) | Uçak | 53.7 | 0.80 | 2 | IIR | 560 |

## TGT-IGL-05 - Earth-Covered Ammunition Magazine (igloo) - betonarme, toprak örtülü

`Point/Hard/Fixed` · `Hardened_Structure` · sertlik 44 psi (Turetilmis) · delme 0.5 m · gerekli yarıçap 8 m · Fixed · pasif savunma Medium · RCS 100 m² · termal Low · TST False · mekanizma Penetration · CDE Medium

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 17 uygun / 198 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | AGM-154C JSOW | Uçak | 80.4 | 0.80 | 2 | IIR | 130 |
| 2 | SOM-B2 | Uçak | 80.4 | 0.80 | 2 | IIR | 250 |
| 3 | Storm Shadow (SCALP-EG) | Uçak | 80.4 | 0.80 | 2 | IIR | 560 |
| 4 | Taurus KEPD 350 | Uçak | 80.4 | 0.80 | 2 | IIR | 500 |
| 5 | AGM-65E Maverick | Uçak | 76.2 | 0.76 | 2 | SAL | 22 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 10 uygun / 218 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | SOM-B2 | Uçak | 80.4 | 0.80 | 2 | IIR | 250 |
| 2 | Storm Shadow (SCALP-EG) | Uçak | 80.4 | 0.80 | 2 | IIR | 560 |
| 3 | Taurus KEPD 350 | Uçak | 80.4 | 0.80 | 2 | IIR | 500 |
| 4 | AGM-84H SLAM-ER | Uçak | 76.2 | 0.76 | 2 | IIR | 270 |
| 5 | Kh-59MK2 | Uçak | 76.2 | 0.76 | 2 | EO | 290 |

## TGT-HQB-06 - Reinforced Concrete Headquarters Building - yerüstü, çok katlı

`Point/Hard/Fixed` · `Soft_Structure` · sertlik 10 psi (Turetilmis) · delme 0.3 m · gerekli yarıçap 15 m · Fixed · pasif savunma Low · RCS 2000 m² · termal Medium · TST False · mekanizma Blast · CDE High

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 105 uygun / 110 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | GBU-16 Paveway II | Uçak | 82.8 | 0.83 | 2 | SAL | 14.8 |
| 2 | KAB-500Kr | Uçak | 82.8 | 0.83 | 2 | EO | 17 |
| 3 | KAB-500L | Uçak | 82.8 | 0.83 | 2 | SAL | 9 |
| 4 | Ra'ad (Hatf-VIII) | Uçak | 82.8 | 0.83 | 2 | EO | 350 |
| 5 | Popeye (AGM-142 Have Nap) | Uçak | 82.8 | 0.83 | 2 | IIR | 78 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 42 uygun / 186 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Ra'ad (Hatf-VIII) | Uçak | 82.8 | 0.83 | 2 | EO | 350 |
| 2 | Kh-555 | Uçak | 82.8 | 0.83 | 2 | EO | 2500 |
| 3 | Kh-101 | Uçak | 82.8 | 0.83 | 2 | EO | 2800 |
| 4 | Kh-47M2 Kinzhal | Uçak | 78.9 | 0.79 | 2 | INS/GPS | 2000 |
| 5 | KD-63 | Uçak | 77.3 | 0.83 | 2 | EO | 200 |

## TGT-RWY-07 - Runway Segment - beton kaplama, kraterleme hedefi

`Area/Hard/Fixed` · `Infrastructure` · sertlik 29 psi (Varsayim) · delme 0.4 m · gerekli yarıçap 6 m · Fixed · pasif savunma Medium · RCS 1000 m² · termal Low · TST False · mekanizma Crater · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 86 uygun / 129 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | GBU-28 | Uçak | 53.3 | 0.76 | 2 | SAL | 9 |
| 2 | GBU-10 Paveway II | Uçak | 50.8 | 0.51 | 4 | SAL | 14.8 |
| 3 | Spice 2000 | Uçak | 50.8 | 0.51 | 4 | IIR | 60 |
| 4 | AGM-130 | Uçak | 50.8 | 0.51 | 4 | IIR | 64 |
| 5 | KAB-1500L | Uçak | 50.8 | 0.51 | 4 | SAL | 20 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 39 uygun / 189 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Ra'ad (Hatf-VIII) | Uçak | 40.3 | 0.40 | 5 | EO | 350 |
| 2 | KD-63 | Uçak | 40.3 | 0.43 | 5 | EO | 200 |
| 3 | Kh-555 | Uçak | 37.8 | 0.38 | 5 | EO | 2500 |
| 4 | Kh-101 | Uçak | 37.2 | 0.37 | 5 | EO | 2800 |
| 5 | Taurus KEPD 350 | Uçak | 32.9 | 0.33 | 6 | IIR | 500 |

## TGT-BRG-08 - Highway Bridge - betonarme/çelik açıklık ve ayak

`Point/Hard/Fixed` · `Infrastructure` · sertlik 30 psi (Varsayim) · delme 0.5 m · gerekli yarıçap 10 m · Fixed · pasif savunma Low · RCS 3000 m² · termal Low · TST False · mekanizma Blast · CDE Medium

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 91 uygun / 124 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | GBU-24 Paveway III | Uçak | 58.0 | 0.83 | 2 | SAL | 18.5 |
| 2 | GBU-28 | Uçak | 58.0 | 0.83 | 2 | SAL | 9 |
| 3 | AGM-158A JASSM | Uçak | 57.1 | 0.57 | 3 | IIR | 370 |
| 4 | AGM-158B JASSM-ER | Uçak | 57.1 | 0.57 | 3 | IIR | 926 |
| 5 | Taurus KEPD 350 | Uçak | 55.4 | 0.55 | 3 | IIR | 500 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 41 uygun / 187 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | AGM-158A JASSM | Uçak | 57.1 | 0.57 | 3 | IIR | 370 |
| 2 | AGM-158B JASSM-ER | Uçak | 57.1 | 0.57 | 3 | IIR | 926 |
| 3 | Taurus KEPD 350 | Uçak | 55.4 | 0.55 | 3 | IIR | 500 |
| 4 | Ra'ad (Hatf-VIII) | Uçak | 55.2 | 0.55 | 3 | EO | 350 |
| 5 | Storm Shadow (SCALP-EG) | Uçak | 53.0 | 0.53 | 4 | IIR | 560 |

## TGT-POL-09 - POL Storage Facility - yerüstü akaryakıt tankları

`Area/Soft/Fixed` · `Soft_Structure` · sertlik 6 psi (Turetilmis) · delme 0 m · gerekli yarıçap 35 m · Fixed · pasif savunma Low · RCS 2000 m² · termal Medium · TST False · mekanizma Blast · CDE Medium

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 98 uygun / 117 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | FAB-3000 UMPK | Uçak | 82.8 | 0.83 | 2 | INS/GPS | - |
| 2 | FAB-1500 UMPK | Uçak | 68.5 | 0.69 | 2 | INS/GPS | 60 |
| 3 | KAB-1500L | Uçak | 54.5 | 0.55 | 3 | SAL | 20 |
| 4 | GBU-31(V)1/B JDAM | Uçak | 48.6 | 0.49 | 4 | INS/GPS | 28 |
| 5 | GBU-10 Paveway II | Uçak | 48.6 | 0.49 | 4 | SAL | 14.8 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 38 uygun / 190 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Kh-47M2 Kinzhal | Uçak | 31.4 | 0.31 | 7 | INS/GPS | 2000 |
| 2 | KD-63 | Uçak | 30.1 | 0.32 | 6 | EO | 200 |
| 3 | Ra'ad (Hatf-VIII) | Uçak | 30.0 | 0.30 | 7 | EO | 350 |
| 4 | Kh-555 | Uçak | 28.2 | 0.28 | 7 | EO | 2500 |
| 5 | YJ-12 | Uçak | 28.1 | 0.40 | 5 | INS/GPS | 400 |

## TGT-AMD-10 - Open Ammunition Storage Area - açık istif, toprak set

`Area/Soft/Fixed` · `Soft_Structure` · sertlik 5 psi (Turetilmis) · delme 0 m · gerekli yarıçap 40 m · Fixed · pasif savunma Low · RCS 200 m² · termal Low · TST False · mekanizma Blast · CDE Medium

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 98 uygun / 117 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | FAB-3000 UMPK | Uçak | 82.8 | 0.83 | 2 | INS/GPS | - |
| 2 | FAB-1500 UMPK | Uçak | 63.3 | 0.63 | 3 | INS/GPS | 60 |
| 3 | KAB-1500L | Uçak | 50.4 | 0.50 | 4 | SAL | 20 |
| 4 | GBU-57A/B MOP | Uçak | 48.3 | 0.69 | 2 | INS/GPS | - |
| 5 | GBU-31(V)1/B JDAM | Uçak | 44.9 | 0.45 | 4 | INS/GPS | 28 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 38 uygun / 190 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Kh-47M2 Kinzhal | Uçak | 29.0 | 0.29 | 7 | INS/GPS | 2000 |
| 2 | Ra'ad (Hatf-VIII) | Uçak | 27.8 | 0.28 | 8 | EO | 350 |
| 3 | KD-63 | Uçak | 27.8 | 0.30 | 7 | EO | 200 |
| 4 | Kh-555 | Uçak | 26.1 | 0.26 | 8 | EO | 2500 |
| 5 | YJ-12 | Uçak | 26.0 | 0.37 | 5 | INS/GPS | 400 |

## TGT-CMN-11 - Communications Node - anten direkleri ve ekipman barınağı

`Point/Soft/Fixed` · `Soft_Structure` · sertlik 3 psi (Varsayim) · delme 0 m · gerekli yarıçap 10 m · Fixed · pasif savunma Low · RCS 150 m² · termal Medium · TST False · mekanizma Fragment · CDE Medium

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 157 uygun / 58 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | MAM-L (Termobarik) | SİHA | 87.4 | 0.87 | 2 | SAL | 15 |
| 2 | AGM-114N Hellfire | Helikopter+SİHA | 87.4 | 0.87 | 2 | SAL | 8 |
| 3 | Kemankeş-2 | SİHA | 82.8 | 0.83 | 2 | EO | 200 |
| 4 | GBU-53/B StormBreaker (SDB II) | Uçak | 82.8 | 0.83 | 2 | MMW | 110 |
| 5 | MAM-T | SİHA | 82.8 | 0.83 | 2 | SAL | 30 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 46 uygun / 182 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Delilah | Uçak | 82.8 | 0.83 | 2 | IIR | 250 |
| 2 | Ice Breaker | Uçak | 82.1 | 0.83 | 2 | IIR | 300 |
| 3 | SOM-B1 | Uçak | 77.8 | 0.83 | 2 | IIR | 250 |
| 4 | SOM-A | Uçak | 77.7 | 0.83 | 2 | INS/GPS | 250 |
| 5 | Kemankeş-2 | SİHA | 77.3 | 0.83 | 2 | EO | 200 |

## TGT-EWR-12 - Early Warning Radar - sabit mevzi, büyük anten

`Point/Soft/Fixed` · `Radar/Air_Defense` · sertlik 3 psi (Varsayim) · delme 0 m · gerekli yarıçap 12 m · Fixed · pasif savunma Low · RCS 300 m² · termal Medium · TST False · mekanizma Fragment · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 165 uygun / 50 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | MAM-L | SİHA | 87.4 | 0.87 | 2 | SAL | 15 |
| 2 | MAM-L IIR | SİHA | 87.4 | 0.87 | 2 | IIR | 25 |
| 3 | GBU-69/B SGM | Uçak+SİHA | 87.4 | 0.87 | 2 | SAL | - |
| 4 | Kemankeş-2 | SİHA | 87.4 | 0.87 | 2 | EO | 200 |
| 5 | GBU-53/B StormBreaker (SDB II) | Uçak | 87.4 | 0.87 | 2 | MMW | 110 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 50 uygun / 178 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Delilah | Uçak | 87.4 | 0.87 | 2 | IIR | 250 |
| 2 | Kh-31PD | Uçak | 85.1 | 0.87 | 2 | Passive_RF | 250 |
| 3 | Ice Breaker | Uçak | 83.1 | 0.87 | 2 | IIR | 300 |
| 4 | Kh-58UShKE | Uçak | 82.4 | 0.87 | 2 | Passive_RF | 245 |
| 5 | Kemankeş-2 | SİHA | 81.6 | 0.87 | 2 | EO | 200 |

## TGT-SAM-13 - Mobile SAM Battery - angajman radarı ve TELAR'lar, sık yer değiştirir

`Area/Soft/Relocatable` · `Radar/Air_Defense` · sertlik 5 psi (Turetilmis) · delme 0 m · gerekli yarıçap 15 m · Slow · pasif savunma High · RCS 40 m² · termal Medium · TST True · mekanizma Fragment · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 123 uygun / 92 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Paveway IV | Uçak | 64.5 | 0.65 | 3 | SAL | 33 |
| 2 | GBU-54 Laser JDAM | Uçak | 64.5 | 0.65 | 3 | SAL | 28 |
| 3 | Teber-82 | Uçak+SİHA | 64.5 | 0.65 | 3 | SAL | - |
| 4 | GBU-12 Paveway II | Uçak+SİHA | 64.5 | 0.65 | 3 | SAL | 14.8 |
| 5 | AASM Hammer SBU-64 | Uçak | 64.5 | 0.65 | 3 | SAL | 70 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 50 uygun / 178 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | SOM-B1 | Uçak | 59.3 | 0.59 | 3 | IIR | 250 |
| 2 | KD-63 | Uçak | 56.9 | 0.61 | 3 | EO | 200 |
| 3 | KD-88 | Uçak | 54.8 | 0.61 | 3 | EO | 180 |
| 4 | SOM-J | Uçak | 47.1 | 0.47 | 4 | IIR | 275 |
| 5 | AGM-88E AARGM | Uçak | 45.7 | 0.54 | 3 | MMW | 150 |

## TGT-SHD-14 - Self-Propelled SHORAD Vehicle - hafif zırhlı, birliklerle hareketli

`Point/Hard/Mobile` · `Radar/Air_Defense` · sertlik 10 psi (Varsayim) · delme 0 m · gerekli yarıçap 4 m · Fast · pasif savunma Medium · RCS 12 m² · termal High · TST True · mekanizma Fragment · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 104 uygun / 111 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | AGM-114L Longbow Hellfire | Helikopter | 57.5 | 0.57 | 3 | MMW | 8 |
| 2 | AGM-179 JAGM | Helikopter | 57.5 | 0.57 | 3 | MMW | 16 |
| 3 | Brimstone | Uçak | 57.2 | 0.57 | 3 | MMW | 20 |
| 4 | Brimstone 2 | Uçak+SİHA | 57.2 | 0.57 | 3 | MMW | 60 |
| 5 | MAM-C | SİHA | 56.3 | 0.56 | 3 | SAL | 8 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 34 uygun / 194 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Delilah | Uçak | 48.8 | 0.60 | 3 | IIR | 250 |
| 2 | ALTIUS-600 | Helikopter+SİHA | 46.5 | 0.47 | 4 | EO | 440 |
| 3 | AGM-88E AARGM | Uçak | 39.2 | 0.68 | 3 | MMW | 150 |
| 4 | SPEAR 3 | Uçak | 38.3 | 0.58 | 3 | MMW | 140 |
| 5 | SOM-B1 | Uçak | 36.2 | 0.60 | 3 | IIR | 250 |

## TGT-TEL-15 - Ballistic Missile TEL - gizlenmiş atış mevzii, kısa sürede yer değiştirir

`Point/Soft/Relocatable` · `Soft_Vehicle` · sertlik 5 psi (Turetilmis) · delme 0 m · gerekli yarıçap 6 m · Slow · pasif savunma High · RCS 25 m² · termal Medium · TST True · mekanizma Fragment · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 139 uygun / 76 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | GBU-53/B StormBreaker (SDB II) | Uçak | 67.8 | 0.68 | 3 | MMW | 110 |
| 2 | MAM-L | SİHA | 64.5 | 0.64 | 3 | SAL | 15 |
| 3 | GBU-69/B SGM | Uçak+SİHA | 64.5 | 0.64 | 3 | SAL | - |
| 4 | MAM-T | SİHA | 64.5 | 0.65 | 3 | SAL | 30 |
| 5 | Bozok | SİHA | 64.4 | 0.64 | 3 | SAL | 15 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 46 uygun / 182 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Delilah | Uçak | 60.7 | 0.61 | 3 | EO | 250 |
| 2 | SOM-B1 | Uçak | 50.9 | 0.59 | 3 | IIR | 250 |
| 3 | KD-88 | Uçak | 49.4 | 0.61 | 3 | EO | 180 |
| 4 | SOM-J | Uçak | 48.6 | 0.50 | 4 | IIR | 275 |
| 5 | Kemankeş-2 | SİHA | 48.3 | 0.52 | 4 | EO | 200 |

## TGT-MBT-16 - Main Battle Tank - tekil, arazide hareket hâlinde

`Point/Hard/Mobile` · `Armored_Vehicle` · sertlik 40 psi (Varsayim) · delme 0 m · gerekli yarıçap 3.5 m · Slow · pasif savunma Medium · RCS 15 m² · termal High · TST False · mekanizma Direct_Hit · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 92 uygun / 123 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Brimstone | Uçak | 60.4 | 0.60 | 3 | MMW | 20 |
| 2 | AGM-114L Longbow Hellfire | Helikopter | 60.4 | 0.60 | 3 | MMW | 8 |
| 3 | Brimstone 2 | Uçak+SİHA | 60.4 | 0.60 | 3 | MMW | 60 |
| 4 | AGM-179 JAGM | Helikopter | 60.4 | 0.60 | 3 | MMW | 16 |
| 5 | 9K121 Vikhr | Uçak+Helikopter | 57.2 | 0.57 | 3 | Laser_Beam_Riding | 10 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 30 uygun / 198 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | AGM-84H SLAM-ER | Uçak | 40.8 | 0.41 | 5 | IIR | 270 |
| 2 | SOM-B1 | Uçak | 40.5 | 0.40 | 5 | IIR | 250 |
| 3 | KD-88 | Uçak | 35.2 | 0.39 | 5 | IIR | 180 |
| 4 | KD-63 | Uçak | 33.9 | 0.36 | 6 | EO | 200 |
| 5 | SOM-B2 | Uçak | 33.7 | 0.34 | 6 | IIR | 250 |

## TGT-AFV-17 - Wheeled Armoured Fighting Vehicle - yüksek hızla manevra

`Point/Hard/Mobile` · `Armored_Vehicle` · sertlik 15 psi (Varsayim) · delme 0 m · gerekli yarıçap 3 m · Fast · pasif savunma Low · RCS 10 m² · termal High · TST True · mekanizma Direct_Hit · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 89 uygun / 126 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Brimstone | Uçak | 71.4 | 0.71 | 2 | MMW | 20 |
| 2 | AGM-114L Longbow Hellfire | Helikopter | 71.4 | 0.71 | 2 | MMW | 8 |
| 3 | Brimstone 2 | Uçak+SİHA | 71.4 | 0.71 | 2 | MMW | 60 |
| 4 | AGM-179 JAGM | Helikopter | 71.4 | 0.71 | 2 | MMW | 16 |
| 5 | Spike ER2 | Helikopter | 59.5 | 0.60 | 3 | IIR | 16 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 27 uygun / 201 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | SOM-B2 | Uçak | 41.4 | 0.41 | 5 | IIR | 250 |
| 2 | AGM-84H SLAM-ER | Uçak | 40.1 | 0.40 | 5 | IIR | 270 |
| 3 | SOM-J | Uçak | 38.7 | 0.39 | 5 | IIR | 275 |
| 4 | SOM-B1 | Uçak | 37.8 | 0.38 | 5 | IIR | 250 |
| 5 | KD-88 | Uçak | 33.7 | 0.37 | 5 | IIR | 180 |

## TGT-ART-18 - Self-Propelled Artillery Battery - ateş mevziinde 6 araç, dağınık

`Area/Hard/Relocatable` · `Armored_Vehicle` · sertlik 30 psi (Varsayim) · delme 0 m · gerekli yarıçap 70 m · Fixed · pasif savunma Medium · RCS 40 m² · termal High · TST True · mekanizma Direct_Hit · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 3 uygun / 212 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | CBU-105 SFW (WCMD) | Uçak | 53.7 | 0.54 | 3 | INS/GPS | - |
| 2 | AGM-154A JSOW | Uçak | 37.1 | 0.37 | 5 | INS/GPS | 130 |
| 3 | Mk-20 Rockeye II | Uçak | 21.7 | 0.22 | 10 | Unguided | 12 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 1 uygun / 227 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | AGM-154A JSOW | Uçak | 28.6 | 0.35 | 6 | INS/GPS | 130 |

## TGT-CPX-19 - Brigade Command Post (TOC) - komuta araçları, çadır/konteyner ve anten parkı

`Area/Soft/Relocatable` · `Soft_Vehicle` · sertlik 5 psi (Turetilmis) · delme 0 m · gerekli yarıçap 40 m · Fixed · pasif savunma High · RCS 30 m² · termal Medium · TST True · mekanizma Fragment · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 94 uygun / 121 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | FAB-3000 UMPK | Uçak | 79.1 | 0.79 | 2 | INS/GPS | - |
| 2 | CBU-105 SFW (WCMD) | Uçak | 75.0 | 0.75 | 2 | INS/GPS | - |
| 3 | AGM-154A JSOW | Uçak | 75.0 | 0.75 | 2 | INS/GPS | 130 |
| 4 | FAB-1500 UMPK | Uçak | 59.6 | 0.60 | 3 | INS/GPS | 60 |
| 5 | KAB-1500L | Uçak | 43.0 | 0.43 | 5 | SAL | 20 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 38 uygun / 190 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | AGM-154A JSOW | Uçak | 57.9 | 0.71 | 2 | INS/GPS | 130 |
| 2 | Kh-47M2 Kinzhal | Uçak | 27.3 | 0.27 | 8 | INS/GPS | 2000 |
| 3 | Ra'ad (Hatf-VIII) | Uçak | 26.1 | 0.26 | 8 | INS/GPS | 350 |
| 4 | Kh-555 | Uçak | 24.6 | 0.25 | 9 | INS/GPS | 2500 |
| 5 | YJ-12 | Uçak | 24.5 | 0.35 | 6 | INS/GPS | 400 |

## TGT-CNV-20 - Logistics Convoy - tekerlekli araçlar, yolda seyir hâlinde

`Area/Soft/Mobile` · `Soft_Vehicle` · sertlik 5 psi (Kaynakli) · delme 0 m · gerekli yarıçap 25 m · Fast · pasif savunma Low · RCS 20 m² · termal Medium · TST True · mekanizma Fragment · CDE Medium

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 73 uygun / 142 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Paveway IV | Uçak | 61.2 | 0.61 | 3 | SAL | 33 |
| 2 | GBU-54 Laser JDAM | Uçak | 61.2 | 0.61 | 3 | SAL | 28 |
| 3 | Teber-82 | Uçak+SİHA | 61.2 | 0.61 | 3 | SAL | - |
| 4 | GBU-12 Paveway II | Uçak+SİHA | 61.2 | 0.61 | 3 | SAL | 14.8 |
| 5 | AASM Hammer SBU-64 | Uçak | 61.2 | 0.61 | 3 | SAL | 70 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 28 uygun / 200 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | SOM-B1 | Uçak | 60.3 | 0.60 | 3 | IIR | 250 |
| 2 | KD-88 | Uçak | 54.3 | 0.60 | 3 | IIR | 180 |
| 3 | KD-63 | Uçak | 48.9 | 0.52 | 4 | EO | 200 |
| 4 | AGM-84H SLAM-ER | Uçak | 44.1 | 0.44 | 4 | IIR | 270 |
| 5 | SOM-J | Uçak | 39.6 | 0.40 | 5 | IIR | 275 |

## TGT-INF-21 - Infantry in Open - toplanma bölgesinde

`Area/Soft/Relocatable` · `Personnel` · sertlik 36 psi (Turetilmis) · delme 0 m · gerekli yarıçap 40 m · Fixed · pasif savunma Low · RCS 1 m² · termal Medium · TST False · mekanizma Fragment · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 139 uygun / 76 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Paveway IV | Uçak | 87.4 | 0.87 | 2 | SAL | 33 |
| 2 | GBU-38 JDAM | Uçak | 87.4 | 0.87 | 2 | INS/GPS | 28 |
| 3 | GBU-54 Laser JDAM | Uçak | 87.4 | 0.87 | 2 | SAL | 28 |
| 4 | Teber-82 | Uçak+SİHA | 87.4 | 0.87 | 2 | SAL | - |
| 5 | GBU-12 Paveway II | Uçak+SİHA | 87.4 | 0.87 | 2 | SAL | 14.8 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 46 uygun / 182 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Ice Breaker | Uçak | 87.4 | 0.87 | 2 | IIR | 300 |
| 2 | SOM-A | Uçak | 87.4 | 0.87 | 2 | INS/GPS | 250 |
| 3 | SOM-B1 | Uçak | 87.4 | 0.87 | 2 | IIR | 250 |
| 4 | Ra'ad (Hatf-VIII) | Uçak | 87.4 | 0.87 | 2 | EO | 350 |
| 5 | Kh-555 | Uçak | 87.4 | 0.87 | 2 | EO | 2500 |

## TGT-INF-22 - Dug-In Infantry - siper ve üstü örtülü mevziler

`Area/Soft/Fixed` · `Personnel` · sertlik 65 psi (Turetilmis) · delme 0 m · gerekli yarıçap 35 m · Fixed · pasif savunma High · RCS 0.5 m² · termal Low · TST False · mekanizma Fragment · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 128 uygun / 87 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | CBU-105 SFW (WCMD) | Uçak | 79.1 | 0.79 | 2 | INS/GPS | - |
| 2 | Spice 1000 | Uçak | 79.1 | 0.79 | 2 | INS/GPS | 100 |
| 3 | GBU-32 JDAM | Uçak | 79.1 | 0.79 | 2 | INS/GPS | 28 |
| 4 | AGM-154A JSOW | Uçak | 79.1 | 0.79 | 2 | INS/GPS | 130 |
| 5 | KAB-500S-E | Uçak | 79.1 | 0.79 | 2 | INS/GPS | 9 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 44 uygun / 184 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Ra'ad (Hatf-VIII) | Uçak | 79.1 | 0.79 | 2 | INS/GPS | 350 |
| 2 | Kh-555 | Uçak | 79.1 | 0.79 | 2 | INS/GPS | 2500 |
| 3 | Kh-101 | Uçak | 79.1 | 0.79 | 2 | INS/GPS | 2800 |
| 4 | Kh-47M2 Kinzhal | Uçak | 79.1 | 0.79 | 2 | INS/GPS | 2000 |
| 5 | SOM-A | Uçak | 70.7 | 0.71 | 2 | INS/GPS | 250 |

## TGT-FRG-23 - Frigate (~4000 t) - seyir hâlinde

`Point/Hard/Mobile` · `Naval` · sertlik 12 psi (Turetilmis) · delme 0 m · gerekli yarıçap 18 m · Slow · pasif savunma Medium · RCS 5000 m² · termal High · TST False · mekanizma Penetration · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 93 uygun / 122 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Kh-59MK | Uçak | 61.5 | 0.62 | 3 | ARH | 285 |
| 2 | BrahMos-A | Uçak | 58.9 | 0.59 | 3 | ARH | 450 |
| 3 | AGM-158C LRASM | Uçak | 56.8 | 0.57 | 3 | IIR | 560 |
| 4 | AGM-84H SLAM-ER | Uçak | 48.9 | 0.49 | 4 | IIR | 270 |
| 5 | Kh-22 | Uçak | 48.2 | 0.48 | 4 | ARH | 600 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 43 uygun / 185 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Kh-59MK | Uçak | 61.5 | 0.62 | 3 | ARH | 285 |
| 2 | BrahMos-A | Uçak | 58.9 | 0.59 | 3 | ARH | 450 |
| 3 | AGM-158C LRASM | Uçak | 56.8 | 0.57 | 3 | IIR | 560 |
| 4 | AGM-84H SLAM-ER | Uçak | 48.9 | 0.49 | 4 | IIR | 270 |
| 5 | Kh-22 | Uçak | 48.2 | 0.48 | 4 | ARH | 600 |

## TGT-FAC-24 - Fast Attack Craft (~400 t) - yüksek süratle manevra

`Point/Soft/Mobile` · `Naval` · sertlik 10 psi (Varsayim) · delme 0 m · gerekli yarıçap 8 m · Fast · pasif savunma Low · RCS 300 m² · termal High · TST True · mekanizma Penetration · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 85 uygun / 130 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Kh-35U | Uçak+Helikopter | 71.9 | 0.72 | 2 | ARH | 260 |
| 2 | Kh-31AD | Uçak | 71.7 | 0.72 | 2 | ARH | 160 |
| 3 | Kh-31A | Uçak | 71.5 | 0.72 | 2 | ARH | 70 |
| 4 | C-802AK | Uçak | 71.4 | 0.72 | 2 | ARH | 180 |
| 5 | Exocet AM39 | Uçak | 71.4 | 0.72 | 2 | ARH | 70 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 34 uygun / 194 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Kh-35U | Uçak+Helikopter | 71.9 | 0.72 | 2 | ARH | 260 |
| 2 | CM-400AKG | Uçak | 70.1 | 0.72 | 2 | ARH | 240 |
| 3 | AGM-84D Harpoon Block 1C | Uçak | 67.1 | 0.72 | 2 | ARH | 220 |
| 4 | AGM-84L Harpoon Block II | Uçak | 67.1 | 0.72 | 2 | ARH | 220 |
| 5 | AGM-84N Harpoon Block II+ | Uçak | 67.1 | 0.72 | 2 | ARH | 220 |

## TGT-PRS-25 - Pier-Side Logistics Ship - rıhtımda bağlı

`Point/Soft/Fixed` · `Naval` · sertlik 10 psi (Varsayim) · delme 0 m · gerekli yarıçap 22 m · Fixed · pasif savunma Low · RCS 8000 m² · termal Medium · TST False · mekanizma Penetration · CDE Medium

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 117 uygun / 98 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Taurus KEPD 350 | Uçak | 75.0 | 0.75 | 2 | IIR | 500 |
| 2 | Kh-59MK | Uçak | 73.6 | 0.74 | 2 | ARH | 285 |
| 3 | AGM-158A JASSM | Uçak | 71.8 | 0.72 | 2 | IIR | 370 |
| 4 | AGM-158B JASSM-ER | Uçak | 71.8 | 0.72 | 2 | IIR | 926 |
| 5 | AGM-158C LRASM | Uçak | 71.8 | 0.72 | 2 | IIR | 560 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 48 uygun / 180 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | Taurus KEPD 350 | Uçak | 75.0 | 0.75 | 2 | IIR | 500 |
| 2 | Kh-59MK | Uçak | 73.6 | 0.74 | 2 | ARH | 285 |
| 3 | AGM-158A JASSM | Uçak | 71.8 | 0.72 | 2 | IIR | 370 |
| 4 | AGM-158B JASSM-ER | Uçak | 71.8 | 0.72 | 2 | IIR | 926 |
| 5 | AGM-158C LRASM | Uçak | 71.8 | 0.72 | 2 | IIR | 560 |

## TGT-ACP-26 - Parked Aircraft on Open Apron - açık park sahasında uçaklar

`Area/Soft/Relocatable` · `Soft_Vehicle` · sertlik 3 psi (Turetilmis) · delme 0 m · gerekli yarıçap 30 m · Fixed · pasif savunma Low · RCS 20 m² · termal Low · TST False · mekanizma Fragment · CDE Low

**Hava savunma: Yok / bastırılmış** (standoff 0 km) - 135 uygun / 80 elenen / 21 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | GBU-38 JDAM | Uçak | 87.4 | 0.87 | 2 | INS/GPS | 28 |
| 2 | GBU-54 Laser JDAM | Uçak | 87.4 | 0.87 | 2 | SAL | 28 |
| 3 | Teber-82 | Uçak+SİHA | 87.4 | 0.87 | 2 | SAL | - |
| 4 | GBU-12 Paveway II | Uçak+SİHA | 87.4 | 0.87 | 2 | SAL | 14.8 |
| 5 | AASM Hammer SBU-38 | Uçak | 87.4 | 0.87 | 2 | INS/GPS | 70 |

**Hava savunma: Uzun menzilli SAM** (standoff 120 km) - 46 uygun / 182 elenen / 8 verisi yetersiz

| # | Mühimmat | Taşıyıcı | Skor | PK | Atış (P_D=0.90) | Güdüm modu | Menzil km |
|---|---|---|---|---|---|---|---|
| 1 | SOM-A | Uçak | 87.4 | 0.87 | 2 | INS/GPS | 250 |
| 2 | SOM-B1 | Uçak | 87.4 | 0.87 | 2 | IIR | 250 |
| 3 | Ra'ad (Hatf-VIII) | Uçak | 87.4 | 0.87 | 2 | EO | 350 |
| 4 | Kh-555 | Uçak | 87.4 | 0.87 | 2 | EO | 2500 |
| 5 | Kh-101 | Uçak | 87.4 | 0.87 | 2 | EO | 2800 |
