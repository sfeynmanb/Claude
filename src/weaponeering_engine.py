#!/usr/bin/env python3
"""
Weaponeering (Mühimmat-Hedef Eşleştirme) Motoru
===============================================

Kural tabanlı, şeffaf bir karar destek modeli. Mühimmat veri setini ve hedef
kırılganlık matrisini (data/targets/target_vulnerability_matrix.csv) alır;
seçilen hedef için her mühimmata 0-100 arası bir "Uygunluk Skoru" verir.

MODELİN NİTELİĞİ (önce bunu okuyun)
-----------------------------------
Bu modül JMEM/JAWS verisi İÇERMEZ ve onların yerini tutmaz. Buradaki "PK",
açık literatürdeki genel ölçekleme yasaları ile temsilî katsayılardan türetilen
bir SÖZDE-OLASILIKTIR (pseudo-PK); kalibre edilmemiş ve doğrulanmamıştır.
Hedefin aktif savunması (önleme), fünye/isabet açısı, bina iç yerleşimi, hava
aracı beka analizi ve tali hasar tahmini modellenmez. Çıktılar mühimmatları
birbirine göre SIRALAMAK ve pasif savunma önlemlerinin göreli etkisini görmek
içindir; operasyonel planlama veya hedefleme için KULLANILAMAZ.

Model özeti
-----------
    R_w   = K(hedef kategorisi) · k(harp başlığı tipi) · c(pasif koruma) · W^(1/3)
            (küp-kök patlama ölçeklemesi; W = harp başlığı kütlesi, kg)
    F_kap = min(1, (R_w / R_gerekli)^2)                    alan kapsama oranı
    P_cep = 1 - 0.5^((d / CEP)^2),  d = max(R_w, R_gerekli) dairesel normal dağılım
    P_isb = P_cep · c_hareketlilik · c_iz(RCS/termal) · c_ortam · c_gizleme
            (mühimmatın her güdüm modu için hesaplanır, en iyisi seçilir)
    D     = C · (W/A)^0.7 · (V - 30.5) · K_kütle           Young (1997) biçiminde
            sadeleştirilmiş beton delme tahmini; HEAT için n · imla çapı
    F_del = 1 (D >= gerekli) | (D/gerekli)^3 | 0 (D < gerekli/2)
    PK    = min(0.95, P_isb · F_kap · P(imha|isabet) · F_del · güvenilirlik)
    Skor  = 100 · PK · K_orantılılık · K_standoff · K_rol · K_CDE
            (K_rol: gemisavar füzenin kara hedefinde, anti-radyasyon füzesinin yayın
             yapmayan hedefte, sığınak delicinin sertleştirilmemiş hedefte kullanımı
             gibi ikincil görevlerde 0.7)

Zorunlu kurallar (eleme)
------------------------
  * Havadan havaya füzeler yüzey hedeflerine atanmaz.
  * Hardened_Structure: harp başlığı Penetrator / BROACH / Tandem_HEAT olmalı;
    diğer tiplerde PK = 0.
  * Fast_Maneuvering: terminal arayıcı (IIR, SAL, ARH, EO, MMW ...) şart;
    yalnız INS/GPS veya güdümsüz mühimmatta isabet çarpanı 0.02-0.03.
  * Hava savunma tehdidi: Maksimum_Menzil_km < gerekli standoff ise elenir.
  * Pasif RF arayıcı yalnız yayın yapan hedefe (radar/hava savunma, gemi) kilitlenir.
  * Seyir/aero-balistik füze ve süzülen bombalarda EO/IIR arayıcı sahne eşleme
    içindir: veri bağı (Data-Link) yoksa hareketli hedefe karşı koordinat modu sayılır.
  * Gemisavar füze (AShM) arayıcıları deniz hedefi içindir: kara hedefinde arayıcı
    modları 0.3 ile çarpılır; koordinat modu (varsa) sabit kara hedefinde kullanılabilir.
  * Tek atış PK'si 0.05'in altında kalan mühimmat "etkisiz" sayılır ve elenir.

Sürüm 2 - doktriner şema ve açık kaynak alt modelleri
-----------------------------------------------------
Hedef matrisi 16 sütunludur (bkz. data/targets/target_matrix_sources.md). Eklenen alt modeller
ve dayanakları:

  Patlama      Tepe gelen aşırı basınç, Kinney & Graham (1985) kapalı form bağıntısı:
               P/P0 = 808·[1+(Z/4.5)²] / √[1+(Z/0.048)²] / √[1+(Z/0.32)²] / √[1+(Z/1.35)²],
               Z = R / W^(1/3)  [m/kg^(1/3)] (Hopkinson-Cranz ölçeklemesi).
               UFC 3-340-02 aynı büyüklüğü Kingery-Bulmash eğrileriyle verir; o eğrilerin
               polinom katsayıları burada kullanılmadı (ezbere yazılmaları güvenilir olmazdı).
  TNT eşdeğeri W_TNT = W_harp · dolgu oranı · RE · Fano kılıf düzeltmesi · 1.8 (yer yüzeyi).
               Dolgu oranları ve Fano düzeltmesi [0.2 + 0.8/(1+2M/C)] YAKLAŞIKTIR ve işaretlidir.
  Delme        calculate_penetration_depth: Young (1997, SAND97-2426) beton denklemi biçimi.
  Hedefleme    Ph = CEP isabeti × hareketlilik × iz × ortam × gizleme × TST uçuş süresi çarpanı.
               AFDP 3-60 süreç ve tanım verir, denklem vermez; TST penceresi bir senaryo girdisidir.
  İmha         Pk = Ph × Pd × güvenilirlik;  Pd = kapsama × P(imha|isabet) × delme yeterliliği.
  Tali hasar   1 psi aşırı basınç yarıçapı (cam kırılması düzeyi) bir GÖSTERGEDİR; CJCSI 3160.01
               yöntemi ve CER tabloları kamuya açık olmadığından CDE'nin yerini tutmaz.

  KULLANILMAYAN: UFC 3-340-01 (dağıtımı kısıtlı), JMEM/JWS verileri (gizli).

Patlama yarıçapı yalnız birincil hasar mekanizması "Blast" olan hedeflerde etki yarıçapını belirler.
Parçacık, doğrudan isabet, delme ve krater mekanizmalı hedeflerde ampirik K katsayıları geçerlidir;
bu hedeflerde hesaplanan aşırı basınç yalnız raporlanır.

Kullanım
--------
    from weaponeering_engine import calculate_weapon_effectiveness, evaluate_jaws_match, Scenario
    df = calculate_weapon_effectiveness("TGT-HAS-01")
    df = calculate_weapon_effectiveness("TGT-SAM-13", Scenario(air_defense="LRSAM"), top_n=5)
    r = evaluate_jaws_match(target_row, munition_row, {"air_defense": "VLRSAM"})

    python3 src/weaponeering_engine.py --list-targets
    python3 src/weaponeering_engine.py TGT-HAS-01 --top 5 --air-defense LRSAM
    python3 src/weaponeering_engine.py --report outputs/weaponeering_report.md
"""

from __future__ import annotations

import argparse
import functools
import math
import os
import sys
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_target_matrix as vtm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUNITION_CANDIDATES = (
    os.path.join(ROOT, "master_air_munitions_dataset_2.csv"),
    os.path.join(ROOT, "data", "master_air_munitions_dataset_2.csv"),
    os.path.join(ROOT, "data", "processed", "master_air_munitions_dataset_2.csv"),
    os.path.join(ROOT, "data", "master_air_munitions.csv"),
    os.path.join(ROOT, "data", "processed", "master_air_munitions_dataset.csv"),
)
TARGET_MATRIX_PATH = vtm.DEFAULT_PATH

# ---------------------------------------------------------------------------
# Şema sabitleri
# ---------------------------------------------------------------------------
TARGET_COLUMNS = list(vtm.COLUMNS)
TARGET_NUMERIC = list(vtm.NUMERIC_RANGES)
MOBILITY_LEVELS = vtm.MOBILITY_CLASSES  # Fixed, Slow, Fast
PASSIVE_LEVELS = ("Low", "Medium", "High", "Extreme")
THERMAL_LEVELS = ("Low", "Medium", "High")

MUNITION_REQUIRED = [
    "Muhimmat_Adi",
    "Mensei_Ulke",
    "Ana_Kategori",
    "Alt_Kategori",
    "Toplam_Kutle_kg",
    "Harp_Basligi_Kutlesi_kg",
    "Harp_Basligi_Tipi",
    "Cap_mm",
    "Maksimum_Menzil_km",
    "Maksimum_Hiz_Mach",
    "Gudum_Sistemi_Midcourse",
    "Gudum_Sistemi_Terminal",
    "Entegre_Platformlar",
    "Veri_Guvenilirlik_Notu",
]
MUNITION_NUMERIC = ["Toplam_Kutle_kg", "Harp_Basligi_Kutlesi_kg", "Cap_mm", "Maksimum_Menzil_km", "Maksimum_Hiz_Mach"]
PREPARED_MARKERS = (
    "Harp_Basligi_Etkin_kg",
    "Harp_Basligi_Tahmini",
    "Tasiyici_Sinifi",
    "Gudum_Modlari",
    "Sahne_Eslemeli",
)

STATUS_OK = "UYGUN"
STATUS_ELIMINATED = "ELENDI"
STATUS_NO_DATA = "VERI_YETERSIZ"
STATUS_ORDER = {STATUS_OK: 0, STATUS_ELIMINATED: 1, STATUS_NO_DATA: 2}

HARDENED = "Hardened_Structure"
ARMORED = "Armored_Vehicle"
NAVAL = "Naval"
FAST = "Fast"
FIXED = "Fixed"

# ---------------------------------------------------------------------------
# MODEL PARAMETRELERİ — tümü temsilîdir; tek yerden ayarlanabilir
# ---------------------------------------------------------------------------
# (1) Ölümcül yarıçap: R = K · W^(1/3)  [m, kg]. K, HE-Frag referans harp başlığının
#     ilgili hedef sınıfını etkisiz bırakma yarıçapı katsayısıdır.
LETHAL_K = {
    "Personnel": 9.0,
    "Radar/Air_Defense": 5.5,
    "Soft_Vehicle": 5.0,
    "Soft_Structure": 4.0,
    "Naval": 2.5,
    HARDENED: 2.2,  # delme sonrası kapalı hacimde iç patlama
    "Infrastructure": 0.9,  # pist/köprü: krater veya yakın ıska
    ARMORED: 0.9,  # yakın ıska / doğrudan isabet gerekir
}
TARGET_CATEGORIES = tuple(LETHAL_K)
assert set(TARGET_CATEGORIES) == set(vtm.TARGET_CLASSES), "hedef sınıfları doğrulayıcıyla uyumsuz"

# Harp başlığı tipi × hedef kategorisi → K çarpanı ("_" = varsayılan)
WARHEAD_K_MOD = {
    "HE-Frag": {"_": 1.0},
    "Thermobaric": {"_": 1.0, "Personnel": 1.25, "Soft_Structure": 1.25, HARDENED: 1.25, NAVAL: 0.9, ARMORED: 0.9},
    "Penetrator": {"_": 0.7, HARDENED: 1.0, NAVAL: 1.1},
    "BROACH": {"_": 0.7, HARDENED: 1.0, NAVAL: 1.1},
    "SAPHE": {"_": 0.85, NAVAL: 1.2},
    "Tandem_HEAT": {"_": 0.5},
    "HEAT": {"_": 0.5},
    "Submunition": {
        "_": 1.5,
        ARMORED: 12.0,
        "Soft_Vehicle": 2.2,
        "Radar/Air_Defense": 2.0,
        "Personnel": 1.3,
        NAVAL: 0.4,
        HARDENED: 0.3,
    },
    "NA": {"_": 0.9},
}
SHAPED_CHARGE_TYPES = ("Tandem_HEAT", "HEAT")
DIRECT_HIT_RADIUS_M = 4.0  # şekilli imla zırhlı araca doğrudan isabetle etkir

