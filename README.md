# Türk-İslam Dünyası Kişiler ve Eserler Atlası

750–1700 yılları arasında Türk devletlerinde yaşamış, onların himayesinde çalışmış ya da Türk-İslam kültürünü doğrudan etkilemiş **112 kişi**, **174 eser** ve **106 ilişki**. Akademik ilgiye yönelik hazırlanmıştır. Üç görünüm var: harita, zaman çizelgesi ve ilişki ağı. Her kaydın kaynağı ve teyit durumu görünür. Arayüz ve içerik Türkçedir.

## Nasıl açılır

`index.html` dosyasına çift tıklamanız yeterli. Veri, stil ve uygulama kodu dosyanın içine gömülüdür; sunucu gerekmez (`file://` altında `fetch` çalışmadığı için böyle tasarlandı).

- **Harita** (Leaflet 1.9.4) ve **ilişki ağı** (vis-network 9.1.9) kütüphaneleri CDN'den yüklenir, bu yüzden internet bağlantısı ister.
- **Zaman çizelgesi**, **sınav kartları**, **arama** ve **detay paneli** çevrimdışı da çalışır.
- Harita altlığı (Natural Earth kıyı çizgileri) dosyaya gömülüdür. İsterseniz "İnternet altlığı" kutusuyla CARTO/OSM karolarını açabilirsiniz.

### Site olarak yayınlama

```bash
python3 scripts/build.py --artifact site.html
```

Bu komut, claude.ai Artifact olarak yayınlanabilecek bir sürüm üretir. Bu sürümde Leaflet stili sayfaya gömülüdür, çünkü platform harici stil dosyasına izin vermiyor. Aynı nedenle harita karoları da engelli olduğundan "İnternet altlığı" seçeneği bu sürümde yoktur. Depodaki `index.html` ise olduğu gibi herhangi bir statik barındırmaya (örneğin GitHub Pages) konabilir.

## Görünümler

| Sekme | Ne gösterir |
|---|---|
| Harita | Şehirlerde, orada bulunmuş kişi sayısına göre büyüyen işaretler. Bir kişi seçilince hayat güzergâhı numaralı duraklarla çizilir. Alttaki yıl kaydırıcısı o yılda hayatta olanları gösterir; **Oynat** zamanı 5'er yıl ilerletir. |
| Zaman çizelgesi | Devlet gruplarına ayrılmış ömür çubukları. Arka plandaki renkli bantlar devlet dönemlerini, ◆ işaretleri eserleri gösterir. Kesikli çubuk, tarihin yaklaşık ya da tartışmalı olduğu anlamına gelir. |
| İlişki ağı | Kişi (daire) ve eser (elmas) düğümleri. Kenar türleri renklidir ve göstergede açıklanır. Bir düğüme tıklayınca komşuları vurgulanır. |
| Sınav kartları | Yalnızca `yks_modu: true` iken görünür (aşağıya bakın). Çevrilebilir eser kartları, sık karıştırılan 15 çift ve kısa test. |

Ortak özellikler:

- **Filtreler:** alan, devlet, dil, yüzyıl (YKS modunda ayrıca YKS önemi).
- **Arama:** aksanlı da aksansız da çalışır. Örneğin `divanu lugat`, `Dîvânu Lugâti't-Türk` ve `Divanü Lügati't-Türk` kaydını bulur; lakapla arama da olur (`muallim-i sani` yazınca Farabi çıkar).
- **Detay paneli:** tarih kesinliği ve tartışmalı köken rozetleri, kaynak bağlantıları ve kaynakla teyit edilmemiş alanlar görünür. "Haritada / zaman çizelgesinde / ağda göster" düğmeleriyle görünümler arasında geçebilirsiniz.
- **Tema:** açık/koyu tema düğmesi üç durum arasında döner: otomatik, açık, koyu.
- **Derin bağlantı:** adres çubuğuna `#harita/kisi/farabi` ya da `#ag/eser/kutadgu-bilig` gibi adresler yazılabilir.

## Klasör yapısı

```
data/
  people.json       kişiler
  works.json        eserler
  relations.json    ilişkiler
  meta.json         devlet dönemleri, gruplama, karıştırılan çiftler, parametreler
  basemap.geojson   çevrimdışı kıyı çizgisi (Natural Earth 1:50m, kırpılmış)
scripts/
  validate.py       veri doğrulama → reports/validation.md
  build.py          index.html üretir
  make_basemap.py   basemap.geojson'u yeniden üretir (normalde gerekmez)
  network_pdf.py    ilişki ağı PDF'i → reports/iliski-agi.pdf
src/                template.html, style.css, app.js
tests/smoke.mjs     Playwright duman testi
reports/validation.md, reports/iliski-agi.pdf
index.html          derlenmiş çıktı (bunu açın)
```

## Çalıştırma

