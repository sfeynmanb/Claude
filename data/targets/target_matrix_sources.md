# Hedef Matrisi — Tanımlar, Kaynaklar ve Güvenilirlik Notları

Dosya: `target_vulnerability_matrix.csv` (`;` ayraçlı, UTF-8, 26 hedef × 16 sütun).
Doğrulama: `python3 src/validate_target_matrix.py`. Motor (`src/weaponeering_engine.py`) bu dosyayı kullanır.
Önceki 9 sütunlu sürüm `target_vulnerability_matrix_v1.csv` yalnız arşiv olarak durur.

## Baştan bilinmesi gerekenler

1. **UFC 3-340-01 kullanılmadı.** Dağıtımı ABD hükümeti ve yüklenicileriyle sınırlı, ihracat kontrollüdür.
   Bu çalışmadaki hiçbir değer veya denklem ondan gelmez.
2. **"UFC sertlik değeri" hedef tipi başına yayımlanmış bir büyüklük değildir.** UFC 3-340-02 bir yük ve
   tasarım kılavuzudur; hedef kataloğu içermez. `UFC_Hardness_Rating_psi` sütunu, açık hasar eşiği
   literatüründen alınan veya türetilen **yaklaşık serbest alan tepe aşırı basıncıdır (ağır hasar düzeyi)**.
3. **Değerlerin çoğu doğrulanmış değildir.** 26 satırın yalnız 1'i `Kaynakli`, 12'si `Turetilmis`,
   13'ü `Varsayim`. Hiçbiri JMEM/JWS verisi değildir.
4. **Basınç birçok hedefte doğru hasar ölçütü değildir.** Araçlar, antenler, köprüler ve uçaklar
   sürüklemeye ve parçacığa; sığınaklar delme + iç patlamaya; pist kraterlemeye duyarlıdır. Bu satırlarda
   psi değeri yalnız "vekil gösterge"dir ve `Hardness_Basis` sütununda böyle yazılmıştır.

## Sütunlar

| Sütun | Tanım | Güvenilirlik |
|---|---|---|
| `Target_ID` | `TGT-XXX-NN` | — |
| `Target_Category` | `Point\|Area / Hard\|Soft / Fixed\|Mobile\|Relocatable` | Genel weaponeering terminolojisi; AFDP 3-60'ta bu üçlü etiketin birebir geçtiği doğrulanamadı |
| `Target_Description` | İngilizce ad + Türkçe ayrıntı | — |
| `UFC_Hardness_Rating_psi` | Ağır hasar için yaklaşık tepe aşırı basınç | Satır bazında `Data_Confidence` |
| `Required_Concrete_Penetration_m` | Delinmesi gereken betonarme kalınlığı | **Tümü varsayım**; v1 matrisinden taşındı, yayımlanmış tasarım verisi değil |
| `Target_Mobility_Class` | Fixed / Slow / Fast | Tanımsal |
| `TST_Status` | Zamana duyarlı hedef adayı mı | **Varsayım.** Doktrinde TST'yi komutan belirler; hedef tipinin sabit özelliği değildir |
| `Radar_Cross_Section_m2` | Mertebe tahmini | **Tümü varsayım**; bakış açısı ve frekansa göre mertebelerce değişir |
| `Required_Lethal_Radius_m` | Hedefin etkisiz kalması için kapsanması gereken yarıçap (hedef izi) | **Tümü varsayım**; hedefin fiziksel boyutundan türetildi |
| `Collateral_Damage_Tier` | Low / Medium / High | **Senaryo varsayımı.** Tali hasar hedef tipine değil konuma bağlıdır; Adım 3'te arayüzden değiştirilebilir olacak |
| `Passive_Defense_Level` | Low / Medium / High / Extreme (ek sütun) | Varsayım; v1'den taşındı |
| `Thermal_Signature` | Low / Medium / High (ek sütun) | Varsayım; v1'den taşındı |
| `Target_Class` | Motorun kural tablolarının anahtarı: sertleştirilmiş yapı, yumuşak yapı, altyapı, zırhsız/zırhlı araç, radar/hava savunma, deniz, personel (ek sütun) | Tanımsal |
| `Primary_Damage_Mechanism` | Blast / Fragment / Direct_Hit / Penetration / Crater (ek sütun). Patlama basıncı modeli yalnız `Blast` satırlarında etki yarıçapını belirler | Mühendislik yargısı; varsayım |
| `Hardness_Basis` | Sertlik değerinin ölçütü ve dayanağı (ek sütun) | — |
| `Data_Confidence` | Yalnız sertlik değeri için: `Kaynakli` / `Turetilmis` / `Varsayim` (ek sütun) | — |

`Data_Confidence` anlamı: **Kaynakli** = değer bu çalışma sırasında bir kaynakta görüldü;
**Turetilmis** = adı geçen kaynağa dayanıyor ama değer bu oturumda birincil metinden teyit edilemedi ya da
benzer bir hedeften uyarlandı; **Varsayim** = yayımlanmış dayanak yok, yalnız göreli sıralama için.

## Sertlik değerlerinin dayanakları

