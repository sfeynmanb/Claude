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
