#!/usr/bin/env python3
"""
Weaponeering motoru için kural ve değişmez (invariant) testleri.

    python3 src/test_weaponeering_engine.py

Model katsayıları değişse de korunması gereken davranışları sınar: zorunlu eleme
kuralları, ölçekleme yasaları, skor aralığı/sıralaması, senaryo kısıtları ve
duyarlılık analizlerinin monotonluğu. Çıkış kodu: 0 = tüm testler geçti.
"""
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weaponeering_engine as we  # noqa: E402

RAW, SOURCE = we.load_munitions()
MUN = we.prepare_munitions(RAW)
TGT = we.load_targets()
TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


def run(target_id, scenario=None, **kw):
    return we.calculate_weapon_effectiveness(target_id, scenario, MUN, TGT, include_eliminated=True, **kw)


def ok_rows(df):
    return df[df["Durum"] == we.STATUS_OK]


def row(df, name):
    hit = df[df["Muhimmat_Adi"] == name]
    assert len(hit) == 1, f"'{name}' sonuçta yok"
    return hit.iloc[0]


def targets_where(**conditions):
    sel = TGT
    for col, val in conditions.items():
        sel = sel[sel[col] == val]
    assert len(sel), f"koşula uyan hedef yok: {conditions}"
    return sel["Target_ID"].tolist()


# --------------------------------------------------------------------------- hedef matrisi
@test
def hedef_matrisi_semasi():
    assert list(TGT.columns) == we.TARGET_COLUMNS and we.TARGET_COLUMNS[:10] == [
        "Target_ID", "Target_Category", "Target_Description", "UFC_Hardness_Rating_psi",
        "Required_Concrete_Penetration_m", "Target_Mobility_Class", "TST_Status", "Radar_Cross_Section_m2",
        "Required_Lethal_Radius_m", "Collateral_Damage_Tier"], "istenen 10 sütun aynı sırada olmalı"
    assert len(TGT) >= 25 and TGT["Target_ID"].is_unique
    assert set(TGT["Target_Class"]) == set(we.TARGET_CATEGORIES)
    assert set(TGT["Target_Mobility_Class"]) == set(we.MOBILITY_LEVELS)
    assert set(TGT["Passive_Defense_Level"]) == set(we.PASSIVE_LEVELS)
    assert TGT["TST_Status"].dtype == bool and 0 < TGT["TST_Status"].sum() < len(TGT)
    soft = TGT[TGT["Target_Category"].str.contains("/Soft/")]
    assert (soft["Required_Concrete_Penetration_m"] == 0).all(), "yumuşak hedefte delme 0 olmalı"
    assert (TGT[TGT["Target_Class"] == "Hardened_Structure"]["Required_Concrete_Penetration_m"] > 0).all()
    assert set(TGT["Data_Confidence"]) <= {"Kaynakli", "Turetilmis", "Varsayim"}
    assert (TGT["Hardness_Basis"].str.len() > 20).all(), "her sertlik değerinin dayanağı yazılmalı"


@test
def hedef_dogrulayici_hata_yakalar():
    base = pd.read_csv(we.TARGET_MATRIX_PATH, sep=";", dtype=str, keep_default_na=False)
    assert we.validate_targets(base) == []
    cases = {
        "geçersiz kategori": ("Target_Category", "Bunker"),
        "geçersiz sınıf": ("Target_Class", "Building"),
        "geçersiz hareketlilik": ("Target_Mobility_Class", "Moving"),
        "geçersiz TST": ("TST_Status", "Evet"),
        "geçersiz CDE": ("Collateral_Damage_Tier", "Extreme"),
        "geçersiz mekanizma": ("Primary_Damage_Mechanism", "Nuclear"),
        "negatif yarıçap": ("Required_Lethal_Radius_m", "-5"),
        "sayısal olmayan": ("Radar_Cross_Section_m2", "büyük"),
        "sıfır sertlik": ("UFC_Hardness_Rating_psi", "0"),
        "kimlik biçimi": ("Target_ID", "T01_HAS"),
    }
    for label, (col, val) in cases.items():
        bad = base.copy()
        bad.loc[0, col] = val
        assert we.validate_targets(bad), label
    soft_with_pen = base.copy()
    row_idx = soft_with_pen.index[soft_with_pen["Target_Category"].str.contains("/Soft/")][0]
    soft_with_pen.loc[row_idx, "Required_Concrete_Penetration_m"] = "1.0"
    assert we.validate_targets(soft_with_pen), "Soft hedefte delme > 0 hata olmalı"
    dup = pd.concat([base, base.iloc[[0]]], ignore_index=True)
    assert any("Mükerrer" in e for e in we.validate_targets(dup))
    assert we.validate_targets(base.drop(columns="Thermal_Signature"))
    assert we.validate_targets(base.head(10)), "25'ten az hedef hata olmalı"


