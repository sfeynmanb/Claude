# Karar Destek Sistemi Tedarik / Geliştirme Kontrol Listesi

Bir çift kullanımlı karar destek sistemini satın alırken, ortak geliştirirken veya yerli bir ürünü
değerlendirirken sorulacak sorular. Ana rapordaki yapısal sorunlardan (Bölüm 8) türetilmiştir.
Her başlık, karşılık gelen sorunu parantez içinde gösterir.

## 1. Veri hakları ve çıkış planı (8.2 Kilitlenme)
- [ ] Veri modeli/ontoloji açık bir formatta (ör. OWL/RDF, JSON Schema) dışa aktarılabiliyor mu?
- [ ] İş akışları, kurallar ve model konfigürasyonları sözleşme bitiminde taşınabilir mi?
- [ ] Belgelenmiş, sürümlenmiş API'ler ve üçüncü taraf modül entegrasyon hakkı var mı?
- [ ] Kaynak kodu emaneti (escrow) ve tedarikçinin iflası/çekilmesi durumunda devam planı var mı?
- [ ] Kurumsal anlaşmalarda **asgari garanti** ile **tavan** ayrı ve açık mı?

## 2. Egemenlik ve hukuki maruziyet (8.3)
- [ ] Veriler hangi ülkede, kimin işlettiği altyapıda tutuluyor? Hava boşluklu kurulum mümkün mü?
- [ ] Tedarikçi hangi ülkelerin veri erişim taleplerine tabi? Bu talepler sözleşmede nasıl ele alınıyor?
- [ ] Tedarikçi personelinin ulusal veri kümelerine erişimi gerekiyor mu? (Bundeswehr örneği)
- [ ] İhracat kontrolü (ITAR, AB 2021/821, ulusal) güncelleme ve bakım sürekliliğini riske atıyor mu?

## 3. Bağımsız doğrulama (8.4 Demo ≠ muharebe)
- [ ] Performans beyanları bağımsız bir test kurumunca, **EH ve DDIL koşulları dâhil**, doğrulandı mı?
- [ ] Test protokolü, veri setleri ve başarı ölçütleri alıcıya açık mı?
- [ ] Saha performansı için sürekli telemetri ve olay raporlama yükümlülüğü var mı?
- [ ] Dağılım kayması (yeni coğrafya, mevsim, düşman taktiği) için yeniden doğrulama prosedürü var mı?

## 4. Anlamlı insan kontrolü (8.5 Otomasyon önyargısı)
- [ ] Sistemin hangi kararlarda öneri, hangi kararlarda eylem ürettiği açıkça tanımlı mı? (Bölüm 2.2 seviyeleri)
- [ ] Arayüz belirsizlik/güven düzeyini ve kanıt zincirini gösteriyor mu?
- [ ] İnceleme kalitesi ölçülüyor mu? (ortalama inceleme süresi, ret oranı, öneri başına operatör yükü)
- [ ] Her öneri ve onay için değiştirilemez denetim kaydı (audit log) tutuluyor mu?
- [ ] Hukuki kısıtlar (IHL, angajman kuralları) planlama/optimizasyon modeline kısıt olarak giriyor mu?

## 5. Güvenlik (8.6)
- [ ] Yazılım malzeme listesi (SBOM) ve tedarik zinciri güvenlik denetimi var mı?
- [ ] Çekişmeli makine öğrenmesi (aldatma, zehirleme) için kırmızı takım testleri yapıldı mı?
- [ ] LLM katmanında istem enjeksiyonuna karşı yalıtım (yetki sınırlı araçlar, girdi sanitizasyonu) var mı?
- [ ] Bağımsız sızma testi sonuçları paylaşılıyor mu? (NGC2 "çok yüksek risk" uyarısı dersi)

## 6. Model sağlayıcı bağımlılığı (8.7)
- [ ] Sistem tek bir temel model sağlayıcısına mı bağlı? Model değiştirildiğinde ne kadar süre/maliyet gerekir?
- [ ] Model sağlayıcısının kullanım politikası alıcının kullanım senaryolarıyla uyumlu ve sözleşmeye yansıtılmış mı?
- [ ] Yerli/açık ağırlıklı modellerle ikame testleri yapıldı mı?

## 7. Tedarik ve sürdürülebilirlik (8.1, 8.8)
- [ ] Yazılım güncelleme döngüsü ile akreditasyon döngüsü uyumlu mu? (sürekli ATO)
- [ ] Tedarikçinin finansal durumu ve gelir doğrulaması (özel şirketlerde) incelendi mi?
- [ ] Tek tedarikçi riskine karşı ikinci kaynak veya açık mimari şartı var mı?

## 8. Çift kullanım ve düzenleyici uyum (8.9)
- [ ] Sistemin sivil kullanımı (kolluk, sınır, afet) planlanıyorsa AB YZ Yasası/ulusal mevzuat kapsamına girip girmediği değerlendirildi mi?
- [ ] Askerîden sivile geçişte yüksek riskli sistem yükümlülükleri (veri yönetişimi, insan gözetimi, kayıt) karşılanıyor mu?
