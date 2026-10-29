# Çift Kullanımlı (Dual-Use) Karar Destek Algoritmaları
## Sektör, Teknoloji ve Şirket Analizi — Palantir, Helsing ve Karşılaştırmalı Ekosistem

**Durum tarihi:** 29 Ekim 2026
**Kapsam:** Askeri ve sivil alanda ortak kullanılan, veriden karara giden zinciri hızlandıran
yazılım/algoritma sistemleri; bunları geliştiren şirketler (Palantir, Helsing, Anduril,
Shield AI ve diğerleri); sektörün yapısal ihtiyaçları, sorunları, düzenleyici çerçevesi ve
Türkiye için çıkarımlar.

Bu klasördeki dosyalar:

| Dosya | İçerik |
|---|---|
| `README.md` | Ana rapor (bu belge) |
| `analiz/sirket_matrisi.csv` | Şirket karşılaştırma matrisi (nitel + nicel alanlar) |
| `analiz/skor_matrisi.csv` | 8 kriterde 1–5 analist puanları ve gerekçeleri |
| `analiz/agirlik_senaryolari.csv` | Farklı alıcı perspektifleri için ağırlık setleri |
| `analiz/karsilastir.py` | Ağırlıklı skorlama + duyarlılık analizi aracı (bağımlılıksız Python 3) |
| `analiz/tedarik_kontrol_listesi.md` | Bir karar destek sistemini satın alırken / geliştirirken sorulacak sorular |

---

## İçindekiler

