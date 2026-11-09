#!/usr/bin/env python3
"""
Keşifsel Veri Analizi (EDA) ve akademik çıktılar.

Girdi : data/processed/master_air_munitions_dataset.csv
Çıktı : outputs/summary_report.md
        outputs/figures/fig1_range_vs_mass.png       (300 DPI)
        outputs/figures/fig2_payload_efficiency.png  (300 DPI)
        outputs/figures/fig3_guidance_matrix.png     (300 DPI)
        outputs/figures/*.csv                        (grafiklerin veri tabloları)
"""
import os
import sys
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "data", "processed", "master_air_munitions_dataset.csv")
OUT = os.path.join(ROOT, "outputs")
FIG = os.path.join(OUT, "figures")
DPI = 300

# Avrupa bloğu: çok uluslu (EUR) + ulusal Avrupa ISO kodları
EUROPE = {"EUR", "GBR", "FRA", "DEU", "ITA", "SWE", "NOR", "ESP"}
FOCUS = ["USA", "TUR", "RUS", "CHN", "EUR"]

# Doğrulanmış referans palet (sabit sıra; dataviz/palette.md slot 1-4) + sıralı mavi rampa
CAT_COLORS = {
    "Fuze": "#2a78d6",
    "Gudumlu_Bomba": "#eb6834",
    "Gudumsuz_Bomba": "#1baf7a",
    "Dolanan_Muhimmat": "#6250d6",
}
CAT_MARKERS = {"Fuze": "o", "Gudumlu_Bomba": "s", "Gudumsuz_Bomba": "D", "Dolanan_Muhimmat": "^"}
CAT_LABELS = {
    "Fuze": "Füze",
    "Gudumlu_Bomba": "Güdümlü bomba",
    "Gudumsuz_Bomba": "Güdümsüz bomba",
    "Dolanan_Muhimmat": "Dolanan mühimmat",
}
SEQ_BLUE = ["#fcfcfb", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def setup_style():
    sns.set_theme(style="ticks", context="paper")
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "legend.frameon": False,
    })


