#!/usr/bin/env python3
"""
Savunma Mühimmatı ve Etkileşim Simülasyon Platformu
====================================================

Hava platformlarından atılan füze ve bombaların (açık kaynak) veri setini
temel alan interaktif Streamlit panosu.

Çalıştırma:   streamlit run app.py

Modüller
--------
1. Envanter Gezgini      : filtre, akıllı arama, detay kartı, ölçekli profil
2. İstasyon Yükleme      : uçak seçimi, hardpoint yüklemesi, ağırlık kısıt kontrolü
3. Menzil Simülatörü     : irtifa/hız/hedef koşullarına göre efektif menzil, harita
4. Karşılaştırma Matrisi : 2-4 mühimmat için radar grafiği ve tablo

Veri kaynağı (sırayla denenir)
------------------------------
    data/master_air_munitions.csv
    data/processed/master_air_munitions_dataset.csv
    -> hiçbiri yoksa kod içine gömülü örnek veri (EMBEDDED_CSV)

UYARI: Tüm fizik modelleri öğretici/yaklaşık sezgisel modellerdir; platform
istasyon limitleri ve RCS indeksi temsilîdir. Operasyonel planlama, hedefleme
veya gerçek performans tahmini için KULLANILAMAZ.
"""
from __future__ import annotations

import html
import io
import math
import os
import unicodedata
from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Sayfa ayarı (ilk Streamlit çağrısı olmalıdır)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Mühimmat Simülasyon Platformu",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CANDIDATES = (
    os.path.join(APP_DIR, "data", "master_air_munitions.csv"),
    os.path.join(APP_DIR, "data", "processed", "master_air_munitions_dataset.csv"),
)

# ---------------------------------------------------------------------------
# Tema renkleri (koyu / füme / neon yeşil)
# ---------------------------------------------------------------------------
BG = "#0a0e0f"
PANEL = "#111a1c"
LINE = "#1f2d30"
GREEN = "#39ff14"
AMBER = "#ffb000"
RED = "#ff3b3b"
CYAN = "#4dd0e1"
PINK = "#ff6e9c"
TEXT = "#d7e0dc"
MUTED = "#8a9a95"

CSS = f"""
<style>
.block-container {{ padding-top: 3.6rem; max-width: 1500px; }}
h1, h2, h3, h4 {{ letter-spacing: .02em; }}
.app-title {{ font-family: monospace; font-size: 1.55rem; color: {GREEN};
  border-left: 4px solid {GREEN}; padding-left: .7rem; margin-bottom: .15rem; }}
.app-sub {{ color: {MUTED}; font-size: .85rem; margin-bottom: 1rem; padding-left: 1.1rem; }}
.kpi {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 6px;
  padding: .55rem .8rem; }}
.kpi .v {{ font-family: monospace; font-size: 1.45rem; color: {GREEN}; line-height: 1.2; }}
.kpi .l {{ color: {MUTED}; font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; }}
.card {{ background: {PANEL}; border: 1px solid {LINE}; border-top: 2px solid {GREEN};
  border-radius: 6px; padding: 1rem 1.2rem; }}
.card h3 {{ margin: 0 0 .1rem 0; color: {GREEN}; font-family: monospace; }}
.card .meta {{ color: {MUTED}; font-size: .82rem; margin-bottom: .7rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .5rem; }}
.cell {{ background: {BG}; border: 1px solid {LINE}; border-radius: 4px; padding: .4rem .6rem; }}
.cell .l {{ color: {MUTED}; font-size: .68rem; text-transform: uppercase; letter-spacing: .06em; }}
.cell .v {{ font-family: monospace; font-size: 1.05rem; color: {TEXT}; }}
.chip {{ display: inline-block; border: 1px solid {GREEN}; color: {GREEN}; border-radius: 12px;
  padding: .05rem .6rem; margin: .12rem .2rem .12rem 0; font-size: .78rem; font-family: monospace; }}
.badge {{ display: inline-block; border-radius: 3px; padding: .05rem .5rem; font-size: .72rem;
  font-family: monospace; margin-right: .4rem; }}
.badge.ok {{ background: rgba(57,255,20,.12); color: {GREEN}; border: 1px solid {GREEN}; }}
.badge.est {{ background: rgba(255,176,0,.12); color: {AMBER}; border: 1px solid {AMBER}; }}
.sbar {{ margin: .45rem 0; }}
.sbar-head {{ display: flex; justify-content: space-between; font-size: .8rem;
  font-family: monospace; color: {TEXT}; }}
.sbar-track {{ background: {BG}; border: 1px solid {LINE}; height: 11px; border-radius: 3px; overflow: hidden; }}
.sbar-fill {{ height: 100%; }}
.banner {{ border-radius: 5px; padding: .7rem 1rem; font-family: monospace; font-size: 1.05rem;
  margin-bottom: .6rem; text-align: center; letter-spacing: .06em; }}
.banner.ok {{ background: rgba(57,255,20,.10); border: 1px solid {GREEN}; color: {GREEN}; }}
.banner.fail {{ background: rgba(255,59,59,.10); border: 1px solid {RED}; color: {RED}; }}
.note {{ color: {MUTED}; font-size: .76rem; }}
.warnline {{ color: {AMBER}; font-size: .8rem; font-family: monospace; }}
.failline {{ color: {RED}; font-size: .8rem; font-family: monospace; }}
</style>
"""