# (2) P(imha | etkili isabet): harp başlığı tipi × hedef kategorisi
HARD_TARGET_WARHEADS = ("Penetrator", "BROACH", "Tandem_HEAT")
KILL_GIVEN_HIT = {
    "HE-Frag": {
        "Infrastructure": 0.60,
        "Soft_Structure": 0.90,
        "Soft_Vehicle": 0.95,
        ARMORED: 0.55,
        "Radar/Air_Defense": 0.95,
        NAVAL: 0.60,
        "Personnel": 0.95,
    },
    "Thermobaric": {
        "Infrastructure": 0.40,
        "Soft_Structure": 0.95,
        "Soft_Vehicle": 0.90,
        ARMORED: 0.45,
        "Radar/Air_Defense": 0.85,
        NAVAL: 0.45,
        "Personnel": 0.95,
    },
    "Penetrator": {
        "Infrastructure": 0.90,
        HARDENED: 0.90,
        "Soft_Structure": 0.75,
        "Soft_Vehicle": 0.70,
        ARMORED: 0.60,
        "Radar/Air_Defense": 0.70,
        NAVAL: 0.85,
        "Personnel": 0.60,
    },
    "BROACH": {
        "Infrastructure": 0.90,
        HARDENED: 0.95,
        "Soft_Structure": 0.80,
        "Soft_Vehicle": 0.70,
        ARMORED: 0.65,
        "Radar/Air_Defense": 0.70,
        NAVAL: 0.85,
        "Personnel": 0.55,
    },
    "Tandem_HEAT": {
        "Infrastructure": 0.25,
        HARDENED: 0.70,
        "Soft_Structure": 0.50,
        "Soft_Vehicle": 0.85,
        ARMORED: 0.92,
        "Radar/Air_Defense": 0.80,
        NAVAL: 0.35,
        "Personnel": 0.35,
    },
    "HEAT": {
        "Infrastructure": 0.25,
        "Soft_Structure": 0.50,
        "Soft_Vehicle": 0.85,
        ARMORED: 0.80,
        "Radar/Air_Defense": 0.80,
        NAVAL: 0.35,
        "Personnel": 0.35,
    },
    "SAPHE": {
        "Infrastructure": 0.75,
        "Soft_Structure": 0.80,
        "Soft_Vehicle": 0.80,
        ARMORED: 0.60,
        "Radar/Air_Defense": 0.80,
        NAVAL: 0.92,
        "Personnel": 0.70,
    },
    "Submunition": {
        "Infrastructure": 0.30,
        "Soft_Structure": 0.70,
        "Soft_Vehicle": 0.90,
        ARMORED: 0.75,
        "Radar/Air_Defense": 0.90,
        NAVAL: 0.30,
        "Personnel": 0.95,
    },
    "NA": {
        "Infrastructure": 0.50,
        "Soft_Structure": 0.75,
        "Soft_Vehicle": 0.80,
        ARMORED: 0.45,
        "Radar/Air_Defense": 0.80,
        NAVAL: 0.50,
        "Personnel": 0.80,
    },
}

# (3) Güdüm modları: temsilî CEP [m] (sabit hedef, açık hava)
MODE_COORD = "INS/GPS"
MODE_INERTIAL = "INS"
MODE_UNGUIDED = "Unguided"
CEP_M = {
    "SAL": 2.0,
    "IIR": 2.0,
    "EO": 3.0,
    "MMW": 1.5,
    "ARH": 5.0,
    "SARH": 5.0,
    "IR": 4.0,
    "Passive_RF": 8.0,
    "Laser_Beam_Riding": 1.5,
    "Command_Guidance": 2.5,
    MODE_COORD: 8.0,
    MODE_INERTIAL: 30.0,
    MODE_UNGUIDED: 60.0,
}
HOMING_MODES = ("SAL", "IIR", "EO", "MMW", "ARH", "SARH", "IR", "Passive_RF", "Laser_Beam_Riding", "Command_Guidance")
COORDINATE_MODES = (MODE_COORD, MODE_INERTIAL)
LASER_MODES = ("SAL", "Laser_Beam_Riding")
RADAR_MODES = ("ARH", "SARH", "MMW")
EMITTER_CATEGORIES = ("Radar/Air_Defense", NAVAL)  # pasif RF'in kilitlenebildiği sınıflar
# Önceden planlanan uzun menzilli sınıflar: EO/IIR arayıcı sabit hedefte sahne eşleme yapar;
# hareketli hedefe ancak uçuşta hedef güncellemesi (Data-Link) varsa kilitlenebilir.
SCENE_MATCHING_SUBCATEGORIES = ("ALCM", "ALBM", "HGV", "PGM_Glide")
SCENE_MATCHING_MODES = ("EO", "IIR")
ANTI_SHIP_SUBCATEGORY = "AShM"
ANTI_SHIP_LAND_FACTOR = 0.3  # gemisavar arayıcının (IIR/IR/pasif RF) kara hedefindeki etkinliği
ANTI_RADIATION_SUBCATEGORY = "ARM"
BUNKER_BUSTER_SUBCATEGORY = "Bunker_Buster"
ROLE_SECONDARY_FACTOR = 0.7  # birincil görev dışı kullanımda uygunluk skoru çarpanı

# Hareketlilik çarpanı: (Fixed, Slow_Moving, Fast_Maneuvering)
MOBILITY_FACTOR = {
    "SAL": (1.0, 0.90, 0.70),
    "IIR": (1.0, 0.90, 0.75),
    "EO": (1.0, 0.85, 0.60),
    "MMW": (1.0, 0.95, 0.85),
    "ARH": (1.0, 0.95, 0.85),
    "SARH": (1.0, 0.90, 0.75),
    "IR": (1.0, 0.90, 0.70),
    "Passive_RF": (1.0, 0.90, 0.70),
    "Laser_Beam_Riding": (1.0, 0.90, 0.70),
    "Command_Guidance": (1.0, 0.85, 0.60),
    MODE_COORD: (1.0, 0.15, 0.02),
    MODE_INERTIAL: (1.0, 0.10, 0.01),
    MODE_UNGUIDED: (1.0, 0.25, 0.03),
}

# İz (signature) çarpanları
RCS_REF_M2 = 10.0  # bu değer ve üzeri radar arayıcı için tam kontrast
RCS_SLOPE = 0.2  # dekad başına azalma
RCS_FLOOR = 0.4
LAND_CLUTTER_FACTOR = 0.3  # cm-dalga ARH/SARH arayıcının kara parazitinde etkinliği
THERMAL_IIR = {"High": 1.0, "Medium": 0.92, "Low": 0.80}
THERMAL_IR = {"High": 1.0, "Medium": 0.85, "Low": 0.60}
IIR_FIXED_FACTOR = 1.0  # sabit yapıda sahne eşleme: hedefin kendi termal izinden bağımsız
IR_LAND_FACTOR = 0.7

# Ortam çarpanları
WEATHER_LABELS = {"CLEAR": "Açık", "OBSCURED": "Kapalı (alçak bulut / sis / duman)"}
WEATHER_FACTOR = {
    "CLEAR": {},
    "OBSCURED": {
        "SAL": 0.45,
        "Laser_Beam_Riding": 0.45,
        "EO": 0.35,
        "Command_Guidance": 0.50,
        "IIR": 0.65,
        "IR": 0.60,
        "MMW": 0.95,
        MODE_UNGUIDED: 0.60,
    },
}
GNSS_JAM_CEP_FACTOR = 4.0  # GNSS karıştırmada INS/GPS modu ataletsel sürüklenmeye düşer

# (4) Pasif savunma düzeyi → iki ayrı etki
CCD_FACTOR = {"Low": 1.0, "Medium": 0.92, "High": 0.82, "Extreme": 0.70}  # gizleme/aldatma → isabet
EMCON_FACTOR = {"Low": 1.0, "Medium": 0.90, "High": 0.70, "Extreme": 0.50}  # yayın kontrolü → pasif RF
PROTECTION_FACTOR = {"Low": 1.0, "Medium": 0.80, "High": 0.60, "Extreme": 0.45}  # tahkimat/dağılma → yarıçap

# (5) Beton delme (Young 1997 biçimi, sadeleştirilmiş)
YOUNG_C = 1.3e-5  # hedef sertliği ve burun katsayısını içeren toplu sabit
YOUNG_SD_EXP = 0.7
YOUNG_V0 = 30.5  # m/s
YOUNG_LIGHT_MASS_KG = 182.0  # altındaki kütlelerde K = 0.46 · W^0.15
SOUND_SPEED = 340.3  # m/s
IMPACT_MACH_DEFAULT = 0.85
IMPACT_MACH_RANGE = (0.7, 1.5)
REF_PENETRATOR_KG = 874.0  # şekil ölçeklemesi referansı (2000 lb sınıfı delici gövde)
REF_PENETRATOR_DIA_M = 0.368
BOMB_DIAMETER_TOLERANCE = 1.25
PEN_TYPE_FACTOR = {
    "Penetrator": 1.0,
    "BROACH": 1.3,
    "SAPHE": 0.55,
    "HE-Frag": 0.35,
    "Thermobaric": 0.30,
    "Submunition": 0.05,
    "NA": 0.30,
}
JET_CALIBERS = {"Tandem_HEAT": 6.5, "HEAT": 5.0}  # beton içinde jet delme ≈ n × imla çapı
SHAPED_CHARGE_DIA_COEF = 0.085  # D[m] ≈ 0.085 · W^(1/3)
PEN_FAIL_RATIO = 0.5

# (5b) Patlama (Kinney & Graham 1985) ve TNT eşdeğeri
ATM_KPA = 101.325
PSI_TO_KPA = 6.894757
SURFACE_BURST_FACTOR = 1.8  # yer yüzeyi patlamasında yarım küre yansıma katsayısı (UFC 3-340-02 yaklaşımı)
TNT_RE_DEFAULT = 1.0  # veri setinde patlayıcı türü yok → TNT kabul edilir (temkinli)
# Harp başlığı kütlesi içindeki patlayıcı oranı. HE-Frag ve Penetrator değerleri açık kaynak bomba
# verilerinden (Mk-82/84 ≈ %38-46, BLU-109 ≈ %27); diğerleri VARSAYIMDIR.
FILL_FRACTION = {
    "HE-Frag": 0.40,
    "Thermobaric": 0.50,
    "Penetrator": 0.27,
    "BROACH": 0.25,
    "SAPHE": 0.30,
    "Tandem_HEAT": 0.45,
    "HEAT": 0.45,
    "Submunition": 0.15,
    "NA": 0.35,
}
COLLATERAL_PSI = 1.0  # tali hasar göstergesi: cam kırılması düzeyi aşırı basınç
CDE_RADIUS_LIMIT_M = {"Low": math.inf, "Medium": 200.0, "High": 75.0}  # VARSAYIM; senaryoya göre ayarlanır
CDE_FACTOR_FLOOR = 0.3
BLAST_MECHANISM = "Blast"

# (5c) Zamana duyarlı hedef (TST) ve uçuş süresi
TST_WINDOW_DEFAULT_S = 600.0  # VARSAYIM: hedefin yerinde kalma süresi; doktrin sayı vermez
TST_DATALINK_FLOOR = 0.8  # uçuşta hedef güncellemesi alan mühimmatta ceza sınırlanır
DEFAULT_ENGAGEMENT_KM = 15.0  # standoff gerekmediğinde varsayılan atış mesafesi
CRUISE_SOUND_SPEED = 300.0  # m/s, orta irtifa
DEFAULT_MACH = {
    "Solid_Rocket": 1.5,
    "Dual_Pulse_Rocket": 2.0,
    "Liquid_Rocket": 3.0,
    "Ramjet": 3.0,
    "Turbojet": 0.8,
    "Turbofan": 0.8,
    "Electric_Propeller": 0.15,
    "Free_Fall": 0.9,
    "Glide_Unpowered": 0.9,
}
AVERAGE_SPEED_RATIO = {
    "Solid_Rocket": 0.7,
    "Dual_Pulse_Rocket": 0.75,
    "Liquid_Rocket": 0.8,
    "Ramjet": 0.9,
    "Turbojet": 0.95,
    "Turbofan": 0.95,
    "Electric_Propeller": 1.0,
    "Free_Fall": 0.75,
    "Glide_Unpowered": 0.7,
}
BDA_LEVELS = ((0.70, "SEVERE"), (0.40, "MODERATE"), (0.15, "LIGHT"), (0.0, "NEGLIGIBLE"))  # VARSAYIM eşikler