def load() -> pd.DataFrame:
    df = pd.read_csv(MASTER, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    num = ["Hizmete_Giris_Yili", "Toplam_Kutle_kg", "Harp_Basligi_Kutlesi_kg", "Uzunluk_m", "Cap_mm",
           "Kanat_Acikligi_m", "Maksimum_Menzil_km", "Maksimum_Hiz_Mach", "Birim_Maliyet_USD"]
    for c in num:
        df[c] = pd.to_numeric(df[c].replace("NA", np.nan))
    df["Payload_Fraction"] = df["Harp_Basligi_Kutlesi_kg"] / df["Toplam_Kutle_kg"]
    df["Blok"] = df["Mensei_Ulke"].where(~df["Mensei_Ulke"].isin(EUROPE), "EUR")
    return df


# ----------------------------------------------------------------------------
# Tablolar
# ----------------------------------------------------------------------------
def md_table(df: pd.DataFrame, floatfmt: str = "{:.2f}") -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |",
             "|" + "|".join("---:" if pd.api.types.is_numeric_dtype(df[c]) else ":---" for c in cols) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append("—" if pd.isna(v) else floatfmt.format(v))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def describe_by(df, by, col):
    g = df.groupby(by)[col]
    t = pd.DataFrame({
        "n_toplam": df.groupby(by).size(),
        "n_veri": g.count(),
        "Ortalama": g.mean(),
        "Medyan": g.median(),
        "Std": g.std(),
        "Min": g.min(),
        "Maks": g.max(),
    }).reset_index()
    return t


def loglog_fit(sub):
    s = sub.dropna(subset=["Toplam_Kutle_kg", "Maksimum_Menzil_km"])
    if len(s) < 4:
        return None
    x, y = np.log10(s["Toplam_Kutle_kg"]), np.log10(s["Maksimum_Menzil_km"])
    b, a = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    return {"n": len(s), "egim_b": b, "kesisim_a": a, "R2": r ** 2}


def terminal_long(df):
    """Çok-modlu arayıcılar ('+') her bir moda ayrı sayılır."""
    rows = []
    for _, r in df.iterrows():
        t = r["Gudum_Sistemi_Terminal"]
        if t == "NA":
            continue
        for tok in t.split("+"):
            rows.append({"Blok": r["Blok"], "Terminal": tok, "Muhimmat_Adi": r["Muhimmat_Adi"]})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# Grafikler
# ----------------------------------------------------------------------------
def fig1(df):
    d = df.dropna(subset=["Toplam_Kutle_kg", "Maksimum_Menzil_km"]).copy()
    d[["Muhimmat_Adi", "Ana_Kategori", "Alt_Kategori", "Mensei_Ulke", "Toplam_Kutle_kg",
       "Maksimum_Menzil_km"]].to_csv(os.path.join(FIG, "fig1_data.csv"), sep=";", index=False)
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    for cat in CAT_COLORS:
        s = d[d["Ana_Kategori"] == cat]
        if s.empty:
            continue
        ax.scatter(s["Toplam_Kutle_kg"], s["Maksimum_Menzil_km"], s=34, marker=CAT_MARKERS[cat],
                   color=CAT_COLORS[cat], edgecolor="white", linewidth=0.8, alpha=0.9, zorder=3,
                   label=f"{CAT_LABELS[cat]} (n={len(s)})")
    # Füzeler için log-log OLS eğilimi
    f = loglog_fit(d[d["Ana_Kategori"] == "Fuze"])
    if f:
        xs = np.logspace(np.log10(d["Toplam_Kutle_kg"].min()), np.log10(d["Toplam_Kutle_kg"].max()), 50)
        ax.plot(xs, 10 ** f["kesisim_a"] * xs ** f["egim_b"], color=CAT_COLORS["Fuze"], lw=1.2,
                ls="--", zorder=2, label=f"Füze OLS: log R = {f['kesisim_a']:.2f} + {f['egim_b']:.2f}·log M "
                                         f"(R²={f['R2']:.2f})")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Toplam kütle [kg] (log ölçek)")
    ax.set_ylabel("Maksimum menzil [km] (log ölçek)")
    ax.set_title("Şekil 1. Havadan atılan mühimmatlarda menzil–kütle ilişkisi")
    ax.grid(True, which="major", color=GRID, lw=0.6, zorder=0)
    # seçici doğrudan etiketler (uç değerler)
    notes = ["Kh-101", "Kh-22", "GBU-57A/B MOP", "MAM-C", "AIM-54C Phoenix", "ALTIUS-600",
             "Kh-47M2 Kinzhal", "GBU-39 SDB I", "Mk-84", "Meteor"]
    for n in notes:
        r = d[d["Muhimmat_Adi"] == n]
        if r.empty:
            continue
        x, y = r.iloc[0]["Toplam_Kutle_kg"], r.iloc[0]["Maksimum_Menzil_km"]
        ax.annotate(n, (x, y), xytext=(5, 4), textcoords="offset points", fontsize=7, color=INK2)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, fontsize=7.5)
    fig.text(0.01, 0.005, "Not: Güdümsüz bombalar için menzil, ~10,7 km irtifa / Mach 0,9 atışta vakum-balistik "
             "yaklaşımıyla 12 km olarak sabitlenmiştir (yatay şerit).", fontsize=6.5, color=INK2)
    fig.set_size_inches(7.2, 5.8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    p = os.path.join(FIG, "fig1_range_vs_mass.png")
    fig.savefig(p, dpi=DPI)
    plt.close(fig)
    return p, f


def fig2(df):
    d = df.dropna(subset=["Payload_Fraction"]).copy()
    counts = d["Alt_Kategori"].value_counts()
    keep = counts[counts >= 3].index
    d = d[d["Alt_Kategori"].isin(keep)]
    order = d.groupby("Alt_Kategori")["Payload_Fraction"].median().sort_values(ascending=False).index.tolist()
    d[["Muhimmat_Adi", "Alt_Kategori", "Harp_Basligi_Kutlesi_kg", "Toplam_Kutle_kg",
       "Payload_Fraction"]].to_csv(os.path.join(FIG, "fig2_data.csv"), sep=";", index=False)
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    sns.boxplot(data=d, y="Alt_Kategori", x="Payload_Fraction", order=order, ax=ax, color="#cde2fb",
                width=0.6, linewidth=0.9, fliersize=0,
                boxprops={"edgecolor": "#256abf"}, medianprops={"color": "#0d366b", "lw": 1.6},
                whiskerprops={"color": "#256abf"}, capprops={"color": "#256abf"})
    sns.stripplot(data=d, y="Alt_Kategori", x="Payload_Fraction", order=order, ax=ax, color="#2a78d6",
                  size=3.6, jitter=0.18, edgecolor="white", linewidth=0.5, alpha=0.9)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([f"{o}  (n={counts[o]})" for o in order])
    ax.set_xlabel("Harp başlığı kütle oranı  PF = M_harp başlığı / M_toplam")
    ax.set_ylabel("")
    ax.set_xlim(0, 1.05)
    ax.grid(True, axis="x", color=GRID, lw=0.6)
    ax.set_title("Şekil 2. Mühimmat sınıflarına göre harp başlığı kütle oranı")
    fig.text(0.01, 0.005, "Not: Güdümsüz bombalarda harp başlığı = bomba gövdesi (PF ≡ 1). n<3 olan sınıflar "
             "gösterilmemiştir. Noktalar tekil mühimmatlardır.", fontsize=6.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    p = os.path.join(FIG, "fig2_payload_efficiency.png")
    fig.savefig(p, dpi=DPI)
    plt.close(fig)
    return p


def fig3(df):
    tl = terminal_long(df[df["Blok"].isin(FOCUS)])
    ct = pd.crosstab(tl["Blok"], tl["Terminal"]).reindex(FOCUS).fillna(0).astype(int)
    col_order = ct.sum().sort_values(ascending=False).index
    ct = ct[col_order]
    share = ct.div(ct.sum(axis=1), axis=0) * 100
    ct.to_csv(os.path.join(FIG, "fig3_data.csv"), sep=";")
    annot = ct.astype(str).where(ct > 0, "")
    cmap = LinearSegmentedColormap.from_list("seq_blue", SEQ_BLUE)
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    sns.heatmap(share, annot=annot, fmt="", cmap=cmap, vmin=0, vmax=max(40, share.values.max()),
                linewidths=2, linecolor="white", cbar_kws={"label": "Satır payı [%]", "shrink": 0.8},
                annot_kws={"fontsize": 8}, ax=ax)
    # metin kontrastı: koyu hücrelerde beyaz
    for t, v in zip(ax.texts, share.values.flatten()):
        t.set_color("white" if v >= 25 else INK)
    labels = {"USA": "ABD", "TUR": "Türkiye", "RUS": "Rusya", "CHN": "Çin", "EUR": "Avrupa (blok)"}
    ax.set_yticklabels([f"{labels[b]}  (n={df[df['Blok'] == b].shape[0]})" for b in ct.index], rotation=0)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_xlabel("Terminal güdüm teknolojisi")
    ax.set_ylabel("")
    ax.set_title("Şekil 3. Ülke/blok bazında terminal güdüm teknolojisi dağılımı")
    fig.text(0.01, 0.005, "Hücre değeri = mühimmat sayısı; renk = ülke içi pay. Çok-modlu arayıcılar "
             "(ör. MMW+SAL) her moda ayrı sayılır; NA hariç.", fontsize=6.5, color=INK2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    p = os.path.join(FIG, "fig3_guidance_matrix.png")
    fig.savefig(p, dpi=DPI)
    plt.close(fig)
    return p, ct


# ----------------------------------------------------------------------------
# Rapor
# ----------------------------------------------------------------------------
def build_report(df, fit, ct):
    n = len(df)
    L = []
    L.append("# Havadan Atılan Mühimmatlar Veri Seti — Özet Rapor (EDA)\n")
    L.append(f"*Oluşturulma tarihi: {date.today().isoformat()} · Kaynak: "
             "`data/processed/master_air_munitions_dataset.csv` · Üretici betik: `src/academic_analysis.py`*\n")
    L.append("## 1. Veri setinin genel görünümü\n")
    rel = df["Veri_Guvenilirlik_Notu"].value_counts()
    L.append(f"- **Toplam kayıt:** {n} mühimmat × 20 öznitelik (+ türetilmiş `Payload_Fraction`)")
    L.append(f"- **Ülke/köken sayısı:** {df['Mensei_Ulke'].nunique()} ISO kodu · "
             f"**Alt kategori sayısı:** {df['Alt_Kategori'].nunique()}")
    L.append(f"- **Güvenilirlik:** {rel.get('Acik_Kaynak_Dogrulanmis', 0)} kayıt `Acik_Kaynak_Dogrulanmis`, "
             f"{rel.get('Tahmini_Acik_Kaynak', 0)} kayıt `Tahmini_Acik_Kaynak`")
    L.append(f"- **Türk envanteri / geliştirmesi (TUR):** {int((df['Mensei_Ulke'] == 'TUR').sum())} kayıt\n")

    L.append("### Tablo 1. Alan doluluk oranları (NA olmayan)\n")
    comp = pd.DataFrame({
        "Sütun": ["Hizmete_Giris_Yili", "Toplam_Kutle_kg", "Harp_Basligi_Kutlesi_kg", "Uzunluk_m", "Cap_mm",
                  "Kanat_Acikligi_m", "Maksimum_Menzil_km", "Maksimum_Hiz_Mach", "Birim_Maliyet_USD",
                  "Payload_Fraction"]})
    comp["Dolu (n)"] = comp["Sütun"].map(lambda c: int(df[c].notna().sum()))
    comp["Doluluk (%)"] = comp["Dolu (n)"] / n * 100
    L.append(md_table(comp, "{:.1f}") + "\n")

    L.append("## 2. Kategorilere göre dağılım\n")
    L.append("### Tablo 2. Ana kategori × alt kategori sayıları ve menzil istatistikleri\n")
    t2 = describe_by(df, ["Ana_Kategori", "Alt_Kategori"], "Maksimum_Menzil_km")
    t2 = t2.rename(columns={"Ortalama": "Ort. menzil [km]", "Medyan": "Medyan [km]", "Std": "Std [km]",
                            "Min": "Min [km]", "Maks": "Maks [km]"})
    L.append(md_table(t2, "{:.1f}") + "\n")

    L.append("### Tablo 3. Ana kategori özet istatistikleri\n")
    g = df.groupby("Ana_Kategori")
    t3 = pd.DataFrame({
        "n": g.size(),
        "Ort. kütle [kg]": g["Toplam_Kutle_kg"].mean(),
        "Medyan kütle [kg]": g["Toplam_Kutle_kg"].median(),
        "Ort. menzil [km]": g["Maksimum_Menzil_km"].mean(),
        "Medyan menzil [km]": g["Maksimum_Menzil_km"].median(),
        "Ort. PF": g["Payload_Fraction"].mean(),
        "Medyan PF": g["Payload_Fraction"].median(),
    }).reset_index()
    L.append(md_table(t3, "{:.2f}") + "\n")

    L.append("## 3. Ülkelere göre dağılım\n")
    L.append("### Tablo 4. Köken ülkeye göre mühimmat sayısı ve ortalama menzil\n")
    gc = df.groupby("Mensei_Ulke")
    t4 = pd.DataFrame({
        "n": gc.size(),
        "Füze": gc["Ana_Kategori"].apply(lambda s: int((s == "Fuze").sum())),
        "Güdümlü bomba": gc["Ana_Kategori"].apply(lambda s: int((s == "Gudumlu_Bomba").sum())),
        "Güdümsüz bomba": gc["Ana_Kategori"].apply(lambda s: int((s == "Gudumsuz_Bomba").sum())),
        "Dolanan": gc["Ana_Kategori"].apply(lambda s: int((s == "Dolanan_Muhimmat").sum())),
        "Ort. menzil [km]": gc["Maksimum_Menzil_km"].mean(),
        "Medyan menzil [km]": gc["Maksimum_Menzil_km"].median(),
        "Ort. PF": gc["Payload_Fraction"].mean(),
    }).reset_index().sort_values("n", ascending=False)
    L.append(md_table(t4, "{:.2f}") + "\n")

    L.append("### Tablo 5. Odak bloklar (Avrupa = EUR + ulusal Avrupa kodları)\n")
    fb = df[df["Blok"].isin(FOCUS)].groupby("Blok")
    t5 = pd.DataFrame({
        "n": fb.size(),
        "Ort. menzil [km]": fb["Maksimum_Menzil_km"].mean(),
        "Medyan menzil [km]": fb["Maksimum_Menzil_km"].median(),
        "Maks menzil [km]": fb["Maksimum_Menzil_km"].max(),
        "Medyan PF": fb["Payload_Fraction"].median(),
        "Doğrulanmış (%)": fb["Veri_Guvenilirlik_Notu"].apply(
            lambda s: 100 * (s == "Acik_Kaynak_Dogrulanmis").mean()),
    }).reindex(FOCUS).reset_index()
    L.append(md_table(t5, "{:.1f}") + "\n")

    L.append("## 4. Harp başlığı kütle oranı (Payload Fraction)\n")
    L.append("$PF = M_{harp\\,başlığı} / M_{toplam}$ — yalnızca her iki kütlesi bilinen kayıtlar.\n")
    L.append("### Tablo 6. Alt kategoriye göre PF istatistikleri\n")
    t6 = describe_by(df, "Alt_Kategori", "Payload_Fraction").sort_values("Medyan", ascending=False)
    L.append(md_table(t6, "{:.3f}") + "\n")

    L.append("## 5. Menzil–kütle ölçeklemesi\n")
    rows = []
    for cat in ["Fuze", "Gudumlu_Bomba"]:
        f = loglog_fit(df[df["Ana_Kategori"] == cat])
        if f:
            rows.append({"Kategori": cat, **f})
    for alt in ["BVRAAM", "WVRAAM", "ALCM", "AShM", "ATGM"]:
        f = loglog_fit(df[df["Alt_Kategori"] == alt])
        if f:
            rows.append({"Kategori": alt, **f})
    t7 = pd.DataFrame(rows)
    t7["n"] = t7["n"].astype(float)
    L.append("### Tablo 7. log₁₀(Menzil) = a + b·log₁₀(Kütle) OLS uyumu\n")
    L.append(md_table(t7, "{:.3f}") + "\n")
    if fit:
        L.append(f"Füze sınıfında esneklik katsayısı b ≈ {fit['egim_b']:.2f} (R² = {fit['R2']:.2f}): kütledeki "
                 f"%10'luk artış, ortalamada menzilde yaklaşık %{(1.1 ** fit['egim_b'] - 1) * 100:.1f}'lik "
                 "artışla ilişkilidir. Düşük R², itki tipinin (roket / turbojet / ramjet) kütleden bağımsız "
                 "güçlü bir menzil belirleyicisi olduğuna işaret eder.\n")

    L.append("## 6. Terminal güdüm teknolojisi matrisi (Şekil 3 veri tablosu)\n")
    L.append(md_table(ct.reset_index().rename(columns={"Blok": "Blok"}), "{:.0f}") + "\n")

    L.append("## 7. Şekiller\n")
    L.append("![Şekil 1](figures/fig1_range_vs_mass.png)\n")
    L.append("![Şekil 2](figures/fig2_payload_efficiency.png)\n")
    L.append("![Şekil 3](figures/fig3_guidance_matrix.png)\n")

    L.append("## 8. Yöntem notları ve sınırlılıklar\n")
    L.append(
        "1. **Kaynaklar:** Üretici katalogları ve resmi açıklamalar (ROKETSAN, TÜBİTAK SAGE, ASELSAN, Baykar, "
        "MBDA, Raytheon/RTX, Lockheed Martin, Boeing), ABD savunma bütçe belgeleri, SIPRI, CSIS Missile Threat, "
        "Jane's ve savunma basını. Satır bazında kaynak belirsizliği `Veri_Guvenilirlik_Notu` ile işaretlenmiştir.\n"
        "2. **Gizli/teyit edilemeyen değerler uydurulmamış, `NA` yazılmıştır.** Bu nedenle özellikle "
        "geliştirme aşamasındaki sistemlerde (AIM-260, Gökhan, Akbaba, KD-21, ARRW) kayıtlar seyrektir.\n"
        "3. **Menzil konvansiyonu:** Aralık verilen durumlarda üst sınır alınmıştır (ör. '65+ km' → 65). "
        "Güdümsüz bombalar için sabit 12 km değeri, ~10,7 km irtifa ve Mach 0,9 atışta vakum-balistik "
        "yaklaşımdır; bir ölçüm değil, sınıf konvansiyonudur.\n"
        "4. **Hız konvansiyonu:** Serbest düşüş GP bombaları Mach 0,9, sığınak deliciler Mach 1,1 "
        "(görev tanımı gereği).\n"
        "5. **Harp başlığı tanımı:** Bombalarda harp başlığı kütlesi = bomba gövdesi (kasa + dolgu); bu "
        "nedenle güdümsüz bombalarda PF ≡ 1 ve güdüm kitlerinde PF ≈ 0,85–0,99'dur. Füzelerde PF patlayıcı "
        "değil, harp başlığı bölümünün tamamıdır.\n"
        "6. **Kütle tanımı:** Havadan atış kütlesi esas alınmıştır; yerden/gemiden atılan sürümlerin "
        "booster kütlesi dahil edilmemiştir (BrahMos-A, Atmaca, Kh-35U).\n"
        "7. **Kinzhal menzili** (2000 km) taşıyıcı uçağın muharebe yarıçapını içeren beyan edilen değerdir.\n"
        "8. **Birleştirilen/ayrıştırılan adlar:** Görev listesindeki `İHA-230`, ROKETSAN'ın `TRG-230-İHA` "
        "sistemiyle aynı olduğu için tek kayıt olarak tutulmuştur (mükerrer önleme). `SOM-J` yalnızca 02 "
        "dosyasındadır. `Minyatür Bomba`, SSB'nin TOLUN'u (ASELSAN) üreten tedarik projesinin adı olduğundan "
        "ayrı satır açılmamıştır.\n"
        "9. **Seçim yanlılığı:** Veri seti tam envanter değil, temsilî bir örneklemdir; Türk sistemlerine "
        "görev gereği ağırlık verilmiştir. Ülke ortalamaları bu nedenle envanter ortalaması olarak "
        "yorumlanmamalıdır.\n"
        "10. **Birim maliyet** yalnızca açık bütçe belgelerinde yayımlanan az sayıda kalem için verilmiştir "
        f"(n = {int(df['Birim_Maliyet_USD'].notna().sum())}); istatistiksel çıkarım için yetersizdir.\n")
    return "\n".join(L)


def main() -> int:
    if not os.path.exists(MASTER):
        print("Master veri seti yok; önce `python3 src/merge_dataset.py` çalıştırın.")
        return 1
    os.makedirs(FIG, exist_ok=True)
    setup_style()
    df = load()
    p1, fit = fig1(df)
    p2 = fig2(df)
    p3, ct = fig3(df)
    report = build_report(df, fit, ct)
    rp = os.path.join(OUT, "summary_report.md")
    with open(rp, "w", encoding="utf-8") as fh:
        fh.write(report)
    for p in (p1, p2, p3, rp):
        print("->", os.path.relpath(p, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