# --------------------------------------------------------------------------- doktriner alt modeller
@test
def patlama_modeli_kinney_graham():
    pressures = [we.incident_overpressure_kpa(z) for z in (0.2, 0.5, 1, 2, 5, 10, 40)]
    assert pressures == sorted(pressures, reverse=True), "basınç ölçekli mesafeyle azalmalı"
    # bağımsız karşılaştırma: depodaki Kingery-Bulmash tipi tablo (PassiveDefenseOptimizer)
    table = {1.0: 680.0, 2.0: 130.0, 5.0: 23.0, 10.0: 7.5}
    for z, ref in table.items():
        ratio = we.incident_overpressure_kpa(z) / ref
        assert 0.8 < ratio < 1.8, f"Z={z}: Kinney-Graham / tablo = {ratio:.2f}"
    for kpa in (5.0, 34.5, 250.0, 2000.0):
        z = we.scaled_distance_for_overpressure(kpa)
        assert math.isclose(we.incident_overpressure_kpa(z), kpa, rel_tol=1e-6)
    # Hopkinson-Cranz: 8 kat yük → aynı basınç 2 kat mesafede
    assert math.isclose(we.blast_radius_m(800, 5.0), 2 * we.blast_radius_m(100, 5.0), rel_tol=1e-9)
    assert we.blast_radius_m(100, 1.0) > we.blast_radius_m(100, 5.0) > we.blast_radius_m(100, 30.0)
    assert math.isclose(we.overpressure_at_psi(100, we.blast_radius_m(100, 5.0)), 5.0, rel_tol=1e-6)


@test
def tnt_esdegeri_ve_kilif_duzeltmesi():
    w = we.tnt_equivalent_kg(925, "HE-Frag")
    fill = 925 * we.FILL_FRACTION["HE-Frag"]
    assert 0.2 * fill * we.SURFACE_BURST_FACTOR < w < fill * we.SURFACE_BURST_FACTOR, "kılıf etkin yükü azaltır"
    assert math.isclose(we.tnt_equivalent_kg(925, "HE-Frag", surface_burst=False) * we.SURFACE_BURST_FACTOR, w)
    assert we.tnt_equivalent_kg(925, "HE-Frag") > we.tnt_equivalent_kg(925, "Penetrator")
    assert math.isclose(we.tnt_equivalent_kg(100, "HE-Frag", relative_effectiveness=1.33),
                        1.33 * we.tnt_equivalent_kg(100, "HE-Frag"))
    assert math.isnan(we.tnt_equivalent_kg(float("nan"), "HE-Frag"))


@test
def delme_fonksiyonu_young():
    base = we.calculate_penetration_depth(300, 874, 0.368)
    assert 1.5 < base < 3.5, f"2000 lb sınıfı delici: {base:.2f} m"
    assert we.calculate_penetration_depth(400, 874, 0.368) > base, "hız arttıkça delme artar"
    assert we.calculate_penetration_depth(300, 1996, 0.368) > base, "kesit yoğunluğu arttıkça delme artar"
    assert we.calculate_penetration_depth(300, 874, 0.5) < base, "çap arttıkça delme azalır"
    assert we.calculate_penetration_depth(50, 874, 0.368) == 0.0, "61 m/s altında denklem geçersiz"
    assert we.calculate_penetration_depth(300, 874, 0.368, "HE-Frag") < base
    ratio = we.calculate_penetration_depth(300, 2 * 874, 0.368) / base
    assert math.isclose(ratio, 2 ** 0.7, rel_tol=1e-9), "D ∝ (m/A)^0.7"