# (6) Bütünleştirme
RELIABILITY = 0.92
PK_CAP = 0.95
OVERKILL_START, OVERKILL_SPAN, OVERKILL_MAX_PENALTY = 2.0, 3.0, 0.40
STANDOFF_BASE = 0.80
MAX_WEAPONS_REPORTED = 99
MIN_PF_SAMPLES = 3
EFFECTIVE_PK_THRESHOLD = 0.30  # duyarlılık analizinde "etkili" sayılma eşiği
MIN_ELIGIBLE_PK = 0.05  # altındaki mühimmat "etkisiz" kabul edilip elenir

# (7) Görev rolü ve taşıyıcı sınıfları
AIR_TO_AIR_SUBCATEGORIES = ("WVRAAM", "BVRAAM")
BOMB_CATEGORIES = ("Gudumlu_Bomba", "Gudumsuz_Bomba")
CARRIER_ORDER = ("Uçak", "Helikopter", "SİHA")
UAV_PLATFORMS = frozenset(
    {
        "TB2",
        "TB3",
        "Akıncı",
        "Aksungur",
        "Anka",
        "Anka-3",
        "Kızılelma",
        "MQ-9",
        "MQ-9B",
        "MQ-1C",
        "MQ-5B Hunter",
        "CH-3",
        "CH-4",
        "CH-5",
        "Wing Loong",
    }
)
HELICOPTER_PLATFORMS = frozenset(
    {
        "AH-1W",
        "AH-1Z",
        "AH-64",
        "AH-64D",
        "AH-64E",
        "AS565 Panther",
        "AW101",
        "AW159",
        "H145M",
        "H225M",
        "Ka-52",
        "Ka-52K",
        "Lynx",
        "MH-60R",
        "Mi-28",
        "Mi-35",
        "NH90",
        "Rooivalk",
        "SH-60B",
        "T129",
        "Tiger",
        "UH-60",
        "Z-10",
        "Z-19",
    }
)


@dataclass(frozen=True)
class AirDefenseTier:
    key: str
    label: str
    standoff_km: float


# Hava savunma kademesi → gerekli standoff (temsilî; senaryoda elle değiştirilebilir)
AIR_DEFENSE_TIERS = {
    t.key: t
    for t in (
        AirDefenseTier("NONE", "Yok / bastırılmış", 0.0),
        AirDefenseTier("SHORAD", "Kısa menzilli (MANPADS / SHORAD / top)", 10.0),
        AirDefenseTier("MRSAM", "Orta menzilli SAM", 40.0),
        AirDefenseTier("LRSAM", "Uzun menzilli SAM", 120.0),
        AirDefenseTier("VLRSAM", "Çok uzun menzilli SAM (S-400 sınıfı, beyan edilen 400 km)", 400.0),
    )
}


@dataclass(frozen=True)
class Scenario:
    """Hedef ortamı ve kullanıcı kısıtları."""

    air_defense: str = "NONE"  # AIR_DEFENSE_TIERS anahtarı
    standoff_km: float | None = None  # None → kademenin varsayılan standoff'u
    weather: str = "CLEAR"  # CLEAR | OBSCURED
    gnss_jamming: bool = False
    laser_designation: bool = True  # SAL / lazer hüzme için işaretleme imkânı
    carrier_classes: tuple[str, ...] = ()  # () → tümü; ("Uçak", "Helikopter", "SİHA") alt kümesi
    platform: str | None = None  # belirli bir platforma entegre olanlar
    desired_damage: float = 0.90  # gerekli atış sayısı için hedeflenen hasar olasılığı
    tst_window_s: float = TST_WINDOW_DEFAULT_S  # TST hedefin yerinde kalma penceresi (s)
    cde_tier: str | None = None  # None → hedef matrisindeki Collateral_Damage_Tier

    def __post_init__(self) -> None:
        if self.tst_window_s <= 0:
            raise ValueError("tst_window_s pozitif olmalı")
        if self.cde_tier is not None and self.cde_tier not in CDE_RADIUS_LIMIT_M:
            raise ValueError(f"cde_tier '{self.cde_tier}' geçersiz; seçenekler: {list(CDE_RADIUS_LIMIT_M)}")
        if self.air_defense not in AIR_DEFENSE_TIERS:
            raise ValueError(f"air_defense '{self.air_defense}' geçersiz; seçenekler: {list(AIR_DEFENSE_TIERS)}")
        if self.weather not in WEATHER_FACTOR:
            raise ValueError(f"weather '{self.weather}' geçersiz; seçenekler: {list(WEATHER_FACTOR)}")
        if self.standoff_km is not None and self.standoff_km < 0:
            raise ValueError("standoff_km negatif olamaz")
        if not 0.0 < self.desired_damage < 1.0:
            raise ValueError("desired_damage (0, 1) aralığında olmalı")
        classes = tuple(self.carrier_classes or ())
        bad = [c for c in classes if c not in CARRIER_ORDER]
        if bad:
            raise ValueError(f"carrier_classes geçersiz: {bad}; seçenekler: {list(CARRIER_ORDER)}")
        object.__setattr__(self, "carrier_classes", classes)

    @property
    def required_standoff_km(self) -> float:
        if self.standoff_km is not None:
            return float(self.standoff_km)
        return AIR_DEFENSE_TIERS[self.air_defense].standoff_km


# ---------------------------------------------------------------------------
# Veri yükleme ve doğrulama
# ---------------------------------------------------------------------------
def _read_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    if df.shape[1] == 1:
        df = pd.read_csv(path, sep=",", dtype=str, keep_default_na=False, encoding="utf-8")
    return df.apply(lambda s: s.str.strip())


def load_munitions(path: str | None = None) -> tuple[pd.DataFrame, str]:
    """Mühimmat veri setini okur. (ham DataFrame, kullanılan yol) döndürür."""
    candidates = (path,) if path else MUNITION_CANDIDATES
    for cand in candidates:
        if cand and os.path.exists(cand):
            return _read_csv(cand), cand
    raise FileNotFoundError("Mühimmat veri seti bulunamadı. Denenen yollar:\n  " + "\n  ".join(map(str, candidates)))


def carrier_classes(platforms: str) -> tuple[str, ...]:
    """'F-16,Akıncı,T129' → ('Uçak', 'Helikopter', 'SİHA')."""
    found = set()
    for tok in str(platforms).split(","):
        tok = tok.strip()
        if not tok or tok == "NA":
            continue
        if tok in UAV_PLATFORMS:
            found.add("SİHA")
        elif tok in HELICOPTER_PLATFORMS:
            found.add("Helikopter")
        else:
            found.add("Uçak")
    return tuple(c for c in CARRIER_ORDER if c in found)


def guidance_modes(terminal: str, midcourse: str) -> tuple[str, ...]:
    """Mühimmatın kullanabileceği güdüm modları: terminal arayıcılar + (varsa) koordinat modu."""
    modes: list[str] = []
    for tok in str(terminal).split("+"):
        tok = tok.strip()
        if tok == "INS/GPS_Only":
            tok = MODE_COORD
        if tok in CEP_M and tok not in modes:
            modes.append(tok)
    mid = {t.strip() for t in str(midcourse).split("/")}
    if "GPS" in mid and MODE_COORD not in modes and MODE_UNGUIDED not in modes:
        modes.append(MODE_COORD)
    if not modes and "INS" in mid:
        modes.append(MODE_INERTIAL)
    return tuple(modes)


def prepare_munitions(df: pd.DataFrame) -> pd.DataFrame:
    """Sayısal dönüşüm + türetilmiş sütunlar. İdempotenttir (hazır veri aynen döner).

    Eklenen sütunlar
      Harp_Basligi_Etkin_kg : bilinen harp başlığı kütlesi; yoksa toplam kütle × alt kategori
                              medyan harp başlığı oranı ile TAHMİN
      Harp_Basligi_Tahmini  : yukarıdaki tahmin kullanıldıysa True
      Tasiyici_Sinifi       : 'Uçak', 'Helikopter', 'SİHA' birleşimleri ('+' ile)
      Gudum_Modlari         : değerlendirilecek güdüm modları ('|' ile)
      Sahne_Eslemeli        : EO/IIR arayıcısı yalnız sabit hedefte kullanılabilen (veri bağsız
                              seyir/aero-balistik füze, süzülen bomba) mühimmat için True
    """
    if all(c in df.columns for c in PREPARED_MARKERS):
        return df
    missing = [c for c in MUNITION_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Mühimmat veri setinde eksik sütun(lar): {missing}")
    out = df.copy()
    for col in MUNITION_NUMERIC:
        if not pd.api.types.is_numeric_dtype(out[col]):
            out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.drop_duplicates(subset="Muhimmat_Adi").reset_index(drop=True)

    warhead, total = out["Harp_Basligi_Kutlesi_kg"], out["Toplam_Kutle_kg"]
    pf = (warhead / total).where(lambda s: (s > 0) & (s <= 1))
    by_sub = pf.groupby(out["Alt_Kategori"]).agg(["median", "count"])
    by_cat = pf.groupby(out["Ana_Kategori"]).median()
    global_pf = float(pf.median()) if pf.notna().any() else 0.3

    def expected_pf(sub: str, cat: str) -> float:
        if sub in by_sub.index and by_sub.loc[sub, "count"] >= MIN_PF_SAMPLES:
            return float(by_sub.loc[sub, "median"])
        if cat in by_cat.index and not pd.isna(by_cat.loc[cat]):
            return float(by_cat.loc[cat])
        return global_pf

    est_pf = [expected_pf(s, c) for s, c in zip(out["Alt_Kategori"], out["Ana_Kategori"])]
    imputed = warhead.isna() & total.notna()
    out["Harp_Basligi_Etkin_kg"] = warhead.where(~imputed, total * pd.Series(est_pf, index=out.index))
    out["Harp_Basligi_Tahmini"] = imputed
    out["Tasiyici_Sinifi"] = ["+".join(carrier_classes(p)) or "NA" for p in out["Entegre_Platformlar"]]
    out["Gudum_Modlari"] = [
        "|".join(guidance_modes(t, m)) for t, m in zip(out["Gudum_Sistemi_Terminal"], out["Gudum_Sistemi_Midcourse"])
    ]
    out["Sahne_Eslemeli"] = [
        sub in SCENE_MATCHING_SUBCATEGORIES
        and "Data-Link" not in str(mid).split("/")
        and any(mode in SCENE_MATCHING_MODES for mode in modes.split("|"))
        for sub, mid, modes in zip(out["Alt_Kategori"], out["Gudum_Sistemi_Midcourse"], out["Gudum_Modlari"])
    ]
    return out


def validate_targets(df: pd.DataFrame, min_rows: int = vtm.MIN_TARGETS) -> list[str]:
    """Hedef matrisinin şema denetimi (validate_target_matrix); hata listesi döner (boş = geçerli)."""
    return vtm.validate(df, min_rows)[0]


def load_targets(path: str | None = None) -> pd.DataFrame:
    """Hedef matrisini okur, doğrular; sayısal sütunlar float, TST_Status bool olur."""
    path = path or TARGET_MATRIX_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Hedef matrisi bulunamadı: {path}")
    return vtm.load_matrix(path)


@functools.lru_cache(maxsize=1)
def _default_munitions() -> pd.DataFrame:
    return prepare_munitions(load_munitions()[0])


@functools.lru_cache(maxsize=1)
def _default_targets() -> pd.DataFrame:
    return load_targets()


# ---------------------------------------------------------------------------
# Alt modeller
# ---------------------------------------------------------------------------
def _isnan(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value)) or bool(pd.isna(value))