# ---------------------------------------------------------------------------
# Gömülü örnek veri (CSV bulunamazsa uygulama yine de ayağa kalkar)
# ---------------------------------------------------------------------------
EMBEDDED_CSV = """Muhimmat_Adi;Mensei_Ulke;Uretici_Firma;Ana_Kategori;Alt_Kategori;Hizmete_Giris_Yili;Toplam_Kutle_kg;Harp_Basligi_Kutlesi_kg;Harp_Basligi_Tipi;Uzunluk_m;Cap_mm;Kanat_Acikligi_m;Maksimum_Menzil_km;Maksimum_Hiz_Mach;Itki_Sistemi;Gudum_Sistemi_Midcourse;Gudum_Sistemi_Terminal;Birim_Maliyet_USD;Entegre_Platformlar;Veri_Guvenilirlik_Notu
AIM-9X Block II;USA;Raytheon;Fuze;WVRAAM;2015;85.3;9.4;HE-Frag;3.02;127;0.45;35;2.5;Solid_Rocket;INS/Data-Link;IIR;472000;F-35,F-22,F-15,F-16,F/A-18;Tahmini_Acik_Kaynak
AIM-120D AMRAAM;USA;Raytheon;Fuze;BVRAAM;2015;161.5;20.5;HE-Frag;3.66;178;0.45;160;4.0;Solid_Rocket;INS/GPS/Data-Link;ARH;1090000;F-35,F-22,F-15,F-16,F/A-18;Tahmini_Acik_Kaynak
Meteor;EUR;MBDA;Fuze;BVRAAM;2016;190;NA;HE-Frag;3.65;178;NA;200;4.0;Ramjet;INS/Data-Link;ARH;2200000;Rafale,Eurofighter,Gripen,F-35;Tahmini_Acik_Kaynak
R-77-1 (RVV-SD);RUS;Vympel (KTRV);Fuze;BVRAAM;2015;190;22.5;HE-Frag;3.71;200;0.40;110;4.0;Solid_Rocket;INS/Data-Link;ARH;NA;Su-35,Su-57,Su-30SM,Su-34;Tahmini_Acik_Kaynak
PL-15;CHN;LOEC (AVIC);Fuze;BVRAAM;2016;230;NA;HE-Frag;4.0;203;NA;200;NA;Dual_Pulse_Rocket;INS/Data-Link;ARH;NA;J-20,J-10C,J-16,J-15,J-35;Tahmini_Acik_Kaynak
Bozdoğan;TUR;TÜBİTAK SAGE;Fuze;WVRAAM;NA;140;NA;HE-Frag;3.3;160;NA;25;4.0;Solid_Rocket;INS;IIR;NA;F-16,KAAN,Kızılelma,Hürjet;Acik_Kaynak_Dogrulanmis
Gökdoğan;TUR;TÜBİTAK SAGE;Fuze;BVRAAM;NA;NA;NA;HE-Frag;NA;NA;NA;65;NA;Solid_Rocket;INS/Data-Link;ARH;NA;F-16,KAAN,Kızılelma,Hürjet;Tahmini_Acik_Kaynak
AGM-158B JASSM-ER;USA;Lockheed Martin;Fuze;ALCM;2014;1021;450;Penetrator;4.27;550;2.4;926;0.8;Turbofan;INS/GPS;IIR;1500000;B-1B,B-52H,F-15E,F-16;Tahmini_Acik_Kaynak
Storm Shadow (SCALP-EG);EUR;MBDA;Fuze;ALCM;2003;1300;450;BROACH;5.1;480;2.84;560;0.8;Turbojet;INS/GPS/TERCOM;IIR;1000000;Tornado,Eurofighter,Rafale,Mirage 2000,Su-24M;Tahmini_Acik_Kaynak
SOM-J;TUR;TÜBİTAK SAGE/ROKETSAN;Fuze;ALCM;NA;540;140;SAPHE;NA;NA;NA;275;NA;Turbojet;INS/GPS/TERCOM/Data-Link;IIR;NA;F-16,KAAN,F-35;Tahmini_Acik_Kaynak
AGM-88E AARGM;USA;Northrop Grumman;Fuze;ARM;2012;361;66;HE-Frag;4.17;254;1.12;150;2.0;Solid_Rocket;INS/GPS/Data-Link;Passive_RF+MMW;870000;F/A-18,EA-18G,Tornado;Tahmini_Acik_Kaynak
Kh-31P;RUS;KTRV (Zvezda-Strela);Fuze;ARM;1988;600;87;HE-Frag;4.7;360;0.914;110;3.5;Ramjet;INS;Passive_RF;NA;Su-24M,Su-30,Su-34,MiG-29;Tahmini_Acik_Kaynak
AGM-114R Hellfire Romeo;USA;Lockheed Martin;Fuze;ATGM;2012;49;9;Tandem_HEAT;1.63;178;0.33;11;1.3;Solid_Rocket;INS;SAL;150000;MQ-9,AH-64,AH-1Z,MH-60R,MQ-1C;Tahmini_Acik_Kaynak
UMTAS;TUR;ROKETSAN;Fuze;ATGM;2016;37.5;NA;Tandem_HEAT;1.8;160;NA;8;NA;Solid_Rocket;INS/Data-Link;IIR;NA;T129,Akıncı,Aksungur;Tahmini_Acik_Kaynak
AGM-84L Harpoon Block II;USA;Boeing;Fuze;AShM;2001;526;221;SAPHE;3.84;343;0.91;220;0.85;Turbojet;INS/GPS;ARH;NA;P-8A,F/A-18,F-16,P-3C;Tahmini_Acik_Kaynak
Kh-47M2 Kinzhal;RUS;KTRV;Fuze;ALBM;2017;4300;480;HE-Frag;7.2;1000;NA;2000;10.0;Solid_Rocket;INS/GPS;NA;NA;MiG-31K,Tu-22M3;Tahmini_Acik_Kaynak
Atmaca (Havadan Atılan);TUR;ROKETSAN;Fuze;AShM;NA;NA;250;HE-Frag;NA;350;NA;250;NA;Turbojet;INS/GPS/TERCOM/Data-Link;ARH;NA;F-16;Tahmini_Acik_Kaynak
Mk-82;USA;General Dynamics;Gudumsuz_Bomba;GP_Bomb;1955;241;241;HE-Frag;2.22;273;NA;12;0.9;Free_Fall;Unpowered_Ballistic;Unguided;NA;F-16,F-15E,F/A-18,A-10,B-52H,F-4E 2020;Acik_Kaynak_Dogrulanmis
BLU-109/B;USA;Lockheed Martin;Gudumsuz_Bomba;Bunker_Buster;1985;874;874;Penetrator;2.5;368;NA;12;1.1;Free_Fall;Unpowered_Ballistic;Unguided;NA;F-15E,F-16,B-2;Tahmini_Acik_Kaynak
GBU-31(V)1/B JDAM;USA;Boeing;Gudumlu_Bomba;PGM_Laser_INS;1997;934;925;HE-Frag;3.88;457;NA;28;0.9;Free_Fall;INS/GPS;INS/GPS_Only;25000;F-16,F-15E,F/A-18,B-1B,B-2,B-52H;Tahmini_Acik_Kaynak
GBU-39 SDB I;USA;Boeing;Gudumlu_Bomba;PGM_Glide;2006;129;93;Penetrator;1.8;190;1.38;110;0.9;Glide_Unpowered;INS/GPS;INS/GPS_Only;40000;F-15E,F-16,F-35,F-22,B-1B,B-2,B-52H,AC-130J;Tahmini_Acik_Kaynak
HGK-84;TUR;TÜBİTAK SAGE;Gudumlu_Bomba;PGM_Laser_INS;NA;950;925;HE-Frag;3.9;457;NA;28;0.9;Free_Fall;INS/GPS;INS/GPS_Only;NA;F-16,F-4E 2020;Tahmini_Acik_Kaynak
Teber-82;TUR;ROKETSAN;Gudumlu_Bomba;PGM_Laser_INS;NA;270;241;HE-Frag;2.65;273;NA;NA;0.9;Free_Fall;INS/GPS;SAL;NA;F-16,F-4E 2020,Akıncı,Aksungur,Kızılelma;Tahmini_Acik_Kaynak
Tolun;TUR;ASELSAN;Gudumlu_Bomba;PGM_Glide;NA;139;NA;NA;NA;NA;NA;100;0.9;Glide_Unpowered;INS/GPS;INS/GPS_Only;NA;F-16,Akıncı,Kızılelma;Tahmini_Acik_Kaynak
KAB-500L;RUS;Region (KTRV);Gudumlu_Bomba;PGM_Laser_INS;1975;534;450;HE-Frag;3.05;400;0.75;9;0.9;Free_Fall;NA;SAL;NA;Su-24M,Su-30,Su-34,MiG-29;Tahmini_Acik_Kaynak
MAM-L;TUR;ROKETSAN;Gudumlu_Bomba;Micro_PGM;2016;22;NA;HE-Frag;1.0;160;NA;15;NA;Glide_Unpowered;INS/GPS;SAL;NA;TB2,TB3,Akıncı,Aksungur,Anka;Acik_Kaynak_Dogrulanmis
MAM-C;TUR;ROKETSAN;Gudumlu_Bomba;Micro_PGM;2018;6.5;NA;HE-Frag;0.97;70;NA;8;NA;Glide_Unpowered;NA;SAL;NA;TB2,Akıncı,Aksungur,Anka;Acik_Kaynak_Dogrulanmis
MAM-T IIR;TUR;ROKETSAN;Gudumlu_Bomba;Micro_PGM;NA;96;70;HE-Frag;NA;NA;NA;50;NA;Glide_Unpowered;INS/GPS;IIR;NA;Akıncı;Tahmini_Acik_Kaynak
"""

NUMERIC_COLS = [
    "Hizmete_Giris_Yili", "Toplam_Kutle_kg", "Harp_Basligi_Kutlesi_kg", "Uzunluk_m", "Cap_mm",
    "Kanat_Acikligi_m", "Maksimum_Menzil_km", "Maksimum_Hiz_Mach", "Birim_Maliyet_USD",
]
CATEGORY_LABELS = {
    "Fuze": "Füze",
    "Gudumlu_Bomba": "Güdümlü Bomba",
    "Gudumsuz_Bomba": "Güdümsüz Bomba",
    "Dolanan_Muhimmat": "Dolanan Mühimmat",
}
NATO = {"USA", "CAN", "GBR", "FRA", "DEU", "ITA", "NOR", "ESP", "SWE", "TUR", "EUR"}
BLOC_OPTIONS = ["NATO", "TUR", "RUS", "CHN", "ISR", "Diğer"]
EMPTY = "— boş —"
KM_PER_NM = 1.852
FT = 0.3048
G0 = 9.80665


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def norm_text(text: str) -> str:
    """Aksan ve büyük/küçük harf farkını yok sayan arama normalizasyonu."""
    text = str(text).replace("ı", "i").replace("İ", "i")
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).casefold()


def fmt(value, unit: str = "", digits: int = 1) -> str:
    """NaN -> 'NA'; aksi halde birimli sayı."""
    if value is None or (isinstance(value, float) and math.isnan(value)) or pd.isna(value):
        return "NA"
    if float(value).is_integer() and digits <= 1:
        s = f"{value:,.0f}"
    else:
        s = f"{value:,.{digits}f}"
    return f"{s} {unit}".strip()


def e(text) -> str:
    return html.escape(str(text))


def tokens(value: str, sep: str) -> list[str]:
    return [] if value in ("NA", "") else [t for t in str(value).split(sep) if t]


def terminal_tokens(value: str) -> list[str]:
    return tokens(value, "+")


def midcourse_tokens(value: str) -> list[str]:
    return tokens(value, "/")


def platform_list(row: pd.Series) -> list[str]:
    return tokens(row["Entegre_Platformlar"], ",")


def bloc_match(country: str, selected: list[str]) -> bool:
    if not selected:
        return True
    in_blocs = set()
    if country in NATO:
        in_blocs.add("NATO")
    if country == "TUR":
        in_blocs.add("TUR")
    for key in ("RUS", "CHN", "ISR"):
        if country == key:
            in_blocs.add(key)
    if not in_blocs:
        in_blocs.add("Diğer")
    return bool(in_blocs & set(selected))


# ---------------------------------------------------------------------------
# Veri yükleme
# ---------------------------------------------------------------------------
def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.apply(lambda s: s.str.strip())
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col].replace("NA", np.nan), errors="coerce")
    df["Payload_Fraction"] = df["Harp_Basligi_Kutlesi_kg"] / df["Toplam_Kutle_kg"]
    df["Kategori_TR"] = df["Ana_Kategori"].map(CATEGORY_LABELS).fillna(df["Ana_Kategori"])
    return df.drop_duplicates(subset="Muhimmat_Adi").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, str]:
    for path in DATA_CANDIDATES:
        if os.path.exists(path):
            df = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
            if df.shape[1] == 1:  # ayraç ',' olabilir
                df = pd.read_csv(path, sep=",", dtype=str, keep_default_na=False, encoding="utf-8")
            return _prepare(df), os.path.relpath(path, APP_DIR)
    df = pd.read_csv(io.StringIO(EMBEDDED_CSV), sep=";", dtype=str, keep_default_na=False)
    return _prepare(df), "gömülü örnek veri (CSV bulunamadı)"