@test
def tst_ucus_suresi_ve_cde():
    assert we.tst_factor(False, 5000, 600, False) == 1.0 and we.tst_factor(True, 300, 600, False) == 1.0
    assert math.isclose(we.tst_factor(True, 1200, 600, False), 0.5)
    assert we.tst_factor(True, 6000, 600, True) == we.TST_DATALINK_FLOOR
    slow = we.time_of_flight_s("Turbojet", 0.8, 400)
    fast = we.time_of_flight_s("Ramjet", 3.0, 400)
    assert fast < 0.4 * slow, "süpersonik füze TST'de avantajlı olmalı"
    far = run("TGT-TEL-15", we.Scenario(air_defense="VLRSAM"))
    sub = far[(far["Durum"] == we.STATUS_OK) & (far["Ucus_Suresi_s"] > 600)]
    assert len(sub) and (sub["C_TST"] < 1).all()
    fixed = ok_rows(run("TGT-HAS-01", we.Scenario(air_defense="VLRSAM")))
    assert (fixed["C_TST"] == 1.0).all(), "TST olmayan hedefte uçuş süresi cezası yok"
    longer = ok_rows(run("TGT-TEL-15", we.Scenario(air_defense="VLRSAM", tst_window_s=3600)))
    assert (longer["C_TST"] == 1.0).all()
    assert we.collateral_factor(50, "High") == 1.0 and we.collateral_factor(150, "High") == 0.5
    assert we.collateral_factor(5000, "High") == we.CDE_FACTOR_FLOOR and we.collateral_factor(5000, "Low") == 1.0
    low = row(run("TGT-HQB-06", we.Scenario(cde_tier="Low")), "GBU-31(V)1/B JDAM")
    high = row(run("TGT-HQB-06"), "GBU-31(V)1/B JDAM")
    assert high["K_CDE"] < 1.0 == low["K_CDE"] and high["PK_Tek_Atis"] == low["PK_Tek_Atis"]
    assert high["Uygunluk_Skoru"] < low["Uygunluk_Skoru"], "yüksek CDE hassasiyetinde büyük bomba cezalanır"
    assert we.expected_bda(0.8) == "SEVERE" and we.expected_bda(0.5) == "MODERATE" and we.expected_bda(0.01) == "NEGLIGIBLE"


@test
def pk_esittir_ph_carpi_pd_ve_jaws_eslesmesi():
    for tid in ("TGT-HAS-01", "TGT-MBT-16", "TGT-POL-09", "TGT-FRG-23"):
        good = ok_rows(run(tid))
        expected = (good["Ph"] * good["Pd"] * we.RELIABILITY).clip(upper=we.PK_CAP)
        assert np.allclose(good["PK_Tek_Atis"], expected, atol=2e-4), f"{tid}: Pk != Ph·Pd·güvenilirlik"
    blast = run("TGT-POL-09")
    jdam = row(blast, "GBU-31(V)1/B JDAM")
    assert jdam["Hasar_Mekanizmasi"] == "Blast"
    assert math.isclose(jdam["Olumcul_Yaricap_m"], jdam["Patlama_Yaricapi_m"], rel_tol=1e-3), "Blast hedefinde yarıçap fizik modelinden"
    assert jdam["Tali_Hasar_Yaricapi_m"] > jdam["Patlama_Yaricapi_m"]
    assert (jdam["Hedefte_Asiri_Basinc_psi"] >= jdam["Sertlik_psi"]) == (jdam["Patlama_Yaricapi_m"] >= jdam["Gerekli_Yaricap_m"])
    tank = row(run("TGT-MBT-16"), "Brimstone")
    assert tank["Hasar_Mekanizmasi"] == "Direct_Hit" and tank["Olumcul_Yaricap_m"] > tank["Patlama_Yaricapi_m"]
    # tekil eşleşme = toplu değerlendirme
    scenario = we.Scenario(air_defense="MRSAM")
    one = we.evaluate_jaws_match("TGT-FRG-23", "BrahMos-A", scenario)
    ref = row(run("TGT-FRG-23", scenario), "BrahMos-A")
    for key in ("Ph", "Pd", "PK_Tek_Atis", "Uygunluk_Skoru", "Durum"):
        assert one[key] == ref[key], key
    same = we.evaluate_jaws_match(we.get_target("TGT-FRG-23", TGT), row(RAW, "BrahMos-A"), {"air_defense": "MRSAM"})
    assert same["PK_Tek_Atis"] == ref["PK_Tek_Atis"], "ham satır ve sözlük ortam girdisi de çalışmalı"
    assert we.evaluate_jaws_match("TGT-HAS-01", "Mk-82")["PK_Tek_Atis"] == 0, "HE-Frag sertleştirilmiş hedefte PK 0"
    s400 = ok_rows(run("TGT-EWR-12", we.Scenario(air_defense="VLRSAM")))
    assert we.AIR_DEFENSE_TIERS["VLRSAM"].standoff_km == 400 and (s400["Maksimum_Menzil_km"] >= 400).all()