def _warhead_key(warhead_type: str) -> str:
    return warhead_type if warhead_type in KILL_GIVEN_HIT else "NA"


def lethal_radius_m(warhead_kg: float, warhead_type: str, target_category: str, passive_level: str = "Low") -> float:
    """Ampirik ölümcül (etkisizleştirme) yarıçapı: R = K · k_tip · c_koruma · W^(1/3)."""
    if _isnan(warhead_kg) or warhead_kg <= 0:
        return float("nan")
    wtype = _warhead_key(warhead_type)
    mod = WARHEAD_K_MOD[wtype]
    protection = PROTECTION_FACTOR[passive_level]
    radius = LETHAL_K[target_category] * mod.get(target_category, mod["_"]) * protection * warhead_kg ** (1 / 3)
    if wtype in SHAPED_CHARGE_TYPES and target_category == ARMORED:
        radius = max(radius, DIRECT_HIT_RADIUS_M * protection)
    return radius


def kill_probability_given_hit(warhead_type: str, target_category: str) -> float:
    """P(imha | etkili isabet). Sertleştirilmiş yapıda izinli tipler dışında 0."""
    wtype = _warhead_key(warhead_type)
    if target_category == HARDENED and wtype not in HARD_TARGET_WARHEADS:
        return 0.0
    return KILL_GIVEN_HIT[wtype].get(target_category, 0.0)


def incident_overpressure_kpa(scaled_distance: float) -> float:
    """Serbest hava patlamasında tepe gelen aşırı basınç [kPa]; Kinney & Graham (1985).

    scaled_distance: Z = R / W^(1/3)  [m/kg^(1/3)], W = TNT eşdeğeri.
    """
    z = max(float(scaled_distance), 1e-6)
    ratio = (
        808.0
        * (1.0 + (z / 4.5) ** 2)
        / math.sqrt(1.0 + (z / 0.048) ** 2)
        / math.sqrt(1.0 + (z / 0.32) ** 2)
        / math.sqrt(1.0 + (z / 1.35) ** 2)
    )
    return ratio * ATM_KPA


def scaled_distance_for_overpressure(pressure_kpa: float) -> float:
    """incident_overpressure_kpa'nın tersi (basınç Z ile tekdüze azalır; log-ikiye bölme)."""
    low, high = 0.02, 2000.0
    if pressure_kpa >= incident_overpressure_kpa(low):
        return low
    if pressure_kpa <= incident_overpressure_kpa(high):
        return high
    for _ in range(80):
        mid = math.sqrt(low * high)
        if incident_overpressure_kpa(mid) > pressure_kpa:
            low = mid
        else:
            high = mid
    return math.sqrt(low * high)


def tnt_equivalent_kg(
    warhead_kg: float, warhead_type: str, surface_burst: bool = True, relative_effectiveness: float = TNT_RE_DEFAULT
) -> float:
    """Harp başlığı kütlesinden etkin TNT eşdeğeri [kg].

    dolgu = W · dolgu oranı;  kılıf M = W - dolgu;
    Fano kılıf düzeltmesi: 0.2 + 0.8 / (1 + 2·M/C)   (parçacığa giden enerji düşülür; YAKLAŞIK)
    yer yüzeyi patlamasında × 1.8.
    """
    if _isnan(warhead_kg) or warhead_kg <= 0:
        return float("nan")
    fill = warhead_kg * FILL_FRACTION[_warhead_key(warhead_type)]
    casing = warhead_kg - fill
    bare = fill * relative_effectiveness * (0.2 + 0.8 / (1.0 + 2.0 * casing / fill))
    return bare * (SURFACE_BURST_FACTOR if surface_burst else 1.0)


def blast_radius_m(tnt_kg: float, overpressure_psi: float) -> float:
    """Tepe aşırı basıncın verilen değere düştüğü mesafe: R = Z(P) · W^(1/3)."""
    if _isnan(tnt_kg) or tnt_kg <= 0:
        return float("nan")
    return scaled_distance_for_overpressure(overpressure_psi * PSI_TO_KPA) * tnt_kg ** (1 / 3)


def overpressure_at_psi(tnt_kg: float, distance_m: float) -> float:
    """Verilen mesafede tepe gelen aşırı basınç [psi]."""
    if _isnan(tnt_kg) or tnt_kg <= 0:
        return float("nan")
    return incident_overpressure_kpa(distance_m / tnt_kg ** (1 / 3)) / PSI_TO_KPA


def collateral_factor(collateral_radius_m: float, tier: str) -> float:
    """Tali hasar göstergesi yarıçapı düzeyin sınırını aşıyorsa skor çarpanı (1.0 → 0.3)."""
    limit = CDE_RADIUS_LIMIT_M[tier]
    if _isnan(collateral_radius_m) or collateral_radius_m <= limit:
        return 1.0
    return max(CDE_FACTOR_FLOOR, limit / collateral_radius_m)


def time_of_flight_s(propulsion: str, mach: float, distance_km: float) -> float:
    """Yaklaşık uçuş süresi: mesafe / (ortalama hız oranı × Mach × ses hızı)."""
    top_mach = DEFAULT_MACH.get(propulsion, 0.8) if _isnan(mach) else float(mach)
    speed = AVERAGE_SPEED_RATIO.get(propulsion, 0.9) * top_mach * CRUISE_SOUND_SPEED
    return distance_km * 1000.0 / max(speed, 10.0)


def tst_factor(is_tst: bool, flight_time_s: float, window_s: float, has_datalink: bool) -> float:
    """Zamana duyarlı hedefte uçuş süresi pencereyi aşarsa isabet çarpanı = pencere / uçuş süresi."""
    if not is_tst or flight_time_s <= window_s:
        return 1.0
    factor = window_s / flight_time_s
    return max(factor, TST_DATALINK_FLOOR) if has_datalink else factor


def expected_bda(pk: float) -> str:
    for threshold, label in BDA_LEVELS:
        if pk >= threshold:
            return label
    return BDA_LEVELS[-1][1]


def calculate_penetration_depth(
    velocity: float, mass: float, diameter: float, warhead_type: str = "Penetrator"
) -> float:
    """Betonarme delme derinliği [m]; Young (1997, SAND97-2426) beton denklemi biçimi.

        D = C · (m/A)^0.7 · (V - 30.5) · K,   A = π·d²/4,   K = 0.46·m^0.15 (m < 182 kg), aksi 1

    velocity [m/s] çarpma hızı, mass [kg] delici kütlesi, diameter [m] gövde çapı.
    C, hedef sertliği (S) ve burun katsayısını (N) içeren toplu sabittir ve TEMSİLÎDİR.
    Denklem V >= 61 m/s için geçerlidir; warhead_type gövde dayanımı çarpanını seçer.
    """
    if min(velocity, mass, diameter) <= 0 or velocity <= 61.0:
        return 0.0
    sectional_density = mass / (math.pi / 4.0 * diameter**2)
    k_mass = 0.46 * mass**0.15 if mass < YOUNG_LIGHT_MASS_KG else 1.0
    depth = YOUNG_C * sectional_density**YOUNG_SD_EXP * (velocity - YOUNG_V0) * k_mass
    return depth * PEN_TYPE_FACTOR.get(_warhead_key(warhead_type), PEN_TYPE_FACTOR["NA"])


def estimate_penetration_m(
    warhead_type: str, warhead_kg: float, diameter_mm: float, mach: float, is_bomb: bool
) -> float:
    """Betonarme delme tahmini [m]. Kinetik deliciler için Young biçimi, HEAT için jet delme."""
    if _isnan(warhead_kg) or warhead_kg <= 0:
        return float("nan")
    wtype = _warhead_key(warhead_type)
    dia = None if _isnan(diameter_mm) or diameter_mm <= 0 else diameter_mm / 1000.0
    if wtype in SHAPED_CHARGE_TYPES:
        charge = SHAPED_CHARGE_DIA_COEF * warhead_kg ** (1 / 3)
        charge = charge if dia is None else min(dia, charge)
        return JET_CALIBERS[wtype] * charge
    # Harp başlığı çapı: bombada gövde çapı; füzede kütleden şekil ölçeklemesiyle tahmin
    d_est = REF_PENETRATOR_DIA_M * (warhead_kg / REF_PENETRATOR_KG) ** (1 / 3)
    if dia is None:
        d = d_est
    elif is_bomb:
        d = dia if dia <= BOMB_DIAMETER_TOLERANCE * d_est else d_est
    else:
        d = min(dia, d_est)
    impact_mach = IMPACT_MACH_DEFAULT if _isnan(mach) else float(np.clip(mach, *IMPACT_MACH_RANGE))
    return calculate_penetration_depth(impact_mach * SOUND_SPEED, warhead_kg, d, wtype)


def penetration_factor(estimated_m: float, required_m: float) -> float:
    """1 (yeterli) | (oran)^3 (kısmi) | 0 (gerekli kalınlığın yarısından az)."""
    if required_m <= 0:
        return 1.0
    if _isnan(estimated_m):
        return 0.0
    ratio = estimated_m / required_m
    if ratio >= 1.0:
        return 1.0
    return 0.0 if ratio < PEN_FAIL_RATIO else ratio**3


def circular_hit_probability(allowed_miss_m: float, cep_m: float) -> float:
    """Dairesel normal dağılımda ıska mesafesinin izinli değerin altında kalma olasılığı."""
    return 1.0 - 0.5 ** ((allowed_miss_m / cep_m) ** 2)


def proportionality_factor(lethal_radius: float, required_radius: float) -> float:
    """Gereğinden büyük etki yarıçapı (aşırı güç / tali hasar riski) için ceza.

    R_w / R_gerekli <= 2 → 1.0; oran 5 ve üzerinde → 0.6 (doğrusal geçiş).
    """
    rho = lethal_radius / required_radius
    return 1.0 - OVERKILL_MAX_PENALTY * float(np.clip((rho - OVERKILL_START) / OVERKILL_SPAN, 0.0, 1.0))


def role_factor(sub_category: str, target_category: str) -> float:
    """Birincil görev uyumu; ikincil görevde 0.7.

    gemisavar → deniz hedefi · anti-radyasyon → yayın yapan hedef · sığınak delici → sertleştirilmiş yapı
    """
    if sub_category == ANTI_SHIP_SUBCATEGORY and target_category != NAVAL:
        return ROLE_SECONDARY_FACTOR
    if sub_category == ANTI_RADIATION_SUBCATEGORY and target_category not in EMITTER_CATEGORIES:
        return ROLE_SECONDARY_FACTOR
    if sub_category == BUNKER_BUSTER_SUBCATEGORY and target_category != HARDENED:
        return ROLE_SECONDARY_FACTOR
    return 1.0


def standoff_factor(range_km: float, standoff_km: float) -> float:
    """Standoff emniyet payı: menzil = gerekli → 0.8; menzil >= 2 × gerekli → 1.0."""
    if standoff_km <= 0:
        return 1.0
    if _isnan(range_km) or range_km < standoff_km:
        return 0.0
    return STANDOFF_BASE + (1.0 - STANDOFF_BASE) * float(np.clip(range_km / standoff_km - 1.0, 0.0, 1.0))


def required_weapons(pk: float, desired_damage: float) -> float:
    """Bağımsız atış varsayımıyla hedeflenen hasar olasılığı için gereken atış sayısı."""
    if _isnan(pk) or pk <= 0:
        return float("nan")
    if pk >= desired_damage:
        return 1.0
    return float(min(MAX_WEAPONS_REPORTED, math.ceil(math.log(1 - desired_damage) / math.log(1 - pk))))


def _signature_factor(mode: str, target: dict, anti_ship: bool = False) -> float:
    category = target["Target_Class"]
    on_land = category != NAVAL
    if mode in RADAR_MODES:
        rcs = max(float(target["Radar_Cross_Section_m2"]), 1e-3)
        factor = float(np.clip(1.0 + RCS_SLOPE * math.log10(rcs / RCS_REF_M2), RCS_FLOOR, 1.0))
        if mode != "MMW" and on_land:
            return factor * LAND_CLUTTER_FACTOR
    elif mode == "IIR":
        fixed = target["Target_Mobility_Class"] == FIXED
        factor = IIR_FIXED_FACTOR if fixed else THERMAL_IIR[target["Thermal_Signature"]]
    elif mode == "IR":
        factor = THERMAL_IR[target["Thermal_Signature"]] * (IR_LAND_FACTOR if on_land else 1.0)
    else:
        factor = 1.0
    if anti_ship and on_land and mode in HOMING_MODES:
        factor *= ANTI_SHIP_LAND_FACTOR
    return factor


