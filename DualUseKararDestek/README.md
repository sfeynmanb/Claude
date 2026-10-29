# Çift Kullanımlı (Dual-Use) Karar Destek Algoritmaları
## Bütünsel Sektör Analizi: Oyuncular, Katmanlar, Bölgeler ve Yapısal Dinamikler

**Durum tarihi:** 29 Ekim 2026
**Kapsam:** Askerî ve sivil alanda ortak kullanılan, veriden karara giden zinciri hızlandıran
yazılım/algoritma sistemleri ve bu sistemlerin değer zincirindeki **tüm oyuncu grupları**:
hesaplama ve temel model sağlayıcıları, veri/karar platformları, otonomi yazılımı şirketleri,
yeni nesil donanım odaklı girişimler ("neo-prime"lar), geleneksel ana yükleniciler, sistem
entegratörleri ve devlet yapımı ekosistemler. ABD, Avrupa, İsrail, Ukrayna, Çin, Asya-Pasifik,
Körfez ve Türkiye bölgesel olarak ele alınmıştır.

Bu klasördeki dosyalar:

| Dosya | İçerik |
|---|---|
| `README.md` | Ana rapor (bu belge) |
| `analiz/sirket_matrisi.csv` | 59 oyunculuk sektör matrisi (katman, bölge, finansman, kanıt düzeyi) |
| `analiz/skor_matrisi.csv` | 8 şirket × 9 kriter analist puanları ve gerekçeleri |
| `analiz/agirlik_senaryolari.csv` | Alıcı perspektiflerine göre ağırlık setleri |
| `analiz/karsilastir.py` | Ağırlıklı skorlama ve duyarlılık analizi aracı (bağımlılıksız Python 3) |
| `analiz/tedarik_kontrol_listesi.md` | Satın alma / geliştirme kontrol listesi |

---

## İçindekiler