0. [Yönetici Özeti](#0-yönetici-özeti)
1. [Kapsam, Yöntem ve Sınırlamalar](#1-kapsam-yöntem-ve-sınırlamalar)
2. [Kavramsal Çerçeve: "Karar Destek" Neyi Kapsar?](#2-kavramsal-çerçeve-karar-destek-neyi-kapsar)
3. [Teknik Taksonomi: Algoritma Katmanları](#3-teknik-taksonomi-algoritma-katmanları)
4. [Sektörün Yapısı: Pazar, Finansman, Değer Zinciri](#4-sektörün-yapısı-pazar-finansman-değer-zinciri)
5. [Şirket Profilleri](#5-şirket-profilleri)
6. [Karşılaştırmalı Analiz](#6-karşılaştırmalı-analiz)
7. [Sektörün Yapısal İhtiyaçları](#7-sektörün-yapısal-ihtiyaçları)
8. [Sektörün Yapısal Sorunları](#8-sektörün-yapısal-sorunları)
9. [Düzenleyici ve Yönetişim Çerçevesi](#9-düzenleyici-ve-yönetişim-çerçevesi)
10. [Türkiye İçin Çıkarımlar ve Öneriler](#10-türkiye-için-çıkarımlar-ve-öneriler)
11. [2027–2030 Senaryoları ve İzlenecek Göstergeler](#11-20272030-senaryoları-ve-izlenecek-göstergeler)
12. [Kaynakça](#12-kaynakça)
13. [Ek: Sözlük](#13-ek-sözlük)

---

## 0. Yönetici Özeti

1. **Sektör "platform savaşı" aşamasına geçti.** 2023–2024'te deneysel pilotlar olan askeri
   yapay zekâ karar destek sistemleri, 2025–2026'da **kayıtlı programlara (program of record)**
   ve on yıllık **kurumsal anlaşmalara (enterprise agreement)** dönüştü. ABD Ordusu Palantir ile
   10 yıllık, tavanı 10 milyar $ olan bir anlaşma imzaladı (Temmuz 2025) [K9]; Palantir'in
   Maven Smart System'i (MSS) 2026'da resmî kayıtlı program statüsüne geçti [K1][K4]; Anduril'in
   de tavanı 20 milyar $ olarak raporlanan bir Ordu kurumsal anlaşması olduğu bildiriliyor [K13].
   Bu, pazarın **tek tedarikçi kilitlenmesi** riskiyle birlikte konsolide olduğunu gösteriyor.

2. **Sermaye akışı tarihi düzeyde.** PitchBook'un geniş tanımıyla (çift kullanım dâhil) savunma
   teknolojisi girişim sermayesi 2025'te 49,1 milyar $'a ulaştı (2024: 27,2 milyar $) [K11].
   Değerlemeler: Anduril 61 milyar $ (Mayıs 2026) [K12], Helsing 18 milyar $ (Temmuz 2026) [K6],
   Shield AI 12,7 milyar $ (Mart 2026) [K20], Quantum Systems 8 milyar $ (Temmuz 2026) [K21].
   Gelir çarpanları (20–30x ileri gelir) **beklentinin gerçekleşmeden fiyatlandığını** gösteriyor.

3. **Palantir ve Helsing farklı katmanlarda oynuyor; doğrudan rakip değiller, ama egemenlik
   tartışmasında karşı karşıya konumlanıyorlar.**
   - **Palantir** = yatay **veri/ontoloji ve karar katmanı** ("savaş alanının işletim sistemi").
     Olgun, kârlı, ölçekli (2025 geliri 4,475 milyar $) [K15]. En güçlü yanı veri entegrasyonu ve
     kurumsal yayılım; en zayıf yanı Avrupa'da **veri egemenliği** kaygıları — İsviçre ordusunun iç
     risk değerlendirmesi [K16] ve Bundeswehr'in askerî bulut/YZ projesinde Palantir'i seçmeme
     kararı (Nisan 2026) [K17].
   - **Helsing** = dikey **"YZ öncelikli yeni nesil ana yüklenici (neo-prime)"**: yazılım (Altra)
     + efektör (HX-2 dolanan mühimmat, CA-1 Europa İHA, SG-1 Fathom denizaltı planörü). En güçlü
     yanı Avrupa egemenliği anlatısı ve sermaye; en zayıf yanı **muharebe doğrulamasının
     tartışmalı olması** — Ukrayna'nın Ocak 2026'da test sorunları gerekçesiyle ek HX-2
     siparişlerini durdurduğu bildirildi (Helsing iddiaları reddetti) [K7].

4. **Gerçek dünya kanıtı artık var — ve sorunları da gösteriyor.** Ukrayna'nın devlet yapımı
   DELTA sistemi Haziran 2026'da ayda 200.000'den fazla İHA vuruşu ve günde 75.000 video akışını
   işliyor [K18]; ABD'nin 2026 İran harekâtında MSS'nin hedefleme hızını belirgin artırdığı
   raporlandı [K19]. Aynı dönem, **otomasyon önyargısı**, "ince insan onayı" ve sivil kayıp
   hesap verebilirliği tartışmalarını (Lavender/Gospel [K22], Minab okulu vurulması [K19]) ana
   gündeme taşıdı.

5. **Yapısal sorunlar teknikten çok kurumsal.** Tedarik döngüleri, veri hakları, akreditasyon
   (ATO), birlikte çalışabilirlik, test-değerlendirme (TEVV) kapasitesi, elektronik harp altında
   doğrulama, model sağlayıcı–devlet ilişkisi (bkz. Anthropic–Pentagon anlaşmazlığı, Mart 2026 [K23])
   ve AB YZ Yasası'nın askeri istisnası (Md. 2(3)) nedeniyle oluşan **düzenleme boşluğu** [K24]
   sektörün asıl darboğazları.

6. **Türkiye için fırsat penceresi:** Türkiye efektör/platform tarafında (İHA, dolanan mühimmat)
   muharebede kanıtlanmış bir sanayiye sahip; zayıf halka **yatay veri/karar katmanı, açık
   mimari standartları, egemen hesaplama altyapısı ve yazılım odaklı tedarik modeli**. Öneriler
   Bölüm 10'da.

---

## 1. Kapsam, Yöntem ve Sınırlamalar

**Yöntem.** Açık kaynak taraması (şirket açıklamaları, yatırımcı raporları, savunma basını,
düşünce kuruluşu analizleri, resmî bakanlık açıklamaları), ardından:
(i) teknik katman taksonomisi, (ii) şirket profilleri, (iii) 8 kriterli ağırlıklı karşılaştırma
(analist yargısı; `analiz/` klasöründe yeniden ağırlıklandırılabilir), (iv) yapısal ihtiyaç/sorun
analizi, (v) senaryo ve gösterge seti.

**Kanıt düzeyi işaretleri.** Rapor boyunca iddialar şu şekilde ayrıştırılmıştır:
- **[Doğrulanmış]** — resmî açıklama veya birden fazla güvenilir kaynakta tutarlı.
- **[Raporlanan]** — tek veya ikincil kaynak; şirket/devlet teyidi yok.
- **[Analist yargısı]** — bu raporun değerlendirmesi.

**Sınırlamalar.**
- Gizli program ayrıntıları, gerçek sözleşme yükümlülükleri (tavan ≠ harcama), özel şirket gelirleri
  (Helsing, Anduril, Shield AI) kamuya açık değildir; verilen gelir rakamları tahmindir.
- Bazı haber kaynakları (agregatörler) düşük güvenilirliklidir; bu rakamlar "[Raporlanan]" olarak
  işaretlenmiştir.
- Çalışma ortamında bazı birincil kaynak sitelerine doğrudan erişilemedi; bu nedenle bazı veriler
  arama sonuç özetlerinden derlenmiştir. Kritik kararlardan önce birincil kaynağa dönülmelidir.
- Palantir'in 3. çeyrek 2026 sonuçları 2 Kasım 2026'da açıklanacak; rapordaki son çeyrek verisi
  2Ç 2026'dır.

**Çıkar çatışması beyanı.** Bu rapor Anthropic tarafından geliştirilen bir yapay zekâ modeli
(Claude) ile hazırlanmıştır. Anthropic, Bölüm 8.7'de ele alınan Pentagon anlaşmazlığının
tarafıdır ve raporlarda Claude'un MSS iş akışlarında kullanıldığı belirtilmektedir [K23].
Bu konu olgusal düzeyde, iki tarafın beyanlarıyla aktarılmış; değerlendirme okuyucuya bırakılmıştır.

**Etik kapsam notu.** Rapor; sistemlerin mimarisini, pazarını, yönetişimini ve risklerini
stratejik/politika düzeyinde ele alır. Silah hedefleme performansını artırmaya yönelik operasyonel
ayrıntı veya tarif içermez.

---

## 2. Kavramsal Çerçeve: "Karar Destek" Neyi Kapsar?

### 2.1 Çift kullanım (dual-use) tanımı

AB mevzuatında (Tüzük 2021/821) çift kullanımlı ürün; hem sivil hem askerî amaçla kullanılabilen
mal, yazılım ve teknolojidir [K27]. Karar destek algoritmalarında çift kullanım üç biçimde ortaya çıkar:

| Biçim | Açıklama | Örnek |
|---|---|---|
| **Aynı çekirdek, farklı alan** | Aynı veri entegrasyonu/ontoloji motoru hem fabrika hem karargâhta | Palantir Foundry (ticari) ↔ Gotham/MSS (askerî) |
| **Sivilden askerîye transfer** | Ticari bilgisayarlı görü, LLM, optimizasyon modelleri askerî kullanıma uyarlanır | Genel amaçlı LLM'lerin istihbarat özetlemede kullanımı |
| **Askerîden sivile transfer** | Askerî için geliştirilen sensör füzyonu/otonomi sivil alana geçer | Akustik deniz izleme → açık deniz altyapısı güvenliği; İHA otonomisi → afet arama-kurtarma |

### 2.2 Karar döngüsü ve "karar üstünlüğü"

Sektörün temel değer önerisi **karar döngüsünü (OODA: Gözle–Yönel–Karar ver–Uygula)** rakipten daha
hızlı ve daha doğru döndürmektir. Askerî terminolojide bu, "sensörden atıcıya" (sensor-to-shooter)
veya hedefleme döngüsü (F2T2EA: Find–Fix–Track–Target–Engage–Assess) olarak ifade edilir. Sivil
karşılığı; acil durum yönetimi, tedarik zinciri, enerji şebekesi, siber olay müdahalesi ve
sağlık kapasitesi planlamasıdır.

**Karar destek ≠ otonom silah.** Bu ayrım hem teknik hem hukuki olarak kritiktir:

| Seviye | İnsan rolü | Örnek |
|---|---|---|
| 0 — Bilgi sunumu | İnsan tüm kararları verir | Ortak operasyon resmi (COP) |
| 1 — Öneri | Sistem seçenek önerir, insan seçer | Hareket tarzı (COA) önerisi |
| 2 — Onaylı eylem (*human-in-the-loop*) | Sistem eylem hazırlar, insan onaylar | Hedef nominasyonu + insan onayı |
| 3 — Denetimli otonomi (*human-on-the-loop*) | Sistem uygular, insan veto edebilir | Hava savunmada otomatik angajman modları |
| 4 — Tam otonomi (*human-out-of-the-loop*) | İnsan müdahalesi yok | Tartışmalı; birçok devlet/şirket kırmızı çizgi kabul ediyor |

Sektördeki tartışmaların çoğu 2 ile 3 arasındaki gri alanda yaşanır: Sistem günde yüzlerce hedef
öneriyorsa, "insan onayı" fiilen anlamlı bir inceleme midir, yoksa damga mı? (Bkz. Bölüm 8.5)

---

## 3. Teknik Taksonomi: Algoritma Katmanları

Bir karar destek sistemi tek bir algoritma değil, katmanlı bir yığındır. Aşağıdaki yığın, şirketlerin
hangi katmanda rekabet ettiğini anlamak için kullanılır.

```
┌───────────────────────────────────────────────────────────────┐
│ L7  İnsan–makine arayüzü, açıklanabilirlik, güven kalibrasyonu│
├───────────────────────────────────────────────────────────────┤
│ L6  Ajan/LLM katmanı: özetleme, sorgulama, plan taslağı       │
├───────────────────────────────────────────────────────────────┤
│ L5  Planlama & optimizasyon: kaynak-görev eşleme, COA, lojistik│
├───────────────────────────────────────────────────────────────┤
│ L4  Değerlendirme & öngörü: tehdit/niyet, risk, simülasyon     │
├───────────────────────────────────────────────────────────────┤
│ L3  Durumsal farkındalık: çoklu hedef takibi, sensör füzyonu   │
├───────────────────────────────────────────────────────────────┤
│ L2  Algılama & sınıflandırma: CV, SAR, RF, akustik            │
├───────────────────────────────────────────────────────────────┤
│ L1  Veri katmanı: entegrasyon, ontoloji, erişim kontrolü       │
├───────────────────────────────────────────────────────────────┤
│ L0  Altyapı: bulut/kenar (edge) hesaplama, ağ, güvenlik        │
└───────────────────────────────────────────────────────────────┘
        Dikey kesit: TEVV (test, değerlendirme, doğrulama, geçerleme)
```

### 3.1 Katman bazında algoritma aileleri ve sivil karşılıkları

| Katman | Başlıca yöntemler | Askerî kullanım | Sivil (dual-use) karşılık | Ana teknik risk |
|---|---|---|---|---|
| **L1 Veri/Ontoloji** | Varlık çözümleme (entity resolution), bilgi grafları, şema eşleme, nitelik tabanlı erişim kontrolü (ABAC), veri soy ağacı (lineage) | Çok kaynaklı istihbarat birleştirme, birlik/lojistik verisi | Hastane kapasitesi, tedarik zinciri, finansal suç | Yanlış eşleme → yanlış kimlik; gizlilik/sınıflandırma ihlali |
| **L2 Algılama** | CNN/Transformer tabanlı nesne tespiti, SAR görüntü sınıflandırma, RF parmak izi, akustik sınıflandırma ("büyük akustik model") | Otomatik hedef tanıma (ATR), gemi/denizaltı tespiti | Tarım, afet hasar tespiti, liman güvenliği | Dağılım kayması, kamuflaj/aldatma, çekişmeli (adversarial) örnekler |
| **L3 Durumsal farkındalık** | Kalman/genişletilmiş/kokusuz Kalman filtreleri, JPDA, MHT, rastgele küme filtreleri (PHD/LMB), dağıtık füzyon | Ortak operasyon resmi, hava/deniz resmi | Hava trafik kontrolü, otonom araçlar, deniz trafiği | Yanlış ilişkilendirme, sensör zehirleme, gecikme |
| **L4 Değerlendirme** | Bayes ağları, grafik sinir ağları, anomali tespiti, ajan tabanlı simülasyon, savaş oyunu motorları | Tehdit önceliklendirme, niyet tahmini | Kritik altyapı risk analizi, salgın modelleme | Nedensellik yerine korelasyon; düşük taban oranlı olaylarda yanlış pozitif patlaması |
| **L5 Planlama/Optimizasyon** | Karma tamsayılı programlama (MILP), kısıt programlama, silah–hedef atama (WTA) problemi, araç rotalama, Monte Carlo ağaç araması, pekiştirmeli öğrenme | Kaynak-görev eşleme, lojistik, COA üretimi | Filo/rota optimizasyonu, enerji dağıtımı, acil müdahale ekip ataması | Model dışı kısıtlar (hukuk, ROE) unutulursa "optimal ama hukuka aykırı" çözüm |
| **L6 Ajan/LLM** | RAG, araç kullanan ajanlar, özetleme, doğal dil sorgu → yapılandırılmış sorgu | İstihbarat özetleme, emir taslağı, planlama asistanı (örn. DIU Thunderforge [K28]) | Kurumsal bilgi yönetimi, çağrı merkezi, mevzuat analizi | Halüsinasyon, istem enjeksiyonu (prompt injection), aşırı güven |
| **L7 Arayüz** | Belirsizlik görselleştirme, açıklanabilir YZ (SHAP, karşı-olgusal açıklama), güven kalibrasyonu | Operatör ekranları | Klinik karar destek | Otomasyon önyargısı, bilişsel aşırı yük |
| **L0 Altyapı** | Kenar çıkarımı (model sıkıştırma, nicemleme), DDIL (kesintili/kısıtlı ağ) senkronizasyonu, sıfır güven güvenliği | Ön hat cihazları, İHA üzeri çıkarım | Endüstriyel IoT, uzak saha operasyonları | EH altında bağlantı kaybı, tedarik zinciri güvenliği |

### 3.2 Bu repodaki bağlantı

Bu repodaki `PassiveDefenseOptimizer/` araç seti, L5 katmanında **fizik tabanlı** bir karar destek
örneğidir: STANAG 4569 tehdit profillerine göre minimum ağırlıklı pasif koruma dizilimini
optimize eder. Bu tür **açıklanabilir, fizik modeline dayalı** optimizasyon araçları, veri güdümlü
kara kutu modellerin aksine doğrulanabilirlik açısından avantajlıdır; sektörün TEVV sorununa
(Bölüm 8.4) kısmi bir cevap olarak hibrit "fizik + öğrenme" mimarileri öne çıkmaktadır.

### 3.3 Mimari eğilimler (2025–2026)

1. **Ontoloji merkezli mimari:** Veriyi tablolar yerine "nesneler, ilişkiler, eylemler" olarak
   modellemek (Palantir'in ayırt edici yaklaşımı). LLM'lerin güvenli kullanımı için de temel
   oluşturuyor: model doğrudan ham veriye değil, yetkilendirilmiş ontoloji eylemlerine erişiyor.
2. **Kenar yerelliği:** EH ortamında bulut bağımlılığı başarısızlık nedeni. Algılama ve terminal
   yönlendirme platform üzerine taşınıyor (Helsing HX-2'nin Altra modülü ile karıştırmaya karşı
   harita tabanlı seyrüsefer iddiası [K25]).
3. **"Tek operatör – çok platform":** Sürü ve insanlı-insansız ekip (MUM-T) konseptleri; tek
   operatörün çok sayıda platformu yönetmesi (Altra ile HX-2 sürüsü [K25], Shield AI Hivemind,
   ABD Hava Kuvvetleri CCA programı [K20]).
4. **LLM'lerin karar zincirine girişi:** 2024'ten itibaren büyük model sağlayıcıları savunma
   kullanımına kapı açtı; 2026'da MSS iş akışlarında LLM kullanımı raporlandı [K23]. Bu, yeni
   bir tedarik zinciri bağımlılığı (model sağlayıcısının kullanım politikası) yarattı.
5. **Açık mimari / modüler yaklaşım:** Ukrayna DELTA ve NATO MSS "Görev Gücü Maven" prototip
   entegrasyonu gibi, üçüncü taraf modüllerin takılabildiği ekosistemler [K4][K18].

---

## 4. Sektörün Yapısı: Pazar, Finansman, Değer Zinciri

### 4.1 Talep tarafı itici güçleri

- **Ukrayna Savaşı (2022–):** Ucuz, kitlesel, yazılımla tanımlanan sistemlerin değerini kanıtladı;
  "savaş alanı laboratuvarı" etkisi.
- **ABD–İran çatışması (2026):** YZ destekli hedeflemenin ölçekli ilk büyük kullanımı olarak
  raporlandı; ilk 24 saatte ~1.000 hedef iddiası [Raporlanan] [K19]. Çin ordusu yayın organı bu
  harekâtı gerekçe göstererek PLA'ya YZ entegrasyonunu hızlandırma çağrısı yaptı [K29].
- **NATO harcama artışı ve Avrupa yeniden silahlanması:** Avrupa'da egemen tedarik talebi.
- **ABD tedarik reformu:** Mart 2025 Hegseth yazılım memorandumu ile Yazılım Tedarik Yolu (SWP),
  Ticari Çözüm Açılışları (CSO) ve Diğer İşlem (OTA) sözleşmelerinin "varsayılan" hâle
  getirilmesi; Kasım 2025'te Portföy Tedarik Yöneticileri (PAE) yapısı [K30].

### 4.2 Finansman

| Gösterge | Değer | Kaynak |
|---|---|---|
| Küresel savunma teknolojisi VC (geniş tanım, 2025) | 49,1 milyar $ (2024: 27,2 milyar $) | PitchBook [K11] |
| Dar tanım (CB Insights, 2025) | 17,9 milyar $ | [K11] |
| Savunma teknolojisi çıkışları (2025) | 54,4 milyar $ (2024: 18,2 milyar $) | PitchBook [K11] |
| Avrupa savunma/güvenlik/dayanıklılık VC'sinde YZ payı (2025) | %44 | [K11] |
| Avrupa savunma girişimleri 2026 (9 Eyl'e kadar) | 48 şirket, 50 tur, 1,5 milyar € (yalnız dar savunma tanımı) | funding.tech.eu [K21] |

**Analist yargısı:** Tanımlar arasındaki 3 katlık fark (17,9 vs 49,1 milyar $), "çift kullanım"
etiketinin yatırımcı pazarlamasında esnek kullanıldığını gösteriyor. Fon tahsisi, gerçek savunma
gelirinden çok "savunmaya uygulanabilir" teknoloji anlatısına akıyor.

### 4.3 Değer zinciri ve oyuncu arketipleri

```
 Hesaplama/Bulut ──► Temel Modeller ──► Veri/Karar Platformu ──► Otonomi Çekirdeği ──► Platform/Efektör ──► Entegratör/Ana Yüklenici ──► Kullanıcı
 (AWS, Azure,         (LLM sağlayıcıları,  (Palantir, Comand AI,   (Shield AI Hivemind,  (Anduril, Helsing,   (Lockheed, Rheinmetall,       (Ordu, NATO,
  Google, Oracle,      açık kaynak,         ChapsVision, Vannevar)  Helsing Centaur,      Quantum Systems,     ASELSAN, HAVELSAN)            sivil kurum)
  egemen bulutlar)     ulusal modeller)                            Auterion)             Baykar, Stark)
```

| Arketip | Tanım | Örnekler | İş modeli |
|---|---|---|---|
| **Veri işletim sistemi** | Yatay, platform-bağımsız veri ve karar katmanı | Palantir, ChapsVision (Fransa), Vannevar Labs | Abonelik/lisans + saha mühendisleri; kurumsal anlaşmalar |
| **YZ öncelikli neo-prime** | Yazılım çekirdeği + kendi donanımı; dikey entegrasyon | Anduril, Helsing | Ürün satışı + yazılım; fabrika yatırımı (Anduril Arsenal-1, Helsing–Grob) |
| **Otonomi çekirdeği** | Platformlara lisanslanan otonomi yazılımı | Shield AI (Hivemind), Auterion | Lisans + kendi platformu (V-BAT) |
| **Uygulama/planlama yazılımı** | Belirli karar problemleri (C2 planlama, ateş destek) | Comand AI (Fransa) | Yazılım lisansı |
| **Devlet yapımı açık ekosistem** | Devletin kendi geliştirdiği platform + özel modül pazarı | Ukrayna DELTA / Avengers / Brave1 | Kamu yatırımı; özel sektör modülleri |
| **Geleneksel ana yüklenici iç yazılımı** | Mevcut C2/CMS ürünlerine YZ eklenmesi | HAVELSAN ADVENT-AI/MAIN, ASELSAN | Program bazlı sözleşmeler |

---

## 5. Şirket Profilleri

### 5.1 Palantir Technologies (ABD)

**Konum:** Veri entegrasyonu + ontoloji + karar uygulamaları. Askerî ve ticari müşteride aynı
çekirdeği kullanan, sektörün en olgun **çift kullanım** örneği.

**Ürün mimarisi**

| Ürün | İşlev | Kullanım |
|---|---|---|
| **Gotham** | İstihbarat/operasyon analitiği, hedefleme iş akışı | Savunma, istihbarat, kolluk |
| **Foundry** | Kurumsal veri entegrasyonu ve ontoloji | Ticari + kamu (sağlık, üretim) |
| **AIP** (Artificial Intelligence Platform) | LLM'leri ontolojiye bağlayan ajan katmanı | Ticari ve askerî |
| **Apollo** | Sürekli dağıtım; bulut, kapalı ağ ve kenar ortamlarına yazılım güncelleme | Tüm ürünler |
| **Maven Smart System (MSS)** | Çok kaynaklı sensör verisini birleştirip hedef tespiti, nominasyon ve angajman iş akışını hızlandıran sistem | ABD Savunma Bakanlığı, NATO |
| **TITAN** | Ordu'nun sensörden atıcıya kara istasyonu programı (Palantir liderliğinde) | ABD Ordusu |

**Temel sayılar**

| Gösterge | Değer | Kanıt |
|---|---|---|
| 2025 geliri | 4,475 milyar $ (+%56); ABD geliri 3,32 milyar $ | Doğrulanmış (şirket) [K15] |
| 2025 düzeltilmiş serbest nakit akışı | 2,3 milyar $ | Doğrulanmış [K15] |
| Kalan sözleşme değeri (RCV, 2025 sonu) | 11,2 milyar $ (+%105) | Doğrulanmış [K15] |
| 2Ç 2026 ABD kamu geliri | 809 milyon $ (+~%90 yıllık) | Doğrulanmış [K1] |
| 2026 gelir rehberi | ~8,15 milyar $ (yükseltilmiş) | Raporlanan [K1] |
| ABD Ordusu kurumsal anlaşması | 10 yıl, tavan 10 milyar $; 75 sözleşmeyi birleştirir (15 ana + 60 bağlı) | Doğrulanmış [K9] |
| MSS | 2026'da kayıtlı program; tavan ~1,3 milyar $; Pentagon 5 yıl için 2,3 milyar $ talep etti | Raporlanan [K1][K4] |
| NATO MSS | NCIA Mart 2025'te satın aldı; 2026'da operasyonel karargâhlara yayılım (JFC Norfolk) | Doğrulanmış/Raporlanan [K4] |
| İngiltere | Palantir'in 1,5 milyar £'a kadar yatırım taahhüdü; Savunma ile 5 yılda 750 milyon £'a kadar fırsat | Doğrulanmış (İngiltere hükümeti) [K15] |

**Güçlü yanlar [Analist yargısı]**
- **Veri katmanı derinliği:** Ontoloji yaklaşımı, LLM'lerin yetki kontrollü ve izlenebilir biçimde
  kullanılmasını sağlıyor; rakiplerin yetişmesi en zor katman.
- **İleri konuşlu mühendis (FDE) modeli:** Müşteri sahasında yazılım uyarlama; kurumsal benimsemeyi hızlandırıyor.
- **Finansal güç:** Kârlı, nakit üreten tek büyük "yeni nesil" savunma yazılım şirketi.
- **Kurumsal yerleşiklik:** Kayıtlı program + kurumsal anlaşmalar = yüksek değişim maliyeti.
- **Çift kullanım dengesi:** ABD ticari geliri 2Ç 2026'da kamu gelirine yaklaştı (764 vs 809 milyon $) [K1];
  savunma bütçesi döngüselliğine karşı doğal koruma.

**Zayıf yanlar / riskler**
- **Tedarikçi kilitlenmesi:** Ordu anlaşmasına yönelik eleştiriler; mega anlaşmaların küçük
  YZ firmalarına rekabeti daraltabileceği kaygısı [K9].
- **Avrupa'da egemenlik direnci:** İsviçre ordusunun Aralık 2024 tarihli iç risk değerlendirmesinin
  ABD makamlarının hassas verilere erişebileceği kaygısıyla alternatif önerdiği raporlandı (Republik);
  Palantir bulguları reddetti ve dergiye dava açtı [K16]. Bundeswehr, Nisan 2026'da askerî bulut/YZ
  projesinde Palantir'i seçmeyeceğini açıkladı; Alman iç istihbaratı BfV Mayıs 2026'da veri analizi
  sözleşmesini Fransız ChapsVision'a verdi [K17].
- **Etik/itibar:** Kolluk ve göç uygulamaları, hedefleme sistemlerindeki rolü nedeniyle sürekli
  kamuoyu baskısı.
- **Değerleme:** Hisse fiyatı yüksek büyüme beklentisini fiyatlıyor; bütçe/siyasi değişikliklere duyarlı.
- **Donanım yok:** Efektör tarafında ortaklara bağımlı (dikey entegre rakiplere karşı potansiyel dezavantaj).

### 5.2 Helsing (Almanya / Avrupa)

**Konum:** 2021'de Münih'te kurulan; yazılım öncelikli başlayıp hızla **donanım + yazılım** dikey
entegre bir Avrupa "neo-prime"ına dönüşen şirket. Anlatısı: "Avrupa'nın egemen savunma YZ'si".

**Ürün mimarisi**

| Ürün | İşlev | Durum |
|---|---|---|
| **Altra** | Keşif-taarruz (recce-strike) yazılım platformu; İSR varlıkları, topçu ve taarruz fonksiyonlarını koordine eder; tek operatörün HX-2 sürüsünü yönetmesini sağlar | İngiliz Ordusu ASGARD projesinde [K25] |
| **HF-1 / HX-2** | Dolanan mühimmat (HX-2: ~100 km menzil iddiası; kenar YZ ile EH altında seyrüsefer iddiası) | Ukrayna'ya 4.000 HF-1 + 6.000 HX-2 siparişi duyuruldu [K25]; Bundestag Şubat 2026'da 269 milyon € ilk sözleşmeyi (7 yılda 1,46 milyar €'ya kadar opsiyonlu) onayladı [K6] |
| **CA-1 Europa** | İnsansız savaş uçağı (UCAV); Centaur otonomi yığını ile | Eylül 2025'te tanıtıldı; ilk uçuş hedefi 2027; Haziran 2026'da elektronik taarruz türevi CA-1EA [K6] |
| **SG-1 Fathom + Lura** | Denizaltı planör İHA'sı + gemi/denizaltı tespiti için "büyük akustik model" | Kraliyet Donanması ilk operasyonel kullanıcı olarak raporlandı [K8] |
| **Eurofighter EH** | Saab ile elektronik harp YZ entegrasyonu | Raporlanan, teyit edilmemiş tutar [K8] |
| **Satın almalar** | Grob Aircraft (Haziran 2025; CA-1 gövde üretimi), Blue Ocean (deniz otonomisi, Ekim 2025) | Doğrulanmış/Raporlanan [K8] |

**Temel sayılar**

| Gösterge | Değer | Kanıt |
|---|---|---|
| Değerleme yolu | ~5 milyar € (Tem 2024) → 12 milyar € (Haz 2025) → 18 milyar $ (Tem 2026) | Raporlanan, tutarlı [K6] |
| Seri E (13 Temmuz 2026) | 1,8 milyar $; Dragoneer liderliğinde | Raporlanan, çok kaynaklı [K6] |
| Gelir | Denetlenmiş güncel veri yok; 2026 için ~441 milyon € tahmini (FT'ye atfen) | Raporlanan, düşük güven [K8] |

**Güçlü yanlar [Analist yargısı]**
- **Avrupa egemenliği:** Bundeswehr'in Palantir kararı ve Avrupa'nın ABD teknolojisine bağımlılık
  kaygısı Helsing'in stratejik konumunu güçlendiriyor.
- **Dikey entegrasyon:** Altra + HX-2 + CA-1 + SG-1 ile çok alanlı (kara, hava, deniz altı) portföy;
  donanım satışı yazılım benimsemesini kolaylaştırıyor.
- **Sermaye erişimi:** Avrupa'nın en yüksek değerli savunma girişimi; üretim kapasitesine yatırım yapabiliyor.
- **Kenar/EH odaklı tasarım:** Ukrayna'nın EH yoğun ortamı için tasarlanmış ürün felsefesi.

**Zayıf yanlar / riskler**
- **Muharebe doğrulaması tartışmalı:** Bloomberg (Ocak 2026), Ukrayna'nın test sorunları nedeniyle
  ek HX-2 siparişlerini durdurduğunu; kalkış sorunları, bazı otonom terminal yönlendirme
  bileşenlerinin eksikliği ve Rus EH'sinin bağlantıyı kesmesi gibi bulgular olduğunu bildirdi.
  Raporlanan rakamlar (cephe testinde fırlatmaların %25'i; 14 denemede 5 isabet) birincil belgeyle
  teyit edilemedi. Helsing, haberin doğrulanmamış bir iç belgeye dayandığını belirterek itiraz etti;
  Alman ve İngiliz ordularıyla Ekim testlerinde hedeflerin neredeyse tamamının vurulduğunu açıkladı [K7].
- **Gelir/değerleme uçurumu:** 18 milyar $ değerleme, gelirle henüz desteklenmiyor.
- **Odak dağılması riski:** Yazılım şirketinden uçak üreticisine geçiş; yürütme riski yüksek.
- **Veri platformu katmanında sığlık:** Palantir'in kurumsal veri/ontoloji katmanına doğrudan
  eşdeğer bir ürünü yok; MDOCore adlı ürünün Hensoldt ile test edildiği raporlanıyor ancak
  zayıf kaynaklı [K17].

### 5.3 Anduril Industries (ABD)

**Konum:** Lattice yazılım çekirdeği üzerine kurulu, en büyük ölçekli YZ öncelikli neo-prime.

| Gösterge | Değer | Kanıt |
|---|---|---|
| Değerleme | 61 milyar $ (Seri H, 5 milyar $, Mayıs 2026); ~100 milyar $'lık yeni tur görüşmesi raporlandı (Tem 2026) | Raporlanan, çok kaynaklı [K12] |
| Gelir (2025) | ~2,2 milyar $ (2024: ~1 milyar $) | Tahmin (Sacra) [K13] |
| Lattice | Sensör füzyonu, C2 ve otonom varlık yönetimi; JIATF-401 kapsamında karşı-İHA C2 omurgası seçildi | Raporlanan [K13] |
| NGC2 | Ordu'nun Yeni Nesil Komuta Kontrol prototipi (Palantir, Microsoft desteğiyle); Ordu CTO'sunun "çok yüksek risk" uyarısı (kalıcı tespit edilemez erişim olasılığı) | Raporlanan [K9] |
| YFQ-44A Fury | CCA Artım 1; ilk uçuş 31 Ekim 2025 | Raporlanan [K13] |
| Arsenal-1 | Ohio'da büyük ölçekli otonom sistem fabrikası; tam üretim hedefi Temmuz 2026 | Raporlanan [K13] |
| Ordu kurumsal anlaşması | 10 yıl, tavan 20 milyar $; 120+ tedarik işlemini birleştirir (Mart 2026) | Raporlanan, birincil teyit gerekli [K13] |

**Değerlendirme [Analist yargısı]:** Anduril, Helsing'in ABD'li ve ~3,4 kat büyük versiyonudur;
yazılım + donanım + üretim kapasitesi üçlüsünü en ileri götüren şirket. NGC2 güvenlik
uyarısı, hızlı geliştirme ile siber güvence arasındaki gerilimin somut örneği.

### 5.4 Shield AI (ABD)

| Gösterge | Değer | Kanıt |
|---|---|---|
| Değerleme | 12,7 milyar $ (Mart 2026) | Raporlanan [K20] |
| Hivemind | Platform-bağımsız uçuş/görev otonomisi; Şubat 2026'da ABD Hava Kuvvetleri CCA programı görev otonomi sağlayıcısı | Raporlanan [K20] |
| Gelir | 2025 ~300 milyon $ → 2026 >540 milyon $ hedefi | Şirket projeksiyonu [K20] |

**Değerlendirme:** "Otonomi çekirdeği" arketipinin en saf örneği. Değer önerisi, otonominin
platformdan bağımsız lisanslanabilir bir katman olması. Riski: büyük ana yüklenicilerin ve
neo-prime'ların kendi otonomi yığınlarını tercih etmesi.

### 5.5 Diğer önemli oyuncular

| Oyuncu | Ülke | Katman | Not |
|---|---|---|---|
| **Scale AI** | ABD | Veri etiketleme, değerlendirme; LLM planlama ajanları | DIU Thunderforge (2025) — INDOPACOM/EUCOM için YZ destekli harekât planlama [K28] |
| **Vannevar Labs** | ABD | Açık kaynak istihbarat (OSINT) analitiği | Yabancı dil kaynaklı istihbarat için LLM |
| **ChapsVision** | Fransa | Veri analitiği (ArgonOS) | BfV, Palantir yerine seçti (Mayıs 2026) [K17] — Avrupa'nın Palantir alternatifi adayı |
| **Comand AI** | Fransa | C2 planlama ve karar destek | 32 milyon € Seri A (Haziran 2026) [K21] |
| **Quantum Systems** | Almanya | İHA + otonomi | 1,2 milyar $ tur, 8 milyar $ değerleme (Temmuz 2026) [K21] |
| **Stark** | Almanya | Dolanan mühimmat | 500 milyon € geç aşama tur (Haziran 2026) [K21] |
| **Auterion** | İsviçre/ABD | İHA otonomi işletim sistemi | Sürü ve terminal yönlendirme yazılımı |
| **DELTA / Avengers** | Ukrayna (devlet) | Durumsal farkındalık + CV | Haziran 2026'da 200.000+ İHA vuruşu kaydı, günde 75.000 video akışı; Avengers otomatik nesne tespiti; YZ asistanı tüm kullanıcılara açık [K18] |
| **HAVELSAN** | Türkiye | C2/CMS + YZ | ADVENT-AI (SAHA EXPO 2026, EFES-2026); MAIN kurumsal YZ platformu ADVENT'e iki aşamada entegre ediliyor (bakım asistanı tamamlandı; ikinci aşama karar destek önerileri) [K26] |
| **ASELSAN** | Türkiye | Sensör, atış kontrol, kent güvenliği | Deniz Kuvvetleri ile sensör/atış kontrolüne YZ entegrasyonu MoU (IDEF 2025); YZ destekli Kent Güvenliği Yönetim Sistemleri için ~470 milyon $ sözleşme [K26][K31] |
| **Baykar** | Türkiye | İHA/SİHA, dolanan mühimmat | SAHA EXPO 2026'da SİVRİSİNEK dolanan mühimmat ve MIZRAK [K31] |
| **PLA / Çin ekosistemi** | Çin | Tüm katmanlar | DeepSeek gibi yerli modellerin "akıllılaştırılmış savaş" için tedarik belgelerinde yer aldığı; otomatik hedef tanıma ve muharebe karar desteği araştırmaları [K29] |

---

## 6. Karşılaştırmalı Analiz

### 6.1 Palantir ve Helsing: Doğrudan karşılaştırma

| Boyut | Palantir | Helsing |
|---|---|---|
| Kuruluş / merkez | 2003, ABD (Denver) | 2021, Almanya (Münih) |
| Arketip | Veri işletim sistemi (yatay) | YZ öncelikli neo-prime (dikey) |
| Yığındaki ana katmanlar | L1, L4, L5, L6, L7 | L0 (kenar), L2, L3, L5 + efektör |
| Donanım | Yok (ortaklarla) | Var (HX-2, CA-1, SG-1; Grob üretimi) |
| Çift kullanım derinliği | Çok yüksek: aynı çekirdek, büyük ticari gelir | Düşük-orta: ağırlıklı askerî; teknoloji dual-use (akustik, otonomi) |
| Gelir ölçeği | 4,475 milyar $ (2025), kârlı | Kamuya açık değil; 2026 tahmini ~441 milyon € (düşük güven) |
| Değerleme | Halka açık, çok yüksek çarpan | 18 milyar $ (özel) |
| Ana müşteriler | ABD Savunma Bakanlığı, ABD Ordusu, NATO, İngiltere, Ukrayna, ticari | Almanya, İngiltere, Ukrayna, Avrupa ülkeleri |
| Muharebe kanıtı | Ukrayna, İran harekâtı (raporlanan), NATO operasyonel kullanım | Ukrayna'da sahada; performans tartışmalı |
| Egemenlik (Avrupalı alıcı için) | Zayıf: ABD hukuku, veri erişimi kaygısı | Güçlü: Avrupa merkezli |
| Kilitlenme riski (alıcı açısından) | Yüksek (ontoloji + kurumsal anlaşma) | Orta-yüksek (donanım-yazılım paketi) |
| Ana risk | Siyasi/egemenlik tepkisi, rekabet daraltma eleştirisi | Yürütme riski, saha performansı, değerleme |
| Stratejik hamle (2025–26) | Kayıtlı program + kurumsal anlaşmalar; NATO yayılımı | Hava/deniz alanına genişleme; üretim satın almaları |

**Analist yargısı — temel bulgu:** Palantir ve Helsing **tamamlayıcı katmanlarda** konumlanıyor;
gerçek rekabet alanları (a) Avrupa'daki **komuta-kontrol/veri platformu ihaleleri** (örn. Bundeswehr
bulut/YZ) ve (b) **"kim karar katmanının sahibi olacak"** sorusu. Helsing'in Altra'yı
efektörlerden bağımsız bir C2 katmanına dönüştürebilmesi, Palantir'in ise Avrupa'da egemen
konuşlandırma modeli (yerel veri merkezi, yerel personel, kaynak kodu emaneti) sunabilmesi, iki
şirketin Avrupa'daki uzun vadeli payını belirleyecek.

### 6.2 Çok kriterli skorlama

`analiz/karsilastir.py` aracıyla üretilmiştir; puanlar 1–5 **analist yargısıdır**, gerekçeleri
`analiz/skor_matrisi.csv` dosyasındadır. Ağırlıklar alıcı perspektifine göre değişir.

**Kriterler:** (K1) Ürün olgunluğu/ölçek, (K2) Muharebe doğrulaması, (K3) Veri/entegrasyon katmanı
derinliği, (K4) Kenar/otonomi ve EH dayanıklılığı, (K5) Donanım/efektör entegrasyonu,
(K6) Egemenlik uygunluğu (Avrupalı alıcı), (K7) Finansal sağlamlık, (K8) Yönetişim/şeffaflık.

| Şirket | K1 | K2 | K3 | K4 | K5 | K6 | K7 | K8 | **A: Dengeli** | **B: Avrupa egemenlik** | **C: Ön hat/EH** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Palantir | 5 | 4 | 5 | 3 | 2 | 2 | 5 | 3 | **75,0** | 68,0 | 67,0 |
| Anduril | 4 | 3 | 4 | 4 | 5 | 2 | 4 | 3 | 73,0 | 68,0 | **76,0** |
| Helsing | 3 | 2 | 3 | 4 | 4 | 5 | 4 | 3 | 68,0 | **73,0** | 68,0 |
| Shield AI | 3 | 3 | 2 | 5 | 4 | 2 | 3 | 3 | 63,0 | 60,0 | 72,0 |

*(0–100 ölçeğine normalize ağırlıklı toplam. Ağırlık setleri `analiz/agirlik_senaryolari.csv`'de.)*

**Duyarlılık:** Dengeli senaryoda yalnızca egemenlik (K6) ağırlığı artırıldığında, K6 ağırlığı
~%20'yi aştığında (20 → 25 arası) liderlik Palantir'den Helsing'e geçiyor
(`karsilastir.py --duyarlilik K6`). Yani Palantir–Helsing tercihi teknik üstünlükten çok
**egemenliğe ne kadar değer biçildiğine** bağlı.

**Okuma:** "En iyi şirket" yoktur; **alıcının problemi** sıralamayı belirler. Kurumsal veri/karar
katmanı arayan dengeli bir alıcı için Palantir öne çıkarken, egemenliği ağırlıklandıran bir Avrupa
alıcısı için Helsing; ön hat EH ortamında otonomi arayan alıcı için Anduril ve Shield AI öne çıkar.
Kendi ağırlıklarınızla yeniden hesaplamak için:

```bash
python3 DualUseKararDestek/analiz/karsilastir.py
```

```bash
python3 DualUseKararDestek/analiz/karsilastir.py --agirlik "K1=10,K2=20,K3=10,K4=20,K5=10,K6=20,K7=5,K8=5"
```

### 6.3 Stratejik konumlanma haritası

```
                Dikey entegrasyon (donanım + yazılım)
                              ▲
                              │
              Anduril ●       │        ● Helsing
                              │
       Shield AI ●            │              ● Quantum Systems / Stark
                              │
 ABD ◄────────────────────────┼────────────────────────► Avrupa / egemen
                              │
                              │        ● HAVELSAN / ASELSAN (Türkiye, ana yüklenici)
              Palantir ●      │        ● ChapsVision
                              │        ● Comand AI
       Scale AI ● Vannevar ●  │        ● DELTA (Ukrayna, devlet)
                              ▼
                Yatay platform (yazılım katmanı)
```

**Boşluk tespiti [Analist yargısı]:** Sağ-alt kadran (Avrupa merkezli, yatay, ölçekli veri/karar
platformu) hâlâ görece boş. Bundeswehr'in 30 YZ aracını değerlendirip 2027'de prototip hedeflemesi [K17]
bu boşluğun talep tarafının oluştuğunu gösteriyor. Türkiye ve Avrupa için en büyük pazar fırsatı burada.

---

## 7. Sektörün Yapısal İhtiyaçları

| # | İhtiyaç | Neden kritik | Mevcut durum |
|---|---|---|---|
| 1 | **Karar hızı ölçeklenmesi** | Hedef/olay sayısı insan kapasitesini aşıyor (DELTA'da günde 6.600+ vuruş kaydı [K18]) | Algılama otomatik; değerlendirme kısmen; onay insanda |
| 2 | **Veri birlikte çalışabilirliği** | Koalisyon operasyonları (NATO), çok tedarikçili ortam | Ulusal sistemler parçalı; NATO MSS ile fiilî standartlaşma, ama tek tedarikçili |
| 3 | **Kenar hesaplama ve DDIL dayanıklılığı** | EH ve bağlantı kesintisi ön hatta norm | Algılamada ilerleme var; HX-2 tartışması sorunun sürdüğünü gösteriyor [K7] |
| 4 | **Hızlı ve güvenilir TEVV** | Yazılım haftalık güncelleniyor, akreditasyon aylar sürüyor | En büyük darboğaz; sürekli ATO ve dijital ikiz test sahaları gelişiyor |
| 5 | **Yazılıma uygun tedarik modeli** | Klasik donanım tedariki (yıllar) yazılım döngüsüne (haftalar) uymuyor | ABD'de SWP/OTA/PAE reformları [K30]; Avrupa ve Türkiye'de sınırlı |
| 6 | **Egemen hesaplama ve model altyapısı** | Gizli veriyle eğitim/çıkarım; yabancı hukuka tabi olmama | Avrupa'da egemen bulut girişimleri; Türkiye 2026–2030 YZ Eylem Planı'nda veri merkezi hedefi [K31] |
| 7 | **Kitle (mass) ve maliyet etkinliği** | Ucuz, harcanabilir (attritable) sistemlerin yazılımla koordinasyonu | Üretim kapasitesi yatırımları (Arsenal-1, Helsing–Grob) |
| 8 | **Yetenek** | YZ mühendisleri + alan uzmanı + güvenlik izni kesişimi çok dar | Kronik açık; FDE modeli kısmi çözüm |
| 9 | **Hukuki uygunluk entegrasyonu** | IHL/ROE kısıtlarının algoritmaya gömülmesi ve denetlenebilir kayıt | Çoğunlukla prosedürel; teknik "hukuk-farkında" planlama erken aşamada |
| 10 | **Sivil–askerî veri köprüsü** | Afet, kritik altyapı, siber savunmada aynı yetenek | Kurumsal ve hukuki ayrım; çift kullanım potansiyeli düşük kullanılıyor |

---

## 8. Sektörün Yapısal Sorunları

### 8.1 Tedarik "ölüm vadisi" ve bütçe yapısı
Prototipten kayıtlı programa geçiş yıllar sürüyor; girişimler pilot projelerde nakit tüketiyor.
2025–2026'daki çözüm olan **kurumsal anlaşmalar**, ölüm vadisini büyük oyuncular için kapatırken
küçük oyuncular için derinleştirme riski taşıyor [K9]. **[Analist yargısı]** Sektör, "çok sayıda
girişim, az sayıda kazanan" yapısına hızla gidiyor.

### 8.2 Tedarikçi kilitlenmesi ve veri hakları
Ontoloji ve iş akışları bir platformda modellendiğinde, veri dışa aktarılabilse bile **anlamsal
model** taşınamıyor. Alıcıların sözleşmede açık veri modeli, API erişimi, kaynak kodu emaneti ve
çıkış planı (exit plan) talep etmesi kritik (bkz. `analiz/tedarik_kontrol_listesi.md`).

### 8.3 Egemenlik ve ekstra-territoriyal hukuk
ABD şirketlerinin ABD hukukuna (örn. veri erişim talepleri) tabi olması, Avrupa ve diğer
müttefiklerde güven sorununa dönüştü (İsviçre ve Almanya örnekleri [K16][K17]). Aynı mantık
Avrupa şirketlerinin ihracat kontrollerine (Alman ihracat politikası) tabi olması nedeniyle
üçüncü ülke alıcıları için de geçerli.

### 8.4 Doğrulama açığı: Demo ≠ muharebe
Laboratuvar/test sahası performansı, EH yoğun gerçek ortamda tekrarlanmayabiliyor. HX-2 tartışması
[K7] bu açığın tipik örneği: şirket testlerinde yüksek isabet beyanı ile cephe raporları arasında
derin fark. **Kök neden [Analist yargısı]:** Bağımsız, standartlaştırılmış, EH dâhil test protokollerinin
yokluğu; alıcıların şirket beyanına bağımlılığı.

### 8.5 Otomasyon önyargısı ve "anlamlı insan kontrolü"
- Lavender/Gospel raporları, yüksek beyan edilen doğruluk oranlarının (örn. ~%90 manuel örneklem)
  insanların sistem çıktısını "insan kararı gibi" kabul etmesine yol açtığını; günde 100+ hedef
  hacminde anlamlı incelemenin zorlaştığını öne sürdü [K22]. (İddialar anonim kaynaklara dayanıyor
  ve İsrail ordusu tarafından tartışmalı.)
- 2026 İran harekâtında hedefleme hızının arttığı, insan onayının "inceldiği" eleştirileri ve sivil
  kayıplar (Minab okulu) hesap verebilirlik tartışmasını büyüttü [K19].
- **Yapısal sorun:** Sistemler hız için optimize edilirken, insan incelemesinin kalitesini ölçen
  metrikler (inceleme süresi, ret oranı, yanlış pozitif geri bildirimi) çoğunlukla tasarım
  gereksinimi değil.

### 8.6 Siber ve çekişmeli makine öğrenmesi riskleri
- Veri zehirleme, sensör aldatma, kamuflaj ve çekişmeli örnekler (L2/L3).
- LLM katmanında istem enjeksiyonu: düşman tarafından üretilen açık kaynak içeriğin istihbarat
  özetine sızması.
- Tedarik zinciri güvenliği: NGC2 prototipi için "kalıcı tespit edilemez erişim" uyarısı [K9].

### 8.7 Model sağlayıcı–devlet yönetişim çatışması
Mart 2026'da ABD Savunma Bakanlığı, Anthropic'i "tedarik zinciri riski" olarak tanımladı — bir ABD
şirketi için ilk. Raporlara göre anlaşmazlık, şirketin modelinin kitlesel yurt içi gözetim ve tam
otonom silahlarda kullanımına koyduğu sınırlar ile Bakanlığın "tüm yasal kullanım" talebi arasında
çıktı; şirket kararı mahkemede itiraz konusu yaptı [K23]. Güncel hukuki durum bu raporda teyit
edilmemiştir. **Sektör için anlamı [Analist yargısı]:**
(i) Temel model sağlayıcılarının kullanım politikaları artık savunma tedarik zincirinin bir parçası;
(ii) platform şirketleri (örn. MSS) tek model sağlayıcısına bağımlılık riskini yönetmek zorunda —
model-agnostik mimari bir gereksinim hâline geliyor;
(iii) "kimin kırmızı çizgisi geçerli: satıcının mı, devletin mi?" sorusu, bu sektörde henüz
çözülmemiş bir yönetişim sorusu.

### 8.8 Değerleme balonu riski
20–30x ileri gelir çarpanları (Anduril ~28x tahmini gelir [K12], Shield AI ~23x ileri gelir [K20]),
savunma bütçelerinin sürekli artacağı ve sözleşme tavanlarının harcamaya dönüşeceği varsayımına
dayanıyor. Tavan ≠ yükümlülük (Ordu–Palantir anlaşmasında yalnızca açıklanmamış bir asgari
garanti var [K9]). Barış/ateşkes, bütçe kesintisi veya siyasi değişim değerlemeleri sert düzeltebilir.

### 8.9 Düzenleme boşluğu
AB YZ Yasası Md. 2(3) yalnızca askerî/savunma/ulusal güvenlik amaçlı sistemleri kapsam dışı
bırakıyor; çift kullanımlı sistemler için "kullanım belirler" ilkesi aynı yazılımın bir bakanlıkta
muaf, bir hastanede düzenlenmiş olmasına yol açıyor [K24]. Askerî sistemlerden sivile (kolluk,
sınır) geçişte boşluk riski yüksek.

### 8.10 Yetenek ve çalışan direnci
2018 Google–Maven protestosundan bu yana teknoloji çalışanları ile savunma işi arasındaki gerilim
azalsa da (büyük teknoloji şirketlerinin 2024–2025'te politikalarını gevşetmesi), etik kaygılar
işe alım ve elde tutmada hâlâ bir faktör.

---

## 9. Düzenleyici ve Yönetişim Çerçevesi

| Çerçeve | Tür | İçerik / Durum (Ekim 2026) |
|---|---|---|
| **ABD DoDD 3000.09** (Ocak 2023 güncellemesi) | Ulusal direktif | Silah sistemlerinde otonomi için üst düzey inceleme, "uygun düzeyde insan muhakemesi" ilkesi [K32] |
| **ABD Siyasi Deklarasyonu** (2023) | Gönüllü, çok taraflı | YZ ve otonominin sorumlu askerî kullanımı ilkeleri |
| **REAIM 2026 — A Coruña "Pathways to Action"** (4–5 Şubat 2026) | Gönüllü | ~40 devlet onayladı; ABD ve Çin onaylamadı — iki süper gücün de desteklemediği ilk REAIM çıktısı [K33] |
| **BM CCW GGE LAWS** | Müzakere süreci | 5 Eylül 2026'da 2024–2026 yetkisini tamamlayan uzlaşı raporu; 70+ devlet müzakere başlatmaya hazır; ABD ve Rusya'nın metni zayıflatan değişiklikler önerdiği eleştirisi; **7. Gözden Geçirme Konferansı 16–20 Kasım 2026** bağlayıcı belge müzakere yetkisi için kritik [K34] |
| **BM Genel Kurulu** (Aralık 2025) | Karar | Gelecekte müzakere hedefiyle bir belgenin unsurları üzerinde çalışma çağrısı; 156 devlet destekledi [K34] |
| **AB YZ Yasası** (2024/1689) | Bağlayıcı | Md. 2(3) askerî istisna; çift kullanımda boşluk [K24][K35] |
| **AB Çift Kullanım Tüzüğü** (2021/821) | Bağlayıcı | İhracat kontrolleri; siber gözetim öğeleri dâhil [K27] |
| **NATO YZ Stratejisi** (2021, 2024 revizyonu) | İttifak | Sorumlu kullanım ilkeleri (yasallık, sorumluluk, açıklanabilirlik, güvenilirlik, yönetilebilirlik, önyargı azaltma) |
| **Türkiye** | Ulusal | 2026–2030 Yapay Zeka Eylem Planı (altyapı odaklı) [K31]; askerî YZ'ye özgü kamuya açık bir otonomi/insan kontrolü direktifi bulunamadı [Analist tespiti] |

**Yönetişim eğilimi [Analist yargısı]:** Gönüllü normlar parçalanıyor (REAIM'de ABD ve Çin dışarıda),
bağlayıcı müzakere ihtimali ise Kasım 2026 Gözden Geçirme Konferansı'na bağlı. Bu belirsizlik
ortamında **sözleşme hukuku** (satıcı kullanım politikaları, alıcı gereksinimleri) fiilî düzenleyici
hâline geliyor.

---

## 10. Türkiye İçin Çıkarımlar ve Öneriler

### 10.1 SWOT

| Güçlü | Zayıf |
|---|---|
| Muharebede kanıtlanmış İHA/SİHA ve dolanan mühimmat sanayisi (Baykar, TUSAŞ, STM) | Yatay veri/ontoloji katmanında ölçekli yerli ürün yok |
| Güçlü ana yükleniciler (ASELSAN, HAVELSAN) ve C2/CMS deneyimi (ADVENT) | Savunma VC ekosistemi ve girişim finansmanı sınırlı |
| NATO üyeliği; NATO ekosistemine entegrasyon iddiası [K26] | Tedarik modeli program/donanım odaklı; yazılım döngüsüne uygun değil |
| İhracat pazarlarında kabul görmüş platformlar | Egemen hesaplama ve savunma için büyük model altyapısı erken aşamada |

| Fırsat | Tehdit |
|---|---|
| Avrupa'daki "egemen, yatay platform" boşluğu (Bölüm 6.3) | ABD/Avrupa platformlarının NATO'da fiilî standart hâline gelmesi (MSS) |
| Mevcut platformların (İHA) üzerine yazılım/otonomi katmanı ile değer artırma | Kritik bileşenlerde (GPU, model) dış bağımlılık ve ihracat kısıtları |
| Sivil–askerî çift kullanım (afet yönetimi — deprem deneyimi, sınır, enerji) | Yetenek göçü |
| Ukrayna modeli: devlet platformu + özel modül ekosistemi | Uluslararası normların (CCW) ihracat pazarlarını etkilemesi |

### 10.2 Öneriler

1. **Ulusal savunma veri yapısı (data fabric) standardı:** Tek bir tedarikçiye değil, açık bir
   ontoloji/veri modeli standardına yatırım. NATO standartlarıyla (FMN, STANAG) uyumlu; tüm
   yüklenicilerin uyması zorunlu. Ukrayna DELTA'nın açık modül yaklaşımı örnek alınabilir.
2. **Yazılıma özgü tedarik yolu:** ABD SWP/OTA benzeri; 90 günlük prototip → sürekli tedarik;
   yazılımın donanım programlarından ayrı bütçelenmesi.
3. **Bağımsız TEVV merkezi ve EH dâhil test sahası:** Şirket beyanlarından bağımsız, standart
   test protokolleri (HX-2 tartışmasının dersi). Sonuçların alıcılar arasında paylaşımı.
4. **Model-agnostik mimari zorunluluğu:** LLM/temel model katmanında tek sağlayıcıya bağımlılığı
   önleyen soyutlama; yerli/açık modellerle ikame edilebilirlik (Bölüm 8.7 dersi).
5. **Anlamlı insan kontrolünü ölçülebilir gereksinim yapmak:** İnceleme süresi, ret oranı,
   belirsizlik gösterimi, denetim kaydı gibi metriklerin sözleşme şartnamesine girmesi. Bu, aynı
   zamanda uluslararası normlar sıkılaşırsa ihracat pazarını koruyan bir sigortadır.
6. **Çift kullanım programı:** AFAD, enerji ve kritik altyapı için aynı karar destek çekirdeğinin
   sivil sürümü — ölçek ekonomisi ve veri çeşitliliği; ayrıca bu repodaki `PassiveDefenseOptimizer`
   gibi fizik tabanlı araçların kritik altyapı korumasına uyarlanması.
7. **Savunma girişim fonu ve "ilk müşteri" garantisi:** SSB/SAVTEK mekanizmalarının girişimlere
   küçük ama hızlı sözleşmelerle (ör. 6–12 ay) kapı açması; NATO DIANA ve NATO Inovasyon Fonu ile
   eşleştirme.
8. **Egemen hesaplama:** 2026–2030 YZ Eylem Planı'ndaki veri merkezi hedeflerinin [K31] bir bölümünün
   sınıflandırılmış iş yüklerine uygun (hava boşluklu/akredite) kapasite olarak planlanması.

---

## 11. 2027–2030 Senaryoları ve İzlenecek Göstergeler

| Senaryo | Açıklama | Olasılık [Analist yargısı] | Kazananlar |
|---|---|---|---|
| **S1 — Platform konsolidasyonu** | ABD platformları (Palantir/Anduril) NATO'da fiilî standart; Avrupa tamamlayıcı | Orta-yüksek | Palantir, Anduril |
| **S2 — Egemen bloklaşma** | Avrupa kendi yatay platformunu (ChapsVision, Helsing, SAP/Atos konsorsiyumları) kurar; NATO'da çok platformlu birlikte çalışabilirlik | Orta | Helsing, ChapsVision, Avrupa ana yüklenicileri |
| **S3 — Normatif sıkılaşma** | CCW'den bağlayıcı belge müzakeresi; insan kontrolü gereksinimleri sıkılaşır | Düşük-orta | Açıklanabilirlik/TEVV güçlü oyuncular |
| **S4 — Değerleme düzeltmesi** | Ateşkes/bütçe kesintisi; tavanlar harcamaya dönüşmez; girişim konsolidasyonu | Orta | Nakit üreten şirketler (Palantir), ana yüklenicilerin satın almaları |

**İzlenecek göstergeler**

| Gösterge | Neden | Sonraki tarih |
|---|---|---|
| Palantir 3Ç 2026 ABD kamu geliri ve RCV | Kurumsal anlaşmaların harcamaya dönüşüm hızı | 2 Kasım 2026 |
| CCW 7. Gözden Geçirme Konferansı kararı | Bağlayıcı düzenleme olasılığı | 16–20 Kasım 2026 |
| Bundeswehr bulut/YZ ihale sonucu | Avrupa egemen platform yönü | 2026 sonu (beklenen) [K17] |
| HX-2'nin Ukrayna'da sipariş durumu ve bağımsız test verisi | Helsing'in muharebe doğrulaması | Sürekli |
| Anthropic–Bakanlık davası sonucu | Model sağlayıcı politikalarının bağlayıcılığı | Belirsiz |
| CA-1 Europa ilk uçuşu | Helsing'in hava alanında yürütme kapasitesi | 2027 hedefi [K6] |
| Anduril ~100 milyar $ turunun kapanışı | Sermaye döngüsünün sürdürülebilirliği | Belirsiz [K12] |
| NATO MSS'ye üçüncü taraf modül sayısı (Görev Gücü Maven) | Platformun açıklık düzeyi | Sürekli [K4] |

---

## 12. Kaynakça

> Not: Bazı kaynaklar ikincil/agregatör niteliğindedir; ilgili iddialar metinde "[Raporlanan]" olarak
> işaretlenmiştir. Kritik kullanımlardan önce birincil kaynak doğrulaması önerilir.

- **[K1]** Palantir 2Ç 2026, Maven ARR ve kayıtlı program haberleri — [Webull/Barchart](https://www.webull.com/news/15497722791912448); [KuCoin özet](https://www.kucoin.com/news/flash/palantir-surpasses-1-billion-in-u-s-government-contracts-in-2026); [YCharts](https://ycharts.com/indicators/palantir_technologies_pltr_us_government_revenue)
- **[K4]** NATO MSS ve Pentagon Maven — [Janes](https://www.janes.com/osint-insights/defence-news/security/natos-jfc-norfolk-to-receive-palantirs-maven-smart-system-by-end-of-may); [Tom's Hardware](https://www.tomshardware.com/tech-industry/artificial-intelligence/pentagon-formalizes-palantirs-maven-ai-as-a-core-military-system-with-multi-year-funding-platforms-investment-grows-to-usd13-billion-from-usd480-million-in-2024); [heise](https://heise.de/-11220659); [AFCEA Signal](https://www.afcea.org/signal-media/emerging-edge/nato-task-force-maven-good-thing-says-program-director); [Resilience Media](https://www.resiliencemedia.co/p/nato-deploys-palantirs-ai-warfighting); [ISS Tracker](https://isstracker.pl/en/news/pentagon-poszukuje-23-miliarda-dolarow-na-system-pola-bitwy-maven-ai,x4x5P)
- **[K6]** Helsing Seri E ve ürünler — [Euro-SD](https://euro-sd.com/2026/07/news/cyber-coms/52272/helsing-raises-us1-8bn-in-series-e/); [DroneXL](https://dronexl.co/2026/05/09/helsing-18-billion-valuation/); [Grosswald](https://www.grosswald.org/helsing-1-8-billion-series-e-18-billion-valuation-europe-largest-defence-tech-round/); [Trending Topics](https://www.trendingtopics.eu/helsing-raises-1-8-billion-in-series-e-round-valuation-climbs-to-18-billion/)
- **[K7]** HX-2 Ukrayna tartışması — [Ukrainska Pravda (Bloomberg'e atfen)](https://www.pravda.com.ua/eng/news/2026/01/19/8016866); [The Defense Post](https://thedefensepost.com/2026/01/20/ukraine-pause-helsing-hx2); [Jerusalem Post](https://www.jpost.com/defense-and-tech/article-886330); [United24](https://united24media.com/latest-news/ukraine-halts-german-hx-2-drone-orders-after-battlefield-failures-bloomberg-reveals-15137); [Defence Blog](https://defence-blog.com/ukraine-halts-additional-orders-of-german-hx-2-attack-drones/)
- **[K8]** Helsing şirket bilgileri, Grob, Blue Ocean, SG-1/Lura — [Wikipedia](https://en.wikipedia.org/wiki/Helsing_(company)); [Sacra](https://sacra.com/chat/h/e4e6f913-5eec-48e4-8bd6-03ab85f1d5c4); [Techleap](https://finder.techleap.nl/news/feed/helsing-acquires-grob-aircraft-for-innovation); [SVIC tear sheet (düşük güven)](https://siliconvalleyinvestclub.com/companies/helsing/tear-sheet.pdf)
- **[K9]** ABD Ordusu–Palantir kurumsal anlaşması, NGC2 eleştirisi — [DefenseScoop](https://defensescoop.com/2025/07/31/army-palantir-software-enterprise-agreement-10-billion/embed/); [The Register](https://www.theregister.com/2025/08/01/palantir_us_army_contract/); [Benzinga](https://www.benzinga.com/markets/equities/25/08/46782374/palantir-lands-10-billion-army-deal-to-unify-75-contracts-into-one-ai-powered-defense-software-f); [Benzinga – NGC2](https://benzinga.com/trading-ideas/movers/25/10/48018068/palantir-and-anduril-under-fire-over-armys-high-risk-battlefield-tech); [Breaking Defense](https://breakingdefense.com/?p=46928)
- **[K11]** Savunma teknolojisi finansmanı — [Defense News](https://www.defensenews.com/industry/2026/01/20/defense-tech-startups-had-their-best-funding-year-ever-in-2025/); [PitchBook Vertical Snapshot](https://files.pitchbook.com/website/files/pdf/2025_Vertical_Snapshot_Defense_Tech_Preview.pdf); [Finger Lakes 1](https://www.fingerlakes1.com/2026/10/21/defense-startups-raise-record-49-billion-as-investor-interest-surges/); [City AM](https://www.cityam.com/?p=2398698)
- **[K12]** Anduril Seri H ve değerleme — [Pulse (özet)](https://www.pulse.bot/venture-capital/news/anduril-secures-5-b-series-h-valuation-hits-61-b-00a942cc-cb8a-4c02-a535-acb44a41e2c3/); [Multiples.vc](https://multiples.vc/private-comps/anduril); [Barchart](https://www.barchart.com/story/news/2399792/anduril-s-61b-valuation-signals-a-defense-industrial-reset-that-will-reshape-the-primes)
- **[K13]** Anduril gelir, Arsenal-1, Fury, Ordu anlaşması — [Sacra](https://sacra.com/research/anduril); [Robotics Press](https://robotics.press/news/anduril-deep-dive/)
- **[K15]** Palantir 2025 sonuçları ve İngiltere ortaklığı — [Panabee](https://www.panabee.com/news/palantir-earnings-2025-annual); [MarketBeat](https://www.marketbeat.com/instant-alerts/palantir-technologies-q4-earnings-call-highlights-2026-02-02/); [GOV.UK](https://www.gov.uk/government/news/new-strategic-partnership-to-unlock-billions-and-boost-military-ai-and-innovation); [Computing](https://www.computing.co.uk/news/2025/ai/uk-signs-defence-ai-partnership-palantir)
- **[K16]** İsviçre ordusu–Palantir değerlendirmesi — [Cybernews](https://cybernews.com/tech/swiss-army-palantir/); [Fair Observer](https://www.fairobserver.com/fofeatures/the-hat-in-the-square-palantir-republik-and-the-pattern-of-swiss-compliance/); [TechRepublic](https://www.techrepublic.com/article/news-uk-government-palantir-contracts/)
- **[K17]** Bundeswehr ve BfV kararları — [Anadolu Ajansı](https://aa.com.tr/en/europe/german-army-excludes-us-tech-firm-palantir-from-cloud-project-over-data-security-concerns/3921703); [Grosswald](https://www.grosswald.org/bundeswehr-rejects-palantir-military-cloud-ai-project-european-alternatives/); [The Next Web](https://thenextweb.com/news/bundeswehr-30-ai-tools-prototype-2027-palantir-alternative)
- **[K18]** Ukrayna DELTA / Avengers — [Ukrayna Savunma Bakanlığı](https://mod.gov.ua/en/news/the-delta-combat-system-records-more-than-6-600-enemy-targets-hit-every-day); [MoD – YZ asistanı](https://mod.gov.ua/en/news/ai-assistant-for-delta-is-now-available-to-all-users); [Wikipedia](https://en.wikipedia.org/wiki/Delta_(situational_awareness_system)); [NCIA](https://www.ncia.nato.int/newsroom/news/ukraine-showcases-battlefield-technology-at-nato-edge-24); [Interfax-Ukraine](https://en.interfax.com.ua/news/general/1126808.html)
- **[K19]** 2026 İran harekâtında Maven — [Al-Monitor](https://www.al-monitor.com/originals/2026/04/ai-war-five-things-know-about-project-maven); [Dawn](https://www.dawn.com/news/1988898); [KOLD](https://www.kold.com/2026/03/26/ai-targeting-system-doubles-pace-us-strikes-iran/); [Vision of Humanity](https://www.visionofhumanity.org/how-ai-is-rewriting-the-rules-of-modern-warfare/)
- **[K20]** Shield AI — [AI Business](https://aibusiness.com/generative-ai/us-military-ai-company-valued-12-7-billion); [Yahoo Finance](https://finance.yahoo.com/sectors/technology/articles/defense-technology-startup-shield-ai-134510466.html); [The Next Web](https://thenextweb.com/news/shield-ai-2-billion-hivemind-autonomous-defence)
- **[K21]** Avrupa girişimleri — [Tech.eu – Quantum Systems](https://tech.eu/2026/07/02/quantum-systems-raises-12bn-at-8bn-valuation/); [Dealroom – Stark](https://dealroom.co/news/135688-stark-confirms-500m-late-stage-round-to-scale-european-defence-manufactu/); [funding.tech.eu](https://funding.tech.eu/sectors/defence/2026); [Dealroom liste](https://dealroom.co/lists/defence-startups-europe/)
- **[K22]** Lavender/Gospel — [+972 Magazine](https://www.972mag.com/lavender-ai-israeli-army-gaza/); [Wikipedia](https://en.wikipedia.org/wiki/AI-assisted_targeting_in_the_Gaza_Strip); [The National](https://www.thenationalnews.com/news/mena/2025/07/09/data-driven-deaths-how-israels-ai-war-machine-pinpoints-palestinian-victims)
- **[K23]** Anthropic–ABD Savunma Bakanlığı anlaşmazlığı — [TechCrunch](https://techcrunch.com/2026/03/05/its-official-the-pentagon-has-labeled-anthropic-a-supply-chain-risk/); [NPR](https://www.npr.org/g-s1-112713); [heise](https://heise.de/-11201896); [Built In](https://builtin.com/articles/anthropic-pentagon-claude-dispute)
- **[K24]** AB YZ Yasası askerî istisnası — [McCann FitzGerald](https://www.mccannfitzgerald.com/knowledge/disputes/application-of-the-eu-ai-act-in-the-military-defence-and-national-security-sectors); [Finabel](https://finabel.org/wp-content/uploads/2026/01/RR-Clara-3.pdf); [Tech Policy Press](https://techpolicy.press/europes-ai-act-leaves-a-gap-for-military-ai-entering-civilian-life); [CFG](https://cfg.eu/enforcement-spotlight-spring-2026/)
- **[K25]** Helsing Altra, HX-2, ASGARD — [Kyiv Independent](https://kyivindependent.com/german-company-to-manufacture-6-000-ai-powered-drones-for-ukraine/amp); [Defence Industry EU – ASGARD](https://defence-industry.eu/?p=57608); [Shephard](https://shephardmedia.com/news/air-warfare/details-revealed-on-new-uas-munition-destined-for-ukraine/); [United24 – deniz platformu](https://united24media.com/war-in-ukraine/ukraines-german-made-hx-2-drone-now-launches-from-boats-for-black-sea-missions-18654)
- **[K26]** HAVELSAN / ASELSAN YZ — [DonanımHaber – ADVENT](https://www.donanimhaber.com/havelsan-advent-e-yapay-zeka-geliyor--194861); [Ekonomist](https://www.ekonomist.com.tr/savunma-sanayi/simulasyondan-yapay-zekaya-havelsan-nilli-platformlari-dijitalle-donatiyor-71516); [Yeni Asır](https://www.yeniasir.com.tr/ekonomi/teknoloji/2026/02/24/havelsan-yeni-tesisiyle-uretim-hizini-artiriyor); [Timeturk – ASELSAN](https://www.timeturk.com/teknoloji/aselsan-dan-mavi-vatan-a-yapay-zeka-destegi-haber-1817249)
- **[K27]** AB Çift Kullanım Tüzüğü 2021/821 — [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2021/821/oj)
- **[K28]** DIU Thunderforge (Scale AI) — DIU duyurusu, Mart 2025 (birincil kaynak: diu.mil)
- **[K29]** PLA ve DeepSeek — [Jamestown](https://jamestown.org/program/deepseek-use-in-prc-military-and-public-security-systems/); [SCMP](https://www.scmp.com/news/china/military/article/3303512/chinas-pla-using-deepseek-ai-non-combat-support-will-actual-combat-be-next); [FDD](https://www.fdd.org/analysis/policy-briefs/chinas-military-reportedly-deploys-deepseek-ai-for-non-combat-duties/); [bdnews24 (Reuters)](https://bdnews24.com/world/8a36d98a5496)
- **[K30]** ABD yazılım tedarik reformu — [Military Times](https://www.militarytimes.com/pentagon/2025/03/07/hegseth-mandates-streamlined-software-acquisition-approach-in-new-memo/); [Defense News](https://www.defensenews.com/pentagon/2025/03/26/in-the-wake-of-hegseths-software-memo-experts-eye-further-change/); [Defense One](https://www.defenseone.com/policy/2025/11/experts-see-promise-risk-pentagons-proposed-acquisition-reforms/409335); [Breaking Defense](https://breakingdefense.com/2025/02/exclusive-hegseth-draft-memo-lays-out-software-acquisition-reform-push)
- **[K31]** Türkiye SSB 2026 programı, YZ Eylem Planı, ASELSAN sözleşmesi, Baykar — [Türkgün](https://www.turkgun.com/gundem/turk-savunma-sanayiinin-2026-hedefleri/335309); [Haber7](https://www.haber7.com/teknoloji/haber/3425466-turk-savunma-sanayisindeki-ustunluk-yapay-zeka-ile-artirilacak); [Bengütürk](https://www.benguturk.com/ekonomi/aselsan-ile-ssb-arasinda-yaklasik-470-milyon-dolarlik-imzalar-269706h); [Finansopia – SSB YZ platformu](https://www.finansopia.com/genel/gundem/cumhurbaskanligi-savunma-sanayii-baskanliginin-yapay-zeka-platformu-tanitildi/)
- **[K32]** DoD Directive 3000.09, "Autonomy in Weapon Systems" (25 Ocak 2023) — [ESD/WHS PDF](https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf)
- **[K33]** REAIM 2026 — [İspanya Dışişleri Bakanlığı](https://exteriores.gob.es/en/REAIM2026/Paginas/default.aspx); [RSIS](https://rsis.edu.sg/rsis-publication/idss/ip26029-the-uncertain-future-of-the-reaim-summit/); [GCSP](https://www.gcsp.ch/publications/third-summit-responsible-ai-military-domain-reaim)
- **[K34]** CCW GGE LAWS — [Opinio Juris (Ekim 2026)](https://opiniojuris.org/2026/10/05/symposium-on-the-ccw-gge-laws-the-end-of-the-beginning-an-introduction/); [Opinio Juris (Ağustos 2026)](https://opiniojuris.org/2026/08/28/autonomous-weapons-systems-mini-symposium-beyond-yes-or-no-the-decisions-states-will-make-this-year-on-autonomous-weapons/); [Reaching Critical Will](https://reachingcriticalwill.org/disarmament-fora/ccw/2026/laws/reports/18145-ccw-report-vol-14-no-1); [Wikipedia](https://en.wikipedia.org/wiki/Group_of_Governmental_Experts_on_Lethal_Autonomous_Weapons_Systems)
- **[K35]** AB YZ Yasası 2024/1689 — [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

---

## 13. Ek: Sözlük

| Terim | Açıklama |
|---|---|
| **ATO** (Authority to Operate) | Bir yazılımın sınıflandırılmış/askerî ağda çalışma yetkisi; akreditasyon |
| **ATR** | Otomatik hedef tanıma |
| **C2 / NGC2** | Komuta-kontrol / ABD Ordusu Yeni Nesil Komuta Kontrol programı |
| **CCA** | İşbirlikçi Savaş Uçağı (Collaborative Combat Aircraft) — insanlı uçakla birlikte çalışan otonom İHA |
| **COA** | Hareket tarzı (Course of Action) |
| **COP** | Ortak operasyon resmi |
| **DDIL** | Kesintili, bağlantısız, kısıtlı bant genişlikli ortam |
| **EH (EW)** | Elektronik harp |
| **FDE** | İleri konuşlu mühendis (Forward Deployed Engineer) — Palantir'in saha mühendisliği modeli |
| **Kayıtlı program (program of record)** | Çok yıllı bütçe satırı olan, kalıcı tedarik programı |
| **Kurumsal anlaşma (enterprise agreement)** | Çok sayıda sözleşmeyi tek çerçevede birleştiren, tavan değerli uzun vadeli anlaşma |
| **MUM-T** | İnsanlı-insansız ekip çalışması |
| **Neo-prime** | Yazılım öncelikli, kendi donanımını üreten yeni nesil ana yüklenici |
| **Ontoloji** | Verinin nesne, ilişki ve eylemler olarak anlamsal modeli |
| **OTA / CSO / SWP** | ABD'de hızlı tedarik araçları: Diğer İşlem Yetkisi / Ticari Çözüm Açılışı / Yazılım Tedarik Yolu |
| **RCV** | Kalan sözleşme değeri (Remaining Contract Value) |
| **TEVV** | Test, değerlendirme, doğrulama ve geçerleme |
| **WTA** | Silah-hedef atama problemi (kombinatoryal optimizasyon) |