# --------------------------------------------------------------------------- alt modeller
@test
def olumcul_yaricap_kup_kok_olcekleme():
    r1 = we.lethal_radius_m(100, "HE-Frag", "Personnel")
    r8 = we.lethal_radius_m(800, "HE-Frag", "Personnel")
    assert math.isclose(r8, 2 * r1, rel_tol=1e-9), "R ∝ W^(1/3): 8 kat kütle → 2 kat yarıçap"
    assert math.isclose(r1, we.LETHAL_K["Personnel"] * 100 ** (1 / 3), rel_tol=1e-9)
    radii = [we.lethal_radius_m(w, "HE-Frag", "Soft_Vehicle") for w in (5, 50, 500, 5000)]
    assert radii == sorted(radii)
    assert we.lethal_radius_m(200, "HE-Frag", "Personnel") > we.lethal_radius_m(200, "HE-Frag", "Armored_Vehicle")
    assert we.lethal_radius_m(200, "HE-Frag", "Personnel", "Extreme") < we.lethal_radius_m(200, "HE-Frag", "Personnel")
    assert math.isnan(we.lethal_radius_m(float("nan"), "HE-Frag", "Personnel"))


@test
def delme_modeli_siralama_ve_esikler():
    heavy = we.estimate_penetration_m("Penetrator", 1996, 368, 1.1, True)
    medium = we.estimate_penetration_m("Penetrator", 874, 368, 1.1, True)
    light = we.estimate_penetration_m("Penetrator", 93, 190, 0.9, True)
    gp = we.estimate_penetration_m("HE-Frag", 925, 457, 0.9, True)
    assert heavy > medium > light > 0 and gp < medium
    assert 1.5 < medium < 3.5, f"2000 lb sınıfı delici açık kaynak mertebesinde olmalı: {medium:.2f} m"
    tandem = we.estimate_penetration_m("BROACH", 450, 480, 0.8, False)
    unitary = we.estimate_penetration_m("Penetrator", 450, 480, 0.8, False)
    assert tandem > unitary
    assert we.penetration_factor(2.0, 0.0) == 1.0 and we.penetration_factor(2.0, 1.5) == 1.0
    assert we.penetration_factor(0.4, 1.0) == 0.0
    assert math.isclose(we.penetration_factor(0.8, 1.0), 0.8 ** 3)


@test
def isabet_ve_atis_sayisi_formulleri():
    assert math.isclose(we.circular_hit_probability(10, 10), 0.5), "ıska = CEP → %50"
    assert we.circular_hit_probability(30, 10) > 0.99 and we.circular_hit_probability(1, 60) < 0.001
    assert we.required_weapons(0.5, 0.9) == 4 and we.required_weapons(0.95, 0.9) == 1
    assert math.isnan(we.required_weapons(0.0, 0.9))
    assert we.required_weapons(0.001, 0.9) == we.MAX_WEAPONS_REPORTED
    assert we.proportionality_factor(10, 10) == 1.0
    assert math.isclose(we.proportionality_factor(100, 10), 1 - we.OVERKILL_MAX_PENALTY)
    assert we.standoff_factor(50, 0) == 1.0 and we.standoff_factor(50, 100) == 0.0
    assert math.isclose(we.standoff_factor(100, 100), we.STANDOFF_BASE) and we.standoff_factor(300, 100) == 1.0


@test
def gudum_modlari_ve_tasiyici_siniflari():
    assert we.guidance_modes("INS/GPS_Only", "INS/GPS") == ("INS/GPS",)
    assert we.guidance_modes("MMW+SAL", "INS") == ("MMW", "SAL")
    assert we.guidance_modes("SAL", "INS/GPS") == ("SAL", "INS/GPS")
    assert we.guidance_modes("Unguided", "Unpowered_Ballistic") == ("Unguided",)
    assert we.guidance_modes("NA", "INS/GPS") == ("INS/GPS",) and we.guidance_modes("NA", "NA") == ()
    assert we.carrier_classes("F-16,Akıncı,T129") == ("Uçak", "Helikopter", "SİHA")
    assert we.carrier_classes("TB2,TB3") == ("SİHA",) and we.carrier_classes("NA") == ()
    known = we.UAV_PLATFORMS | we.HELICOPTER_PLATFORMS
    tokens = {p for v in MUN["Entegre_Platformlar"] for p in v.split(",")}
    assert we.UAV_PLATFORMS <= tokens | {"MQ-9B"}, "veri setinde olmayan SİHA adı"
    assert not (we.UAV_PLATFORMS & we.HELICOPTER_PLATFORMS) and known


# --------------------------------------------------------------------------- zorunlu kurallar
@test
def kural_sertlestirilmis_hedefte_harp_basligi():
    for tid in targets_where(Target_Class="Hardened_Structure"):
        res = run(tid)
        wrong = res[~res["Harp_Basligi_Tipi"].isin(we.HARD_TARGET_WARHEADS)]
        assert (wrong["Durum"] != we.STATUS_OK).all(), f"{tid}: izinsiz harp başlığı UYGUN çıktı"
        scored = wrong[wrong["PK_Tek_Atis"].notna()]
        assert len(scored) > 50 and (scored["PK_Tek_Atis"] == 0).all(), f"{tid}: HE-Frag PK'si 0 olmalı"
        assert ok_rows(res)["Harp_Basligi_Tipi"].isin(we.HARD_TARGET_WARHEADS).all()
        assert (ok_rows(res)["Tahmini_Delme_m"] >= we.PEN_FAIL_RATIO * res.attrs["target"][
            "Required_Concrete_Penetration_m"]).all()