0. [Yönetici Özeti](#0-yönetici-özeti)
1. [Kapsam, Yöntem ve Sınırlamalar](#1-kapsam-yöntem-ve-sınırlamalar)
2. [Kavramsal Çerçeve](#2-kavramsal-çerçeve)
3. [Teknik Taksonomi: Algoritma Katmanları](#3-teknik-taksonomi-algoritma-katmanları)
4. [Pazar Büyüklüğü, Sermaye ve Birleşmeler](#4-pazar-büyüklüğü-sermaye-ve-birleşmeler)
5. [Sektör Haritası: Yedi Oyuncu Grubu](#5-sektör-haritası-yedi-oyuncu-grubu)
6. [Bölgesel Analiz](#6-bölgesel-analiz)
7. [Rekabet Dinamikleri ve Değer Yakalama](#7-rekabet-dinamikleri-ve-değer-yakalama)
8. [Karşılaştırmalı Analiz ve Skorlama](#8-karşılaştırmalı-analiz-ve-skorlama)
9. [Sektörün Yapısal İhtiyaçları](#9-sektörün-yapısal-ihtiyaçları)
10. [Sektörün Yapısal Sorunları](#10-sektörün-yapısal-sorunları)
11. [Düzenleyici ve Yönetişim Çerçevesi](#11-düzenleyici-ve-yönetişim-çerçevesi)
12. [Türkiye İçin Çıkarımlar ve Öneriler](#12-türkiye-için-çıkarımlar-ve-öneriler)
13. [2027–2030 Senaryoları ve Göstergeler](#13-20272030-senaryoları-ve-göstergeler)
14. [Kaynakça](#14-kaynakça)
15. [Ek: Sözlük](#15-ek-sözlük)

---

## 0. Yönetici Özeti

1. **Sektör yedi katmanlı bir değer zinciri olarak yeniden kuruluyor.** En altta hesaplama ve
   temel model sağlayıcıları (OpenAI, Google, Microsoft, AWS, Oracle, NVIDIA, xAI), ortada veri ve
   karar platformları (Palantir, Scale AI, ChapsVision, Thales HexaForce) ile otonomi yazılımı
   (Shield AI, Applied Intuition, Auterion), üstte donanımı da üreten yeni nesil şirketler (Anduril,
   Helsing, Saronic, Castelion, Quantum Systems) ve geleneksel ana yükleniciler (Lockheed, RTX,
   Rheinmetall, Thales, Saab, Hanwha, ASELSAN) yer alıyor. Rekabetin asıl konusu **"karar katmanının
   sahibi kim olacak"** sorusu.

2. **Pazar küçük ama sermaye çok büyük.** 2026 için askerî YZ pazar tahminleri 4–22 milyar $
   aralığında, uzlaşı 10–20 milyar $ [K40]. Buna karşın 2025'te savunma teknolojisine giden girişim
   sermayesi geniş tanımla 49,1 milyar $ [K11]. **Sermaye, mevcut harcamanın birkaç katı.** Bu,
   değerlemelerin 20–30x ileri gelir çarpanına çıkmasını ve 2026'da başlayan konsolidasyon dalgasını
   (ilk yarıda 42 savunma birleşmesi, %56 artış [K41]) açıklıyor.

3. **Temel model sağlayıcıları artık savunma tedarik zincirinin parçası.** Pentagon'un GenAI.mil
   platformu 1,3 milyondan fazla kullanıcıya ulaştı; Mayıs 2026'da sekiz şirketle gizli ağlarda
   (IL6/IL7) öncü model kullanım anlaşması imzalandı. Anthropic, kullanım sınırları nedeniyle
   "tedarik zinciri riski" ilan edilip dışarıda kaldı [K23][K42]. **Model sağlayıcının kullanım
   politikası, artık bir askerî kabiliyet değişkeni.**

4. **ABD ölçekte, Avrupa egemenlikte, Ukrayna sahada, Çin devlet yönlendirmesinde öne çıkıyor.**
   ABD platform şirketleri (Palantir, Anduril) kayıtlı programlar ve on yıllık kurumsal anlaşmalarla
   kilit konumda [K9][K13]. Avrupa'da Bundeswehr ve BfV'nin Palantir'i seçmemesi egemen alternatiflere
   (ChapsVision, Helsing, Thales, Hensoldt) pazar açıyor [K17]. Ukrayna'nın DELTA sistemi dünyanın en
   büyük gerçek zamanlı savaş alanı veri setini üretiyor [K18]. Çin ise CETC/CASIC gibi devlet
   konglomeraları ve DeepSeek gibi yerli modellerle "akıllılaştırılmış savaş" doktrinini izliyor [K29][K48].

5. **Geleneksel ana yükleniciler kaybetmiyor, ortaklık ve satın almayla uyum sağlıyor.** Safran
   Preligens'i satın aldı (Safran.AI) [K44]; Saab Helsing'e ortak oldu ve Eurofighter EH yazılımı için
   sözleşme imzaladı; Hensoldt CA-1 Europa için Helsing ile ittifak kurdu [K45]; RTX ve Lockheed,
   Shield AI'ın Hivemind'ını entegre ediyor [K46]; LIG Nex1 Palantir ile anlaştı [K47]. **Gelecek
   muhtemelen "yeni nesil yazılım + mevcut yüklenici üretim kapasitesi" melezleri.**

6. **Yapısal sorunlar teknikten çok kurumsal:** tedarik döngüleri, tek tedarikçiye bağımlılık, veri
   egemenliği, bağımsız test kapasitesi eksikliği (Helsing HX-2 tartışması [K7]), otomasyon önyargısı
   (Lavender/Gospel [K22], 2026 İran harekâtı [K19]), model sağlayıcı–devlet çatışması, sermaye-gelir
   uçurumu ve AB YZ Yasası'nın askerî istisnasından doğan düzenleme boşluğu [K24].

7. **Türkiye platform katmanında güçlü, yatay karar katmanında ve girişim finansmanında zayıf.**
   Baykar, ASELSAN, HAVELSAN, TUSAŞ, STM ve Roketsan güçlü; ancak kamuya açık güvenilir savunma
   girişimi yatırım verisi bulunamadı [K31][K50]. Öneriler Bölüm 12'de.

---

## 1. Kapsam, Yöntem ve Sınırlamalar

**Yöntem.** Açık kaynak taraması (şirket açıklamaları, yatırımcı raporları, savunma basını,
düşünce kuruluşları, bakanlık açıklamaları), ardından:
(i) teknik katman taksonomisi, (ii) yedi oyuncu grubuna göre sektör haritası (59 oyuncu),
(iii) sekiz bölgeli coğrafi analiz, (iv) rekabet dinamikleri ve değer yakalama analizi,
(v) 9 kriterli ağırlıklı karşılaştırma (8 şirket; `analiz/` altında yeniden ağırlıklandırılabilir),
(vi) yapısal ihtiyaç/sorun analizi, (vii) senaryo ve gösterge seti.

**Kanıt düzeyi işaretleri.**
- **[Doğrulanmış]** — resmî açıklama veya birden fazla güvenilir kaynakta tutarlı.
- **[Raporlanan]** — tek veya ikincil kaynak; şirket/devlet teyidi yok.
- **[Analist yargısı]** — bu raporun değerlendirmesi.

**Sınırlamalar.**
- Gizli program ayrıntıları, gerçek sözleşme yükümlülükleri (tavan ≠ harcama) ve özel şirket
  gelirleri kamuya açık değildir; gelir rakamları çoğunlukla tahmindir.
- Bazı haber kaynakları (agregatörler, otomatik derleme siteleri) düşük güvenilirliklidir; bu
  rakamlar "[Raporlanan]" olarak işaretlenmiştir.
- Çalışma ortamının ağ kısıtı nedeniyle bazı birincil kaynak sitelerine doğrudan erişilemedi;
  veriler arama sonuç özetlerinden derlendi. Kritik kararlardan önce birincil kaynağa dönülmelidir.
- **Kapsam boşlukları:** Japonya'nın 2026 savunma YZ faaliyetleri, Rusya'nın sistemleri ve Türk
  savunma girişimlerinin yatırım turları için güvenilir açık kaynak veri bulunamadı.
- Palantir'in 3. çeyrek 2026 sonuçları 2 Kasım 2026'da açıklanacak; rapordaki son veri 2Ç 2026.

**Çıkar çatışması beyanı.** Bu rapor Anthropic tarafından geliştirilen bir yapay zekâ modeli
(Claude) ile hazırlanmıştır. Anthropic, Bölüm 5.1 ve 10.7'de ele alınan Pentagon anlaşmazlığının
tarafıdır. Konu olgusal düzeyde, iki tarafın beyanlarıyla aktarılmıştır.

**Etik kapsam notu.** Rapor; mimari, pazar, yönetişim ve risk analizini stratejik/politika
düzeyinde ele alır. Silah hedefleme performansını artırmaya yönelik operasyonel ayrıntı içermez.

---

## 2. Kavramsal Çerçeve

### 2.1 Çift kullanım

AB Tüzüğü 2021/821'e göre çift kullanımlı ürün; hem sivil hem askerî amaçla kullanılabilen mal,
yazılım ve teknolojidir [K27]. Karar destek algoritmalarında üç biçimde görülür:

| Biçim | Açıklama | Örnek |
|---|---|---|
| **Aynı çekirdek, farklı alan** | Aynı veri/ontoloji motoru hem fabrika hem karargâhta | Palantir Foundry ↔ Gotham/MSS |
| **Sivilden askerîye** | Ticari model ve otonomi yığınları askerî kullanıma uyarlanır | Genel amaçlı dil modelleri (GenAI.mil); Applied Intuition'ın otomotiv otonomisinden kara araçlarına geçişi [K43] |
| **Askerîden sivile** | Askerî sensör füzyonu ve otonomi sivil alana geçer | Akustik deniz izleme → açık deniz altyapı güvenliği; sınır algoritmaları → kritik tesis güvenliği |

### 2.2 Karar döngüsü ve otonomi seviyeleri

Sektörün değer önerisi, karar döngüsünü (OODA; askerî hedeflemede F2T2EA) rakipten hızlı ve
doğru döndürmektir. **Karar destek ≠ otonom silah:**

| Seviye | İnsan rolü | Örnek |
|---|---|---|
| 0 — Bilgi sunumu | Tüm kararlar insanda | Ortak operasyon resmi (COP) |
| 1 — Öneri | Sistem seçenek önerir, insan seçer | Hareket tarzı (COA) önerisi |
| 2 — Onaylı eylem (*in-the-loop*) | Sistem eylem hazırlar, insan onaylar | Hedef nominasyonu + insan onayı |
| 3 — Denetimli otonomi (*on-the-loop*) | Sistem uygular, insan veto edebilir | Hava savunmada otomatik angajman |
| 4 — Tam otonomi (*out-of-the-loop*) | İnsan müdahalesi yok | Tartışmalı; birçok aktör için kırmızı çizgi |

Tartışmaların çoğu 2 ile 3 arasındaki gri alanda: günde yüzlerce öneri üreten bir sistemde "insan
onayı" fiilen anlamlı bir inceleme midir? (Bkz. 10.5)

---

## 3. Teknik Taksonomi: Algoritma Katmanları

```
┌───────────────────────────────────────────────────────────────┐
│ L7  İnsan–makine arayüzü, açıklanabilirlik, güven kalibrasyonu│
│ L6  Ajan / dil modeli katmanı: özetleme, sorgu, plan taslağı   │
│ L5  Planlama & optimizasyon: kaynak-görev eşleme, COA, lojistik│
│ L4  Değerlendirme & öngörü: tehdit/niyet, risk, simülasyon     │
│ L3  Durumsal farkındalık: çoklu hedef takibi, sensör füzyonu   │
│ L2  Algılama & sınıflandırma: görüntü, SAR, RF, akustik        │
│ L1  Veri katmanı: entegrasyon, ontoloji, erişim kontrolü       │
│ L0  Altyapı: bulut/kenar hesaplama, ağ, güvenlik, temel modeller│
└───────────────────────────────────────────────────────────────┘
        Dikey kesit: TEVV (test, değerlendirme, doğrulama, geçerleme)
```

| Katman | Başlıca yöntemler | Askerî kullanım | Sivil karşılık | Ana teknik risk |
|---|---|---|---|---|
| **L0 Altyapı** | Gizli bulut bölgeleri, kenar çıkarımı (nicemleme, model sıkıştırma), DDIL senkronizasyonu, temel modeller | İHA üzeri çıkarım, gizli ağlarda dil modelleri | Endüstriyel IoT, kurumsal YZ | EH altında bağlantı kaybı; model sağlayıcı bağımlılığı |
| **L1 Veri/Ontoloji** | Varlık çözümleme, bilgi grafları, nitelik tabanlı erişim kontrolü, veri soy ağacı | Çok kaynaklı istihbarat, lojistik verisi | Hastane kapasitesi, tedarik zinciri, finansal suç | Yanlış eşleme → yanlış kimlik; sınıflandırma ihlali |
| **L2 Algılama** | CNN/Transformer nesne tespiti, SAR sınıflandırma, RF parmak izi, akustik modeller | Otomatik hedef tanıma, gemi/denizaltı tespiti | Afet hasar tespiti, liman güvenliği | Dağılım kayması, kamuflaj, çekişmeli örnekler |
| **L3 Durumsal farkındalık** | Kalman ailesi, JPDA, MHT, rastgele küme filtreleri, dağıtık füzyon | Hava/deniz resmi, karşı-İHA | Hava/deniz trafik kontrolü, otonom araçlar | Yanlış ilişkilendirme, sensör zehirleme |
| **L4 Değerlendirme** | Bayes ağları, grafik sinir ağları, anomali tespiti, ajan tabanlı simülasyon | Tehdit önceliklendirme, niyet tahmini | Kritik altyapı risk analizi, salgın modelleme | Düşük taban oranlı olaylarda yanlış pozitif patlaması |
| **L5 Planlama** | MILP, kısıt programlama, silah–hedef atama, araç rotalama, ağaç araması, pekiştirmeli öğrenme | Kaynak-görev eşleme, lojistik, harekât planlama | Filo rotası, enerji dağıtımı, acil ekip ataması | Hukuk/ROE kısıtı modele girmezse "optimal ama hukuka aykırı" çözüm |
| **L6 Ajan/dil modeli** | RAG, araç kullanan ajanlar, doğal dil → yapılandırılmış sorgu | İstihbarat özeti, emir taslağı, planlama ajanları (Thunderforge [K28]) | Kurumsal bilgi yönetimi, mevzuat analizi | Halüsinasyon, istem enjeksiyonu, aşırı güven |
| **L7 Arayüz** | Belirsizlik görselleştirme, açıklanabilir YZ, güven kalibrasyonu | Operatör ekranları | Klinik karar destek | Otomasyon önyargısı, bilişsel aşırı yük |

**Repodaki bağlantı:** `PassiveDefenseOptimizer/` L5 katmanında **fizik tabanlı** bir karar destek
örneğidir. Bu tür açıklanabilir optimizasyon araçları doğrulanabilirlik açısından kara kutu
modellere göre avantajlıdır; hibrit "fizik + öğrenme" mimarileri TEVV sorununa (10.4) kısmi cevaptır.

**2025–2026 mimari eğilimler:**
1. **Ontoloji merkezli mimari:** Dil modelleri ham veriye değil, yetkilendirilmiş nesne ve eylemlere erişiyor.
2. **Gizli ağlarda öncü modeller:** IL6/IL7 ortamlarında ticari modellerin kullanımı [K42].
3. **Kenar yerelliği:** EH ortamında algılama ve terminal yönlendirme platform üzerine taşınıyor.
4. **Tek operatör – çok platform:** Sürü ve insanlı-insansız ekip (Altra–HX-2 [K25], Hivemind, CETC "Atlas" sürüsü [K48]).
5. **Açık modüler ekosistemler:** DELTA ve NATO Görev Gücü Maven üçüncü taraf modüllere yer açıyor [K4][K18].
6. **Ajan tabanlı planlama:** Scale AI'ın Mayıs 2026'daki 500 milyon $'lık sözleşmesi, YZ ajanlarını harekât planlamaya taşımayı hedefliyor [K28].

---

## 4. Pazar Büyüklüğü, Sermaye ve Birleşmeler

### 4.1 Pazar büyüklüğü

| Kaynak | 2026 tahmini | Uzun vade | Not |
|---|---|---|---|
| Visiongain | 14,49 milyar $ | ~45 milyar $ (2036), %12 YBBO | Askerî YZ sistemleri |
| Fortune Business Insights | 22,41 milyar $ | ~101 milyar $ (2034), %20,7 | En yüksek |
| Next Move Strategy | 18,60 milyar $ | 79,4 milyar $ (2035) | |
| Persistence Market Research | 11,6 milyar $ | 34,2 milyar $ (2033) | |
| Knowledge Sourcing | 8,5 milyar $ | 32,8 milyar $ (2031) | |
| Meticulous Research | 4,2 milyar $ | 42,8 milyar $ (2036) | Farklı kapsam |

Kaynak: [K40]. **Uzlaşı:** 2026 tabanı 10–20 milyar $, yıllık %12–20 büyüme. Tanım farkları
çok büyük; rakamlar doğrudan karşılaştırılmamalı.

### 4.2 Sermaye akışı

| Gösterge | Değer | Kaynak |
|---|---|---|
| Küresel savunma teknolojisi VC, geniş tanım (2025) | 49,1 milyar $ (2024: 27,2) | PitchBook [K11] |
| Dar tanım (2025) | 17,9 milyar $ | CB Insights [K11] |
| Savunma teknolojisi çıkışları (2025) | 54,4 milyar $ (2024: 18,2) | PitchBook [K11] |
| Avrupa savunma-güvenlik-dayanıklılık VC'si (2025) | 8,7 milyar $ (rekor) | Dealroom / NATO İnovasyon Fonu [K49] |
| Avrupa dar savunma girişimleri (2025) | ~3,5 milyar € | [K21] |
| İsrail savunma teknolojisi yatırımı (2026 ilk yarı) | ~3 milyar $ [Raporlanan, zayıf kaynak] | [K51] |
| Ukrayna savunma teknolojisi (2025, kamuya açık) | 105 milyon $+ (2023: 1,1 milyon $) | Brave1 [K52] |
| Hindistan savunma teknolojisi girişimleri (2025) | ~68 milyon $ | [K53] |

**Analist yargısı:** 2026 pazar büyüklüğü ile 2025 VC akışı aynı mertebede veya VC daha büyük.
Yatırımcılar mevcut harcamayı değil, NATO'nun artan bütçelerini, kayıtlı program dönüşümlerini ve
"yazılım tanımlı savaş" tezini fiyatlıyor. ABD ile Avrupa arasındaki fark (49 milyar $'a karşı
~9 milyar $) ve İsrail–Ukrayna–Hindistan ölçekleri, sermayenin ne kadar yoğunlaştığını gösteriyor.

### 4.3 Birleşme ve satın almalar: Konsolidasyon başladı

| İşlem | Tarih | Anlamı |
|---|---|---|
| Safran → Preligens (220 milyon € şirket değeri; Safran.AI) | 2024 | Ana yüklenici YZ yeteneğini satın alıyor [K44] |
| Saab → Helsing (%5 hisse, 75 milyon €) + Eurofighter EH yazılım sözleşmesi | 2023 / Kas 2025 | Ana yüklenici–neo-prime ortaklığı [K45] |
| Anduril → ExoAnalytic Solutions | Mart 2026 | Uzay gözetimi verisi ile platformu genişletme [K41] |
| Leonardo → Iveco Defence Vehicles (~1,7 milyar €) | Mart 2026 kapanış | Klasik yükleniciler arası ölçek [K41] |
| Naval Group → cortAIx France'ın %20'si (Thales'ten) | Mart 2026 [Raporlanan] | Avrupa yükleniciler arası YZ paylaşımı [K54] |
| Chaos Industries → Atropos (otonom uçak) | Temmuz 2026 | Girişimler birbirini satın alıyor: sensör + efektör birleşimi [K41] |
| Helsing → Grob Aircraft, Blue Ocean | 2025 | Yazılım şirketi donanım üreticisi satın alıyor [K8] |

White & Case verisine göre 2026 ilk yarısında küresel olarak 42 savunma birleşmesi tamamlandı
(%56 artış) [K41]. **Analist yargısı:** Üç birleşme türü var: (a) ana yüklenicilerin YZ satın
alması, (b) neo-prime'ların donanım ve veri satın alması, (c) fazla sermayeli girişimlerin ölçek için
birbirini satın alması. Önümüzdeki 18–24 ayda (c) türü hızlanacak.

---

## 5. Sektör Haritası: Yedi Oyuncu Grubu

```
 G1 Hesaplama & temel modeller ─► G2 Veri/karar platformları ─► G3 Otonomi yazılımı ─► G4 Neo-prime'lar ─► G5 Ana yükleniciler ─► Kullanıcı
                                                                                        ▲                     ▲
                                  G6 Sistem entegratörleri / hizmet şirketleri ──────────┴─────────────────────┘
                                  G7 Devlet yapımı ekosistemler (DELTA, PLA/CETC, iDEX) — tüm katmanlarda
```

### 5.1 G1 — Hesaplama ve temel model sağlayıcıları

| Oyuncu | Savunma konumu (2025–2026) | Kanıt |
|---|---|---|
| **OpenAI** | CDAO prototip anlaşması (tavan 200 milyon $, Tem 2025); ChatGPT'nin GenAI.mil'e entegrasyonu (Şub 2026); gizli ağ anlaşması (May 2026); Leidos ortaklığı (Oca 2026); Anduril ortaklığı (Ara 2024) | Doğrulanmış/Raporlanan [K42][K55] |
| **Google** | GenAI.mil'in ilk modeli Gemini for Government (Ara 2025); gizli ağ anlaşması; 2025'te silah kullanımına ilişkin ilkesini kaldırdı | Raporlanan [K42] |
| **Microsoft** | Azure Government; gizli ağ anlaşması; Thunderforge ve NGC2'de bileşen sağlayıcı | Raporlanan [K28][K42] |
| **AWS / Oracle** | Gizli bulut bölgeleri; gizli ağ YZ anlaşmaları | Raporlanan [K42] |
| **NVIDIA** | Hesaplama + gizli ağ anlaşması; Northrop ile otonom uzay araçları (2025) | Raporlanan [K42][K46] |
| **xAI / SpaceX** | "xAI for Government" GenAI.mil'de; gizli ağ erişimi Senato soruşturmasına yol açtı | Raporlanan [K42] |
| **Reflection AI** | Mayıs 2026 gizli ağ anlaşmaları listesinde (açık ağırlıklı model odaklı ABD girişimi) | Raporlanan [K42] |
| **Meta** | Llama modellerini ABD savunmasına açtı (2024); Scale AI'ın %49'unu 14,3 milyar $'a aldı (2025) | Raporlanan [K28] |
| **Anthropic** | CDAO prototip anlaşması (Tem 2025); Palantir–AWS üzerinden gizli kullanım; Mart 2026'da "tedarik zinciri riski" ilanı, gizli ağ anlaşmalarının dışında; NSA'nın yine de bir Claude modelini gizli ağlarda kullandığı raporlandı; dava sürüyor | Doğrulanmış/Raporlanan [K23][K42] |
| **Mistral** (Fransa) | Helsing ile savunma için görsel-dil-eylem modelleri ortaklığı (Şub 2025) — Avrupa'nın egemen model seçeneği | Doğrulanmış (şirket duyuruları) |
| **DeepSeek** (Çin) | PLA tedarik belgelerinde; sürü kararları için patent başvuruları [K29][K48] | Raporlanan |

**Analist yargısı:** G1 oyuncuları için savunma gelir olarak küçük, ama stratejik olarak (gizli veri,
devlet ilişkisi, "ulusal şampiyon" konumu) büyük önem taşıyor. ABD Savunma Bakanlığı'nın sekiz
sağlayıcıyla paralel anlaşma yapması, **tek model sağlayıcıya bağımlılıktan kaçınma** stratejisi
olarak okunmalı.

### 5.2 G2 — Veri ve karar platformları

| Oyuncu | Ülke | Ürün / konum | Öne çıkan veri |
|---|---|---|---|
| **Palantir** | ABD | Gotham, Foundry, AIP, Apollo, Maven Smart System, TITAN | 2025 geliri 4,475 milyar $; Ordu kurumsal anlaşması (10 yıl, tavan 10 milyar $); MSS 2026'da kayıtlı program; NATO MSS [K1][K4][K9][K15] |
| **Scale AI** | ABD | Veri etiketleme, değerlendirme, planlama ajanları (Thunderforge) | Pentagon 500 milyon $ (May 2026; Eyl 2025'te 100 milyon $); Meta %49 hisse [K28] |
| **Vannevar Labs** | ABD | Açık kaynak/yabancı dil istihbaratı için ajan tabanlı YZ | ~90 milyon $ toplam finansman [Raporlanan] [K56] |
| **Govini** | ABD | Savunma sanayi tabanı ve tedarik analitiği | Kamuya açık güncel veri sınırlı |
| **ChapsVision** | Fransa | ArgonOS veri analitiği | Alman BfV, Palantir yerine seçti (May 2026) [K17] |
| **Thales (HexaForce, cortAIx)** | Fransa | YZ destekli komuta-kontrol; cortAIx YZ hızlandırıcısı | HexaForce için birden fazla NATO ülkesiyle ileri görüşme (Eyl 2026) [Raporlanan] [K54] |
| **Hensoldt (MDOcore)** | Almanya | Çok alanlı harekât yazılım omurgası | CA-1 Europa için Helsing ile ittifak (Şub 2026) [K45] |
| **Comand AI** | Fransa | Komuta-kontrol planlama ve karar destek | 32 milyon € Seri A (Haz 2026) [K21] |
| **HAVELSAN (ADVENT-AI, MAIN)** | Türkiye | Deniz muharebe yönetim sistemine YZ karar destek | SAHA EXPO 2026, EFES-2026 gösterimleri [K26] |

### 5.3 G3 — Otonomi yazılımı

| Oyuncu | Ülke | Konum | Öne çıkan veri |
|---|---|---|---|
| **Shield AI (Hivemind)** | ABD | Platform-bağımsız uçuş/görev otonomisi | 12,7 milyar $ (Mar 2026); ABD Hava Kuvvetleri CCA görev otonomisi; RTX, Lockheed, General Atomics entegrasyonları [K20][K46] |
| **Applied Intuition** | ABD | Otomotiv otonomisinden savunmaya geçen simülasyon ve otonomi yığını | 15 milyar $ değerleme; Ordu araç otonomisi işi [K43] |
| **Auterion** | İsviçre/ABD | İHA otonomi işletim sistemi, sürü ve terminal yönlendirme | 1,2 milyar $+ değerlemeyle tur görüşmesi [Raporlanan] [K21] |
| **Swarmer** | Ukrayna/ABD | İHA sürü otonomisi; 100.000+ muharebe görevi iddiası | Mart 2026'da Nasdaq halka arzı (SWMR), 17,3 milyon $; 1Ç 2026 geliri ~20 bin $ [K57] |
| **Helsing (Centaur)** | Almanya | Savaş uçağı otonomi yığını | CA-1 Europa için [K6] |

**Analist yargısı:** Swarmer örneği sektörün iki yüzünü birlikte gösteriyor: gerçek muharebe kullanımı
ve çok düşük ticari gelir. Otonomi yazılımının bağımsız iş modeli olarak sürdürülebilirliği,
platform üreticilerinin kendi otonomi yığınlarını geliştirmesi karşısında belirsiz.

### 5.4 G4 — Neo-prime'lar (yazılım öncelikli donanım üreticileri)

| Oyuncu | Ülke | Alan | Değerleme / finansman |
|---|---|---|---|
| **Anduril** | ABD | Lattice + İHA, karşı-İHA, CCA (Fury), Arsenal-1 fabrikası | 61 milyar $ (May 2026); ~2,2 milyar $ tahmini 2025 geliri; Ordu kurumsal anlaşması tavanı 20 milyar $ [Raporlanan] [K12][K13] |
| **Helsing** | Almanya | Altra + HX-2, CA-1 Europa, SG-1 Fathom | 18 milyar $ (Tem 2026) [K6] |
| **Saronic** | ABD | Otonom yüzey gemileri | 1,75 milyar $ tur, 9,25 milyar $ (Mar 2026) [K58] |
| **Castelion** | ABD | Düşük maliyetli hipersonik füzeler (Blackbeard) | 1 milyar $ Seri C, ~13 milyar $ (Ağu 2026) [Raporlanan] [K59] |
| **Chaos Industries** | ABD | Karşı-İHA radar ve sensör ağları | 510 milyon $, 4,5 milyar $ (Kas 2025); Atropos satın alması [K59][K41] |
| **Epirus** | ABD | Yüksek güçlü mikrodalga karşı-İHA (Leonidas) | 250 milyon $ Seri D (Mar 2025) [K59] |
| **Quantum Systems** | Almanya | Keşif İHA'ları | 1,2 milyar $ tur, 8 milyar $ (Tem 2026) [K21] |
| **Stark** | Almanya | Dolanan mühimmat | 500 milyon € (Haz 2026) [K21] |
| **Tekever** | Portekiz | İHA + YZ; İngiltere'de 400 milyon £'luk OVERMATCH programı | Mayıs 2025'te unicorn; Ağu 2026'da 5,5 milyar € değerlemeyle 500 milyon € arayışı [Raporlanan] [K60] |
| **XTEND** | İsrail | YZ destekli modüler saldırı İHA'ları; ABD Savunma Bakanlığı sözleşmesi | Şub 2026'da 152 milyon $ tur [Raporlanan] [K51] |

### 5.5 G5 — Geleneksel ana yükleniciler

| Oyuncu | Ülke | YZ stratejisi |
|---|---|---|
| **Lockheed Martin** | ABD | DARPA AIR programı; IBM Granite modellerinin "AI Factory" araçlarına entegrasyonu; Hivemind entegrasyonu [K46] |
| **RTX** | ABD | Shield AI ile kendi finanslı ortaklık; Hivemind'ı silah ve sensörlere entegre etme (Tem 2025) [K46] |
| **Northrop Grumman** | ABD | NVIDIA ile otonom uzay araçları (2025) [K46] |
| **General Atomics** | ABD | CCA YFQ-42A; Hivemind entegrasyonu [K13][K46] |
| **Thales** | Fransa | cortAIx hızlandırıcısı; HexaForce YZ destekli komuta-kontrol; "YZ karar vericiyi destekler, yerini almaz" ilkesi; 2026'da ~9.000 işe alım [K54] |
| **Safran** | Fransa | Preligens satın alması → Safran.AI [K44] |
| **Saab** | İsveç | Helsing'de %5 hisse; Eurofighter Arexis EH paketine Helsing Cirra YZ entegrasyonu (Kas 2025, "üç haneli milyon €") [K45] |
| **Hensoldt** | Almanya | MDOcore; CA-1 için Helsing ittifakı [K45] |
| **Rheinmetall** | Almanya | 2022'de Helsing ile kara sistemleri YZ işbirliği; sonra bazı İHA otonomisinde Auterion [Raporlanan] [K45] |
| **Leonardo** | İtalya | Uzay ittifakı (Telespazio, Thales Alenia Space); Iveco Defence satın alması [K41][K54] |
| **BAE Systems** | İngiltere | AUKUS ve GCAP odaklı; YZ stratejisine ilişkin kamuya açık ayrıntı sınırlı [K54] |
| **Elbit, Rafael, IAI** | İsrail | Sınır koruma algoritmaları, lazer hava savunma; girişimlerin bu platformlara bileşen olarak takılması modeli [K51] |
| **Hanwha, LIG Nex1** | G. Kore | İnsanlı-insansız ekip platformları; LIG Nex1–Palantir mutabakatı (Mar 2026), YZ sürü İHA'ları; Hanwha Defense News Top 100'de 16. sıra [K47] |
| **EDGE Group** | BAE | SIRBAI ile YZ sürü İHA ortaklığı; insansız deniz araçları [K61] |
| **ASELSAN** | Türkiye | Deniz sensör/atış kontrolüne YZ; YZ destekli Kent Güvenliği sistemleri (~470 milyon $); Sensör Verisi İşleme ve YZ Merkezi planı [K26][K31] |
| **Baykar, TUSAŞ, STM, Roketsan** | Türkiye | Otonom platformlar; Baykar SAHA 2026'da 6 yeni otonom sistem [K50] |

### 5.6 G6 — Sistem entegratörleri ve hizmet şirketleri

| Oyuncu | Konum |
|---|---|
| **Booz Allen Hamilton** | ABD federal YZ sözleşme yükümlülüklerinde 2022–2024 mali yıllarında 1. sıra (Deltek); Palantir uygulama ortaklığı; sivil kurum işlerinde DOGE kesintilerinden etkilendi [K62] |
| **Leidos** | YZ ile askerî karar destek ve siber güvenlik; OpenAI ortaklığı (Oca 2026) [K62] |
| **SAIC** | Savunma BT modernizasyonu, JWCC bulut entegrasyonu; istihbarat alanında 400 milyon $ yenileme (Ağu 2026) [K62] |

**Analist yargısı:** Entegratörler, yeni platformların kurumlara yerleştirilmesinde vazgeçilmez
ama marjları sıkışıyor: platform şirketlerinin ileri konuşlu mühendis modeli (Palantir) ve
neo-prime'ların doğrudan satışı, geleneksel "insan saati" iş modelini aşındırıyor.

### 5.7 G7 — Devlet yapımı ekosistemler

| Ekosistem | Ülke | Yapı |
|---|---|---|
| **DELTA / Avengers / Brave1** | Ukrayna | Devletin geliştirdiği durumsal farkındalık platformu + bilgisayarlı görü modülü + girişim hızlandırıcı. Haziran 2026'da 200.000+ İHA vuruşu kaydı, günde 75.000 video akışı [K18]. Brave1: 2025'te 105 milyon $+ kamuya açık yatırım [K52] |
| **PLA / CETC / CASIC / Norinco** | Çin | Devlet konglomeraları (CETC 14. ve 38. enstitüler); CSET'e göre PLA tedarik belgelerinde tüm alanlarda YZ karar destek, sensör iyileştirme ve veri füzyonu talepleri; 3–6 aylık ticari prototipleme hedefleri; "Atlas" sürüsü (tek operatör, 96 İHA), Jiu Tian ana gemi İHA'sı (prototip) [K48] |
| **iDEX** | Hindistan | 600'den fazla girişime hibe (iDEX Prime'da 10 crore ₹'ye kadar); 14. Savunma Girişim Yarışması'nda 82 problem [K53] |
| **NATO DIANA / NATO İnovasyon Fonu** | İttifak | DIANA 2026: 24 ülkeden 150 girişim (3.000+ başvuru); NIF: 1 milyar € fon, proje başına 15 milyon €'ya kadar [K49] |

---

## 6. Bölgesel Analiz

| Bölge | Güçlü yanlar | Zayıf yanlar | Belirleyici aktörler |
|---|---|---|---|
| **ABD** | Sermaye derinliği (2025 VC'nin büyük kısmı); öncü modeller ve hesaplama; yazılım tedarik reformları (SWP/OTA/PAE) [K30]; kayıtlı programa dönüşüm | Tek tedarikçi kilitlenmesi; model sağlayıcı politikasının siyasallaşması (Anthropic); müttefiklerde egemenlik direnci | Palantir, Anduril, Shield AI, Scale AI, OpenAI, Google, Microsoft |
| **Avrupa** | Egemenlik talebi; güçlü ana yükleniciler (Thales, Saab, Rheinmetall, Safran, Hensoldt); hızla büyüyen neo-prime'lar | ABD'nin ~1/5'i sermaye; 27 ayrı tedarik sistemi; ölçekli yatay veri platformu eksikliği; ihracat kısıtları | Helsing, ChapsVision, Thales, Quantum Systems, Stark, Tekever, Mistral |
| **İsrail** | Sahada kanıt; askerî istihbarat birimlerinden yetenek akışı; hızlı girişim-yüklenici entegrasyonu | Etik ve hukuki tartışmalar (Lavender/Gospel [K22]); ihracat kısıtları ve itibar riski | Elbit, Rafael, IAI, XTEND |
| **Ukrayna** | Dünyanın en büyük gerçek zamanlı savaş alanı veri seti; açık modüler devlet platformu; hızlı yineleme | Ticari gelir çok düşük; sermaye kıtlığı; savaş sonrası sürdürülebilirlik | DELTA, Brave1, Swarmer |
| **Çin** | Devlet yönlendirmesi; yerli modeller (DeepSeek); sürü ve insanlı-insansız ekip odaklı; hızlı prototipleme | Gerçek muharebe eğitim verisi eksikliği; bilgi kontrolü kısıtları; ABD'nin veri merkezi üstünlüğü [K48] | PLA, CETC, CASIC, Norinco |
| **Asya-Pasifik** | Kore'nin hızla yükselen ihracatçı yüklenicileri; Hindistan'ın iDEX modeli | Hindistan'da küçük girişim sermayesi (~68 milyon $, 2025); Japonya için açık veri sınırlı | Hanwha, LIG Nex1, iDEX girişimleri |
| **Körfez** | Büyük bütçe; yerelleştirme zorunluluğu; ucuz karşı-İHA ve YZ ağlarına yönelim [K61] | 2026 İran savaşında dijital altyapıya saldırılar ve onarım maliyetleri YZ yatırımlarını geciktiriyor [K61] | EDGE, SAMI |
| **Türkiye** | Muharebede kanıtlanmış İHA/SİHA ve dolanan mühimmat; güçlü yüklenici tabanı; NATO üyeliği | Yatay veri/karar platformu yok; girişim sermayesi ve açık veri sınırlı; yazılıma uygun tedarik modeli yok | Baykar, ASELSAN, HAVELSAN, TUSAŞ, STM, Roketsan |

---

## 7. Rekabet Dinamikleri ve Değer Yakalama

### 7.1 Beş güç çerçevesi (karar destek yazılımı pazarı için)

| Güç | Düzey | Gerekçe |
|---|---|---|
| **Alıcı gücü** | Yüksek, ama azalıyor | Tek büyük alıcı (devlet); ancak kurumsal anlaşmalar ve kayıtlı programlar değişim maliyetini yükseltiyor ve satıcıyı güçlendiriyor |
| **Tedarikçi gücü** (hesaplama, model, çip) | Yükseliyor | Öncü modeller ve GPU birkaç şirkette; model sağlayıcı kullanım politikaları kabiliyeti kısıtlayabiliyor (Anthropic örneği) |
| **Yeni giriş tehdidi** | Orta | Rekor sermaye girişi kolaylaştırıyor; ama güvenlik izni, akreditasyon ve gizli veri erişimi ciddi giriş engelleri |
| **İkame tehdidi** | Orta | Ana yüklenicilerin kendi YZ yığınları (Thales cortAIx), devlet yapımı platformlar (DELTA), açık kaynak modeller |
| **Rekabet yoğunluğu** | Yüksek ve konsolide oluyor | 2026'da birleşme dalgası; kazanan-hepsini-alır eğilimli kurumsal anlaşmalar |

### 7.2 Değer kim tarafından yakalanıyor?

| Katman | Marj / değer yakalama | Savunma özgüllüğü | Eğilim [Analist yargısı] |
|---|---|---|---|
| G1 Hesaplama/model | Yüksek, ama savunma payı küçük | Düşük (genel amaçlı) | Metalaşma baskısı; ayrışma gizli ağ akreditasyonu ve kullanım politikası üzerinden |
| G2 Veri/karar platformu | En yüksek yazılım marjı (Palantir kârlı) | Orta-yüksek (ontoloji, iş akışı) | En stratejik katman; kilitlenme gücü burada |
| G3 Otonomi yazılımı | Orta; lisans geliri küçük | Yüksek | Platform üreticilerine entegre olma veya satın alınma baskısı |
| G4 Neo-prime | Donanım marjı + yazılım primi | Yüksek | Üretim ölçeği (fabrikalar) belirleyici; sermaye yoğun |
| G5 Ana yükleniciler | İstikrarlı ama düşük büyüme | Çok yüksek | Ortaklık/satın alma ile YZ edinme |
| G6 Entegratörler | Sıkışan marj | Orta | Platform şirketlerinin saha mühendisliği modeli rakip |

**Temel bulgu [Analist yargısı]:** Değer en çok **G2 (veri/karar katmanı)** ve **üretim ölçeğine
ulaşmış G4** oyuncularında birikiyor. G1 için savunma stratejik ama küçük; G3 bağımsız kalmakta
zorlanıyor; G5 ise ortaklıklarla zaman kazanıyor.

### 7.3 Stratejik konumlanma haritası

```
                Dikey entegrasyon (donanım + yazılım)
                              ▲
     Anduril ●  Saronic ●     │      ● Helsing   ● Quantum Systems / Stark / Tekever
   Castelion ● Chaos ●        │
     Lockheed ● RTX ●         │      ● Thales ● Saab ● Rheinmetall    ● Baykar / ASELSAN
       Shield AI ●            │      ● Hanwha / LIG Nex1 (Kore)
 ABD ◄────────────────────────┼────────────────────────► Avrupa / egemen / diğer
       Applied Intuition ●    │      ● Hensoldt MDOcore  ● HAVELSAN
          Palantir ●          │      ● ChapsVision ● Comand AI
   Scale AI ● Vannevar ●      │      ● DELTA (Ukrayna, devlet)
 OpenAI ● Google ● Microsoft ●│      ● Mistral
                              ▼
                Yatay platform (yazılım katmanı)
```

**Boşluk tespiti [Analist yargısı]:** Sağ-alt kadran (ABD dışı, yatay, ölçekli veri/karar
platformu) hâlâ görece boş. Bundeswehr'in 30 YZ aracını değerlendirip 2027'de prototip hedeflemesi
[K17] bu boşluğun talep tarafının oluştuğunu gösteriyor. Türkiye ve Avrupa için en büyük pazar
fırsatı burada.

---

## 8. Karşılaştırmalı Analiz ve Skorlama

### 8.1 Oyuncu grubu arketipleri

| Arketip | Kazanma koşulu | Kaybetme riski | Temsilci |
|---|---|---|---|
| Veri işletim sistemi | Kurumsal yerleşiklik, ontoloji kilitlenmesi | Egemenlik tepkisi, açık standart dayatması | Palantir, ChapsVision |
| Veri + ajan sağlayıcı | Değerlendirme ve veri altyapısında uzmanlık | Model sağlayıcıların dikeyleşmesi | Scale AI |
| Otonomi çekirdeği | Platform bağımsızlığı, çok sayıda entegrasyon | Platform üreticilerinin kendi yığını | Shield AI, Applied Intuition, Auterion |
| Neo-prime | Üretim ölçeği + yazılım hızı | Sermaye yoğunluğu, saha performansı | Anduril, Helsing, Saronic |
| Ana yüklenici | Muharebede kanıt, üretim, müşteri ilişkisi | Yazılım hızında geri kalma | Thales, Lockheed, ASELSAN |
| Devlet ekosistemi | Veri ve sahadan geri bildirim | Ticari sürdürülebilirlik | DELTA, iDEX |

### 8.2 Palantir ve Helsing (merkez vaka)

| Boyut | Palantir | Helsing |
|---|---|---|
| Arketip | Veri işletim sistemi (yatay) | Neo-prime (dikey) |
| Ana katmanlar | L1, L4, L5, L6, L7 | L0, L2, L3, L5 + efektör |
| Gelir | 4,475 milyar $ (2025), kârlı | Açık değil; 2026 için ~441 milyon € tahmini (düşük güven) [K8] |
| Muharebe kanıtı | Ukrayna, İran harekâtı [Raporlanan], NATO | Ukrayna'da sahada; HX-2 performansı tartışmalı [K7] |
| Avrupalı alıcı için egemenlik | Zayıf (İsviçre, Bundeswehr) [K16][K17] | Güçlü |
| Ortaklık ağı | Booz Allen, Anthropic/AWS, LIG Nex1, NATO | Saab, Hensoldt, Mistral, Grob |

Bu iki şirket rakip değil, tamamlayıcı katmanlarda; rekabet Avrupa'daki komuta-kontrol ve veri
platformu ihalelerinde, egemenlik ekseninde yaşanıyor.

### 8.3 Çok kriterli skorlama (8 şirket, 9 kriter)

Puanlar 1–5 **analist yargısıdır**; gerekçeler `analiz/skor_matrisi.csv` dosyasındadır. Yeni
eklenen şirketler (Scale AI, Thales, ChapsVision, HAVELSAN) için kamuya açık veri daha sınırlı
olduğundan güven düzeyi daha düşüktür.

**Kriterler:** K1 Ürün olgunluğu/ölçek · K2 Muharebe doğrulaması · K3 Veri/entegrasyon katmanı ·
K4 Kenar/EH dayanıklılığı · K5 Donanım/efektör entegrasyonu · K6 Egemenlik (Avrupalı alıcı) ·
K7 Finansal sağlamlık · K8 Yönetişim/şeffaflık · K9 Yazılım hızı ve yenilik

| Şirket | K1 | K2 | K3 | K4 | K5 | K6 | K7 | K8 | K9 | **A: Dengeli** | **B: Avrupa egemenlik** | **C: Ön hat/EH** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Palantir | 5 | 4 | 5 | 3 | 2 | 2 | 5 | 3 | 5 | **79,0** | 70,0 | 69,0 |
| Thales | 5 | 3 | 3 | 4 | 5 | 5 | 5 | 4 | 2 | **79,0** | **82,0** | **81,0** |
| Anduril | 4 | 3 | 4 | 4 | 5 | 2 | 4 | 3 | 5 | 76,0 | 69,0 | 78,0 |
| Helsing | 3 | 2 | 3 | 4 | 4 | 5 | 4 | 3 | 4 | 69,0 | 73,0 | 69,0 |
| Shield AI | 3 | 3 | 2 | 5 | 4 | 2 | 3 | 3 | 4 | 63,0 | 59,0 | 73,0 |
| Scale AI | 3 | 2 | 4 | 2 | 1 | 2 | 4 | 3 | 5 | 58,0 | 52,0 | 46,0 |
| ChapsVision | 3 | 2 | 4 | 2 | 1 | 5 | 3 | 3 | 3 | 58,0 | 64,0 | 46,0 |
| HAVELSAN | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 55,0 | 56,0 | 55,0 |

*(0–100 ölçeğine normalize ağırlıklı toplam; ağırlıklar `analiz/agirlik_senaryolari.csv`'de.)*

**Okuma:**
- **Ana yükleniciler hafife alınmamalı:** Thales, yazılım hızındaki düşük puanına rağmen olgunluk,
  donanım, egemenlik ve finansal güçle dengeli senaryoda Palantir ile eşit, diğer iki senaryoda
  birinci. "Neo-prime'lar yüklenicileri yerinden edecek" anlatısı en azından Avrupa'da abartılı.
- **Yazılım hızının değeri:** Dengeli senaryoda yazılım hızı (K9) ağırlığı %10'un altına indiğinde
  Thales, üstüne çıktığında Palantir lider (`karsilastir.py --duyarlilik K9`). Sıralamayı alıcının
  hız ile güvence arasındaki tercihi belirliyor.
- **Egemenlik:** Egemenlik (K6) ağırlığı %15'i geçince Thales tek başına lider; yaklaşık %27'yi
  geçince Helsing de Palantir'in önüne geçiyor.

```bash
python3 DualUseKararDestek/analiz/karsilastir.py --duyarlilik K9
```

```bash
python3 DualUseKararDestek/analiz/karsilastir.py --agirlik "K1=10,K2=20,K3=10,K4=15,K5=10,K6=20,K7=5,K8=5,K9=5"
```

---

## 9. Sektörün Yapısal İhtiyaçları

| # | İhtiyaç | Neden kritik | Mevcut durum |
|---|---|---|---|
| 1 | **Karar hızının ölçeklenmesi** | Hedef/olay sayısı insan kapasitesini aşıyor (DELTA'da günde 6.600+ vuruş kaydı [K18]) | Algılama otomatik; değerlendirme kısmen; onay insanda |
| 2 | **Veri birlikte çalışabilirliği** | Koalisyon operasyonları, çok tedarikçili ortam | Parçalı; NATO MSS ile fiilî ama tek tedarikçili standartlaşma |
| 3 | **Kenar hesaplama ve DDIL dayanıklılığı** | EH ve bağlantı kesintisi ön hatta norm | Algılamada ilerleme; HX-2 tartışması sorunun sürdüğünü gösteriyor [K7] |
| 4 | **Hızlı ve güvenilir TEVV** | Yazılım haftalık güncelleniyor, akreditasyon aylar sürüyor | En büyük darboğaz |
| 5 | **Yazılıma uygun tedarik** | Donanım tedariki (yıllar) yazılım döngüsüne (haftalar) uymuyor | ABD'de reformlar [K30]; Avrupa ve Türkiye'de sınırlı |
| 6 | **Çoklu model ve egemen hesaplama** | Tek model sağlayıcı riski; gizli veri; yabancı hukuka tabi olmama | ABD'de 8 sağlayıcılı yaklaşım [K42]; Avrupa'da Mistral; Türkiye'de altyapı planı [K31] |
| 7 | **Kitle ve maliyet etkinliği** | Ucuz, harcanabilir sistemlerin yazılımla koordinasyonu | Fabrika yatırımları (Arsenal-1, Saronic, Castelion) |
| 8 | **Yetenek** | YZ mühendisliği + alan uzmanlığı + güvenlik izni kesişimi çok dar | Kronik açık; Thales'in 9.000 kişilik 2026 işe alım planı [K54] |
| 9 | **Hukuka uygunluğun koda girmesi** | IHL/ROE kısıtlarının algoritmaya gömülmesi ve denetlenebilir kayıt | Çoğunlukla prosedürel |
| 10 | **Sivil–askerî köprü** | Afet, kritik altyapı, siber savunmada aynı yetenek | Kurumsal ve hukuki ayrım nedeniyle düşük kullanım |

---

## 10. Sektörün Yapısal Sorunları

### 10.1 Tedarik "ölüm vadisi"
Prototipten kayıtlı programa geçiş yıllar sürüyor. Kurumsal anlaşmalar vadiyi büyük oyuncular için
kapatırken küçükler için derinleştiriyor [K9]. Sektör "çok sayıda girişim, az sayıda kazanan"
yapısına gidiyor.

### 10.2 Tedarikçi kilitlenmesi ve veri hakları
Ontoloji ve iş akışları bir platformda modellendiğinde anlamsal model taşınamıyor. Açık veri modeli,
API, kaynak kodu emaneti ve çıkış planı sözleşmeye girmeli (bkz. `analiz/tedarik_kontrol_listesi.md`).

### 10.3 Egemenlik ve ekstra-territoriyal hukuk
ABD şirketlerinin ABD hukukuna tabi olması müttefiklerde güven sorunu yaratıyor (İsviçre ordusu iç
değerlendirmesi [K16], Bundeswehr ve BfV kararları [K17]). Aynı mantık Avrupa ve İsrail
şirketlerinin ihracat kontrolleri için de geçerli.

### 10.4 Doğrulama açığı: Demo ≠ muharebe
Bloomberg'in Ocak 2026 haberine göre Ukrayna, test sorunları nedeniyle ek HX-2 siparişlerini durdurdu
(kalkış sorunları, eksik otonom bileşenler, Rus EH'si nedeniyle bağlantı kopması); Helsing haberin
doğrulanmamış bir iç belgeye dayandığını belirterek itiraz etti [K7]. Kök neden: bağımsız, EH dâhil,
standart test protokollerinin yokluğu.

### 10.5 Otomasyon önyargısı ve anlamlı insan kontrolü
Lavender/Gospel raporları yüksek beyan edilen doğruluk oranlarının çıktının "insan kararı gibi"
kabul edilmesine yol açtığını öne sürdü (iddialar anonim kaynaklara dayanıyor ve tartışmalı) [K22].
2026 İran harekâtında hedefleme hızının arttığı, insan onayının "inceldiği" eleştirileri ve sivil
kayıplar hesap verebilirlik tartışmasını büyüttü [K19]. İnceleme kalitesini ölçen metrikler
çoğunlukla tasarım gereksinimi değil.

### 10.6 Siber ve çekişmeli makine öğrenmesi
Veri zehirleme, sensör aldatma, dil modellerinde istem enjeksiyonu; NGC2 prototipi için ABD Ordusu
teknoloji direktörünün "kalıcı tespit edilemez erişim" uyarısı [K9].

### 10.7 Model sağlayıcı–devlet çatışması
Mart 2026'da ABD Savunma Bakanlığı Anthropic'i "tedarik zinciri riski" ilan etti; anlaşmazlık, şirketin
kitlesel yurt içi gözetim ve tam otonom silahlara koyduğu sınırlar ile Bakanlığın "tüm yasal kullanım"
talebi arasında çıktı [K23]. Mayıs 2026'daki gizli ağ anlaşmaları Anthropic'i dışarıda bıraktı [K42].
**Sektörel anlam:** (i) kullanım politikaları tedarik zincirinin parçası; (ii) model bağımsız mimari
zorunlu hâle geliyor; (iii) "kimin kırmızı çizgisi geçerli" sorusu çözülmedi.

### 10.8 Sermaye–gelir uçurumu
Anduril ~28x tahmini gelir [K12], Shield AI ~23x ileri gelir [K20], Swarmer'ın halka arz ilk gününde
%520 artışına karşın 1Ç 2026 geliri ~20 bin $ [K57]. Tavan ≠ yükümlülük. Barış, bütçe kesintisi
veya siyasi değişim sert düzeltme getirebilir; konsolidasyon dalgası bunun erken işareti [K41].

### 10.9 Düzenleme boşluğu
AB YZ Yasası Md. 2(3) yalnızca askerî amaçlı sistemleri kapsam dışı bırakıyor; aynı yazılım bir
bakanlıkta muaf, bir hastanede düzenlenmiş olabiliyor [K24].

### 10.10 Yetenek ve çalışan direnci
2018 Google–Maven protestosundan bu yana büyük teknoloji şirketleri politikalarını gevşetti; etik
kaygılar işe alımda hâlâ etkili.

---

## 11. Düzenleyici ve Yönetişim Çerçevesi

| Çerçeve | Tür | Durum (Ekim 2026) |
|---|---|---|
| **ABD DoDD 3000.09** (Ocak 2023) | Ulusal direktif | Silah sistemlerinde otonomi için üst düzey inceleme; "uygun düzeyde insan muhakemesi" [K32] |
| **ABD Siyasi Deklarasyonu** (2023) | Gönüllü | Sorumlu askerî YZ ilkeleri |
| **REAIM 2026 A Coruña** (Şubat 2026) | Gönüllü | ~40 devlet onayladı; ABD ve Çin onaylamadı [K33] |
| **BM CCW GGE LAWS** | Müzakere | 5 Eylül 2026'da uzlaşı raporu; 70+ devlet müzakereye hazır; **Gözden Geçirme Konferansı 16–20 Kasım 2026** [K34] |
| **BM Genel Kurulu** (Aralık 2025) | Karar | 156 devlet destekledi [K34] |
| **AB YZ Yasası** (2024/1689) | Bağlayıcı | Md. 2(3) askerî istisna [K24][K35] |
| **AB Çift Kullanım Tüzüğü** (2021/821) | Bağlayıcı | İhracat kontrolleri [K27] |
| **NATO YZ Stratejisi** (2021, 2024 revizyonu) | İttifak | Sorumlu kullanım ilkeleri; DIANA ve NIF ile finansman [K49] |
| **Türkiye** | Ulusal | 2026–2030 YZ Eylem Planı (altyapı odaklı) [K31]; askerî YZ'ye özgü kamuya açık insan kontrolü direktifi bulunamadı |

**Eğilim [Analist yargısı]:** Gönüllü normlar parçalanıyor; bu boşlukta satıcı kullanım politikaları
ve alıcı şartnameleri fiilî düzenleyici hâline geliyor.

---

## 12. Türkiye İçin Çıkarımlar ve Öneriler

### 12.1 Türkiye sektör haritasının neresinde?

| Grup | Türk oyuncular | Durum |
|---|---|---|
| G1 Hesaplama/model | — (kamu YZ platformu, TÜBİTAK çağrıları) | Erken aşama; SSB YZ platformu ve 2026–2030 eylem planı [K31] |
| G2 Veri/karar platformu | HAVELSAN (ADVENT-AI, MAIN) | Program bazlı; yatay, çok kurumlu bir platform yok |
| G3 Otonomi yazılımı | Baykar, STM, ASELSAN içinde | Bağımsız otonomi yazılımı şirketi kamuya açık veride görünmüyor |
| G4 Neo-prime | Baykar (fiilen yazılım hızında çalışan platform üreticisi) | Güçlü; SİVRİSİNEK, MIZRAK ve SAHA 2026'daki 6 yeni otonom sistem [K50] |
| G5 Ana yükleniciler | ASELSAN, TUSAŞ, Roketsan, HAVELSAN, STM | Güçlü; YZ ortaklık ve merkez yatırımları |
| G6 Entegratörler | Yüklenicilerin içinde | Ayrı pazar yok |
| G7 Devlet ekosistemi | SSB, SAVTEK, TÜBİTAK | Hibe ve program odaklı; Ukrayna/Hindistan tarzı açık modül pazarı yok |

### 12.2 SWOT

| Güçlü | Zayıf |
|---|---|
| Muharebede kanıtlanmış İHA/SİHA ve dolanan mühimmat | Yatay veri/ontoloji katmanında ölçekli yerli ürün yok |
| Güçlü yükleniciler ve C2/CMS deneyimi | Savunma girişim sermayesi ve açık veri sınırlı |
| NATO üyeliği | Tedarik modeli donanım odaklı |
| İhracat pazarlarında kabul görmüş platformlar | Egemen hesaplama ve savunma için büyük model altyapısı erken aşamada |

| Fırsat | Tehdit |
|---|---|
| ABD dışı yatay platform boşluğu (7.3) | ABD/Avrupa platformlarının NATO'da fiilî standart olması |
| Mevcut İHA'ların üzerine yazılım/otonomi katmanı | GPU ve modelde dış bağımlılık |
| Afet, sınır, enerjide çift kullanım | Yetenek göçü |
| Körfez ve Asya'daki büyüyen talep (EDGE, Kore örnekleri) | Sıkılaşan uluslararası normların ihracatı etkilemesi |

### 12.3 Öneriler

1. **Ulusal savunma veri standardı:** Tek tedarikçiye değil, NATO standartlarıyla uyumlu açık bir
   ontoloji/veri modeline yatırım; tüm yükleniciler için zorunlu. DELTA'nın açık modül yaklaşımı örnek.
2. **Yazılıma özgü tedarik yolu:** 90 günlük prototip → sürekli tedarik; yazılımın donanım
   programlarından ayrı bütçelenmesi.
3. **Bağımsız TEVV merkezi:** EH dâhil standart test protokolleri ve paylaşılan sonuçlar.
4. **Çoklu model mimarisi:** ABD'nin 8 sağlayıcılı yaklaşımı gibi, model katmanında değiştirilebilirlik;
   yerli ve açık modellerle ikame.
5. **Ölçülebilir insan kontrolü:** İnceleme süresi, ret oranı, belirsizlik gösterimi, denetim kaydı
   şartnameye girsin; normlar sıkılaşırsa ihracatı da korur.
6. **Çift kullanım programı:** AFAD, enerji ve kritik altyapı için aynı karar destek çekirdeğinin
   sivil sürümü; `PassiveDefenseOptimizer` gibi fizik tabanlı araçların kritik altyapı korumasına uyarlanması.
7. **Girişimlere ilk müşteri garantisi ve şeffaf veri:** 6–12 aylık küçük, hızlı sözleşmeler;
   NATO DIANA ve NIF ile eşleştirme; savunma girişim yatırımlarının yıllık raporlanması (bugün bu
   veri kamuya açık değil).
8. **Egemen hesaplama:** YZ Eylem Planı'ndaki veri merkezi hedeflerinin bir kısmı akredite,
   sınıflandırılmış iş yüküne uygun kapasite olarak planlansın.
9. **Ortaklık stratejisi:** Saab–Helsing, Hensoldt–Helsing, LIG Nex1–Palantir örneklerindeki gibi,
   Türk yüklenicilerin yerli veya müttefik yazılım şirketleriyle hisse + sözleşme bazlı ortaklıklar kurması.

---

## 13. 2027–2030 Senaryoları ve Göstergeler

| Senaryo | Açıklama | Olasılık [Analist yargısı] | Kazananlar |
|---|---|---|---|
| **S1 — Platform konsolidasyonu** | ABD platformları NATO'da fiilî standart; Avrupa tamamlayıcı | Orta-yüksek | Palantir, Anduril, ABD model sağlayıcıları |
| **S2 — Egemen bloklaşma** | Avrupa kendi yatay platformunu kurar; NATO'da çok platformlu birlikte çalışma | Orta | Thales, Helsing, ChapsVision, Hensoldt, Mistral |
| **S3 — Melez yükleniciler** | Ana yükleniciler neo-prime'larla birleşir veya onları satın alır | Orta-yüksek | Thales, Saab, Rheinmetall, Lockheed, RTX + seçili girişimler |
| **S4 — Normatif sıkılaşma** | CCW'den bağlayıcı belge müzakeresi | Düşük-orta | Açıklanabilirlik ve test gücü olanlar |
| **S5 — Değerleme düzeltmesi** | Ateşkes veya bütçe kesintisi; tavanlar harcamaya dönüşmez | Orta | Nakit üretenler, satın alma yapan büyük oyuncular |

| Gösterge | Neden | Tarih |
|---|---|---|
| Palantir 3Ç 2026 ABD kamu geliri | Kurumsal anlaşmaların harcamaya dönüşümü | 2 Kasım 2026 |
| CCW Gözden Geçirme Konferansı kararı | Bağlayıcı düzenleme olasılığı | 16–20 Kasım 2026 |
| Bundeswehr bulut/YZ ihale sonucu | Avrupa egemen platform yönü | 2026 sonu |
| Thales HexaForce NATO sözleşmeleri | Ana yüklenicilerin karar katmanına girişi | Sürekli |
| Scale AI ajanlarının simüle muharebe testleri | Ajan tabanlı planlamanın olgunluğu | 2026–2027 |
| Anthropic–Bakanlık davası | Model sağlayıcı politikalarının bağlayıcılığı | Belirsiz |
| Neo-prime halka arzları (Anduril, Saronic vb.) | Sermaye döngüsünün sürdürülebilirliği | Belirsiz |
| Savunma birleşme sayısı (2026 ikinci yarı) | Konsolidasyon hızı | 2027 başı |
| CA-1 Europa ilk uçuşu | Helsing'in hava alanında yürütmesi | 2027 hedefi |

---

## 14. Kaynakça

> Bazı kaynaklar ikincil/agregatör niteliğindedir; ilgili iddialar metinde "[Raporlanan]" olarak
> işaretlidir. Kritik kullanımlardan önce birincil kaynak doğrulaması önerilir.

- **[K1]** Palantir 2Ç 2026 ve Maven — [Webull](https://www.webull.com/news/15497722791912448); [YCharts](https://ycharts.com/indicators/palantir_technologies_pltr_us_government_revenue)
- **[K4]** NATO MSS ve Pentagon Maven — [Janes](https://www.janes.com/osint-insights/defence-news/security/natos-jfc-norfolk-to-receive-palantirs-maven-smart-system-by-end-of-may); [heise](https://heise.de/-11220659); [AFCEA Signal](https://www.afcea.org/signal-media/emerging-edge/nato-task-force-maven-good-thing-says-program-director); [ISS Tracker](https://isstracker.pl/en/news/pentagon-poszukuje-23-miliarda-dolarow-na-system-pola-bitwy-maven-ai,x4x5P)
- **[K6]** Helsing Seri E — [Euro-SD](https://euro-sd.com/2026/07/news/cyber-coms/52272/helsing-raises-us1-8bn-in-series-e/); [DroneXL](https://dronexl.co/2026/05/09/helsing-18-billion-valuation/); [Trending Topics](https://www.trendingtopics.eu/helsing-raises-1-8-billion-in-series-e-round-valuation-climbs-to-18-billion/)
- **[K7]** HX-2 Ukrayna tartışması — [Ukrainska Pravda](https://www.pravda.com.ua/eng/news/2026/01/19/8016866); [The Defense Post](https://thedefensepost.com/2026/01/20/ukraine-pause-helsing-hx2); [Jerusalem Post](https://www.jpost.com/defense-and-tech/article-886330)
- **[K8]** Helsing şirket bilgileri — [Wikipedia](https://en.wikipedia.org/wiki/Helsing_(company)); [Techleap](https://finder.techleap.nl/news/feed/helsing-acquires-grob-aircraft-for-innovation); [SVIC (düşük güven)](https://siliconvalleyinvestclub.com/companies/helsing/tear-sheet.pdf)
- **[K9]** ABD Ordusu–Palantir anlaşması, NGC2 — [DefenseScoop](https://defensescoop.com/2025/07/31/army-palantir-software-enterprise-agreement-10-billion/embed/); [The Register](https://www.theregister.com/2025/08/01/palantir_us_army_contract/); [Benzinga](https://benzinga.com/trading-ideas/movers/25/10/48018068/palantir-and-anduril-under-fire-over-armys-high-risk-battlefield-tech)
- **[K11]** Finansman — [Defense News](https://www.defensenews.com/industry/2026/01/20/defense-tech-startups-had-their-best-funding-year-ever-in-2025/); [PitchBook](https://files.pitchbook.com/website/files/pdf/2025_Vertical_Snapshot_Defense_Tech_Preview.pdf); [City AM](https://www.cityam.com/?p=2398698)
- **[K12]** Anduril değerleme — [Barchart](https://www.barchart.com/story/news/2399792/anduril-s-61b-valuation-signals-a-defense-industrial-reset-that-will-reshape-the-primes); [Multiples.vc](https://multiples.vc/private-comps/anduril)
- **[K13]** Anduril gelir, Fury, Ordu anlaşması — [Sacra](https://sacra.com/research/anduril); [Robotics Press](https://robotics.press/news/anduril-deep-dive/)
- **[K15]** Palantir 2025 ve İngiltere — [Panabee](https://www.panabee.com/news/palantir-earnings-2025-annual); [GOV.UK](https://www.gov.uk/government/news/new-strategic-partnership-to-unlock-billions-and-boost-military-ai-and-innovation)
- **[K16]** İsviçre ordusu — [Cybernews](https://cybernews.com/tech/swiss-army-palantir/); [Fair Observer](https://www.fairobserver.com/fofeatures/the-hat-in-the-square-palantir-republik-and-the-pattern-of-swiss-compliance/)
- **[K17]** Bundeswehr ve BfV — [Anadolu Ajansı](https://aa.com.tr/en/europe/german-army-excludes-us-tech-firm-palantir-from-cloud-project-over-data-security-concerns/3921703); [The Next Web](https://thenextweb.com/news/bundeswehr-30-ai-tools-prototype-2027-palantir-alternative)
- **[K18]** DELTA — [Ukrayna Savunma Bakanlığı](https://mod.gov.ua/en/news/the-delta-combat-system-records-more-than-6-600-enemy-targets-hit-every-day); [Wikipedia](https://en.wikipedia.org/wiki/Delta_(situational_awareness_system))
- **[K19]** İran harekâtında Maven — [Al-Monitor](https://www.al-monitor.com/originals/2026/04/ai-war-five-things-know-about-project-maven); [Dawn](https://www.dawn.com/news/1988898)
- **[K20]** Shield AI — [AI Business](https://aibusiness.com/generative-ai/us-military-ai-company-valued-12-7-billion); [The Next Web](https://thenextweb.com/news/shield-ai-2-billion-hivemind-autonomous-defence)
- **[K21]** Avrupa girişimleri — [Tech.eu – Quantum Systems](https://tech.eu/2026/07/02/quantum-systems-raises-12bn-at-8bn-valuation/); [Dealroom – Stark](https://dealroom.co/news/135688-stark-confirms-500m-late-stage-round-to-scale-european-defence-manufactu/); [funding.tech.eu](https://funding.tech.eu/sectors/defence/2026); [deeptech.build](https://www.deeptech.build/content/europes-defence-gold-rush)
- **[K22]** Lavender/Gospel — [+972 Magazine](https://www.972mag.com/lavender-ai-israeli-army-gaza/); [Wikipedia](https://en.wikipedia.org/wiki/AI-assisted_targeting_in_the_Gaza_Strip)
- **[K23]** Anthropic–ABD Savunma Bakanlığı — [TechCrunch](https://techcrunch.com/2026/03/05/its-official-the-pentagon-has-labeled-anthropic-a-supply-chain-risk/); [NPR](https://www.npr.org/g-s1-112713); [heise](https://heise.de/-11201896)
- **[K24]** AB YZ Yasası askerî istisnası — [McCann FitzGerald](https://www.mccannfitzgerald.com/knowledge/disputes/application-of-the-eu-ai-act-in-the-military-defence-and-national-security-sectors); [Finabel](https://finabel.org/wp-content/uploads/2026/01/RR-Clara-3.pdf); [Tech Policy Press](https://techpolicy.press/europes-ai-act-leaves-a-gap-for-military-ai-entering-civilian-life)
- **[K25]** Helsing Altra ve HX-2 — [Kyiv Independent](https://kyivindependent.com/german-company-to-manufacture-6-000-ai-powered-drones-for-ukraine/amp); [Defence Industry EU – ASGARD](https://defence-industry.eu/?p=57608)
- **[K26]** HAVELSAN / ASELSAN — [DonanımHaber](https://www.donanimhaber.com/havelsan-advent-e-yapay-zeka-geliyor--194861); [Ekonomist](https://www.ekonomist.com.tr/savunma-sanayi/simulasyondan-yapay-zekaya-havelsan-nilli-platformlari-dijitalle-donatiyor-71516); [Timeturk](https://www.timeturk.com/teknoloji/aselsan-dan-mavi-vatan-a-yapay-zeka-destegi-haber-1817249)
- **[K27]** AB Çift Kullanım Tüzüğü 2021/821 — [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2021/821/oj)
- **[K28]** Scale AI, Thunderforge, 500 milyon $ sözleşme — [Executive Gov](https://executivegov.com/2025/03/scale-ai-diu-thunderforge-contract/); [Scale AI](https://scale.com/blog/thunderforge-ai-for-american-defense); [Briefs](https://www.briefs.co/news/scale-ai-pentagon-500m/); [Bernama](https://bernama.com/en/news.php?id=2553821)
- **[K29]** PLA ve DeepSeek — [Jamestown](https://jamestown.org/program/deepseek-use-in-prc-military-and-public-security-systems/); [FDD](https://www.fdd.org/analysis/policy-briefs/chinas-military-reportedly-deploys-deepseek-ai-for-non-combat-duties/); [bdnews24 (Reuters)](https://bdnews24.com/world/8a36d98a5496)
- **[K30]** ABD yazılım tedarik reformu — [Military Times](https://www.militarytimes.com/pentagon/2025/03/07/hegseth-mandates-streamlined-software-acquisition-approach-in-new-memo/); [Defense One](https://www.defenseone.com/policy/2025/11/experts-see-promise-risk-pentagons-proposed-acquisition-reforms/409335)
- **[K31]** Türkiye SSB, YZ Eylem Planı, ASELSAN — [Türkgün](https://www.turkgun.com/gundem/turk-savunma-sanayiinin-2026-hedefleri/335309); [Bengütürk](https://www.benguturk.com/ekonomi/aselsan-ile-ssb-arasinda-yaklasik-470-milyon-dolarlik-imzalar-269706h); [Finansopia](https://www.finansopia.com/genel/gundem/cumhurbaskanligi-savunma-sanayii-baskanliginin-yapay-zeka-platformu-tanitildi/)
- **[K32]** DoD Directive 3000.09 — [ESD/WHS](https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodd/300009p.pdf)
- **[K33]** REAIM 2026 — [İspanya Dışişleri](https://exteriores.gob.es/en/REAIM2026/Paginas/default.aspx); [RSIS](https://rsis.edu.sg/rsis-publication/idss/ip26029-the-uncertain-future-of-the-reaim-summit/)
- **[K34]** CCW GGE LAWS — [Opinio Juris](https://opiniojuris.org/2026/10/05/symposium-on-the-ccw-gge-laws-the-end-of-the-beginning-an-introduction/); [Reaching Critical Will](https://reachingcriticalwill.org/disarmament-fora/ccw/2026/laws/reports/18145-ccw-report-vol-14-no-1)
- **[K35]** AB YZ Yasası 2024/1689 — [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- **[K40]** Askerî YZ pazar büyüklüğü — [Visiongain](https://visiongain.com/military-artificial-intelligence-ai-systems-market/); [Military Embedded Systems](https://militaryembedded.com/ai/machine-learning/military-ai-market-to-grow-to-45-billion-in-a-decade-study-predicts); [Persistence](https://www.persistencemarketresearch.com/market-research/ai-in-military-market.asp); [Next Move](https://www.nextmsc.com/report/ai-in-defense-market-ad6095); [Meticulous](https://www.meticulousresearch.com/product/ai-in-defense-and-aerospace-market-6379)
- **[K41]** Savunma birleşmeleri 2026 — [White & Case](https://mergers.whitecase.com/explorer/charticle/print/3698636); [Washington Technology](https://www.washingtontechnology.com/companies/2026/10/defense-tech-m-runs-hot-government-services-firms-work-past-doge-effect/416680/); [Dealroom – Chaos/Atropos](https://dealroom.co/news/141810-chaos-industries-buys-atropos-to-add-autonomous-aircraft-to-its-arsenal/); [Trending Topics](https://www.trendingtopics.eu/defence-ma-record-2026/)
- **[K42]** GenAI.mil ve gizli ağ YZ anlaşmaları — [Decrypt](https://decrypt.co/366351/pentagon-ai-deals-google-openai-nvidia-microsoft-amazon-spacex); [Executive Gov](https://www.executivegov.com/articles/war-department-ai-deals-oracle-openai-google-spacex); [NewsNation](https://www.newsnationnow.com/us-news/military/pentagon-deal-openai-google-nvidia-reflection-microsoft-aws-spacex-anthropic/amp/)
- **[K43]** Applied Intuition — [TechCrunch](https://techcrunch.com/?p=3019532)
- **[K44]** Safran–Preligens — [Defense News](https://www.defensenews.com/global/europe/2024/06/24/safran-in-talks-to-buy-french-ai-startup-preligens-for-220-million/); [Army Recognition](https://www.armyrecognition.com/archives/archives-land-defense/land-defense-2024/safran-completes-acquisition-of-ai-specialist-preligens)
- **[K45]** Helsing ortaklıkları (Saab, Hensoldt, Rheinmetall) — [Asia Pacific Defence Reporter](https://asiapacificdefencereporter.com/saab-signs-strategic-agreement-and-makes-investment-in-helsing/); [Defence Industry EU – Hensoldt](https://defence-industry.eu/?p=67693); [Shephard – Rheinmetall](https://www.shephardmedia.com/news/digital-battlespace/rheinmetall-joins-helsing-to-accelerate-ai-for-land-systems)
- **[K46]** ABD ana yüklenicileri ve Shield AI — [Washington Times](https://m.washingtontimes.com/news/2025/jul/3/shield-ai-rtx-team-bring-next-generation-ai-defense-platforms/); [Defence Connect](https://www.defenceconnect.com.au/joint-capabilities/16350-raytheon-shield-ai-partner-on-enhanced-mission-autonomy-systems); [Shephard – Lockheed/DARPA](https://www.shephardmedia.com/news/digital-battlespace/lockheed-martin-to-work-with-darpa-on-ai-effort)
- **[K47]** Kore — [Asia Economy – LIG Nex1 sürü İHA](https://www.asiae.co.kr/en/article/2026022509564640150); [Korea Times – ADEX 2025](https://www.koreatimes.co.kr/amp/southkorea/defense/20251021/koreas-defense-industry-showcases-ai-space-tech-at-adex-2025); [Defence Blog](https://defence-blog.com/?p=83569)
- **[K48]** Çin askerî YZ ekosistemi — [CSET – China's Military AI Wish List](https://cset.georgetown.edu/wp-content/uploads/CSET-Chinas-Military-AI-Wish-List.pdf); [CSET – Kentsel otonom savaş](https://cset.georgetown.edu/article/machines-in-the-alleyways-chinas-bet-on-autonomous-urban-warfare/); [OECD.AI – Jiu Tian](https://oecd.ai/en/incidents/2025-10-20-1d14); [DroneXL](https://dronexl.co/2025/10/28/china-military-deepseek-ai-drone-swarms-robot-dogs)
- **[K49]** NATO DIANA ve NIF — [NATO DIANA](https://www.diana.nato.int/connect/nato-diana-announces-largestever-cohort-150-innovators-selected-across-ten-challenge-areas-for-2026-challenge-programme.html); [Science Business](https://sciencebusiness.net/news/nato-launch-eu1b-fund-high-tech-start-ups-dual-use-technologies); [NIF – Tekever](https://www.nif.fund/news/nato-innovation-fund-backed-tekever-becomes-europes-newest-unicorn/)
- **[K50]** Türkiye otonom sistemler ve girişim ekosistemi — [Hürriyet Daily News – Baykar](https://hurriyetdailynews.com/turkiyes-baykar-unveils-next-generation-homegrown-drones-221444); [Webrazzi](https://webrazzi.com/2026/04/20/son-5-yil-icinde-en-cok-yatirim-alan-yapay-zeka-destekli-savunma-sirketleri/); [Türkgün – sürü İHA](https://www.turkgun.com/bilim-teknoloji/turkiyeden-suru-dron-hamlesi-yeni-nesil-savas-konsepti/376705)
- **[K51]** İsrail — [Jerusalem Post](https://www.jpost.com/defense-and-tech/article-879734); [CB Insights – XTEND](https://www.cbinsights.com/compare/elbit-systems-vs-xtend); [Baonghean (zayıf kaynak)](https://baonghean.vn/en/print/10344694.html)
- **[K52]** Ukrayna ekosistemi — [Kyiv Post – Swarmer](https://www.kyivpost.com/post/60321); [Censor.net – Brave1](https://censor.net/en/news/3575054/brave1-defense-tech-valley-2025-100m-pledged-for-ukrainian-defense-tech); [Defence Industry EU](https://defence-industry.eu/ukraines-swarmer-raises-15-million-series-a-largest-defence-tech-funding-since-start-of-the-war/)
- **[K53]** Hindistan iDEX — [Angel One](https://www.angelone.in/news/market-updates/3-853-crore-defence-prototypes-cleared-as-idex-ecosystem-expands); [Analytics India Magazine](https://analyticsindiamag.com/defence-ministry-to-fund-startups-working-on-ai-big-data-analytics/); [Entrepreneur India](https://india.entrepreneur.com/?p=85426)
- **[K54]** Avrupa ana yüklenicileri ve YZ — [ICDS – Neo-primes (Ekim 2026)](https://icds.ee/static/icds-brief_eu-defence-series-no-7_neoprimes_thomson_october-2026.pdf); [SDA – Thales röportajı](https://english.sdarabia.com/eurosatory-2026-sda-exclusive-interview-with-thales-building-europes-next-generation-of-integrated-air-defense-and-battlefield-superiority/); [ZeroG Talent – Thales işe alım](https://zerogtalent.com/blog/thales-group-s-9-000-person-2026-hiring-blitz-reveals-a-defense-skills-gap-in-ai-cyber-and-space-software-and-france-is-ground-zero); [Robotics Press – Thales](https://www.robotics.press/companies/thales-sa/)
- **[K55]** OpenAI ve entegratörler — [Executive Gov](https://www.executivegov.com/articles/war-department-ai-deals-oracle-openai-google-spacex)
- **[K56]** Vannevar Labs — [Wikipedia](https://en.wikipedia.org/wiki/Vannevar_Labs); [Gunderson](https://www.gunder.com/en/news-insights/client-news/defense-technology-vannevar-labs-announces-75m-series-b-financing)
- **[K57]** Swarmer halka arzı — [Business Wire](https://www.businesswire.com/news/home/20260316719643/en/); [IPO Scoop](https://www.iposcoop.com/ipo/swarmer-inc/); [Kyiv Independent](https://kyivindependent.com/ukrainian-defense-tech-finally-makes-its-way-to-u-s-markets)
- **[K58]** Saronic — [SiliconANGLE](https://siliconangle.com/?p=736972); [Pulse](https://www.pulse.bot/transportation/news/saronic-raises-175b-at-925b-valuation-to-gear-up-autonomous-ship-production-4965a5a1-b593-4636-a783-4eb40ab6d721)
- **[K59]** Castelion, Chaos Industries, Epirus — [Orrick – Castelion](https://www.orrick.com/en/News/2026/08/Castelion-Raises-1B-Series-C-to-Scale-Production-of-Low-Cost-Hypersonic-Weapons); [LA Business Journal – Chaos](https://labusinessjournal.com/featured/chaos-industries-reaches-nearly-5-billion-valuation/); [DroneXL – Chaos](https://dronexl.co/2025/11/13/counter-drone-radar-firm-chaos-industries-raises-510m); [Built In LA – Epirus](https://www.builtinla.com/articles/epirus-raises-250m-series-d-20250307)
- **[K60]** Tekever — [Tech.eu](https://tech.eu/2025/05/06/tekever-becomes-the-latest-unicorn-in-europes-defencetech-industry/); [ECO News](https://econews.pt/2026/08/14/tekever-seeks-e500m-in-funding-at-e5-5bn-valuation/); [Sifted](https://sifted.eu/articles/defence-unicorn-tekever)
- **[K61]** Körfez — [Gulf News – EDGE/SIRBAI](https://gulfnews.com/uae/sirbai-edge-team-up-to-boost-ai-powered-drone-swarm-capabilities-1.500418483); [Aranca – Rearming the Gulf](https://www.aranca.com/knowledge-library/special-reports/investment-research/gulf-defense-market-outlook); [Verdantix](https://research.verdantix.com/vantage/blog/iran-war-challenges-gulf-ambitions-to-embed-ai-in-operations--ehs-and-esg)
- **[K62]** ABD entegratörleri — [Booz Allen 10-K FY2026 (SEC)](https://www.sec.gov/Archives/edgar/data/0001443646/000162828026037521/bah-20260331.htm); [Booz Allen – YZ hizmetleri](https://www.boozallen.com/insights/ai/booz-allen-ranks-first-in-artificial-intelligence-services.html); [Motley Fool](https://www.fool.com/investing/2025/05/27/this-key-palantir-partner-was-a-victim-of-doge-cut)

---

## 15. Ek: Sözlük

| Terim | Açıklama |
|---|---|
| **ATO** | Bir yazılımın askerî/gizli ağda çalışma yetkisi; akreditasyon |
| **C2 / NGC2** | Komuta-kontrol / ABD Ordusu Yeni Nesil Komuta Kontrol programı |
| **CCA** | İşbirlikçi Savaş Uçağı — insanlı uçakla birlikte çalışan otonom İHA |
| **COA / COP** | Hareket tarzı / Ortak operasyon resmi |
| **DDIL** | Kesintili, bağlantısız, kısıtlı bant genişlikli ortam |
| **EH (EW)** | Elektronik harp |
| **FDE** | İleri konuşlu mühendis — Palantir'in saha mühendisliği modeli |
| **GenAI.mil** | ABD Savunma Bakanlığı'nın kurumsal üretken YZ platformu (Aralık 2025) |
| **IL6 / IL7** | ABD Savunma Bakanlığı bulut etki seviyeleri; gizli ve üzeri sınıflandırma |
| **Kayıtlı program** | Çok yıllı bütçe satırı olan kalıcı tedarik programı |
| **Kurumsal anlaşma** | Çok sayıda sözleşmeyi tek çerçevede birleştiren, tavan değerli uzun vadeli anlaşma |
| **Neo-prime** | Yazılım öncelikli, kendi donanımını üreten yeni nesil ana yüklenici |
| **Ontoloji** | Verinin nesne, ilişki ve eylemler olarak anlamsal modeli |
| **OTA / CSO / SWP / PAE** | ABD hızlı tedarik araçları ve portföy tedarik yöneticileri |
| **TEVV** | Test, değerlendirme, doğrulama ve geçerleme |
| **WTA** | Silah-hedef atama problemi |
| **YBBO** | Yıllık bileşik büyüme oranı |
