# Pasif Savunma Çözümü Optimizasyonu ve Eşleştirme

STANAG 4569 (Seviye 1-4+) tehdit profillerine (kinetik enerjili mühimmat,
patlayıcı/IED, topçu-havan mühimmatı) karşı optimum pasif savunma
dizilimini (Seramik-Kompozit-UHPC-Metal-Toprak sandviç zırh) minimum
ağırlık ve lojistik yük ile hesaplayan MATLAB (Octave uyumlu) araç seti.

Bu araç, Ar-Ge ekiplerinin **LS-DYNA / AUTODYN** simülasyonlarından önce
kullanabileceği hızlı bir **ön-analiz / eleme (screening)** aracı olarak
tasarlanmıştır. Sonuçlar nihai tasarım onayı için kullanılmadan önce
hidrokod simülasyonları ve fiziksel V50 atış testleri ile doğrulanmalıdır.

## Çalıştırma

MATLAB veya GNU Octave içinde:

```matlab
cd PassiveDefenseOptimizer
main_PassiveDefenseOptimizer
```

Tehdit senaryosunu değiştirmek için `main_PassiveDefenseOptimizer.m`
dosyasının başındaki **KULLANICI GIRDILERI** bölümünü düzenleyin
(`threat.type = 'KE' | 'HE' | 'HE_FRAG'` ve ilgili parametreler).

Optimization Toolbox (`fmincon`) mevcutsa otomatik olarak ince ayar için
kullanılır; mevcut değilse (varsayılan) kaba-ince (coarse-to-fine) ızgara
taraması sezgisel (heuristic) algoritması ile çalışır — ek kurulum
gerekmez.

## Dosya Yapısı

| Dosya | Görev |
|---|---|
| `main_PassiveDefenseOptimizer.m` | Ana çalıştırma betiği (kullanıcı girdileri burada) |
| `loadMaterialDatabase.m` | Zırh malzeme mikro-veritabanı (UHPC, Seramik, Kompozit, RHA, Toprak) |
| `loadExplosiveDatabase.m` | Patlayıcı TNT eşdeğerlik (RE) faktörleri |
| `loadThreatPresetDatabase.m` | STANAG 4569 Seviye 1-6 mühimmat referans tablosu |
| `loadBlastScaledDistanceTable.m` | Kingery-Bulmash tipi ölçeklendirilmiş mesafe (Z) tablosu |
| `loadDamageThresholdTable.m` | Biyolojik/strüktürel hasar eşikleri (Bowen eğrisi) |
| `classifyThreatSTANAG.m` | Tehdidi STANAG 4569 seviyesine eşler |
| `computeTNTEquivalent.m` | Patlayıcı kütlesini TNT eşdeğerine çevirir |
| `blastLoad.m` | Z, Pso, Pr, td, iso hesaplayıcı (log-log interpolasyon) |
| `kineticEnergyMetrics.m` | E_k, kesit yoğunluğu (SD), enerji yoğunluğu (E_d) |
| `deMarrePenetration.m` | Modifiye De Marre denklemi — gerekli RHA-eşdeğer kalınlık |
| `residualVelocityLambertJonas.m` | Lambert-Jonas kalan hız modeli |
| `sdofPanelResponse.m` | SDOF elasto-plastik blast panel tepkisi (Biggs/UFC 3-340-02) |
| `evaluateDesign.m` | Maliyet/skor fonksiyonu — tüm kısıtları kontrol eder |
| `optimizePassiveDefense.m` | Kaba→ince ızgara taraması (+ opsiyonel `fmincon`) optimizasyon çekirdeği |
| `plotResults.m` | Pareto Front, Kalınlık-Beka, Mesafe-Hasar Olasılığı grafikleri |
| `printDesignReport.m` | Command Window özet raporu |

## Varsayımlar ve Sınırlamalar

- Tüm ampirik katsayılar (De Marre K_DM, malzeme kütlesel verimlilik
  faktörleri E_mat, SDOF süneklik limitleri) mühendislik yaklaşımlarıdır;
  ilgili `.m` dosyalarının içinde kaynağıyla birlikte belgelenmiştir.
- SDOF modeli tek yönlü (basit mesnetli) düzlemsel panel varsayar.
- Toprak bariyer, blast basınç/impulsunu üstel olarak zayıflatan bir
  "standoff" katmanı olarak modellenir; yapısal (SDOF) eleman değildir.