def _concealment_factor(mode: str, target: dict) -> float:
    level = target["Passive_Defense_Level"]
    factor = CCD_FACTOR[level]
    if mode in COORDINATE_MODES and target["Target_Mobility_Class"] == FIXED:
        factor = math.sqrt(factor)  # koordinatı bilinen sabit tesiste aldatmanın etkisi sınırlı
    if mode == "Passive_RF":
        factor *= EMCON_FACTOR[level]
    return factor


def _mode_unusable_reason(mode: str, target: dict, scenario: Scenario) -> str | None:
    if mode == "Passive_RF" and target["Target_Class"] not in EMITTER_CATEGORIES:
        return "pasif RF arayıcı yalnız yayın yapan hedefe kilitlenir"
    if mode in LASER_MODES and not scenario.laser_designation:
        return "lazer işaretleme imkânı yok"
    return None


def _mode_hit(
    mode: str,
    allowed_miss_m: float,
    target: dict,
    scenario: Scenario,
    scene_matching: bool = False,
    anti_ship: bool = False,
) -> dict:
    cep = CEP_M[mode]
    if mode == MODE_COORD and scenario.gnss_jamming:
        cep *= GNSS_JAM_CEP_FACTOR
    p_cep = circular_hit_probability(allowed_miss_m, cep)
    # Sahne eşlemeli EO/IIR hareketli hedefi izleyemez → hareketlilikte koordinat modu gibi davranır
    tracks_movers = mode in HOMING_MODES and not (scene_matching and mode in SCENE_MATCHING_MODES)
    mobility_key = mode if tracks_movers or mode not in HOMING_MODES else MODE_COORD
    f_mob = MOBILITY_FACTOR[mobility_key][MOBILITY_LEVELS.index(target["Target_Mobility_Class"])]
    f_sig = _signature_factor(mode, target, anti_ship)
    f_env = WEATHER_FACTOR[scenario.weather].get(mode, 1.0)
    f_ccd = _concealment_factor(mode, target)
    return {
        "mode": mode,
        "cep": cep,
        "p_cep": p_cep,
        "f_mob": f_mob,
        "f_sig": f_sig,
        "f_env": f_env,
        "f_ccd": f_ccd,
        "tracks_movers": tracks_movers,
        "p": p_cep * f_mob * f_sig * f_env * f_ccd,
    }


# ---------------------------------------------------------------------------
# Çekirdek değerlendirme
# ---------------------------------------------------------------------------
RESULT_COLUMNS = [
    "Sira",
    "Muhimmat_Adi",
    "Mensei_Ulke",
    "Ana_Kategori",
    "Alt_Kategori",
    "Tasiyici_Sinifi",
    "Entegre_Platformlar",
    "Durum",
    "Uygunluk_Skoru",
    "PK_Tek_Atis",
    "Gerekli_Atis_Sayisi",
    "Secilen_Gudum_Modu",
    "P_Isabet",
    "Kapsama_Orani",
    "Harp_Basligi_Uyumu",
    "Delme_Yeterliligi",
    "Olumcul_Yaricap_m",
    "Gerekli_Yaricap_m",
    "Tahmini_Delme_m",
    "Gerekli_Delme_m",
    "Maksimum_Menzil_km",
    "Standoff_Payi_km",
    "K_Orantililik",
    "K_Standoff",
    "K_Rol",
    "K_CDE",
    "Ph",
    "Pd",
    "Beklenen_BDA",
    "Hasar_Mekanizmasi",
    "TNT_Esdeger_kg",
    "Patlama_Yaricapi_m",
    "Hedefte_Asiri_Basinc_psi",
    "Sertlik_psi",
    "Tali_Hasar_Yaricapi_m",
    "Ucus_Suresi_s",
    "C_TST",
    "CEP_Etkin_m",
    "Izinli_Iska_m",
    "P_CEP",
    "C_Hareketlilik",
    "C_Iz",
    "C_Ortam",
    "C_Gizleme",
    "Guvenilirlik",
    "Harp_Basligi_Tipi",
    "Harp_Basligi_Etkin_kg",
    "Harp_Basligi_Tahmini",
    "Toplam_Kutle_kg",
    "Veri_Guvenilirlik_Notu",
    "Eleme_Kodu",
    "Eleme_Nedeni",
    "Gerekce",
]
_NUMERIC_RESULT = [
    "Uygunluk_Skoru",
    "PK_Tek_Atis",
    "Gerekli_Atis_Sayisi",
    "P_Isabet",
    "Kapsama_Orani",
    "Harp_Basligi_Uyumu",
    "Delme_Yeterliligi",
    "Olumcul_Yaricap_m",
    "Tahmini_Delme_m",
    "Standoff_Payi_km",
    "K_Orantililik",
    "K_Standoff",
    "K_Rol",
    "CEP_Etkin_m",
    "Izinli_Iska_m",
    "P_CEP",
    "C_Hareketlilik",
    "C_Iz",
    "C_Ortam",
    "C_Gizleme",
    "K_CDE",
    "Ph",
    "Pd",
    "TNT_Esdeger_kg",
    "Patlama_Yaricapi_m",
    "Hedefte_Asiri_Basinc_psi",
    "Tali_Hasar_Yaricapi_m",
    "Ucus_Suresi_s",
    "C_TST",
]
_ROUNDING = {
    "Uygunluk_Skoru": 1,
    "PK_Tek_Atis": 4,
    "P_Isabet": 4,
    "Kapsama_Orani": 4,
    "Harp_Basligi_Uyumu": 2,
    "Delme_Yeterliligi": 4,
    "Olumcul_Yaricap_m": 2,
    "Tahmini_Delme_m": 2,
    "Standoff_Payi_km": 1,
    "K_Orantililik": 3,
    "K_Standoff": 3,
    "K_Rol": 2,
    "CEP_Etkin_m": 1,
    "Izinli_Iska_m": 2,
    "P_CEP": 4,
    "C_Hareketlilik": 2,
    "C_Iz": 3,
    "C_Ortam": 2,
    "C_Gizleme": 3,
    "Harp_Basligi_Etkin_kg": 1,
    "K_CDE": 3,
    "Ph": 4,
    "Pd": 4,
    "TNT_Esdeger_kg": 1,
    "Patlama_Yaricapi_m": 2,
    "Hedefte_Asiri_Basinc_psi": 2,
    "Tali_Hasar_Yaricapi_m": 1,
    "Ucus_Suresi_s": 0,
    "C_TST": 3,
}