```bash
python3 scripts/validate.py   # hata varsa çıkış kodu 1; rapor: reports/validation.md
python3 scripts/build.py      # index.html'i yeniden üretir
node tests/smoke.mjs shots/   # Playwright testi (isteğe bağlı ekran görüntüsü klasörü)
python3 scripts/network_pdf.py   # ilişki ağı PDF'i → reports/iliski-agi.pdf
```

`reports/iliski-agi.pdf` ilişki ağının basılabilir, tam dökümüdür (26 sayfa, vektörel şekiller, yer imleri). İçeriği:
- Kronolojik ağ (A3) ve kişi-eser tam ağı (A2)
- Her ilişki türü için ayrı katmanlı ağ
- 106 ilişkinin notları ve teyit durumuyla tam listesi
- Kişi bazında bağlantı dizini
- Merkezîlik ölçüleri ve bağlı bileşenler
- Yazar–eser listesi

Üretmek için `pip install networkx scipy matplotlib reportlab pypdf` gerekir.

Test, sayfayı Chromium'da açar. Dört görünümü, aramayı, filtreyi, testi ve 390 px genişlikte yatay kaydırma olmadığını kontrol eder; konsolda hata olmamalıdır. CDN'e erişimi olmayan bir ortamda, aynı kütüphane sürümleri yerel bir klasörden sunulabilir:

```bash
npm i leaflet@1.9.4 vis-network@9.1.9
ATLAS_LIB_DIR=$PWD/node_modules node tests/smoke.mjs
```

## Veri nasıl genişletilir

Veri doğrudan `data/*.json` dosyalarında tutulur. Bir kayıt ekledikten sonra önce `validate.py`, ardından `build.py` çalıştırın.

### Yeni kişi

`data/people.json` dizisine eklenir:

```json
{
  "id": "lamii-celebi",
  "ad": "Lamii Çelebi",
  "ad_akademik": "Lâmiî Çelebi",
  "tam_ad": "Mahmûd b. Osmân b. Ali en-Nakkāş",
  "lakap": null,
  "dogum": 1472,
  "olum": 1532,
  "tarih_kesinligi": "kesin",
  "tarih_notu": "Kaynaktaki tarih ifadesini buraya yazın.",
  "koken": "Türk (Bursalı).",
  "koken_tartismali": false,
  "devletler": ["Osmanlı"],
  "hami": ["Yavuz Sultan Selim"],
  "alanlar": ["edebiyat", "tasavvuf"],
  "duraklar": [
    {"sehir": "Bursa", "enlem": 40.19, "boylam": 29.06, "yil_baslangic": 1472, "yil_bitis": 1532, "ne_yapti": "Doğdu, yaşadı, eserlerini yazdı."}
  ],
  "ozet": "2–3 cümlelik özet, kendi cümlelerinizle.",
  "katkilar": ["Kısa madde 1", "Kısa madde 2"],
  "yks_onemi": "düşük",
  "kaynaklar": [{"ad": "TDV İslâm Ansiklopedisi – Lâmiî Çelebi", "url": "https://islamansiklopedisi.org.tr/lamii-celebi"}],
  "teyitsiz_alanlar": ["hami"],
  "dogrulanamadi": false
}
```

Kurallar:

- `dogum` ve `olum` bir tam sayı (`1037`), yaklaşık değer (`"~980"`) ya da `null` olabilir. `tarih_kesinligi` değeri `kesin`, `yaklaşık` veya `tartışmalı` olmalı.
- `devletler` listesindeki **ilk** devlet, kişinin zaman çizelgesinde hangi gruba yerleşeceğini belirler. Gruplar ve eşlemeler `meta.json` → `grup_eslemesi` içinde tanımlıdır.
- Koordinatlar enlem 0–50, boylam -10–80 aralığında olmalı. Bilerek dışarıda kalan bir durak (örneğin İtil Bulgar) `"bolge_disi": true` ile işaretlenir.
- Kaynakta görmediğiniz, genel bilgiye dayanan alanları `teyitsiz_alanlar` listesine yazın; validate bunları raporlar. Bir bilgiyi hiç doğrulayamadıysanız `"dogrulanamadi": true` yapın.

### Yeni eser

`data/works.json` dizisine eklenir. `yazar_id` mevcut bir kişinin kimliği olmalıdır; yazarı bilinmeyen eserlerde `null` ve `"anonim": true` kullanılır. `yil` alanı `1069`, `"1069-1070"`, `"~1100"` ya da `null` olabilir. Eser yazarın ölümünden sonra başkası tarafından tamamlandıysa `"olum_sonrasi_tamamlandi": true` ekleyin.

### Yeni ilişki

`data/relations.json` dizisine eklenir:

```json
{"kaynak": "kadizade-rumi", "hedef": "ali-kuscu", "tur": "hoca-öğrenci", "not": "isteğe bağlı açıklama"}
```

