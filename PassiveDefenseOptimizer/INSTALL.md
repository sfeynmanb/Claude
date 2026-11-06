# Kurulum ve Çalıştırma Direktifi

## 1) Gereksinimler

- **MATLAB R2016b veya üzeri** (uifigure / App Designer bileşenleri gerektiği için `PassiveDefenseOptimizerApp.m` bu sürümden eskisinde çalışmaz).
- **Ek bir toolbox gerekmez.** Optimization Toolbox kuruluysa (`fmincon`) optimizasyon otomatik olarak onunla ince ayar yapar; kurulu değilse program kendi sezgisel (heuristic) ızgara arama algoritmasıyla çalışır — fark etmeden devam edebilirsiniz.
- **GNU Octave** yalnızca komut satırı sürümünü (`main_PassiveDefenseOptimizer.m`) çalıştırabilir. Etkileşimli uygulama (`PassiveDefenseOptimizerApp.m`) Octave'de **çalışmaz**, çünkü Octave `uifigure`/App Designer bileşenlerini desteklemiyor.

## 2) Dosyaları Edinin

Proje `PassiveDefenseOptimizer/` klasöründe, `claude/passive-defense-optimization-matlab-yfzksr` branşında.

**Seçenek A — Git ile:**
```bash
git clone <repo-url>
cd Claude
git checkout claude/passive-defense-optimization-matlab-yfzksr
```

**Seçenek B — Doğrudan dosya indirme:**
Daha önce gönderdiğim dosyaları (`PassiveDefenseOptimizerApp.m`, `runFullPipeline.m`, `main_PassiveDefenseOptimizer.m` ve diğer tüm `.m` dosyaları) **aynı klasöre** kaydedin. Hepsi aynı dizinde olmalı — fonksiyonlar birbirini bu şekilde bulur.

## 3) MATLAB'de Klasörü Tanıtın

MATLAB'i açın, Command Window'a şunlardan birini yazın:

```matlab
cd('C:\...\PassiveDefenseOptimizer')     % Windows ornegi
% veya
cd('/Users/.../PassiveDefenseOptimizer') % macOS/Linux ornegi
```

ya da sağ üstteki **Current Folder** panelinden klasöre çift tıklayın. (Current Folder çubuğunda klasör yolunun göründüğünden emin olun.)

## 4) Çalıştırın

**Etkileşimli uygulama (önerilen):**
```matlab
PassiveDefenseOptimizerApp
```
Pencere açılır → soldan tehdit parametrelerini girin (veya üstten bir STANAG preseti seçin) → **HESAPLA / OPTIMIZE ET** → sağda Rapor / Grafikler / Malzeme Veritabanı sekmelerini inceleyin.

**Komut satırı sürümü (alternatif):**
```matlab
main_PassiveDefenseOptimizer
```
Tehdit parametrelerini bu dosyanın başındaki **KULLANICI GIRDILERI** bölümünden düzenleyip tekrar çalıştırırsınız.

## 5) Doğrulama

Uygulama ilk açıldığında varsayılan değerlerle (STANAG Seviye 3/4 benzeri kombine tehdit) **HESAPLA / OPTIMIZE ET**'e basın. Birkaç saniye içinde:
- **Rapor** sekmesinde STANAG sınıflandırması, patlama yükü ve optimum dizilim metni,
- **Grafikler** sekmesinde 4 panelli sonuç grafikleri

görünmelidir. Bu çıkarsa kurulum doğru tamamlanmış demektir.

## 6) Sık Karşılaşılan Hatalar

| Hata | Çözüm |
|---|---|
| `Undefined function 'uifigure'` | MATLAB sürümünüz R2016b'den eski, ya da Octave kullanıyorsunuz. MATLAB'i güncelleyin veya `main_PassiveDefenseOptimizer` kullanın. |
| `Undefined function or variable 'loadMaterialDatabase'` | Klasör MATLAB path'inde değil. Adım 3'ü tekrarlayın; Current Folder'ın `PassiveDefenseOptimizer` olduğundan emin olun. |
| Grafikler sekmesi boş görünüyor | Önce **HESAPLA / OPTIMIZE ET** düğmesine basmanız gerekir. |
| `Hazır STANAG Senaryosu` seçince alanlar dolmuyor | Normal — preset yalnızca KE (kalibre/kütle/hız/penetratör) alanlarını doldurur; patlayıcı alanlarını (HE_FRAG kullanıyorsanız) elle girmeniz gerekir. |