# ---------------------------------------------------------------------------
# Hava platformu veritabanı (TEMSİLÎ / YAKLAŞIK açık kaynak değerler)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Station:
    sid: str
    label: str
    kind: str            # wingtip | wing | fuselage | internal
    max_kg: float
    x: float             # hardpoint haritası: yanal konum (-1..1)
    y: float             # hardpoint haritası: boyuna konum
    max_len_m: float | None = None    # yalnızca dahili bölmeler
    max_dia_mm: float | None = None


@dataclass(frozen=True)
class Platform:
    name: str
    aliases: tuple[str, ...]      # veri setindeki 'Entegre_Platformlar' eşleşmesi (küçük harf)
    kind: str                     # "Savaş uçağı" | "SİHA"
    empty_kg: float
    fuel_kg: float
    mtow_kg: float
    max_payload_kg: float
    low_observable: bool
    stations: tuple[Station, ...]
    note: str = "Temsili/yaklaşık açık kaynak değerler"


def _s(sid, label, kind, max_kg, x, y, max_len=None, max_dia=None) -> Station:
    return Station(sid, label, kind, max_kg, x, y, max_len, max_dia)


def _build_platforms() -> dict[str, Platform]:
    p: list[Platform] = []

    p.append(Platform(
        "F-16C Block 70", ("f-16",), "Savaş uçağı", 8570, 3175, 21772, 7700, False, (
            _s("S1", "Kanat ucu SOL", "wingtip", 200, -1.00, -0.10),
            _s("S2", "Dış kanat SOL", "wing", 450, -0.78, -0.05),
            _s("S3", "Orta kanat SOL", "wing", 1100, -0.56, 0.00),
            _s("S4", "İç kanat SOL", "wing", 2000, -0.34, 0.05),
            _s("S5", "Gövde altı (merkez)", "fuselage", 1130, 0.00, 0.15),
            _s("S6", "İç kanat SAĞ", "wing", 2000, 0.34, 0.05),
            _s("S7", "Orta kanat SAĞ", "wing", 1100, 0.56, 0.00),
            _s("S8", "Dış kanat SAĞ", "wing", 450, 0.78, -0.05),
            _s("S9", "Kanat ucu SAĞ", "wingtip", 200, 1.00, -0.10),
        )))

    p.append(Platform(
        "F-35A Lightning II", ("f-35",), "Savaş uçağı", 13290, 8280, 31800, 8160, True, (
            _s("B1", "Dahili HH bölmesi SOL", "internal", 200, -0.10, 0.30, 3.8, 220),
            _s("B2", "Dahili HH bölmesi SAĞ", "internal", 200, 0.10, 0.30, 3.8, 220),
            _s("B3", "Dahili bomba bölmesi SOL", "internal", 1000, -0.10, 0.05, 4.5, 500),
            _s("B4", "Dahili bomba bölmesi SAĞ", "internal", 1000, 0.10, 0.05, 4.5, 500),
            _s("W1", "Kanat dışı SOL", "wingtip", 200, -1.00, -0.10),
            _s("W2", "Kanat orta SOL", "wing", 1130, -0.72, -0.02),
            _s("W3", "Kanat iç SOL", "wing", 2270, -0.45, 0.04),
            _s("W4", "Kanat iç SAĞ", "wing", 2270, 0.45, 0.04),
            _s("W5", "Kanat orta SAĞ", "wing", 1130, 0.72, -0.02),
            _s("W6", "Kanat dışı SAĞ", "wingtip", 200, 1.00, -0.10),
        )))

    p.append(Platform(
        "F-15E Strike Eagle", ("f-15",), "Savaş uçağı", 14300, 5950, 36700, 11000, False, (
            _s("A1", "Kanat pilonu SOL", "wing", 2300, -0.60, 0.00),
            _s("A2", "Gövde merkez", "fuselage", 2300, 0.00, 0.12),
            _s("A3", "Kanat pilonu SAĞ", "wing", 2300, 0.60, 0.00),
            _s("C1", "CFT ön SOL", "fuselage", 1100, -0.22, 0.20),
            _s("C2", "CFT arka SOL", "fuselage", 1100, -0.22, -0.05),
            _s("C3", "CFT ön SAĞ", "fuselage", 1100, 0.22, 0.20),
            _s("C4", "CFT arka SAĞ", "fuselage", 1100, 0.22, -0.05),
            _s("M1", "Gövde HH SOL ön", "fuselage", 250, -0.12, 0.28),
            _s("M2", "Gövde HH SAĞ ön", "fuselage", 250, 0.12, 0.28),
        )))

    p.append(Platform(
        "Eurofighter Typhoon", ("eurofighter",), "Savaş uçağı", 11000, 5000, 23500, 9000, False, (
            _s("E1", "Dış kanat SOL", "wing", 300, -0.85, -0.02),
            _s("E2", "Orta kanat SOL", "wing", 1000, -0.62, 0.00),
            _s("E3", "İç kanat SOL", "wing", 1500, -0.40, 0.04),
            _s("E4", "Gövde merkez", "fuselage", 1000, 0.00, 0.12),
            _s("E5", "İç kanat SAĞ", "wing", 1500, 0.40, 0.04),
            _s("E6", "Orta kanat SAĞ", "wing", 1000, 0.62, 0.00),
            _s("E7", "Dış kanat SAĞ", "wing", 300, 0.85, -0.02),
            _s("E8", "Gövde yarı gömme SOL ön", "fuselage", 250, -0.14, 0.22),
            _s("E9", "Gövde yarı gömme SOL arka", "fuselage", 250, -0.14, 0.02),
            _s("E10", "Gövde yarı gömme SAĞ ön", "fuselage", 250, 0.14, 0.22),
            _s("E11", "Gövde yarı gömme SAĞ arka", "fuselage", 250, 0.14, 0.02),
        )))

    p.append(Platform(
        "Rafale", ("rafale",), "Savaş uçağı", 10300, 4700, 24500, 9500, False, (
            _s("R1", "Kanat ucu SOL", "wingtip", 200, -1.00, -0.08),
            _s("R2", "Dış kanat SOL", "wing", 300, -0.78, -0.03),
            _s("R3", "Orta kanat SOL", "wing", 1000, -0.55, 0.02),
            _s("R4", "İç kanat SOL", "wing", 2000, -0.32, 0.06),
            _s("R5", "Gövde merkez", "fuselage", 1500, 0.00, 0.14),
            _s("R6", "İç kanat SAĞ", "wing", 2000, 0.32, 0.06),
            _s("R7", "Orta kanat SAĞ", "wing", 1000, 0.55, 0.02),
            _s("R8", "Dış kanat SAĞ", "wing", 300, 0.78, -0.03),
            _s("R9", "Kanat ucu SAĞ", "wingtip", 200, 1.00, -0.08),
            _s("R10", "Gövde SOL", "fuselage", 300, -0.14, 0.20),
            _s("R11", "Gövde SAĞ", "fuselage", 300, 0.14, 0.20),
        )))

    p.append(Platform(
        "Su-35S", ("su-35",), "Savaş uçağı", 19000, 11500, 34500, 8000, False, (
            _s("K1", "Kanat ucu SOL", "wingtip", 200, -1.00, -0.08),
            _s("K2", "Dış kanat SOL", "wing", 1500, -0.70, -0.02),
            _s("K3", "İç kanat SOL", "wing", 1500, -0.42, 0.04),
            _s("K4", "Gövde SOL", "fuselage", 700, -0.16, 0.14),
            _s("K5", "Gövde SAĞ", "fuselage", 700, 0.16, 0.14),
            _s("K6", "İç kanat SAĞ", "wing", 1500, 0.42, 0.04),
            _s("K7", "Dış kanat SAĞ", "wing", 1500, 0.70, -0.02),
            _s("K8", "Kanat ucu SAĞ", "wingtip", 200, 1.00, -0.08),
        )))

    p.append(Platform(
        "KAAN", ("kaan",), "Savaş uçağı", 14000, 7500, 27000, 8000, True, (
            _s("D1", "Dahili HH bölmesi SOL-1", "internal", 250, -0.14, 0.30, 3.9, 230),
            _s("D2", "Dahili HH bölmesi SOL-2", "internal", 250, -0.08, 0.30, 3.9, 230),
            _s("D3", "Dahili HH bölmesi SAĞ-1", "internal", 250, 0.08, 0.30, 3.9, 230),
            _s("D4", "Dahili HH bölmesi SAĞ-2", "internal", 250, 0.14, 0.30, 3.9, 230),
            _s("D5", "Dahili ana bölme SOL", "internal", 1000, -0.08, 0.05, 4.7, 520),
            _s("D6", "Dahili ana bölme SAĞ", "internal", 1000, 0.08, 0.05, 4.7, 520),
            _s("X1", "Kanat dışı SOL", "wing", 300, -0.85, -0.02),
            _s("X2", "Kanat orta SOL", "wing", 1000, -0.60, 0.02),
            _s("X3", "Kanat iç SOL", "wing", 1500, -0.38, 0.06),
            _s("X4", "Kanat iç SAĞ", "wing", 1500, 0.38, 0.06),
            _s("X5", "Kanat orta SAĞ", "wing", 1000, 0.60, 0.02),
            _s("X6", "Kanat dışı SAĞ", "wing", 300, 0.85, -0.02),
        ), note="Geliştirme aşamasında; tüm değerler tahminidir"))

    p.append(Platform(
        "Bayraktar Kızılelma", ("kızılelma", "kizilelma"), "SİHA", 3400, 1100, 6000, 1500, True, (
            _s("I1", "Dahili bölme SOL", "internal", 300, -0.08, 0.10, 3.3, 330),
            _s("I2", "Dahili bölme SAĞ", "internal", 300, 0.08, 0.10, 3.3, 330),
            _s("Y1", "Kanat altı SOL", "wing", 450, -0.55, 0.02),
            _s("Y2", "Kanat altı SAĞ", "wing", 450, 0.55, 0.02),
        ), note="Tahmini; üretici tam yük profili yayımlamamıştır"))

    p.append(Platform(
        "Bayraktar Akıncı", ("akıncı", "akinci"), "SİHA", 3300, 850, 5500, 1350, False, (
            _s("H1", "Dış kanat SOL", "wing", 150, -0.85, 0.00),
            _s("H2", "Orta kanat SOL", "wing", 300, -0.60, 0.02),
            _s("H3", "İç kanat SOL", "wing", 450, -0.35, 0.04),
            _s("H4", "İç kanat SAĞ", "wing", 450, 0.35, 0.04),
            _s("H5", "Orta kanat SAĞ", "wing", 300, 0.60, 0.02),
            _s("H6", "Dış kanat SAĞ", "wing", 150, 0.85, 0.00),
        )))

    p.append(Platform(
        "Bayraktar TB2", ("tb2",), "SİHA", 400, 150, 700, 150, False, (
            _s("T1", "Kanat altı SOL-dış", "wing", 60, -0.62, 0.00),
            _s("T2", "Kanat altı SOL-iç", "wing", 60, -0.34, 0.03),
            _s("T3", "Kanat altı SAĞ-iç", "wing", 60, 0.34, 0.03),
            _s("T4", "Kanat altı SAĞ-dış", "wing", 60, 0.62, 0.00),
        )))

    return {pl.name: pl for pl in p}