@test
def kural_hizli_hedefte_terminal_arayici():
    coordinate_only = {"INS/GPS", "INS", "Unguided"}
    for tid in targets_where(Target_Mobility_Class="Fast"):
        res = run(tid)
        merged = res.merge(MUN[["Muhimmat_Adi", "Gudum_Modlari"]], on="Muhimmat_Adi")
        blind = merged[merged["Gudum_Modlari"].map(lambda s: bool(s) and set(s.split("|")) <= coordinate_only)]
        assert len(blind) > 30
        assert (blind["Durum"] != we.STATUS_OK).all(), f"{tid}: INS/GPS_Only mühimmat UYGUN çıktı"
        scored = blind[blind["P_Isabet"].notna()]
        assert (scored["P_Isabet"] <= 0.03).all(), f"{tid}: isabet sıfıra yakınsamalı"
        assert ok_rows(res)["Secilen_Gudum_Modu"].isin(we.HOMING_MODES).all()


@test
def kural_sam_varsa_standoff_elemesi():
    for tid in ("TGT-HAS-01", "TGT-SAM-13", "TGT-INF-21"):
        base = ok_rows(run(tid))
        for key, tier in we.AIR_DEFENSE_TIERS.items():
            res = run(tid, we.Scenario(air_defense=key))
            good = ok_rows(res)
            assert len(good) <= len(base)
            if tier.standoff_km > 0:
                assert good["Maksimum_Menzil_km"].notna().all(), "menzili bilinmeyen mühimmat standoff'ta elenmeli"
                assert (good["Maksimum_Menzil_km"] >= tier.standoff_km).all()
                short = res[res["Maksimum_Menzil_km"] < tier.standoff_km]
                assert len(short) and (short["Durum"] == we.STATUS_ELIMINATED).all()
                assert (good["K_Standoff"] >= we.STANDOFF_BASE).all()
            else:
                assert (good["K_Standoff"] == 1.0).all()
        assert len(ok_rows(run(tid, we.Scenario(air_defense="LRSAM")))) < len(base)
    custom = ok_rows(run("TGT-INF-21", we.Scenario(air_defense="LRSAM", standoff_km=500)))
    assert (custom["Maksimum_Menzil_km"] >= 500).all(), "elle girilen standoff kademeyi ezmeli"


@test
def kural_havadan_havaya_fuze_atanmaz():
    for tid in TGT["Target_ID"]:
        res = run(tid)
        aam = res[res["Alt_Kategori"].isin(we.AIR_TO_AIR_SUBCATEGORIES)]
        assert len(aam) >= 40 and (aam["Durum"] == we.STATUS_ELIMINATED).all()
        assert aam["Eleme_Kodu"].str.startswith("ROL").all()


@test
def kural_pasif_rf_ve_lazer_isaretleme():
    assert row(run("TGT-MBT-16"), "AGM-88B HARM")["Eleme_Kodu"] == "GUDUM_MODU"
    assert row(run("TGT-EWR-12"), "AGM-88B HARM")["Durum"] == we.STATUS_OK
    no_laser = run("TGT-INF-21", we.Scenario(laser_designation=False))
    assert row(no_laser, "GBU-12 Paveway II")["Eleme_Kodu"] == "GUDUM_MODU"
    assert row(no_laser, "GBU-54 Laser JDAM")["Secilen_Gudum_Modu"] == "INS/GPS", "LJDAM koordinat moduna düşmeli"
    assert not ok_rows(no_laser)["Secilen_Gudum_Modu"].isin(we.LASER_MODES).any()


