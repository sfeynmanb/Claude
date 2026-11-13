# Akademik Hava Mühimmatları Veri Seti ve Doğrulama Hattı

Uçak ve SİHA'lardan atılan füze, güdümlü/güdümsüz bomba ve dolanan mühimmatların
fiziksel, balistik ve taksonomik özelliklerini içeren, şema doğrulamalı açık kaynak veri seti.

## Dizin yapısı
```
data/raw/        5 modüler CSV (';' ayraçlı, UTF-8, 20 sütun)
data/processed/  master_air_munitions_dataset.csv / .xlsx
src/             schema_validator.py, test_schema_validator.py, merge_dataset.py, academic_analysis.py
outputs/         summary_report.md, validation_report*.txt, figures/ (300 DPI PNG + veri tabloları)
```

## Çalıştırma
```bash
pip install -r requirements.txt
python3 src/schema_validator.py        # data/raw/*.csv şema denetimi (çıkış kodu 0 = sıfır hata)
python3 src/test_schema_validator.py   # doğrulayıcının hata yakalama testleri
python3 src/merge_dataset.py           # doğrula -> birleştir -> master CSV/XLSX -> yeniden doğrula
python3 src/academic_analysis.py       # EDA raporu ve 3 akademik şekil
```

Yöntem notları, konvansiyonlar ve sınırlılıklar: `outputs/summary_report.md` §8.
Gizli veya teyit edilemeyen değerler `NA` olarak bırakılmıştır.

## Simülasyon platformu (Streamlit)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Veri sırasıyla `data/master_air_munitions.csv`, `data/processed/master_air_munitions_dataset.csv`
yollarından okunur; ikisi de yoksa koda gömülü örnek veriyle açılır. Modüller: Envanter Gezgini,
İstasyon Yükleme (ağırlık/istasyon kısıt kontrolü), Menzil Simülatörü (harita), Karşılaştırma Matrisi.
Fizik modelleri öğretici sezgisel modellerdir; operasyonel kullanım için değildir.

## Weaponeering karar desteği (JAWS benzeri, kural tabanlı)
```
data/targets/target_vulnerability_matrix.csv     26 hedef × 14 sütun: doktriner şema (Adım 1; motor henüz kullanmıyor)
data/targets/target_matrix_sources.md           sütun tanımları, kaynaklar ve güvenilirlik notları
data/targets/target_vulnerability_matrix_v1.csv 20 hedef × 9 sütun: motorun şu an kullandığı sürüm
src/weaponeering_engine.py                     hesap motoru (Streamlit'ten bağımsız kütüphane + CLI)
src/test_weaponeering_engine.py                kural ve değişmez testleri
app_jaws_integrated.py                         app.py klonu + Modül 5 (Weaponeering ve Hedef Analizi)
outputs/weaponeering_report.md                 20 hedef için iki senaryoda ilk 5 öneri
```
```bash
streamlit run app_jaws_integrated.py                              # 5 modüllü pano
python3 src/test_weaponeering_engine.py                           # motor testleri
python3 src/weaponeering_engine.py --list-targets                 # hedef matrisi
python3 src/weaponeering_engine.py T01_HAS --top 5 --air-defense LRSAM --show-eliminated
python3 src/weaponeering_engine.py --report outputs/weaponeering_report.md
```
```python
from weaponeering_engine import Scenario, calculate_weapon_effectiveness
df = calculate_weapon_effectiveness("T10_MOBILE_SAM", Scenario(air_defense="MRSAM"), top_n=5)
```
Mühimmat verisi önce `master_air_munitions_dataset_2.csv` (kök, `data/` veya `data/processed/`), sonra
`data/master_air_munitions.csv` ve `data/processed/master_air_munitions_dataset.csv` yollarında aranır.

**Model:** ölümcül yarıçap `R = K·W^(1/3)`, dairesel normal isabet olasılığı (CEP), Young (1997) biçiminde
sadeleştirilmiş beton delme tahmini, harp başlığı × hedef uyum matrisi ve pasif savunma çarpanları;
`Skor = 100 × PK × orantılılık × standoff payı × rol uyumu`. Tüm katsayılar `weaponeering_engine.py`
başındaki "MODEL PARAMETRELERİ" bölümünden ayarlanır.

**Sınırlılık:** JMEM/JAWS verisi içermez; "PK" kalibre edilmemiş bir sözde-olasılıktır. Hedef matrisindeki
değerler ve model katsayıları temsilîdir. Hedefin aktif savunması, fünye/isabet açısı, taşıyıcı bekası ve
tali hasar modellenmez. Çıktılar göreli sıralama ve pasif savunma duyarlılığı içindir; operasyonel
planlama veya hedefleme için kullanılamaz.