def _evaluate(m: dict, target: dict, scenario: Scenario) -> dict:
    """Tek mühimmat × tek hedef değerlendirmesi."""
    category = target["Target_Class"]
    r_req = float(target["Required_Lethal_Radius_m"])
    p_req = float(target["Required_Concrete_Penetration_m"])
    standoff = scenario.required_standoff_km
    wtype = m["Harp_Basligi_Tipi"]
    warhead = m["Harp_Basligi_Etkin_kg"]
    rng = m["Maksimum_Menzil_km"]
    codes: list[str] = []
    reasons: list[str] = []

    def drop(code: str, text: str) -> None:
        codes.append(code)
        reasons.append(text)

    out = {col: float("nan") for col in _NUMERIC_RESULT}
    out.update(
        {
            "Sira": float("nan"),
            "Muhimmat_Adi": m["Muhimmat_Adi"],
            "Mensei_Ulke": m["Mensei_Ulke"],
            "Ana_Kategori": m["Ana_Kategori"],
            "Alt_Kategori": m["Alt_Kategori"],
            "Tasiyici_Sinifi": m["Tasiyici_Sinifi"],
            "Entegre_Platformlar": m["Entegre_Platformlar"],
            "Secilen_Gudum_Modu": "-",
            "Gerekli_Yaricap_m": r_req,
            "Gerekli_Delme_m": p_req,
            "Maksimum_Menzil_km": rng,
            "Guvenilirlik": RELIABILITY,
            "Harp_Basligi_Tipi": wtype,
            "Harp_Basligi_Etkin_kg": warhead,
            "Harp_Basligi_Tahmini": bool(m["Harp_Basligi_Tahmini"]),
            "Toplam_Kutle_kg": m["Toplam_Kutle_kg"],
            "Veri_Guvenilirlik_Notu": m["Veri_Guvenilirlik_Notu"],
            "Gerekce": "",
            "Beklenen_BDA": "-",
            "Hasar_Mekanizmasi": target["Primary_Damage_Mechanism"],
            "Sertlik_psi": float(target["UFC_Hardness_Rating_psi"]),
        }
    )

    def finish(status: str) -> dict:
        out["Durum"] = status
        out["Eleme_Kodu"] = ",".join(codes)
        out["Eleme_Nedeni"] = " | ".join(reasons)
        if status != STATUS_OK:
            out["Uygunluk_Skoru"] = 0.0
        return out

    # 1) Görev rolü
    if m["Alt_Kategori"] in AIR_TO_AIR_SUBCATEGORIES:
        drop("ROL", "Havadan havaya füze - yüzey hedefi için uygun değil")
        return finish(STATUS_ELIMINATED)

    # 2) Taşıyıcı filtresi
    classes = [c for c in m["Tasiyici_Sinifi"].split("+") if c and c != "NA"]
    if scenario.carrier_classes and not set(classes) & set(scenario.carrier_classes):
        drop("TASIYICI", f"Seçilen taşıyıcı sınıfına entegre değil ({'/'.join(scenario.carrier_classes)})")
    if scenario.platform:
        platforms = [p.strip() for p in m["Entegre_Platformlar"].split(",")]
        if scenario.platform not in platforms:
            drop("PLATFORM", f"{scenario.platform} için entegrasyon kaydı yok")

    # 3) Standoff
    if not _isnan(rng):
        out["Standoff_Payi_km"] = rng - standoff
    if standoff > 0:
        if _isnan(rng):
            drop("MENZIL_VERISI_YOK", f"Menzil verisi yok - {standoff:.0f} km standoff doğrulanamadı")
        elif rng < standoff:
            drop("STANDOFF", f"Standoff yetersiz: menzil {rng:.0f} km < gerekli {standoff:.0f} km")
    out["K_Standoff"] = standoff_factor(rng, standoff)

    # 4) Veri yeterliliği
    if _isnan(warhead) or warhead <= 0:
        if codes:
            return finish(STATUS_ELIMINATED)
        drop("VERI", "Harp başlığı ve toplam kütle verisi yok - etki hesaplanamadı")
        return finish(STATUS_NO_DATA)

    # 5) Etki yarıçapı ve kapsama
    level = target["Passive_Defense_Level"]
    r_w = lethal_radius_m(warhead, wtype, category, level)
    # 5b) Patlama: hedef sertliğini aşan aşırı basıncın ulaştığı yarıçap
    hardness_psi = float(target["UFC_Hardness_Rating_psi"])
    w_tnt = tnt_equivalent_kg(warhead, wtype)
    blast_radius = blast_radius_m(w_tnt, hardness_psi)
    collateral_radius = blast_radius_m(w_tnt, COLLATERAL_PSI)
    if target["Primary_Damage_Mechanism"] == BLAST_MECHANISM:
        r_w = blast_radius * PROTECTION_FACTOR[level]
    k_cde = collateral_factor(collateral_radius, scenario.cde_tier or target["Collateral_Damage_Tier"])
    out.update(
        {
            "TNT_Esdeger_kg": w_tnt,
            "Patlama_Yaricapi_m": blast_radius,
            "K_CDE": k_cde,
            "Hedefte_Asiri_Basinc_psi": overpressure_at_psi(w_tnt, r_req),
            "Tali_Hasar_Yaricapi_m": collateral_radius,
        }
    )
    coverage = min(1.0, (r_w / r_req) ** 2)
    allowed_miss = max(r_w, r_req)
    kill_hit = kill_probability_given_hit(wtype, category)
    if category == HARDENED and _warhead_key(wtype) not in HARD_TARGET_WARHEADS:
        drop(
            "HARP_BASLIGI", f"Sertleştirilmiş hedef: harp başlığı {wtype} " f"({' / '.join(HARD_TARGET_WARHEADS)} şart)"
        )

    # 6) Delme
    is_bomb = m["Ana_Kategori"] in BOMB_CATEGORIES
    p_est = estimate_penetration_m(wtype, warhead, m["Cap_mm"], m["Maksimum_Hiz_Mach"], is_bomb)
    f_pen = penetration_factor(p_est, p_req)
    if p_req > 0 and f_pen == 0.0 and "HARP_BASLIGI" not in codes:
        drop("DELME", f"Delme yetersiz: tahmini {p_est:.1f} m < gerekli {p_req:.1f} m")

    # 7) Güdüm modu seçimi
    modes = [x for x in m["Gudum_Modlari"].split("|") if x]
    scene_matching = bool(m["Sahne_Eslemeli"])
    anti_ship = m["Alt_Kategori"] == ANTI_SHIP_SUBCATEGORY
    usable, blocked = [], []
    for mode in modes:
        why = _mode_unusable_reason(mode, target, scenario)
        if why:
            blocked.append(f"{mode}: {why}")
        else:
            usable.append(_mode_hit(mode, allowed_miss, target, scenario, scene_matching, anti_ship))
    best = max(usable, key=lambda h: h["p"]) if usable else None
    if not modes:
        drop("GUDUM", "Güdüm bilgisi yok (NA)")
    elif best is None:
        drop("GUDUM_MODU", "Kullanılabilir güdüm modu yok (" + "; ".join(blocked) + ")")
    elif target["Target_Mobility_Class"] == FAST and not any(h["tracks_movers"] for h in usable):
        have = "/".join(h["mode"] for h in usable)
        note = " - EO/IIR sahne eşleme, veri bağı yok" if scene_matching else ""
        drop(
            "HAREKETLILIK",
            "Hızlı manevralı hedef: hareketli hedefi izleyen terminal arayıcı şart "
            f"(IIR/SAL/ARH/EO/MMW); mevcut mod {have}{note}",
        )

    # 8) PK ve skor
    distance_km = (
        standoff if standoff > 0 else (DEFAULT_ENGAGEMENT_KM if _isnan(rng) else min(rng, DEFAULT_ENGAGEMENT_KM))
    )
    flight_time = time_of_flight_s(m.get("Itki_Sistemi", "NA"), m["Maksimum_Hiz_Mach"], distance_km)
    c_tst = tst_factor(
        bool(target["TST_Status"]),
        flight_time,
        scenario.tst_window_s,
        "Data-Link" in str(m["Gudum_Sistemi_Midcourse"]).split("/"),
    )
    p_hit = (best["p"] if best else 0.0) * c_tst  # Ph
    p_damage = coverage * kill_hit * f_pen  # Pd
    pk = min(PK_CAP, p_hit * p_damage * RELIABILITY)
    out.update(
        {"Ph": p_hit, "Pd": p_damage, "Ucus_Suresi_s": flight_time, "C_TST": c_tst, "Beklenen_BDA": expected_bda(pk)}
    )
    k_prop = proportionality_factor(r_w, r_req)
    k_role = role_factor(m["Alt_Kategori"], category)
    out.update(
        {
            "PK_Tek_Atis": pk,
            "Gerekli_Atis_Sayisi": required_weapons(pk, scenario.desired_damage),
            "P_Isabet": p_hit,
            "Kapsama_Orani": coverage,
            "Harp_Basligi_Uyumu": kill_hit,
            "Delme_Yeterliligi": f_pen,
            "Olumcul_Yaricap_m": r_w,
            "Tahmini_Delme_m": p_est,
            "K_Orantililik": k_prop,
            "K_Rol": k_role,
            "Izinli_Iska_m": allowed_miss,
        }
    )
    if best:
        out.update(
            {
                "Secilen_Gudum_Modu": best["mode"],
                "CEP_Etkin_m": best["cep"],
                "P_CEP": best["p_cep"],
                "C_Hareketlilik": best["f_mob"],
                "C_Iz": best["f_sig"],
                "C_Ortam": best["f_env"],
                "C_Gizleme": best["f_ccd"],
            }
        )
    if not codes and pk < MIN_ELIGIBLE_PK:
        drop(
            "ETKISIZ",
            f"Etki yetersiz: tek atış PK {pk:.3f} < {MIN_ELIGIBLE_PK:.2f} "
            f"(isabet {p_hit:.2f}, kapsama %{coverage * 100:.0f}, {wtype} uyumu {kill_hit:.2f})",
        )
    if codes:
        return finish(STATUS_ELIMINATED)

    out["Uygunluk_Skoru"] = 100.0 * pk * k_prop * out["K_Standoff"] * k_role * k_cde
    parts = [
        f"{best['mode']} güdüm",
        f"isabet {p_hit:.2f}",
        f"kapsama %{coverage * 100:.0f}",
        f"{wtype} uyumu {kill_hit:.2f}",
    ]
    if p_req > 0:
        parts.append(f"delme {p_est:.1f}/{p_req:.1f} m")
    if standoff > 0:
        parts.append(f"standoff payı +{rng - standoff:.0f} km")
    if k_prop < 0.999:
        parts.append(f"aşırı güç cezası x{k_prop:.2f}")
    if k_role < 0.999:
        parts.append(f"ikincil görev x{k_role:.2f}")
    if c_tst < 0.999:
        parts.append(f"TST uçuş süresi {flight_time:.0f} s x{c_tst:.2f}")
    if k_cde < 0.999:
        parts.append(f"tali hasar yarıçapı {collateral_radius:.0f} m x{k_cde:.2f}")
    if m["Harp_Basligi_Tahmini"]:
        parts.append("harp başlığı kütlesi tahmini")
    out["Gerekce"] = " · ".join(parts)
    return finish(STATUS_OK)


def evaluate_jaws_match(target_data, munition_data, environment_threats=None) -> dict:
    """Tek hedef × tek mühimmat eşleşmesi: Pk = Ph × Pd × güvenilirlik.

    target_data         : hedef matrisi satırı (dict / Series) ya da Target_ID
    munition_data       : mühimmat satırı (dict / Series) ya da Muhimmat_Adi
    environment_threats : Scenario, Scenario alanlarını içeren dict (ör. {"air_defense": "VLRSAM",
                          "weather": "OBSCURED", "gnss_jamming": True}) ya da None

    Dönüş: RESULT_COLUMNS anahtarlı sözlük (Ph, Pd, PK_Tek_Atis, Uygunluk_Skoru, Durum, Eleme_Nedeni ...).
    Mühimmat satırı hazırlanmamışsa (ham veri) harp başlığı kütlesi tahmini için varsayılan veri setinin
    alt kategori medyanları kullanılır.
    """
    if isinstance(environment_threats, Scenario):
        scenario = environment_threats
    else:
        scenario = Scenario(**(environment_threats or {}))
    target = get_target(target_data) if isinstance(target_data, str) else dict(target_data)
    missing = [c for c in TARGET_COLUMNS if c not in target]
    if missing:
        raise KeyError(f"Hedef verisinde eksik alan(lar): {missing}")
    for col in TARGET_NUMERIC:
        target[col] = float(target[col])
    target["TST_Status"] = str(target["TST_Status"]) == "True"

    if isinstance(munition_data, str):
        pool = _default_munitions()
        hit = pool[pool["Muhimmat_Adi"] == munition_data]
        if hit.empty:
            raise KeyError(f"Mühimmat bulunamadı: '{munition_data}'")
        munition = hit.iloc[0].to_dict()
    else:
        munition = dict(munition_data)
        if not all(c in munition for c in PREPARED_MARKERS):
            pool = _default_munitions()
            hit = pool[pool["Muhimmat_Adi"] == munition.get("Muhimmat_Adi")]
            if not hit.empty and _isnan(pd.to_numeric(munition.get("Harp_Basligi_Kutlesi_kg"), errors="coerce")):
                munition = {**hit.iloc[0].to_dict(), **{k: v for k, v in munition.items() if k not in MUNITION_NUMERIC}}
            else:
                munition = prepare_munitions(pd.DataFrame([munition])).iloc[0].to_dict()
    result = _evaluate(munition, target, scenario)
    return {
        k: (round(v, _ROUNDING[k]) if k in _ROUNDING and isinstance(v, float) and not math.isnan(v) else v)
        for k, v in result.items()
    }


# ---------------------------------------------------------------------------
# Görev akışı: özel hedef tanımı, istenen etki, çarpma koşulları
# ---------------------------------------------------------------------------
# Young (1997) hedef delinebilirlik sayısı S (büyük S = kolay delinir). Delme derinliği S ile orantılıdır;
# bu yüzden bir katmanın beton eşdeğeri kalınlığı = kalınlık × S_beton / S_malzeme. Değerler SAND97-2426'daki
# tipik aralıkların orta noktalarıdır ve HAFIZADAN yazılmıştır: birincil kaynaktan teyit edilmelidir.
CONCRETE_S = 0.9
MATERIALS = {
    "Reinforced_Concrete": ("Betonarme (≈35 MPa)", 0.9),
    "High_Strength_Concrete": ("Yüksek dayanımlı beton (≈70 MPa)", 0.65),
    "Plain_Concrete": ("Donatısız beton", 1.0),
    "Masonry": ("Tuğla / yığma duvar", 1.6),
    "Hard_Rock": ("Sert kaya (granit vb.)", 0.8),
    "Weathered_Rock": ("Ayrışmış / çatlaklı kaya", 1.5),
    "Dense_Sand_Gravel": ("Sıkı kum / çakıl dolgu", 5.0),
    "Compacted_Soil": ("Sıkıştırılmış toprak örtü", 8.0),
    "Soft_Clay": ("Yumuşak kil / gevşek toprak", 15.0),
}
# Sınıf varsayılanları: (birincil hasar mekanizması, sertlik psi, termal iz, RCS m²) - sertlik değerleri VARSAYIMDIR
CLASS_DEFAULTS = {
    HARDENED: ("Penetration", 30.0, "Low", 100.0),
    "Soft_Structure": ("Blast", 6.0, "Medium", 500.0),
    "Infrastructure": ("Blast", 30.0, "Low", 1000.0),
    "Soft_Vehicle": ("Fragment", 5.0, "Medium", 20.0),
    ARMORED: ("Direct_Hit", 30.0, "High", 15.0),
    "Radar/Air_Defense": ("Fragment", 4.0, "Medium", 100.0),
    NAVAL: ("Penetration", 12.0, "High", 3000.0),
    "Personnel": ("Fragment", 36.0, "Medium", 1.0),
}
# İstenen etki → (etiket, kapsanacak alan oranı, hedeflenen hasar olasılığı, açıklama). Oranlar VARSAYIMDIR.
DESIRED_EFFECTS = {
    "SUPPRESS": ("Baskılama / geçici etkisizleştirme", 0.30, 0.50, "hedef alanının ~%30'u, P_D 0.50"),
    "PARTIAL": ("Kısmi yıkım", 0.60, 0.70, "hedef alanının ~%60'ı, P_D 0.70"),
    "DESTROY": ("Tam yıkım", 1.00, 0.90, "hedef alanının tamamı, P_D 0.90"),
    "AREA": ("Alana taarruz", 1.00, 0.70, "alanın tamamı; tek atış kapsama düşükse çok sayıda mühimmat, P_D 0.70"),
}
AREA_RADIUS_THRESHOLD_M = 25.0
CUSTOM_TARGET_ID = "TGT-USR-00"
GRAVITY = 9.80665
DESIRED_IMPACT_ANGLE = {"Penetration": 70.0, "Crater": 60.0, "Blast": 45.0, "Fragment": 45.0, "Direct_Hit": 45.0}
MAX_SHAPED_ANGLE = 80.0
SEA_SKIM_ANGLE = 10.0