PLATFORMS = _build_platforms()


# ---------------------------------------------------------------------------
# Atmosfer ve menzil modeli (öğretici sezgisel model)
# ---------------------------------------------------------------------------
REF_ALT_M = 35_000 * FT   # veri setindeki "optimum yüksek irtifa" referansı
REF_MACH = 0.9


def isa_temperature(h: float) -> float:
    return 288.15 - 0.0065 * h if h <= 11_000 else 216.65


def isa_density(h: float) -> float:
    if h <= 11_000:
        return 1.225 * (isa_temperature(h) / 288.15) ** 4.2559
    return 0.36392 * math.exp(-(h - 11_000) / 6341.6)


def speed_of_sound(h: float) -> float:
    return math.sqrt(1.4 * 287.05 * isa_temperature(h))


def propulsion_group(itki: str) -> str:
    if itki == "Free_Fall":
        return "free_fall"
    if itki == "Glide_Unpowered":
        return "glide"
    if itki in ("Turbojet", "Turbofan", "Electric_Propeller"):
        return "cruise"
    if itki == "Ramjet":
        return "ramjet"
    return "rocket"


def is_air_target_class(row: pd.Series) -> bool:
    return row["Alt_Kategori"] in ("WVRAAM", "BVRAAM")


def effective_range(row: pd.Series, alt_m: float, mach: float, tgt_alt_m: float) -> dict:
    """Baz menzili irtifa, atış hızı ve hedef irtifasına göre ölçekler.

    Model (basitleştirilmiş, sürükleme ve manevra ayrıntısı yok):
      * Serbest düşüş : R ∝ v_atış · √(düşüş yüksekliği)            (balistik)
      * Süzülen       : R ∝ özgül enerji yüksekliği (h + v²/2g)       (süzülme oranı sabit)
      * Roket/Ramjet  : R ∝ (ρ_ref / ρ_ort)^k · (v_füze + M_atış)/(v_füze + M_ref)
      * Turbojet/fan  : zayıf irtifa bağımlılığı (k = 0.12), hıza duyarsız
    Referans: 35.000 ft, Mach 0.9 (veri setindeki baz menzil koşulu).
    """
    base = float(row["Maksimum_Menzil_km"])
    grp = propulsion_group(row["Itki_Sistemi"])
    air = is_air_target_class(row)
    ref_tgt = REF_ALT_M if air else 0.0
    h_mean = max((alt_m + tgt_alt_m) / 2, 0.0)
    ref_mean = (REF_ALT_M + ref_tgt) / 2
    v = mach * speed_of_sound(alt_m)
    v_ref = REF_MACH * speed_of_sound(REF_ALT_M)
    mach_max = row["Maksimum_Hiz_Mach"]
    if pd.isna(mach_max):
        mach_max = {"rocket": 3.0, "ramjet": 3.0, "cruise": 0.85}.get(grp, 0.9)
    drop = max(alt_m - tgt_alt_m, 1.0)
    ref_drop = max(REF_ALT_M - ref_tgt, 1.0)
    parts: dict[str, float] = {}

    if grp == "free_fall":
        parts["Atış hızı (v)"] = v / v_ref
        parts["Düşüş yüksekliği (√h)"] = math.sqrt(drop / ref_drop)
    elif grp == "glide":
        he = max(alt_m - tgt_alt_m, 0.0) + v ** 2 / (2 * G0)
        he_ref = (REF_ALT_M - ref_tgt) + v_ref ** 2 / (2 * G0)
        parts["Özgül enerji yüksekliği"] = he / he_ref
    elif grp in ("rocket", "ramjet"):
        k = 0.7 if grp == "rocket" else 0.35
        parts["Hava yoğunluğu (irtifa)"] = (isa_density(ref_mean) / isa_density(h_mean)) ** k
        vm = 0.6 * mach_max
        parts["Atış platformu hızı"] = (vm + mach) / (vm + REF_MACH)
    else:  # cruise
        parts["Hava yoğunluğu (irtifa)"] = (isa_density(ref_mean) / isa_density(h_mean)) ** 0.12

    ratio = float(np.clip(np.prod(list(parts.values())), 0.10, 2.5))
    eff = base * ratio

    # Yaklaşık uçuş süresi
    if grp == "free_fall":
        tof = math.sqrt(2 * drop / G0)
    elif grp == "glide":
        tof = eff * 1000 / max(0.75 * v, 50.0)
    elif grp == "cruise":
        tof = eff * 1000 / (mach_max * speed_of_sound(h_mean) * 0.95)
    else:
        tof = eff * 1000 / (0.6 * mach_max * speed_of_sound(h_mean))
    return {"base_km": base, "eff_km": eff, "ratio": ratio, "parts": parts, "tof_s": tof, "group": grp}


AAM_ASPECT = {"Kafa kafaya (head-on)": 1.0, "Yan (beam)": 0.8, "Kuyruk takibi (tail-chase)": 0.5}
AAM_MANEUVER = {"Manevra yok": 0.60, "Orta manevra": 0.40, "Sert manevra (9g+)": 0.25}
SURFACE_BEHAVIOR = {
    "Sabit hedef": 0.95,
    "Yavaş hareketli (≤30 kt)": 0.80,
    "Hızlı hareketli / manevralı": 0.60,
}


# ---------------------------------------------------------------------------
# Coğrafi yardımcılar (harita)
# ---------------------------------------------------------------------------
EARTH_R_KM = 6371.0088
CITY_PRESETS = {
    "Ankara": (39.93, 32.86),
    "İstanbul": (41.01, 28.98),
    "İzmir": (38.42, 27.14),
    "Konya": (37.87, 32.48),
    "Berlin": (52.52, 13.40),
    "Özel koordinat": (39.93, 32.86),
}


def destination_point(lat: float, lon: float, bearing_deg: float, dist_km: float) -> tuple[float, float]:
    d = dist_km / EARTH_R_KM
    b = math.radians(bearing_deg)
    la1, lo1 = math.radians(lat), math.radians(lon)
    la2 = math.asin(math.sin(la1) * math.cos(d) + math.cos(la1) * math.sin(d) * math.cos(b))
    lo2 = lo1 + math.atan2(math.sin(b) * math.sin(d) * math.cos(la1),
                           math.cos(d) - math.sin(la1) * math.sin(la2))
    return math.degrees(la2), (math.degrees(lo2) + 540) % 360 - 180


def geodesic_circle(lat: float, lon: float, radius_km: float, n: int = 181) -> tuple[list, list]:
    pts = [destination_point(lat, lon, b, radius_km) for b in np.linspace(0, 360, n)]
    return [p[0] for p in pts], [p[1] for p in pts]


def map_zoom(radius_km: float, lat: float) -> float:
    if radius_km <= 0:
        return 6.0
    z = math.log2(440 * 156543.03 * math.cos(math.radians(lat)) / (2 * radius_km * 1000)) - 1
    return float(np.clip(z, 0.6, 11.0))