@test
def kural_sahne_esleme_ve_gemisavar_rolu():
    assert bool(row(MUN, "AGM-158A JASSM")["Sahne_Eslemeli"]) and not bool(row(MUN, "SOM-B1")["Sahne_Eslemeli"])
    jassm_vs_ship = row(run("TGT-FRG-23"), "AGM-158A JASSM")
    assert jassm_vs_ship["P_Isabet"] <= 0.16, "veri bağsız seyir füzesi hareketli gemiyi izleyemez"
    assert row(run("TGT-AFV-17"), "AGM-158A JASSM")["Eleme_Kodu"] == "HAREKETLILIK"
    assert row(run("TGT-PRS-25"), "AGM-158A JASSM")["PK_Tek_Atis"] > 0.5, "rıhtımdaki (sabit) gemide kullanılabilir"
    lrasm_sea = row(run("TGT-FRG-23"), "AGM-158C LRASM")
    lrasm_land = row(run("TGT-MBT-16"), "AGM-158C LRASM")
    assert lrasm_sea["K_Rol"] == 1.0 and lrasm_land["K_Rol"] == we.ROLE_SECONDARY_FACTOR
    assert lrasm_land["Uygunluk_Skoru"] < 0.5 * lrasm_sea["Uygunluk_Skoru"]
    assert we.role_factor("ARM", "Radar/Air_Defense") == 1.0 and we.role_factor("ARM", "Soft_Vehicle") < 1.0
    assert we.role_factor("Bunker_Buster", "Hardened_Structure") == 1.0
    assert we.role_factor("Bunker_Buster", "Naval") == we.ROLE_SECONDARY_FACTOR
    frigate = ok_rows(run("TGT-FRG-23"))
    first = frigate.iloc[0]
    assert first["Alt_Kategori"] == "AShM", f"fırkateynde ilk sıra gemisavar olmalı: {first['Muhimmat_Adi']}"


@test
def kural_etkisiz_muhimmat_elenir():
    for tid in TGT["Target_ID"]:
        res = run(tid)
        assert (ok_rows(res)["PK_Tek_Atis"] >= we.MIN_ELIGIBLE_PK).all(), f"{tid}: PK eşiği altı UYGUN çıktı"
        weak = res[res["Eleme_Kodu"] == "ETKISIZ"]
        assert (weak["PK_Tek_Atis"] < we.MIN_ELIGIBLE_PK).all() and (weak["Durum"] == we.STATUS_ELIMINATED).all()
    battery = run("TGT-ART-18")
    assert row(battery, "GBU-31(V)1/B JDAM")["Eleme_Kodu"] == "ETKISIZ", "tek parça bomba dağınık bataryada etkisiz"
    assert set(ok_rows(battery)["Harp_Basligi_Tipi"]) == {"Submunition"}


# --------------------------------------------------------------------------- çıktı bütünlüğü
@test
def skor_araligi_ve_siralama():
    for tid in TGT["Target_ID"]:
        res = run(tid)
        assert list(res.columns) == we.RESULT_COLUMNS
        assert set(res["Durum"]) <= set(we.STATUS_ORDER) and len(res) == len(MUN)
        good = ok_rows(res)
        assert good["Uygunluk_Skoru"].between(0, 100).all()
        assert good["PK_Tek_Atis"].between(0, we.PK_CAP).all()
        assert good["Uygunluk_Skoru"].is_monotonic_decreasing, f"{tid}: skor sırası bozuk"
        assert list(good["Sira"]) == list(range(1, len(good) + 1))
        assert (good["Eleme_Nedeni"] == "").all() and (good["Gerekce"] != "").all()
        rest = res[res["Durum"] != we.STATUS_OK]
        assert (rest["Uygunluk_Skoru"] == 0).all() and (rest["Eleme_Nedeni"] != "").all()
        assert (good["Uygunluk_Skoru"] <= 100 * good["PK_Tek_Atis"] + 0.06).all(), "çarpanlar skoru yalnız düşürür"


@test
def varsayilan_donus_filtreli_ve_top_n():
    full = run("TGT-MBT-16")
    default = we.calculate_weapon_effectiveness("TGT-MBT-16", munitions=MUN, targets=TGT)
    assert (default["Durum"] == we.STATUS_OK).all() and len(default) == len(ok_rows(full))
    top = we.calculate_weapon_effectiveness("TGT-MBT-16", munitions=MUN, targets=TGT, top_n=5)
    assert len(top) == 5 and top["Muhimmat_Adi"].tolist() == default["Muhimmat_Adi"].head(5).tolist()
    assert we.recommend("TGT-MBT-16", top_n=3, munitions=MUN, targets=TGT)["Sira"].tolist() == [1, 2, 3]
    from_disk = we.calculate_weapon_effectiveness("TGT-MBT-16")
    assert from_disk["Muhimmat_Adi"].tolist() == default["Muhimmat_Adi"].tolist(), "varsayılan yükleme farklı"