def concrete_equivalent_m(layers) -> float:
    """[(malzeme anahtarı, kalınlık m), ...] katmanlarının betonarme eşdeğeri toplam kalınlığı."""
    total = 0.0
    for material, thickness in layers:
        if material not in MATERIALS:
            raise KeyError(f"Bilinmeyen malzeme '{material}'; seçenekler: {list(MATERIALS)}")
        total += max(float(thickness), 0.0) * CONCRETE_S / MATERIALS[material][1]
    return total


def build_custom_target(
    description: str,
    target_class: str,
    length_m: float,
    width_m: float,
    layers=(),
    mobility: str = FIXED,
    passive_level: str = "Low",
    tst: bool = False,
    cde_tier: str = "Low",
    hardness_psi: float | None = None,
) -> dict:
    """Kullanıcı tanımlı hedef: malzeme katmanları + geometri → motorun beklediği hedef sözlüğü.

    layers        : dıştan içe [(malzeme, kalınlık m)]; örn. [("Compacted_Soil", 2.0), ("Reinforced_Concrete", 1.2)]
    length/width  : hedef izinin boyutları; gerekli etki yarıçapı eşdeğer daire yarıçapıdır √(L·W/π)
    Sertlik (psi), termal iz ve RCS sınıf varsayılanlarından gelir (VARSAYIM); hardness_psi ile ezilebilir.
    """
    if target_class not in CLASS_DEFAULTS:
        raise KeyError(f"Bilinmeyen hedef sınıfı '{target_class}'; seçenekler: {list(CLASS_DEFAULTS)}")
    if length_m <= 0 or width_m <= 0:
        raise ValueError("Hedef boyutları pozitif olmalı")
    mechanism, psi, thermal, rcs = CLASS_DEFAULTS[target_class]
    penetration = round(concrete_equivalent_m(layers), 2) if mobility == FIXED else 0.0
    radius = round(math.sqrt(length_m * width_m / math.pi), 1)
    hard = penetration > 0 or target_class in (HARDENED, ARMORED)
    movement = "Fixed" if mobility == FIXED else "Mobile"
    target = {
        "Target_ID": CUSTOM_TARGET_ID,
        "Target_Category": f"{'Area' if radius >= AREA_RADIUS_THRESHOLD_M else 'Point'}/{'Hard' if hard else 'Soft'}/{movement}",
        "Target_Description": description.strip() or "Kullanıcı tanımlı hedef",
        "UFC_Hardness_Rating_psi": float(hardness_psi if hardness_psi else psi),
        "Required_Concrete_Penetration_m": penetration,
        "Target_Mobility_Class": mobility,
        "TST_Status": bool(tst),
        "Radar_Cross_Section_m2": rcs,
        "Required_Lethal_Radius_m": max(radius, 0.5),
        "Collateral_Damage_Tier": cde_tier,
        "Passive_Defense_Level": passive_level,
        "Thermal_Signature": thermal,
        "Target_Class": target_class,
        "Primary_Damage_Mechanism": mechanism,
        "Hardness_Basis": "Kullanıcı tanımlı hedef: sertlik sınıf varsayılanı, delme Young S sayılarıyla beton eşdeğeri",
        "Data_Confidence": "Varsayim",
    }
    check = pd.DataFrame([{c: str(target[c]) for c in TARGET_COLUMNS}], columns=TARGET_COLUMNS)
    errors = validate_targets(check, min_rows=1)
    if errors:
        raise ValueError("Geçersiz hedef tanımı:\n  " + "\n  ".join(errors))
    return target


def apply_desired_effect(target: dict, effect: str) -> tuple[dict, float]:
    """İstenen etkiye göre kapsanacak yarıçapı ölçekler; (hedef kopyası, hedeflenen hasar olasılığı) döner.

    Kapsanacak alan oranı f ise gerekli yarıçap √f ile çarpılır. Delme gereksinimi değişmez:
    kısmi yıkım için de yapının delinmesi gerekir.
    """
    if effect not in DESIRED_EFFECTS:
        raise KeyError(f"Bilinmeyen etki '{effect}'; seçenekler: {list(DESIRED_EFFECTS)}")
    _, fraction, desired, _ = DESIRED_EFFECTS[effect]
    scaled = dict(target)
    scaled["Required_Lethal_Radius_m"] = max(
        0.5, round(float(target["Required_Lethal_Radius_m"]) * math.sqrt(fraction), 2)
    )
    return scaled, desired


def impact_conditions(
    flight: str,
    release_alt_m: float,
    release_mach: float,
    max_mach: float,
    guided: bool,
    mechanism: str = "Blast",
    naval: bool = False,
) -> tuple[float, float]:
    """Yaklaşık çarpma açısı [° yataydan] ve çarpma hızı [m/s]. Sürükleme yoktur; hız azami Mach ile sınırlanır.

    flight: "free_fall" | "glide" | "powered"
      free_fall, güdümsüz : balistik açı atan(√(2gh) / v0)
      güdümlü             : terminal manevrayla hedef mekanizmasının istediği açıya (delme 70°, diğer 45°)
                            çıkabilir; balistik açı daha dikse o kullanılır; üst sınır 80°
      powered, deniz      : deniz yüzeyini yalayan profil (~10°)
    """
    v0 = release_mach * SOUND_SPEED
    cap = (IMPACT_MACH_DEFAULT if _isnan(max_mach) else float(max_mach)) * SOUND_SPEED
    vertical = math.sqrt(2.0 * GRAVITY * max(release_alt_m, 0.0))
    ballistic = math.degrees(math.atan2(vertical, max(v0, 1.0)))
    desired = DESIRED_IMPACT_ANGLE.get(mechanism, 45.0)
    if flight == "powered":
        angle = SEA_SKIM_ANGLE if naval else desired
        return angle, min(cap, IMPACT_MACH_RANGE[1] * SOUND_SPEED)
    speed = min(math.hypot(v0, vertical), cap)
    if not guided:
        return ballistic, speed
    return min(MAX_SHAPED_ANGLE, max(ballistic, desired)), speed


def penetration_at_impact(
    reference_depth_m: float, reference_mach: float, impact_speed: float, impact_angle_deg: float
) -> float:
    """Veri setindeki hızda hesaplanan dik delme değerini verilen çarpma hızı ve açısına ölçekler.

    Young: D ∝ (V - 30.5); eğik çarpmada yüzeye dik bileşen ≈ D · sin(açı) (basitleştirme).
    """
    if _isnan(reference_depth_m) or reference_depth_m <= 0:
        return 0.0
    ref_mach = IMPACT_MACH_DEFAULT if _isnan(reference_mach) else float(np.clip(reference_mach, *IMPACT_MACH_RANGE))
    scale = max(impact_speed - YOUNG_V0, 0.0) / (ref_mach * SOUND_SPEED - YOUNG_V0)
    return reference_depth_m * scale * math.sin(math.radians(impact_angle_deg))


def get_target(target_id, targets: pd.DataFrame | None = None, overrides: dict | None = None) -> dict:
    """Hedef satırını sözlük olarak döndürür; 'overrides' ile ne-olur analizi yapılabilir.

    target_id bir sözlükse (build_custom_target çıktısı gibi) matris yerine o hedef kullanılır.
    """
    if isinstance(target_id, dict):
        target = dict(target_id)
        missing = [c for c in TARGET_COLUMNS if c not in target]
        if missing:
            raise KeyError(f"Hedef sözlüğünde eksik alan(lar): {missing}")
        for col in TARGET_NUMERIC:
            target[col] = float(target[col])
        target["TST_Status"] = str(target["TST_Status"]) == "True"
        return _apply_overrides(target, overrides)
    targets = _default_targets() if targets is None else targets
    hit = targets[targets["Target_ID"] == target_id]
    if hit.empty:
        raise KeyError(f"Hedef bulunamadı: '{target_id}'. Geçerli kimlikler: {targets['Target_ID'].tolist()}")
    target = hit.iloc[0].to_dict()
    for col in TARGET_NUMERIC:
        target[col] = float(target[col])
    target["TST_Status"] = str(target["TST_Status"]) == "True"
    return _apply_overrides(target, overrides)


def _apply_overrides(target: dict, overrides: dict | None) -> dict:
    if overrides:
        unknown = [k for k in overrides if k not in TARGET_COLUMNS]
        if unknown:
            raise KeyError(f"Bilinmeyen hedef özniteliği: {unknown}")
        target.update(overrides)
        check = pd.DataFrame([{c: str(target[c]) for c in TARGET_COLUMNS}], columns=TARGET_COLUMNS)
        errors = validate_targets(check, min_rows=1)
        if errors:
            raise ValueError("Geçersiz hedef özniteliği:\n  " + "\n  ".join(errors))
    return target


def calculate_weapon_effectiveness(
    target_id,
    scenario: Scenario | None = None,
    munitions: pd.DataFrame | None = None,
    targets: pd.DataFrame | None = None,
    include_eliminated: bool = False,
    top_n: int | None = None,
    target_overrides: dict | None = None,
) -> pd.DataFrame:
    """Seçilen hedef için tüm mühimmatları Uygunluk Skoru'na (0-100) göre sıralar.

    Parametreler
      target_id          : hedef matrisindeki Target_ID (ör. "TGT-HAS-01") ya da hedef sözlüğü
      scenario           : hava savunma / ortam kısıtları (varsayılan: tehdit yok, açık hava)
      munitions, targets : verilmezse varsayılan dosyalardan yüklenir
      include_eliminated : True ise elenen ve verisi yetersiz kayıtlar da nedenleriyle döner
      top_n              : yalnız ilk n UYGUN kayıt
      target_overrides   : hedef özniteliklerini geçici değiştirir (duyarlılık analizi)

    Dönüş: RESULT_COLUMNS sütunlu DataFrame. Varsayılan olarak yalnız Durum == "UYGUN"
    satırları, skora göre azalan sırada. Eşit skorda (0.1 puan) daha hafif mühimmat öne alınır.
    """
    scenario = scenario or Scenario()
    target = get_target(target_id, targets, target_overrides)
    prepared = _default_munitions() if munitions is None else prepare_munitions(munitions)
    rows = [_evaluate(m, target, scenario) for m in prepared.to_dict("records")]
    result = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    result = result.round(_ROUNDING)
    result["_status"] = result["Durum"].map(STATUS_ORDER)
    result = (
        result.sort_values(
            ["_status", "Uygunluk_Skoru", "Toplam_Kutle_kg", "Muhimmat_Adi"],
            ascending=[True, False, True, True],
            na_position="last",
            kind="mergesort",
        )
        .drop(columns="_status")
        .reset_index(drop=True)
    )
    ok = result["Durum"] == STATUS_OK
    result.loc[ok, "Sira"] = np.arange(1, int(ok.sum()) + 1)
    if not include_eliminated:
        result = result[ok]
    if top_n is not None:
        keep = result[result["Durum"] == STATUS_OK].head(top_n)
        result = pd.concat([keep, result[result["Durum"] != STATUS_OK]]) if include_eliminated else keep
    result = result.reset_index(drop=True)
    result.attrs["target"] = target
    result.attrs["required_standoff_km"] = scenario.required_standoff_km
    return result


def recommend(target_id: str, scenario: Scenario | None = None, top_n: int = 5, **kwargs) -> pd.DataFrame:
    """En uygun n mühimmat (kısayol)."""
    return calculate_weapon_effectiveness(target_id, scenario, top_n=top_n, **kwargs)