# ---------------------------------------------------------------------------
# Plotly stil
# ---------------------------------------------------------------------------
def style_fig(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PANEL,
        font=dict(color=TEXT, family="monospace", size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        colorway=[GREEN, AMBER, CYAN, PINK],
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=LINE, zerolinecolor=LINE)
    fig.update_yaxes(gridcolor=LINE, zerolinecolor=LINE)
    return fig


def kpi(label: str, value: str) -> str:
    return f'<div class="kpi"><div class="v">{e(value)}</div><div class="l">{e(label)}</div></div>'


def status_bar(label: str, value: float, limit: float, unit: str, warn_at: float = 0.9) -> str:
    ratio = value / limit if limit else 0.0
    color = GREEN if ratio <= warn_at else AMBER if ratio <= 1.0 else RED
    width = min(ratio, 1.0) * 100
    return (
        f'<div class="sbar"><div class="sbar-head"><span>{e(label)}</span>'
        f'<span style="color:{color}">{value:,.0f} / {limit:,.0f} {e(unit)} ({ratio * 100:.0f}%)</span></div>'
        f'<div class="sbar-track"><div class="sbar-fill" style="width:{width:.1f}%;background:{color}"></div>'
        f'</div></div>'
    )


# ---------------------------------------------------------------------------
# MODÜL 1 — Envanter Gezgini
# ---------------------------------------------------------------------------
def apply_filters(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    out = df
    if f["blocs"]:
        out = out[out["Mensei_Ulke"].map(lambda c: bloc_match(c, f["blocs"]))]
    if f["countries"]:
        out = out[out["Mensei_Ulke"].isin(f["countries"])]
    if f["cats"]:
        out = out[out["Ana_Kategori"].isin(f["cats"])]
    if f["subs"]:
        out = out[out["Alt_Kategori"].isin(f["subs"])]
    lo, hi = f["years"]
    yr = out["Hizmete_Giris_Yili"]
    mask = yr.between(lo, hi)
    out = out[mask | (yr.isna() & f["include_na_year"])]
    if f["terminal"]:
        out = out[out["Gudum_Sistemi_Terminal"].map(lambda v: bool(set(terminal_tokens(v)) & set(f["terminal"])))]
    if f["midcourse"]:
        out = out[out["Gudum_Sistemi_Midcourse"].map(lambda v: bool(set(midcourse_tokens(v)) & set(f["midcourse"])))]
    q = norm_text(f["query"]).split()
    if q:
        hay = (out["Muhimmat_Adi"] + " " + out["Uretici_Firma"] + " " + out["Entegre_Platformlar"]
               + " " + out["Mensei_Ulke"]).map(norm_text)
        out = out[hay.map(lambda h: all(t in h for t in q))]
    return out


def profile_figure(row: pd.Series) -> go.Figure | None:
    length, dia_mm = row["Uzunluk_m"], row["Cap_mm"]
    if pd.isna(length) or pd.isna(dia_mm):
        return None
    d = dia_mm / 1000
    nose = min(0.18 * length, 3 * d)
    xs = [0, length - nose, length, length - nose, 0, 0]
    ys = [-d / 2, -d / 2, 0, d / 2, d / 2, -d / 2]
    fig = go.Figure(go.Scatter(x=xs, y=ys, fill="toself", mode="lines", line=dict(color=GREEN, width=1.5),
                               fillcolor="rgba(57,255,20,.12)", hoverinfo="skip"))
    span = row["Kanat_Acikligi_m"]
    if not pd.isna(span):
        xr = length * 0.55
        fig.add_trace(go.Scatter(x=[xr, xr + 0.12 * length], y=[span / 2, 0], mode="lines",
                                 line=dict(color=AMBER, width=1.2), hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=[xr, xr + 0.12 * length], y=[-span / 2, 0], mode="lines",
                                 line=dict(color=AMBER, width=1.2), hoverinfo="skip", showlegend=False))
    fig.add_annotation(x=length / 2, y=-d / 2, yshift=-14, showarrow=False,
                       text=f"{length:.2f} m × Ø{dia_mm:.0f} mm", font=dict(color=MUTED, size=11))
    style_fig(fig, 170)
    fig.update_layout(showlegend=False, margin=dict(l=5, r=5, t=5, b=5),
                      xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1))
    return fig


def render_detail_card(row: pd.Series) -> None:
    rel_ok = row["Veri_Guvenilirlik_Notu"] == "Acik_Kaynak_Dogrulanmis"
    badge = ('<span class="badge ok">AÇIK KAYNAK · DOĞRULANMIŞ</span>' if rel_ok
             else '<span class="badge est">TAHMİNİ · AÇIK KAYNAK</span>')
    chips = "".join(f'<span class="chip">{e(p)}</span>' for p in platform_list(row)) or '<span class="note">NA</span>'
    pf = row["Payload_Fraction"]
    cells = [
        ("Toplam kütle", fmt(row["Toplam_Kutle_kg"], "kg")),
        ("Harp başlığı", fmt(row["Harp_Basligi_Kutlesi_kg"], "kg")),
        ("Harp başlığı oranı", "NA" if pd.isna(pf) else f"{pf * 100:.1f} %"),
        ("Harp başlığı tipi", row["Harp_Basligi_Tipi"]),
        ("Uzunluk", fmt(row["Uzunluk_m"], "m", 2)),
        ("Çap", fmt(row["Cap_mm"], "mm", 0)),
        ("Kanat açıklığı", fmt(row["Kanat_Acikligi_m"], "m", 2)),
        ("Maks. menzil", fmt(row["Maksimum_Menzil_km"], "km")),
        ("Maks. hız", fmt(row["Maksimum_Hiz_Mach"], "Mach")),
        ("İtki sistemi", row["Itki_Sistemi"]),
        ("Güdüm (orta safha)", row["Gudum_Sistemi_Midcourse"]),
        ("Güdüm (terminal)", row["Gudum_Sistemi_Terminal"]),
        ("Hizmete giriş", fmt(row["Hizmete_Giris_Yili"], "", 0)),
        ("Birim maliyet", "NA" if pd.isna(row["Birim_Maliyet_USD"]) else f"${row['Birim_Maliyet_USD']:,.0f}"),
    ]
    grid = "".join(f'<div class="cell"><div class="l">{e(l)}</div><div class="v">{e(v)}</div></div>' for l, v in cells)
    st.markdown(
        f'<div class="card"><h3>{e(row["Muhimmat_Adi"])}</h3>'
        f'<div class="meta">{e(row["Uretici_Firma"])} · {e(row["Mensei_Ulke"])} · '
        f'{e(row["Kategori_TR"])} / {e(row["Alt_Kategori"])}</div>'
        f'<div style="margin-bottom:.6rem">{badge}</div>'
        f'<div class="grid">{grid}</div>'
        f'<div style="margin-top:.8rem"><div class="cell" style="border:none;padding:0">'
        f'<div class="l">Entegre platformlar</div></div>{chips}</div></div>',
        unsafe_allow_html=True,
    )
    fig = profile_figure(row)
    if fig is not None:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def tab_inventory(df: pd.DataFrame) -> None:
    left, right = st.columns([1, 3], gap="large")
    with left:
        st.markdown("#### Filtreler")
        query = st.text_input("Akıllı arama", placeholder="ör. akinci, roketsan, f-35 …",
                              help="Ad, üretici, platform ve ülkede arar; aksan/harf farkını yok sayar.")
        blocs = st.multiselect("Ülke / Blok", BLOC_OPTIONS)
        countries = st.multiselect("Ülke (ISO)", sorted(df["Mensei_Ulke"].unique()))
        cats = st.multiselect("Ana kategori", list(CATEGORY_LABELS),
                              format_func=lambda c: CATEGORY_LABELS[c])
        subs_pool = sorted(df[df["Ana_Kategori"].isin(cats)]["Alt_Kategori"].unique()) if cats \
            else sorted(df["Alt_Kategori"].unique())
        subs = st.multiselect("Alt kategori", subs_pool)
        ymin = int(df["Hizmete_Giris_Yili"].min()) if df["Hizmete_Giris_Yili"].notna().any() else 1950
        ymax = int(df["Hizmete_Giris_Yili"].max()) if df["Hizmete_Giris_Yili"].notna().any() else 2030
        years = st.slider("Hizmete giriş yılı", ymin, max(ymax, ymin + 1), (ymin, max(ymax, ymin + 1)))
        include_na = st.checkbox("Yılı bilinmeyenleri (NA) dahil et", value=True)
        term_pool = sorted({t for v in df["Gudum_Sistemi_Terminal"] for t in terminal_tokens(v)})
        mid_pool = sorted({t for v in df["Gudum_Sistemi_Midcourse"] for t in midcourse_tokens(v)})
        terminal = st.multiselect("Terminal güdüm", term_pool, help="ARH, IIR, SAL, INS/GPS_Only …")
        midcourse = st.multiselect("Orta safha güdüm", mid_pool, help="INS, GPS, Data-Link …")

    filt = apply_filters(df, dict(query=query, blocs=blocs, countries=countries, cats=cats, subs=subs,
                                  years=years, include_na_year=include_na, terminal=terminal,
                                  midcourse=midcourse))
    with right:
        c = st.columns(4)
        c[0].markdown(kpi("Eşleşen kayıt", f"{len(filt)} / {len(df)}"), unsafe_allow_html=True)
        c[1].markdown(kpi("Ülke", str(filt["Mensei_Ulke"].nunique())), unsafe_allow_html=True)
        c[2].markdown(kpi("Medyan menzil", fmt(filt["Maksimum_Menzil_km"].median(), "km")), unsafe_allow_html=True)
        c[3].markdown(kpi("Medyan kütle", fmt(filt["Toplam_Kutle_kg"].median(), "kg")), unsafe_allow_html=True)
        st.write("")
        if filt.empty:
            st.warning("Filtrelerle eşleşen mühimmat yok.")
            return

        show = filt[["Muhimmat_Adi", "Mensei_Ulke", "Uretici_Firma", "Kategori_TR", "Alt_Kategori",
                     "Hizmete_Giris_Yili", "Toplam_Kutle_kg", "Maksimum_Menzil_km", "Maksimum_Hiz_Mach",
                     "Gudum_Sistemi_Terminal"]].reset_index(drop=True)
        show.columns = ["Mühimmat", "Ülke", "Üretici", "Kategori", "Alt kat.", "Yıl", "Kütle (kg)",
                        "Menzil (km)", "Mach", "Terminal güdüm"]
        styled = show.style.format({"Yıl": "{:.0f}", "Kütle (kg)": "{:,.0f}", "Menzil (km)": "{:,.0f}",
                                    "Mach": "{:.2f}"}, na_rep="NA")
        event = st.dataframe(styled, width="stretch", height=300, hide_index=True,
                             on_select="rerun", selection_mode="single-row", key="inv_table")
        st.download_button("Filtrelenmiş veriyi indir (CSV)",
                           filt.drop(columns=["Kategori_TR"]).to_csv(sep=";", index=False).encode("utf-8"),
                           "filtrelenmis_muhimmat.csv", "text/csv")

        sel_rows = event.selection.rows if event and event.selection else []
        names = filt["Muhimmat_Adi"].tolist()
        if sel_rows:
            chosen = filt.iloc[sel_rows[0]]["Muhimmat_Adi"]
            st.caption(f"Tabloda seçili: **{chosen}**")
        else:
            chosen = st.selectbox("Detay kartı için mühimmat seçin (veya tablodan satır seçin)", names)
        render_detail_card(filt[filt["Muhimmat_Adi"] == chosen].iloc[0])


# ---------------------------------------------------------------------------
# MODÜL 2 — İstasyon yükleme ve uyumluluk
# ---------------------------------------------------------------------------
def integrated(row: pd.Series, plat: Platform) -> bool:
    hay = row["Entegre_Platformlar"].lower()
    return any(a in hay for a in plat.aliases)


def evaluate_loadout(plat: Platform, selections: dict[str, str], by_name: pd.DataFrame, fuel_pct: float) -> dict:
    rows, total, frontal, cost, cost_na, mass_na = [], 0.0, 0.0, 0.0, 0, 0
    rcs = 100.0
    for stn in plat.stations:
        name = selections.get(stn.sid, EMPTY)
        if name == EMPTY or name not in by_name.index:
            rows.append(dict(stn=stn, name=None, mass=0.0, status="empty", msgs=[]))
            continue
        m = by_name.loc[name]
        mass = m["Toplam_Kutle_kg"]
        msgs, status = [], "ok"
        if pd.isna(mass):
            msgs.append("kütle verisi NA — hesaba katılmadı")
            status = "warn"
            mass = 0.0
            mass_na += 1
        if mass > stn.max_kg:
            msgs.append(f"istasyon limiti aşıldı ({mass:.0f} > {stn.max_kg:.0f} kg)")
            status = "fail"
        if stn.kind == "internal":
            if stn.max_len_m and not pd.isna(m["Uzunluk_m"]) and m["Uzunluk_m"] > stn.max_len_m:
                msgs.append(f"bölmeye sığmaz (boy {m['Uzunluk_m']:.2f} > {stn.max_len_m:.2f} m)")
                status = "fail"
            if stn.max_dia_mm and not pd.isna(m["Cap_mm"]) and m["Cap_mm"] > stn.max_dia_mm:
                msgs.append(f"bölmeye sığmaz (çap {m['Cap_mm']:.0f} > {stn.max_dia_mm:.0f} mm)")
                status = "fail"
        if not integrated(m, plat):
            msgs.append("veri setinde bu platform için entegrasyon kaydı yok")
            if status == "ok":
                status = "warn"
        total += mass
        if stn.kind != "internal":
            d = 0.2 if pd.isna(m["Cap_mm"]) else m["Cap_mm"] / 1000
            frontal += 1.2 * math.pi / 4 * d ** 2
            k_fix, k_area = (35.0, 25.0) if plat.low_observable else (6.0, 4.0)
            rcs += k_fix + k_area * (d / 0.2) ** 2
        if pd.isna(m["Birim_Maliyet_USD"]):
            cost_na += 1
        else:
            cost += m["Birim_Maliyet_USD"]
        rows.append(dict(stn=stn, name=name, mass=mass, status=status, msgs=msgs))
    fuel = plat.fuel_kg * fuel_pct / 100
    gtow = plat.empty_kg + fuel + total
    fail_rows = [r for r in rows if r["status"] == "fail"]
    ok = not fail_rows and total <= plat.max_payload_kg and gtow <= plat.mtow_kg
    return dict(rows=rows, total=total, fuel=fuel, gtow=gtow, frontal=frontal, rcs=rcs, cost=cost,
                cost_na=cost_na, mass_na=mass_na, ok=ok, fail_rows=fail_rows,
                n_loaded=sum(1 for r in rows if r["name"]))


def hardpoint_figure(plat: Platform, ev: dict) -> go.Figure:
    fig = go.Figure()
    fig.add_shape(type="line", x0=0, x1=0, y0=-0.55, y1=0.45, line=dict(color=MUTED, width=4))
    fig.add_shape(type="line", x0=-1.1, x1=1.1, y0=0.0, y1=0.0, line=dict(color=MUTED, width=2))
    colors = {"ok": GREEN, "warn": AMBER, "fail": RED, "empty": LINE}
    for r in ev["rows"]:
        stn = r["stn"]
        label = r["name"] or "boş"
        size = 16 if r["status"] == "empty" else 22
        fig.add_trace(go.Scatter(
            x=[stn.x], y=[stn.y], mode="markers+text", text=[stn.sid], textposition="top center",
            textfont=dict(color=TEXT, size=10), showlegend=False,
            marker=dict(size=size, color=colors[r["status"]], line=dict(color=TEXT, width=1),
                        symbol="diamond" if stn.kind == "internal" else "circle"),
            hovertemplate=f"<b>{stn.label}</b><br>{label}<br>limit {stn.max_kg:.0f} kg<extra></extra>"))
    style_fig(fig, 300)
    fig.update_layout(margin=dict(l=5, r=5, t=5, b=5),
                      xaxis=dict(visible=False, range=[-1.25, 1.25]),
                      yaxis=dict(visible=False, range=[-0.6, 0.55], scaleanchor="x", scaleratio=0.45))
    return fig


def tab_stations(df: pd.DataFrame) -> None:
    by_name = df.set_index("Muhimmat_Adi")
    top = st.columns([1.2, 1.2, 1, 1])
    plat = PLATFORMS[top[0].selectbox("Hava platformu", list(PLATFORMS))]
    fuel_pct = top[1].slider("Dahili yakıt doluluğu (%)", 0, 100, 60, 5)
    only_integrated = top[2].checkbox("Sadece entegre kayıtlı olanları listele", value=True)
    cat_filter = top[3].multiselect("Kategori filtresi", list(CATEGORY_LABELS),
                                    format_func=lambda c: CATEGORY_LABELS[c])
    pool = df if not cat_filter else df[df["Ana_Kategori"].isin(cat_filter)]
    if only_integrated:
        pool_i = pool[pool.apply(lambda r: integrated(r, plat), axis=1)]
        pool = pool_i if not pool_i.empty else pool
    base_options = sorted(pool["Muhimmat_Adi"].tolist())

    st.caption(f"{plat.kind} · boş {plat.empty_kg:,.0f} kg · dahili yakıt {plat.fuel_kg:,.0f} kg · "
               f"MTOW {plat.mtow_kg:,.0f} kg · azami mühimmat {plat.max_payload_kg:,.0f} kg · "
               f"{plat.note}")

    def label_of(name: str) -> str:
        if name == EMPTY:
            return name
        m = by_name.loc[name, "Toplam_Kutle_kg"]
        return f"{name} · {'kütle NA' if pd.isna(m) else f'{m:.0f} kg'}"

    left, right = st.columns([1.35, 1], gap="large")
    selections: dict[str, str] = {}
    with left:
        st.markdown("#### İstasyonlar (hardpoint)")
        ncols = 2
        cols = st.columns(ncols)
        for i, stn in enumerate(plat.stations):
            key = f"sel::{plat.name}::{stn.sid}"
            current = st.session_state.get(key, EMPTY)
            options = [EMPTY] + sorted(set(base_options) | ({current} - {EMPTY}))
            with cols[i % ncols]:
                selections[stn.sid] = st.selectbox(
                    f"{stn.sid} · {stn.label} (≤{stn.max_kg:,.0f} kg)", options, key=key,
                    format_func=label_of)

        def _clear() -> None:
            for s in plat.stations:
                st.session_state[f"sel::{plat.name}::{s.sid}"] = EMPTY

        st.button("Tüm istasyonları temizle", on_click=_clear)

    ev = evaluate_loadout(plat, selections, by_name, fuel_pct)
    with right:
        st.markdown("#### Kısıt kontrolü")
        if ev["ok"]:
            st.markdown('<div class="banner ok">YÜKLEME UYGUN — TÜM LİMİTLER İÇİNDE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="banner fail">LİMİT AŞIMI — YÜKLEME UYGUN DEĞİL</div>', unsafe_allow_html=True)
        bars = status_bar("Mühimmat yükü", ev["total"], plat.max_payload_kg, "kg")
        bars += status_bar("Kalkış kütlesi (GTOW)", ev["gtow"], plat.mtow_kg, "kg", warn_at=0.97)
        worst = max(ev["rows"], key=lambda r: (r["mass"] / r["stn"].max_kg) if r["name"] else 0)
        if worst["name"]:
            bars += status_bar(f"En yüklü istasyon ({worst['stn'].sid})", worst["mass"], worst["stn"].max_kg, "kg")
        st.markdown(bars, unsafe_allow_html=True)
        for r in ev["rows"]:
            for msg in r["msgs"]:
                cls = "failline" if r["status"] == "fail" else "warnline"
                st.markdown(f'<div class="{cls}">{"✖" if r["status"] == "fail" else "▲"} '
                            f'{e(r["stn"].sid)} · {e(r["name"])}: {e(msg)}</div>', unsafe_allow_html=True)
        if ev["total"] > plat.max_payload_kg:
            st.markdown(f'<div class="failline">✖ Toplam yük {ev["total"] - plat.max_payload_kg:,.0f} kg fazla</div>',
                        unsafe_allow_html=True)
        if ev["gtow"] > plat.mtow_kg:
            st.markdown(f'<div class="failline">✖ MTOW {ev["gtow"] - plat.mtow_kg:,.0f} kg aşıldı — '
                        f'yakıtı azaltın veya yükü hafifletin</div>', unsafe_allow_html=True)

        st.markdown("#### Aerodinamik / gözlenebilirlik özeti")
        a, b = st.columns(2)
        a.markdown(kpi("Yüklü istasyon", f"{ev['n_loaded']} / {len(plat.stations)}"), unsafe_allow_html=True)
        b.markdown(kpi("Mühimmat kütlesi", f"{ev['total']:,.0f} kg"), unsafe_allow_html=True)
        a.markdown(kpi("Kalkış kütlesi", f"{ev['gtow']:,.0f} kg"), unsafe_allow_html=True)
        b.markdown(kpi("Ek frontal alan", f"{ev['frontal']:.2f} m²"), unsafe_allow_html=True)
        a.markdown(kpi("Göreli RCS indeksi", f"{ev['rcs']:.0f}  (×{ev['rcs'] / 100:.1f})"), unsafe_allow_html=True)
        cost_txt = f"${ev['cost'] / 1e6:.2f} M" if ev["cost"] >= 1e6 else f"${ev['cost']:,.0f}"
        cost_lbl = "Bilinen maliyet" + (f" (+{ev['cost_na']} NA)" if ev["cost_na"] else "")
        b.markdown(kpi(cost_lbl, cost_txt), unsafe_allow_html=True)
        st.markdown(
            f'<div class="note" style="margin-top:.4rem">RCS indeksi <b>görsel/göreli</b> bir temsildir '
            f'(temiz konfigürasyon = 100); gerçek RCS değildir. '
            f'{"Düşük gözlenebilirlik platformunda harici yük indeksi hızla artırır; dahili bölme yükü artırmaz." if plat.low_observable else "Harici pilon ve mühimmatlar ilave kesit ekler."}'
            f'</div>', unsafe_allow_html=True)
        st.plotly_chart(hardpoint_figure(plat, ev), width="stretch", config={"displayModeBar": False})
        st.caption("◆ dahili bölme · ● harici istasyon · yeşil=uygun · sarı=uyarı · kırmızı=limit aşımı")


# ---------------------------------------------------------------------------
# MODÜL 3 — Görev profili ve menzil simülatörü
# ---------------------------------------------------------------------------
def _on_preset() -> None:
    lat, lon = CITY_PRESETS[st.session_state["m_preset"]]
    st.session_state["m_lat"], st.session_state["m_lon"] = lat, lon


def range_altitude_figure(row: pd.Series, alt_ft: int, mach: float, tgt_alt_m: float) -> go.Figure:
    alts = list(range(0, 60_001, 2_000))
    fig = go.Figure()
    for m, color in zip((0.9, 1.4, 1.8), (GREEN, AMBER, CYAN)):
        ys = [effective_range(row, a * FT, m, tgt_alt_m)["eff_km"] for a in alts]
        fig.add_trace(go.Scatter(x=alts, y=ys, mode="lines", name=f"Mach {m}", line=dict(color=color, width=2)))
    cur = effective_range(row, alt_ft * FT, mach, tgt_alt_m)["eff_km"]
    fig.add_trace(go.Scatter(x=[alt_ft], y=[cur], mode="markers", name="Mevcut senaryo",
                             marker=dict(size=12, color=RED, symbol="diamond", line=dict(color=TEXT, width=1))))
    style_fig(fig, 320)
    fig.update_layout(title="Efektif menzil – atış irtifası", xaxis_title="Atış irtifası (ft)",
                      yaxis_title="Efektif menzil (km)")
    return fig


MAP_STYLES = {
    "Koyu (Carto)": "carto-darkmatter",
    "Sokak (OpenStreetMap)": "open-street-map",
    "Altlıksız (çevrimdışı)": {
        "version": 8, "sources": {},
        "layers": [{"id": "bg", "type": "background", "paint": {"background-color": "#0d1416"}}],
    },
}


def range_map(lat: float, lon: float, r_max: float, r_nez: float, bearing: float, name: str,
              style="carto-darkmatter") -> go.Figure:
    scatter = getattr(go, "Scattermap", None) or go.Scattermapbox
    key = "map" if hasattr(go, "Scattermap") else "mapbox"
    fig = go.Figure()
    la, lo = geodesic_circle(lat, lon, r_max)
    fig.add_trace(scatter(lat=la, lon=lo, mode="lines", fill="toself", fillcolor="rgba(255,176,0,.07)",
                          line=dict(color=AMBER, width=2), name=f"Maks. menzil · {r_max:,.0f} km",
                          hoverinfo="name"))
    la, lo = geodesic_circle(lat, lon, r_nez)
    fig.add_trace(scatter(lat=la, lon=lo, mode="lines", fill="toself", fillcolor="rgba(57,255,20,.20)",
                          line=dict(color=GREEN, width=2), name=f"Kaçışsız bölge · {r_nez:,.0f} km",
                          hoverinfo="name"))
    end = destination_point(lat, lon, bearing, r_max)
    fig.add_trace(scatter(lat=[lat, end[0]], lon=[lon, end[1]], mode="lines",
                          line=dict(color=TEXT, width=1), showlegend=False, hoverinfo="skip"))
    fig.add_trace(scatter(lat=[lat], lon=[lon], mode="markers+text", text=["Atış noktası"],
                          textposition="top right", textfont=dict(color=TEXT),
                          marker=dict(size=12, color=GREEN), name=name, showlegend=False))
    style_fig(fig, 560)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend=dict(x=0.01, y=0.99, bgcolor="rgba(10,14,15,.75)"))
    fig.update_layout(**{key: dict(style=style, center=dict(lat=lat, lon=lon),
                                   zoom=map_zoom(r_max, lat))})
    return fig