`tur` şunlardan biri olmalı: `hoca-öğrenci`, `himaye`, `etkiledi`, `çağdaş-tartışma`, `tercüme etti`, `şerh yazdı`. Uçlar kişi de olabilir, eser de. Hoca-öğrenci ilişkisinde validate, iki kişinin ömürlerinin çakışıp çakışmadığını kontrol eder.

### Parametreler

`meta.json` içinde tanımlıdır:

- `zaman_araligi`: zaman çizelgesi ve yıl kaydırıcısının sınırları (varsayılan 750–1700).
- `yks_modu`: varsayılan `false`. Bu durumda atlas akademik kullanım içindir: YKS vurguları, rozetleri, "YKS önemi" filtresi ve Sınav sekmesi gösterilmez. `true` yapılırsa sınav hazırlığı araçları (çevrilebilir kartlar, karıştırılan çiftler, kısa test) geri gelir. Kayıtlardaki `yks_onemi` alanı veride korunur.
- `karistirilanlar`: karıştırılan eser çiftleri ve aralarındaki ayırt edici nokta.

## Doğrulama yaklaşımı ve bilinen belirsizlikler

- **Kaynak erişimi:** Bu veri hazırlanırken TDV İslâm Ansiklopedisi sitesine doğrudan erişilemedi. Her kayıttaki TDV URL'si ile temel tarih ve olgular, web aramasının döndürdüğü TDV madde özetlerinden teyit edildi. Özetlerde görülmeyen alanlar kayıtlarda `teyitsiz_alanlar` olarak işaretlidir. Bu alanların çoğu duraklar, bazı doğum yılları ve bazı eserlerin yazıldığı yerdir; dökümü `reports/validation.md` içindedir. Bir sonraki adım, bu alanları madde metinleriyle tek tek karşılaştırmaktır.
- **Ayrı TDV maddesi bulunamayan kişi:** Mercimek Ahmed. Bilgileri Keykâvus b. İskender maddesinden alındı.
- **`dogrulanamadi` işaretli kayıtlar:** Cevâhirü'n-nahv (kayıp eser), Hacı Bektaş'ın Makālât'ı (aslı kayıp, aidiyeti tartışmalı), Matrakçı'nın Umdetü'l-hisâb'ı (tarih ve sunuluş teyit edilemedi) ve dört ilişki. Bunlar arayüzde uyarı rozetiyle, ağda kesikli kenarla gösterilir.
- **Tartışmalı tarihler:**
  - Kadızâde-i Rûmî'nin ölümü: bazı ansiklopedilerde 1412 geçer, ancak TDV 1440'tan sonrayı verir.
  - Ömer Hayyâm: TDV doğumu 1039–1048, ölümü 1123–1132 aralığında verir.
  - Evliya Çelebi'nin ölümü: 1682 mi 1684 mü olduğu tartışmalıdır.
  - Molla Fenârî'nin ölümü: 1431, bir görüşe göre 1434-35.
  - Nesîmî'nin ölümü: 1404 ile 1433 arasında çeşitli tarihler önerilir.
  - Takıyyüddin'in rasathanesinin kuruluşu: kaynaklarda 1575 ve 1577 olarak iki tarih geçer.
  - Atebetü'l-hakāyık'ın yazıldığı yüzyıl: XII. mi XIII. mü olduğu tartışmalıdır.
- **Tartışmalı kökenler** nötr biçimde, görüşleriyle birlikte yazıldı: Fârâbî, İbn Sînâ, Mevlânâ, Mimar Sinan, Fergānî, Mâtürîdî, Nizâmî ve Ahî Evran'ın kimliği.
- **Yazım:** Eser adları iki biçimde tutulur. `ad` alanı akademik yazımı (Dîvânu Lugâti't-Türk), `ad_sade` alanı sadeleştirilmiş yazımı (Divanü Lügati't-Türk) içerir. TDV maddesi "Atebetü'l-hakāyık" yazımını kullanır; yaygın kullanım "Atabetü'l-Hakayık"tır, arama ikisini de bulur.
- **Bilinçli yorumlar:**
  - Mimar Sinan'ın yapıları (Şehzade, Süleymaniye, Selimiye) eser olarak alındı ve dil alanına "Yok (mimari eser)" yazıldı.
  - Hükümdarlar himaye ilişkilerini gösterebilmek için kişi olarak eklendi.
  - Divanü Lügati't-Türk Bağdat'ta yazılıp Abbasi halifesinin oğluna sunulduğu hâlde yazarı Karahanlı çevresinden olduğu ve literatürde genellikle böyle sınıflandırıldığı için Karahanlı dönemi eseri sayıldı; durum eserin `devlet_notu` alanında açıklanır.
  - Yüzyıl filtresi 1001–1100 gibi geleneksel yüzyıl sınırlarını kullanır.
  - Tarihi bilinmeyen kişilerin çubukları eser ve durak yıllarından tahmin edilir ve "tahmini" rozetiyle gösterilir.