@test
def belirleyicilik_ve_girdi_bicimleri():
    a, b = run("TGT-SAM-13"), run("TGT-SAM-13")
    pd.testing.assert_frame_equal(a, b)
    from_raw = we.calculate_weapon_effectiveness("TGT-SAM-13", munitions=RAW, targets=TGT, include_eliminated=True)
    pd.testing.assert_frame_equal(a, from_raw)
    numeric = RAW.copy()
    for col in we.MUNITION_NUMERIC:
        numeric[col] = pd.to_numeric(numeric[col], errors="coerce")
    numeric["Ek_Sutun"] = 1
    from_numeric = we.calculate_weapon_effectiveness("TGT-SAM-13", munitions=numeric, targets=TGT,
                                                     include_eliminated=True)
    pd.testing.assert_frame_equal(a, from_numeric)
    assert we.prepare_munitions(MUN) is MUN, "hazır veri yeniden işlenmemeli"


@test
def hatali_girdiler():
    for bad in (dict(air_defense="S-400"), dict(weather="RAIN"), dict(standoff_km=-1), dict(desired_damage=1.0),
                dict(carrier_classes=("Tank",)), dict(tst_window_s=0), dict(cde_tier="Extreme")):
        try:
            we.Scenario(**bad)
        except ValueError:
            continue
        raise AssertionError(f"Scenario({bad}) hata vermeliydi")
    for call in (lambda: run("TGT-YOK-99"), lambda: run("TGT-HAS-01", target_overrides={"Yok_Sutun": 1})):
        try:
            call()
        except KeyError:
            continue
        raise AssertionError("KeyError bekleniyordu")
    try:
        run("TGT-HAS-01", target_overrides={"Passive_Defense_Level": "Ultra"})
    except ValueError:
        pass
    else:
        raise AssertionError("geçersiz override ValueError vermeliydi")
    try:
        we.prepare_munitions(RAW.drop(columns="Harp_Basligi_Tipi"))
    except ValueError:
        pass
    else:
        raise AssertionError("eksik sütun ValueError vermeliydi")


# --------------------------------------------------------------------------- senaryo etkileri
@test
def ortam_kisitlari_etkisi():
    clear, murky = run("TGT-MBT-16"), run("TGT-MBT-16", we.Scenario(weather="OBSCURED"))
    for name in ("AGM-114K Hellfire II", "L-UMTAS"):
        assert row(murky, name)["P_Isabet"] < 0.6 * row(clear, name)["P_Isabet"], f"{name}: kapalı havada SAL düşmeli"
    assert math.isclose(row(murky, "Brimstone")["P_Isabet"], 0.95 * row(clear, "Brimstone")["P_Isabet"], rel_tol=1e-3)
    jam = run("TGT-POL-09", we.Scenario(gnss_jamming=True))
    free = run("TGT-POL-09")
    assert row(jam, "GBU-38 JDAM")["CEP_Etkin_m"] == we.GNSS_JAM_CEP_FACTOR * row(free, "GBU-38 JDAM")["CEP_Etkin_m"]
    assert row(jam, "GBU-38 JDAM")["PK_Tek_Atis"] < row(free, "GBU-38 JDAM")["PK_Tek_Atis"]
    assert row(jam, "GBU-12 Paveway II")["PK_Tek_Atis"] == row(free, "GBU-12 Paveway II")["PK_Tek_Atis"]


@test
def tasiyici_ve_platform_filtresi():
    uav = ok_rows(run("TGT-INF-21", we.Scenario(carrier_classes=("SİHA",))))
    assert len(uav) > 10 and uav["Tasiyici_Sinifi"].str.contains("SİHA").all()
    both = ok_rows(run("TGT-INF-21", we.Scenario(carrier_classes=("SİHA", "Helikopter"))))
    assert len(both) >= len(uav)
    akinci = ok_rows(run("TGT-MBT-16", we.Scenario(platform="Akıncı")))
    assert len(akinci) > 5 and akinci["Entegre_Platformlar"].map(lambda s: "Akıncı" in s.split(",")).all()
    assert "L-UMTAS" in akinci["Muhimmat_Adi"].head(5).tolist()


@test
def istenen_hasar_atis_sayisini_degistirir():
    low = row(run("TGT-MBT-16", we.Scenario(desired_damage=0.5)), "Brimstone")
    high = row(run("TGT-MBT-16", we.Scenario(desired_damage=0.99)), "Brimstone")
    assert low["Gerekli_Atis_Sayisi"] < high["Gerekli_Atis_Sayisi"] and low["PK_Tek_Atis"] == high["PK_Tek_Atis"]