def tab_mission(df: pd.DataFrame) -> None:
    pool = df[df["Maksimum_Menzil_km"].notna()]
    names = sorted(pool["Muhimmat_Adi"])
    default = names.index("AIM-120D AMRAAM") if "AIM-120D AMRAAM" in names else 0
    left, right = st.columns([1, 2.2], gap="large")
    with left:
        st.markdown("#### Senaryo")
        name = st.selectbox("Mühimmat", names, index=default, key="m_name")
        row = pool[pool["Muhimmat_Adi"] == name].iloc[0]
        air = is_air_target_class(row)
        alt_ft = st.slider("Atış irtifası (ft)", 0, 60_000, 35_000, 1_000, key="m_alt")
        mach = st.slider("Platform hızı (Mach)", 0.3, 2.2, 0.9, 0.1, key="m_mach")
        tgt_ft = st.slider("Hedef irtifası (ft)", 0, 50_000, 35_000 if air else 0, 1_000,
                           key=f"m_tgt_{'air' if air else 'surf'}")
        if air:
            aspect = st.selectbox("Hedef açısı", list(AAM_ASPECT))
            maneuver = st.selectbox("Hedef manevrası", list(AAM_MANEUVER))
        else:
            behavior = st.selectbox("Hedef davranışı", list(SURFACE_BEHAVIOR))
        st.markdown("#### Atış noktası")
        st.selectbox("Hazır konum", list(CITY_PRESETS), key="m_preset", on_change=_on_preset)
        st.session_state.setdefault("m_lat", CITY_PRESETS["Ankara"][0])
        st.session_state.setdefault("m_lon", CITY_PRESETS["Ankara"][1])
        c1, c2 = st.columns(2)
        lat = c1.number_input("Enlem", -85.0, 85.0, step=0.1, key="m_lat", format="%.2f")
        lon = c2.number_input("Boylam", -180.0, 180.0, step=0.1, key="m_lon", format="%.2f")
        bearing = st.slider("Atış istikameti (°)", 0, 359, 90, 5, key="m_brg")
        map_style = st.selectbox("Harita altlığı", list(MAP_STYLES), key="m_style",
                                 help="Altlık karoları tarayıcınızdan yüklenir; internet yoksa 'Altlıksız' seçin.")

    res = effective_range(row, alt_ft * FT, mach, tgt_ft * FT)
    if air:
        r_max = res["eff_km"] * AAM_ASPECT[aspect]
        r_nez = r_max * AAM_MANEUVER[maneuver]
    else:
        r_max = res["eff_km"]
        r_nez = r_max * SURFACE_BEHAVIOR[behavior]

    with right:
        c = st.columns(4)
        c[0].markdown(kpi("Baz menzil", f"{res['base_km']:,.0f} km"), unsafe_allow_html=True)
        c[1].markdown(kpi(f"Efektif menzil ({r_max / KM_PER_NM:,.0f} nm)", f"{r_max:,.0f} km"), unsafe_allow_html=True)
        c[2].markdown(kpi("Kaçışsız bölge", f"{r_nez:,.0f} km"), unsafe_allow_html=True)
        tof = res["tof_s"]
        c[3].markdown(kpi("Uçuş süresi (≈)", f"{int(tof // 60)} dk {int(tof % 60):02d} sn"), unsafe_allow_html=True)
        st.write("")
        st.plotly_chart(range_map(lat, lon, r_max, r_nez, bearing, name, MAP_STYLES[map_style]),
                        width="stretch")
        with st.expander("Hesap ayrıntısı ve model varsayımları", expanded=False):
            parts = " × ".join(f"{k}: {v:.2f}" for k, v in res["parts"].items())
            st.markdown(
                f"**Toplam ölçek katsayısı:** {res['ratio']:.2f} → {res['base_km']:,.0f} km × {res['ratio']:.2f}"
                f" = **{res['eff_km']:,.0f} km**  \n**Çarpanlar:** {parts}  \n"
                + (f"**Açı çarpanı:** {AAM_ASPECT[aspect]:.2f} · **Manevra çarpanı:** {AAM_MANEUVER[maneuver]:.2f}"
                   if air else f"**Hedef davranış çarpanı:** {SURFACE_BEHAVIOR[behavior]:.2f}"))
            st.caption("Baz menzil = veri setindeki optimum yüksek irtifa değeri (35.000 ft, Mach 0.9). "
                       "Model; sürükleme, yakıt/itki profili, güdüm sınırları, rüzgâr ve gerçek manevra "
                       "dinamiğini içermeyen ÖĞRETİCİ bir sezgisel yaklaşımdır. Halkalar eğrisel dünya üzerinde "
                       "yer mesafesidir. Kaçışsız bölge katsayıları temsilîdir.")
        st.plotly_chart(range_altitude_figure(row, alt_ft, mach, tgt_ft * FT), width="stretch")