| Dayanak | Kullanıldığı satırlar | Not |
|---|---|---|
| Glasstone & Dolan (1977): 5 psi'de yandan yük alan kamyon devrilir, yığma ev ağır hasar görür | CNV-20 (Kaynakli); SAM-13, TEL-15, CPX-19, AMD-10 (Turetilmis) | Nükleer (uzun süreli) patlama verisi; konvansiyonel kısa süreli darbede aynı basınç daha az hasar verir |
| Glasstone & Dolan (1977) yapı/gemi/uçak/tank hasar mertebeleri | HQB-06, POL-09, FRG-23, ACP-26 | Değerler hafızadan; birincil tablo bu oturumda açılamadı → Turetilmis |
| Depodaki `PassiveDefenseOptimizer/loadDamageThresholdTable.m` (UFC 3-340-02, Bowen eğrisi, ASCE, ACI 349 atıflı): betonarme parçalanma 200 kPa, akciğer hasarı 250 kPa, %99 ölümcül 450 kPa | PBX-04, INF-21, INF-22 | Tablonun kendi atıfları bu çalışmada yeniden doğrulanmadı |
| DoD 6055.09 toprak örtülü depo sınıfları (7-bar / 3-bar / tanımsız) | IGL-05 | Sınıf adları hafızadan; hangi sınıfın seçileceği varsayım |
| Dayanak yok | HAS-01, C2B-02, DUF-03, RWY-07, BRG-08, CMN-11, EWR-12, SHD-14, MBT-16, AFV-17, ART-18, FAC-24, PRS-25 | Varsayim |

Personel eşikleri kaynaklar arasında büyük fark gösterir: kulak zarı yırtılması ~5 psi (%50 için ~15 psi),
akciğer hasarı eşiği 10–40 psi, ölümcül düzey darbe süresine göre 80–200 psi. Tek bir sayı güvenilir değildir.

## Doğrulanamayan noktalar

- AFDP 3-60'ın güncel metnine erişilemedi; TST tanımı 2019 tarihli Annex 3-60 girişinden alındı.
- STANAG 3596 hedef kategori numaralarının tam listesi doğrulanamadı; bu yüzden numara atfedilmedi.
- CJCSI 3160.01 tali etki yarıçapı (CER) tabloları kamuya açık değil; `Collateral_Damage_Tier` onlardan türetilmedi.
- Sığınak, HAS ve gömülü tesislerin gerçek tasarım dirençleri yayımlanmamıştır.

## Kaynaklar

- UFC 3-340-01 dağıtım kısıtı: https://www.wbdg.org/FFC/DOD/UFC/ufc_3_340_01_2002.pdf
- UFC 3-340-02 (2014, Değişiklik 1, arşiv): https://stg.wbdg.org/FFC/DOD/UFC/ARCHIVES/ufc_3_340_02_2014_c1.pdf
- Glasstone & Dolan, *The Effects of Nuclear Weapons* (1977), özet: https://archive.org/download/DnaEm1CapabilitiesOfNuclearWeapons/Glasstone%20and%20Dolan%20Effects%20of%20Nuclear%20Weapons%201977%20edition%20EXTRACT.pdf
- FEMA 426, Bölüm 4 (patlama hasar düzeyleri): https://www.scribd.com/document/319988920/fema426-ch4
- FM 8-9, patlama yaralanmaları: https://nuke.fas.org/guide/usa/doctrine/dod/fm8-9/1ch4.htm
- Annex 3-60 Targeting, giriş (2019): https://www.doctrine.af.mil/Portals/61/documents/Annex_3-60/3-60-D01-Target-Intro.pdf
- NATO hedef raporlama kategorileri (NCAP): https://ncap.org.uk/sites/default/files/NATO_Target_Reporting_Categories_v2.pdf
- CJCSI 3160.01B (2015): https://www.esd.whs.mil/Portals/54/Documents/FOID/Reading%20Room/Joint_Staff/16-F-0427_Damage_Estimate_Methodology.pdf

## Motorda kullanılan alt modeller (Adım 2)

| Alt model | Dayanak | Güvenilirlik |
|---|---|---|
| Tepe gelen aşırı basınç | Kinney & Graham (1985), *Explosive Shocks in Air* kapalı form bağıntısı | Yayımlanmış bağıntı; depodaki Kingery-Bulmash tipi tabloyla 0.8-1.8 kat aralığında uyumlu (testte denetlenir). UFC 3-340-02'nin Kingery-Bulmash polinomları kullanılmadı |
| Yer yüzeyi katsayısı 1.8 | UFC 3-340-02 yarım küre yüzey patlaması yaklaşımı | Yaygın mühendislik yaklaşımı |
| Dolgu oranları | Mk-82/84 (%38-46) ve BLU-109 (%27) açık kaynak değerleri | Diğer harp başlığı tipleri **varsayım** |
| Fano kılıf düzeltmesi `0.2 + 0.8/(1+2M/C)` | Fisher (1953) değiştirilmiş Fano bağıntısı | Hafızadan; birincil kaynaktan teyit edilmedi |
| TNT eşdeğerlik katsayısı | Veri setinde patlayıcı türü yok → 1.0 (TNT) | Temkinli varsayım |
| Beton delme | Young (1997), SAND97-2426 beton denklemi biçimi | Toplu sabit C temsilî; açık kaynak delme değerlerine göre ayarlı |
| TST penceresi (600 s), CDE yarıçap sınırları (200 / 75 m), BDA eşikleri | Yok | **Varsayım**; senaryodan değiştirilebilir |
| Tali hasar halkası (1 psi) | Cam kırılması düzeyi aşırı basınç | Parçacık tehlikesini içermez; CDE yerine geçmez |