# --------------------------------------------------------------------------- beklenen davranışlar
@test
def her_hedef_icin_makul_oneri():
    expected_any = {
        "TGT-HAS-01": {"Storm Shadow (SCALP-EG)", "Taurus KEPD 350", "SOM-B2", "AGM-154C JSOW", "GBU-24 Paveway III"},
        "TGT-DUF-03": {"GBU-57A/B MOP"},
        "TGT-MBT-16": {"Brimstone", "Brimstone 2", "AGM-179 JAGM", "AGM-114L Longbow Hellfire"},
        "TGT-ART-18": {"CBU-105 SFW (WCMD)"},
        "TGT-FRG-23": {"BrahMos-A", "Kh-59MK", "AGM-158C LRASM"},
        "TGT-FAC-24": {"Exocet AM39", "Kh-35U", "YJ-83K", "C-802AK"},
    }
    for tid in TGT["Target_ID"]:
        good = ok_rows(run(tid))
        assert len(good) >= 1, f"{tid}: temel senaryoda uygun mühimmat yok"
        assert good.iloc[0]["PK_Tek_Atis"] >= 0.5, f"{tid}: en iyi seçenek PK {good.iloc[0]['PK_Tek_Atis']}"
        if tid in expected_any:
            top = set(good["Muhimmat_Adi"].head(5))
            assert top & expected_any[tid], f"{tid}: ilk 5 beklenen sınıfı içermiyor → {sorted(top)}"
    deep = ok_rows(run("TGT-DUF-03"))
    assert deep.iloc[0]["Muhimmat_Adi"] == "GBU-57A/B MOP" and len(deep) <= 3
    assert ok_rows(run("TGT-DUF-03", we.Scenario(air_defense="LRSAM"))).empty, "boş sonuç desteklenmeli"
    radar = run("TGT-EWR-12", we.Scenario(air_defense="LRSAM"))
    assert row(radar, "AGM-88E AARGM")["Durum"] == we.STATUS_OK and row(radar, "MAM-L")["Durum"] == we.STATUS_ELIMINATED


@test
def veri_yetersiz_ve_tahmin_isaretleri():
    res = run("TGT-INF-21")
    no_data = res[res["Durum"] == we.STATUS_NO_DATA]
    assert len(no_data) >= 10 and no_data["PK_Tek_Atis"].isna().all()
    assert "NEB-84" in no_data["Muhimmat_Adi"].tolist()
    maml = row(res, "MAM-L")
    assert bool(maml["Harp_Basligi_Tahmini"]) and 5 < maml["Harp_Basligi_Etkin_kg"] < 22
    assert "tahmini" in maml["Gerekce"]
    assert not bool(row(res, "Mk-82")["Harp_Basligi_Tahmini"])
    summary = we.elimination_summary(res)
    assert summary["Adet"].sum() == (res["Durum"] != we.STATUS_OK).sum()


@test
def pasif_savunma_duyarliligi_monoton():
    for tid in ("TGT-SAM-13", "TGT-HAS-01", "TGT-INF-22", "TGT-FRG-23"):
        sweep = we.sensitivity_passive_defense(tid, munitions=MUN, targets=TGT)
        assert sweep["Passive_Defense_Level"].tolist() == list(we.PASSIVE_LEVELS) and sweep["Mevcut"].sum() == 1
        assert sweep["En_Yuksek_PK"].is_monotonic_decreasing, f"{tid}: pasif savunma arttıkça PK düşmeli"
        assert sweep["Etkili_Muhimmat_Sayisi"].is_monotonic_decreasing
        assert sweep["En_Yuksek_PK"].iloc[-1] < sweep["En_Yuksek_PK"].iloc[0]


@test
def sertlestirme_duyarliligi_monoton():
    sweep = we.sensitivity_hardening("TGT-HAS-01", munitions=MUN, targets=TGT)
    assert sweep["Etkili_Muhimmat_Sayisi"].is_monotonic_decreasing
    assert sweep["Uygun_Muhimmat_Sayisi"].is_monotonic_decreasing
    assert sweep["Etkili_Muhimmat_Sayisi"].iloc[0] > sweep["Etkili_Muhimmat_Sayisi"].iloc[-1]
    wide = we.sensitivity_hardening("TGT-HAS-01", thicknesses=[0, 30], munitions=MUN, targets=TGT)
    assert wide["Uygun_Muhimmat_Sayisi"].iloc[-1] == 0 and wide["En_Iyi_Muhimmat"].iloc[-1] == "-"
    assert np.isfinite(sweep["En_Yuksek_PK"]).all()


def main() -> int:
    failed = 0
    for fn in TESTS:
        try:
            fn()
            print(f"[OK ] {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"[FAIL] {fn.__name__}: {exc}")
    print(f"\n{len(TESTS) - failed}/{len(TESTS)} test geçti "
          f"({len(MUN)} mühimmat × {len(TGT)} hedef; veri: {os.path.relpath(SOURCE, we.ROOT)})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