# ---------------------------------------------------------------------------
# MODÜL 4 — Karşılaştırma matrisi
# ---------------------------------------------------------------------------
RADAR_METRICS = [
    ("Toplam_Kutle_kg", "Toplam kütle", "log"),
    ("Payload_Fraction", "Harp başlığı oranı", "lin1"),
    ("Maksimum_Menzil_km", "Menzil", "log"),
    ("Maksimum_Hiz_Mach", "Hız", "linmax"),
    ("Birim_Maliyet_USD", "Birim maliyet", "log"),
]


def normalize_metric(series: pd.Series, value: float, mode: str) -> float:
    if pd.isna(value):
        return 0.0
    s = series.dropna()
    s = s[s > 0]
    if mode == "lin1":
        return float(np.clip(value, 0, 1))
    if s.empty or value <= 0:
        return 0.0
    if mode == "linmax":
        return float(np.clip(value / s.max(), 0, 1))
    lo, hi = math.log10(s.min()), math.log10(s.max())
    return float(np.clip((math.log10(value) - lo) / (hi - lo), 0, 1)) if hi > lo else 1.0


def tab_compare(df: pd.DataFrame) -> None:
    names = sorted(df["Muhimmat_Adi"])
    wanted = ["AIM-120D AMRAAM", "Meteor", "PL-15", "R-77-1 (RVV-SD)"]
    default = [n for n in wanted if n in names] or names[:3]
    chosen = st.multiselect("Karşılaştırılacak mühimmatlar (2–4 adet)", names, default=default[:4],
                            max_selections=4)
    if len(chosen) < 2:
        st.info("Karşılaştırma için en az 2 mühimmat seçin.")
        return
    sub = df[df["Muhimmat_Adi"].isin(chosen)].set_index("Muhimmat_Adi").loc[chosen]

    fig = go.Figure()
    colors = [GREEN, AMBER, CYAN, PINK]
    for i, n in enumerate(chosen):
        r = sub.loc[n]
        vals = [normalize_metric(df[c], r[c], mode) for c, _, mode in RADAR_METRICS]
        labels = [lbl for _, lbl, _ in RADAR_METRICS]
        fig.add_trace(go.Scatterpolar(
            r=vals + vals[:1], theta=labels + labels[:1], name=n, fill="toself",
            line=dict(color=colors[i], width=2),
            fillcolor=f"rgba({int(colors[i][1:3], 16)},{int(colors[i][3:5], 16)},{int(colors[i][5:7], 16)},.12)"))
    style_fig(fig, 480)
    fig.update_layout(polar=dict(bgcolor=PANEL, radialaxis=dict(range=[0, 1], gridcolor=LINE, tickvals=[.25, .5, .75, 1],
                                                                tickfont=dict(size=9, color=MUTED)),
                                 angularaxis=dict(gridcolor=LINE)),
                      margin=dict(l=40, r=40, t=30, b=30))
    left, right = st.columns([1.1, 1.3], gap="large")
    with left:
        st.plotly_chart(fig, width="stretch")
        st.caption("Eksenler veri setine göre 0–1 normalize edilmiştir (kütle, menzil, maliyet: logaritmik; "
                   "oran: doğrusal; hız: veri setindeki maksimuma göre). Maliyet ekseninde yüksek = pahalı. "
                   "NA değerler 0 olarak çizilir.")
    with right:
        rows = {
            "Toplam kütle": [fmt(sub.loc[n, "Toplam_Kutle_kg"], "kg") for n in chosen],
            "Harp başlığı": [fmt(sub.loc[n, "Harp_Basligi_Kutlesi_kg"], "kg") for n in chosen],
            "Harp başlığı oranı": ["NA" if pd.isna(sub.loc[n, "Payload_Fraction"])
                                    else f"{sub.loc[n, 'Payload_Fraction'] * 100:.1f} %" for n in chosen],
            "Maks. menzil": [fmt(sub.loc[n, "Maksimum_Menzil_km"], "km") for n in chosen],
            "Maks. hız": [fmt(sub.loc[n, "Maksimum_Hiz_Mach"], "Mach") for n in chosen],
            "Birim maliyet": ["NA" if pd.isna(sub.loc[n, "Birim_Maliyet_USD"])
                              else f"${sub.loc[n, 'Birim_Maliyet_USD']:,.0f}" for n in chosen],
            "İtki": [sub.loc[n, "Itki_Sistemi"] for n in chosen],
            "Terminal güdüm": [sub.loc[n, "Gudum_Sistemi_Terminal"] for n in chosen],
            "Ülke": [sub.loc[n, "Mensei_Ulke"] for n in chosen],
        }
        st.dataframe(pd.DataFrame(rows, index=chosen).T, width="stretch", height=370)
        bar = go.Figure()
        for i, (col, lbl) in enumerate((("Maksimum_Menzil_km", "Menzil (km)"), ("Toplam_Kutle_kg", "Kütle (kg)"))):
            bar.add_trace(go.Bar(x=chosen, y=[sub.loc[n, col] for n in chosen], name=lbl,
                                 marker_color=[GREEN, AMBER][i], yaxis="y" if i == 0 else "y2",
                                 offsetgroup=i))
        style_fig(bar, 260)
        bar.update_layout(barmode="group", yaxis=dict(title="Menzil (km)"),
                          yaxis2=dict(title="Kütle (kg)", overlaying="y", side="right", gridcolor="rgba(0,0,0,0)"),
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(bar, width="stretch")


# ---------------------------------------------------------------------------
# Ana akış
# ---------------------------------------------------------------------------
def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    df, source = load_data()

    st.markdown('<div class="app-title">SAVUNMA MÜHİMMATI VE ETKİLEŞİM SİMÜLASYON PLATFORMU</div>'
                '<div class="app-sub">Açık kaynak veri · eğitim / analiz amaçlı · '
                'operasyonel planlama için kullanılamaz</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Veri kaynağı")
        st.write(f"`{source}`")
        st.metric("Kayıt sayısı", len(df))
        rel = df["Veri_Guvenilirlik_Notu"].value_counts()
        st.write(f"Doğrulanmış: **{rel.get('Acik_Kaynak_Dogrulanmis', 0)}**  \n"
                 f"Tahmini: **{rel.get('Tahmini_Acik_Kaynak', 0)}**")
        st.caption("Platform istasyon limitleri, RCS indeksi, menzil ölçekleme ve kaçışsız bölge "
                   "katsayıları temsilî/öğretici modellerdir. Gizli veriler NA bırakılmıştır.")
        if st.button("Önbelleği temizle ve veriyi yeniden yükle"):
            st.cache_data.clear()
            st.rerun()

    k = st.columns(5)
    k[0].markdown(kpi("Mühimmat", str(len(df))), unsafe_allow_html=True)
    k[1].markdown(kpi("Ülke / köken", str(df["Mensei_Ulke"].nunique())), unsafe_allow_html=True)
    k[2].markdown(kpi("Türk sistemi", str(int((df["Mensei_Ulke"] == "TUR").sum()))), unsafe_allow_html=True)
    k[3].markdown(kpi("Hava platformu", str(len(PLATFORMS))), unsafe_allow_html=True)
    k[4].markdown(kpi("En uzun menzil", fmt(df["Maksimum_Menzil_km"].max(), "km")), unsafe_allow_html=True)
    st.write("")

    t1, t2, t3, t4 = st.tabs(["① Envanter Gezgini", "② İstasyon Yükleme", "③ Menzil Simülatörü",
                              "④ Karşılaştırma Matrisi"])
    with t1:
        tab_inventory(df)
    with t2:
        tab_stations(df)
    with t3:
        tab_mission(df)
    with t4:
        tab_compare(df)


if __name__ == "__main__":
    main()