def elimination_summary(all_results: pd.DataFrame) -> pd.DataFrame:
    """include_eliminated=True sonucundan eleme nedenlerinin dağılımı (birincil koda göre)."""
    labels = {
        "ROL": "Havadan havaya füze",
        "TASIYICI": "Taşıyıcı sınıfı filtresi",
        "PLATFORM": "Platform filtresi",
        "STANDOFF": "Standoff yetersiz",
        "MENZIL_VERISI_YOK": "Menzil verisi yok",
        "HARP_BASLIGI": "Harp başlığı tipi uygun değil",
        "DELME": "Delme yetersiz",
        "GUDUM": "Güdüm bilgisi yok",
        "GUDUM_MODU": "Kullanılabilir güdüm modu yok",
        "HAREKETLILIK": "Hareketli hedef için arayıcı yok",
        "VERI": "Kütle verisi yok",
        "ETKISIZ": f"Etki yetersiz (PK < {MIN_ELIGIBLE_PK:.2f})",
    }
    dropped = all_results[all_results["Durum"] != STATUS_OK]
    primary = dropped["Eleme_Kodu"].str.split(",").str[0].map(labels).fillna("Diğer")
    out = primary.value_counts().rename_axis("Neden").reset_index(name="Adet")
    return out


def _sweep(target_id: str, column: str, values, scenario, munitions, targets, pk_threshold: float) -> pd.DataFrame:
    prepared = _default_munitions() if munitions is None else prepare_munitions(munitions)
    current = get_target(target_id, targets)[column]
    rows = []
    for value in values:
        res = calculate_weapon_effectiveness(target_id, scenario, prepared, targets, target_overrides={column: value})
        best = res.iloc[0] if len(res) else None
        rows.append(
            {
                column: value,
                "Uygun_Muhimmat_Sayisi": len(res),
                "Etkili_Muhimmat_Sayisi": int((res["PK_Tek_Atis"] >= pk_threshold).sum()),
                "En_Yuksek_PK": float(res["PK_Tek_Atis"].max()) if len(res) else 0.0,
                "En_Yuksek_Skor": float(best["Uygunluk_Skoru"]) if best is not None else 0.0,
                "En_Iyi_Muhimmat": best["Muhimmat_Adi"] if best is not None else "-",
                "Mevcut": value == current,
            }
        )
    return pd.DataFrame(rows)


def sensitivity_passive_defense(
    target_id: str,
    scenario: Scenario | None = None,
    munitions: pd.DataFrame | None = None,
    targets: pd.DataFrame | None = None,
    pk_threshold: float = EFFECTIVE_PK_THRESHOLD,
) -> pd.DataFrame:
    """Pasif savunma düzeyi Low→Extreme değişirken tehdit envanterinin etkinliği."""
    return _sweep(target_id, "Passive_Defense_Level", PASSIVE_LEVELS, scenario, munitions, targets, pk_threshold)


def sensitivity_hardening(
    target_id: str,
    thicknesses=None,
    scenario: Scenario | None = None,
    munitions: pd.DataFrame | None = None,
    targets: pd.DataFrame | None = None,
    pk_threshold: float = EFFECTIVE_PK_THRESHOLD,
) -> pd.DataFrame:
    """Gerekli beton delme kalınlığı değişirken etkili kalan mühimmat sayısı."""
    if thicknesses is None:
        thicknesses = [round(x, 2) for x in np.arange(0.0, 6.01, 0.5)]
    return _sweep(
        target_id,
        "Required_Concrete_Penetration_m",
        [float(t) for t in thicknesses],
        scenario,
        munitions,
        targets,
        pk_threshold,
    )


# ---------------------------------------------------------------------------
# Komut satırı
# ---------------------------------------------------------------------------
CLI_COLUMNS = [
    "Sira",
    "Muhimmat_Adi",
    "Tasiyici_Sinifi",
    "Uygunluk_Skoru",
    "Ph",
    "Pd",
    "PK_Tek_Atis",
    "Beklenen_BDA",
    "Secilen_Gudum_Modu",
    "Olumcul_Yaricap_m",
    "Patlama_Yaricapi_m",
    "Tali_Hasar_Yaricapi_m",
    "Ucus_Suresi_s",
    "Maksimum_Menzil_km",
]


def _md_table(df: pd.DataFrame) -> str:
    def cell(v) -> str:
        if isinstance(v, float):
            return "-" if math.isnan(v) else (f"{v:.0f}" if v.is_integer() else f"{v:g}")
        return str(v)

    head = "| " + " | ".join(df.columns) + " |\n|" + "|".join("---" for _ in df.columns) + "|\n"
    return head + "\n".join("| " + " | ".join(cell(v) for v in row) + " |" for row in df.itertuples(index=False))


def write_report(path: str, top_n: int = 5) -> None:
    """Tüm hedefler için iki senaryoda (tehdit yok / uzun menzilli SAM) ilk n öneriyi yazar."""
    targets = _default_targets()
    cols = [
        "Sira",
        "Muhimmat_Adi",
        "Tasiyici_Sinifi",
        "Uygunluk_Skoru",
        "PK_Tek_Atis",
        "Gerekli_Atis_Sayisi",
        "Secilen_Gudum_Modu",
        "Maksimum_Menzil_km",
    ]
    names = ["#", "Mühimmat", "Taşıyıcı", "Skor", "PK", "Atış (P_D=0.90)", "Güdüm modu", "Menzil km"]
    lines = [
        "# Weaponeering Motoru - Toplu Sonuç Raporu\n",
        f"*Oluşturulma: {date.today().isoformat()} · Üretici: `src/weaponeering_engine.py --report`*\n",
        "> Sözde-PK değerleri temsilî katsayılı, kalibre edilmemiş bir sezgisel modelden gelir; "
        "JMEM/JAWS verisi değildir ve operasyonel planlama için kullanılamaz.\n",
    ]
    for t in targets.to_dict("records"):
        lines.append(f"## {t['Target_ID']} - {t['Target_Description']}\n")
        lines.append(
            f"`{t['Target_Category']}` · `{t['Target_Class']}` · sertlik {t['UFC_Hardness_Rating_psi']:g} psi "
            f"({t['Data_Confidence']}) · delme {t['Required_Concrete_Penetration_m']:g} m · "
            f"gerekli yarıçap {t['Required_Lethal_Radius_m']:g} m · {t['Target_Mobility_Class']} · "
            f"pasif savunma {t['Passive_Defense_Level']} · RCS {t['Radar_Cross_Section_m2']:g} m² · "
            f"termal {t['Thermal_Signature']} · TST {t['TST_Status']} · "
            f"mekanizma {t['Primary_Damage_Mechanism']} · CDE {t['Collateral_Damage_Tier']}\n"
        )
        for key in ("NONE", "LRSAM"):
            scenario = Scenario(air_defense=key)
            full = calculate_weapon_effectiveness(t["Target_ID"], scenario, include_eliminated=True)
            ok = full[full["Durum"] == STATUS_OK]
            tier = AIR_DEFENSE_TIERS[key]
            lines.append(
                f"**Hava savunma: {tier.label}** (standoff {tier.standoff_km:g} km) - "
                f"{len(ok)} uygun / {int((full['Durum'] == STATUS_ELIMINATED).sum())} elenen / "
                f"{int((full['Durum'] == STATUS_NO_DATA).sum())} verisi yetersiz\n"
            )
            if ok.empty:
                lines.append("_Bu koşullarda envanterde uygun mühimmat yok._\n")
                continue
            table = ok.head(top_n)[cols].copy()
            table["Sira"] = table["Sira"].astype(int)
            table["Uygunluk_Skoru"] = table["Uygunluk_Skoru"].map("{:.1f}".format)
            table["PK_Tek_Atis"] = table["PK_Tek_Atis"].map("{:.2f}".format)
            table["Gerekli_Atis_Sayisi"] = table["Gerekli_Atis_Sayisi"].map(
                lambda n: "99+" if n >= MAX_WEAPONS_REPORTED else f"{n:.0f}"
            )
            table.columns = names
            lines.append(_md_table(table) + "\n")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kural tabanlı weaponeering motoru (öğretici model)")
    ap.add_argument("target_id", nargs="?", help="Hedef kimliği (ör. TGT-HAS-01)")
    ap.add_argument("--list-targets", action="store_true", help="Hedef matrisini listele")
    ap.add_argument("--validate", action="store_true", help="Hedef matrisini doğrula")
    ap.add_argument("--top", type=int, default=5, help="Gösterilecek öneri sayısı")
    ap.add_argument("--air-defense", choices=list(AIR_DEFENSE_TIERS), default="NONE")
    ap.add_argument("--standoff", type=float, default=None, help="Gerekli standoff (km); kademeyi ezer")
    ap.add_argument("--weather", choices=list(WEATHER_FACTOR), default="CLEAR")
    ap.add_argument("--gnss-jamming", action="store_true")
    ap.add_argument("--no-laser", action="store_true", help="Lazer işaretleme imkânı yok")
    ap.add_argument("--carrier", nargs="*", default=[], choices=list(CARRIER_ORDER))
    ap.add_argument("--platform", default=None)
    ap.add_argument("--tst-window", type=float, default=TST_WINDOW_DEFAULT_S, help="TST penceresi (s)")
    ap.add_argument("--cde-tier", choices=list(CDE_RADIUS_LIMIT_M), default=None)
    ap.add_argument("--show-eliminated", action="store_true", help="Eleme nedenlerinin dağılımını göster")
    ap.add_argument("--report", metavar="PATH", help="Tüm hedefler için Markdown raporu yaz")
    args = ap.parse_args(argv)
    pd.set_option("display.width", 250)

    try:
        targets = _default_targets()
    except (FileNotFoundError, ValueError) as exc:
        print(exc)
        return 1
    if args.validate:
        print(
            f"Hedef matrisi geçerli: {len(targets)} hedef, {len(TARGET_COLUMNS)} sütun "
            f"({os.path.relpath(TARGET_MATRIX_PATH, ROOT)})"
        )
    if args.list_targets:
        print(targets.to_string(index=False))
    if args.report:
        write_report(args.report, args.top)
        print(f"Rapor yazıldı: {args.report}")
    if not args.target_id:
        return 0

    scenario = Scenario(
        air_defense=args.air_defense,
        standoff_km=args.standoff,
        weather=args.weather,
        gnss_jamming=args.gnss_jamming,
        laser_designation=not args.no_laser,
        carrier_classes=tuple(args.carrier),
        platform=args.platform,
        tst_window_s=args.tst_window,
        cde_tier=args.cde_tier,
    )
    try:
        full = calculate_weapon_effectiveness(args.target_id, scenario, include_eliminated=True)
    except KeyError as exc:
        print(exc.args[0])
        return 1
    target = full.attrs["target"]
    ok = full[full["Durum"] == STATUS_OK]
    print(f"\nHEDEF  {target['Target_ID']} - {target['Target_Description']}")
    print(
        f"       {target['Target_Category']} | {target['Target_Class']} | sertlik "
        f"{target['UFC_Hardness_Rating_psi']:g} psi | mekanizma {target['Primary_Damage_Mechanism']} | "
        f"TST {target['TST_Status']} | CDE {target['Collateral_Damage_Tier']}"
    )
    print(
        f"       delme {target['Required_Concrete_Penetration_m']:g} m | "
        f"yarıçap {target['Required_Lethal_Radius_m']:g} m | {target['Target_Mobility_Class']} | "
        f"pasif savunma {target['Passive_Defense_Level']}"
    )
    print(
        f"ORTAM  {AIR_DEFENSE_TIERS[scenario.air_defense].label} | standoff "
        f"{scenario.required_standoff_km:g} km | hava {WEATHER_LABELS[scenario.weather]} | "
        f"GNSS karıştırma {'var' if scenario.gnss_jamming else 'yok'} | "
        f"lazer işaretleme {'var' if scenario.laser_designation else 'yok'}"
    )
    print(
        f"SONUÇ  {len(ok)} uygun / {int((full['Durum'] == STATUS_ELIMINATED).sum())} elenen / "
        f"{int((full['Durum'] == STATUS_NO_DATA).sum())} verisi yetersiz\n"
    )
    if ok.empty:
        print("Bu koşullarda envanterde uygun mühimmat yok.")
    else:
        view = ok.head(args.top)[CLI_COLUMNS].copy()
        view["Sira"] = view["Sira"].astype(int)
        print(view.to_string(index=False))
    if args.show_eliminated:
        print("\nEleme nedenleri:\n" + elimination_summary(full).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
