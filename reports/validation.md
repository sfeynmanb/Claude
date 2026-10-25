# Doğrulama Raporu

_Oluşturma: 2026-10-25 · `python3 scripts/validate.py`_

## Özet

| | Sayı |
|---|---:|
| Kişi | 112 |
| Eser | 174 |
| İlişki | 106 |
| Karıştırılan çift | 15 |
| **Hata** | **0** |
| Uyarı | 0 |
| Not | 34 |
| Kaynaksız kayıt | 0 |
| `dogrulanamadi` işaretli kayıt | 7 |
| Kendi bilgimize dayanan alan içeren kayıt | 226 |

Kontroller: yazar kimlikleri, eser yılının yazarın ömrüyle uyumu (yaklaşık/tartışmalı tarihlerde ±15 yıl), ilişki kimlikleri ve türleri, hoca-öğrenci ömür çakışması, koordinatların bölge içinde olması (enlem 0–50, boylam -10–80), zorunlu alanlar, kaynak URL'leri, karıştırılan çiftler.

## Hatalar (0)

_Yok._

## Uyarılar (0)

_Yok._

## Notlar (34)

- `kişi:edip-ahmet-yukneki` — doğum ve ölüm yılları bilinmiyor
- `kişi:ibn-fadlan` — doğum ve ölüm yılları bilinmiyor
- `kişi:ibn-fadlan` — Bulgar (İtil) (54.98, 49.04) çalışma bölgesi dışında; bilerek 'bolge_disi' işaretli
- `kişi:mercimek-ahmed` — doğum ve ölüm yılları bilinmiyor
- `eser:hayyam-rubailer` — eser yılı belirtilmemiş
- `eser:fihi-ma-fih` — eser yılı belirtilmemiş
- `eser:makalat-haci-bektas` — eser yılı belirtilmemiş
- `eser:tusi-tecrid` — eser yılı belirtilmemiş
- `eser:maddetul-hayat` — eser yılı belirtilmemiş
- `eser:risaletun-nuriyye` — eser yılı belirtilmemiş
- `eser:fenari-isagoci` — eser yılı belirtilmemiş
- `eser:fuzuli-turkce-divan` — eser yılı belirtilmemiş
- `eser:kitabut-tevhid` — eser yılı belirtilmemiş
- `eser:tevilatul-kuran` — eser yılı belirtilmemiş
- `eser:razi-cuderi` — eser yılı belirtilmemiş
- `eser:razi-isarat-serhi` — eser yılı belirtilmemiş
- `eser:fevaihul-cemal` — eser yılı belirtilmemiş
- `eser:bakirgan-kitabi` — eser yılı belirtilmemiş
- `eser:tezkiretul-evliya` — eser yılı belirtilmemiş
- `eser:akaidun-nesefi` — eser yılı belirtilmemiş
- `eser:maarif-bahaeddin` — eser yılı belirtilmemiş
- `eser:miftahul-gayb` — eser yılı belirtilmemiş
- `eser:el-fukuk` — eser yılı belirtilmemiş
- `eser:nesimi-divan` — eser yılı belirtilmemiş
- `eser:muntahab-i-sifa` — eser yılı belirtilmemiş
- `eser:gayetul-emani` — eser yılı belirtilmemiş
- `eser:et-tarifat` — eser yılı belirtilmemiş
- `eser:huseyni-divan` — eser yılı belirtilmemiş
- `eser:maruzat` — eser yılı belirtilmemiş
- `eser:miftahus-saade` — eser yılı belirtilmemiş
- `eser:nefi-turkce-divan` — eser yılı belirtilmemiş
- `eser:muhibbi-divani` — eser yılı belirtilmemiş
- `eser:avni-divani` — eser yılı belirtilmemiş
- `eser:dede-korkut` — anonim eser (yazar_id yok)

## Kaynağı olmayan kayıtlar (0)

_Yok; her kayıtta en az bir kaynak URL'si var._

## `dogrulanamadi` işaretli kayıtlar (7)

Bu kayıtlar tutuldu ama dayandıkları bilgi kaynakla teyit edilemedi; arayüzde uyarı etiketiyle gösterilir.

- eser: `cevahirun-nahv`
- eser: `makalat-haci-bektas`
- eser: `umdetul-hisab`
- ilişki: `kasi→ali-kuscu (hoca-öğrenci)`
- ilişki: `ahmet-yesevi→haci-bektas-veli (etkiledi)`
- ilişki: `mevlana→sadreddin-konevi (çağdaş-tartışma)`
- ilişki: `ahi-evran→haci-bektas-veli (çağdaş-tartışma)`

## Kendi bilgimize dayanan, kaynakla teyit edilmemiş alanlar (226 kayıt)

TDV İslâm Ansiklopedisi sitesine bu ortamdan doğrudan erişilemedi. Her kayıttaki TDV URL'si ve temel tarihler web aramasıyla dönen TDV madde özetlerinden teyit edildi. Aşağıdaki alanlar ise bu özetlerde görülmedi; genel bilgiye dayanır ve TDV maddesinin tam metniyle karşılaştırılmalıdır.

Alan bazında: `yil` (97), `duraklar` (86), `dogum` (55), `sunuldugu_kisi` (25), `yazildigi_yer` (23), `hami` (18), `koken` (14), `olum` (9), `konu` (6), `dil` (5), `ilk_olma` (4), `devlet` (4), `onemi` (2), `kisi_tdv_maddesi` (1), `tam_ad` (1)

| Tür | Kimlik | Teyitsiz alanlar |
|---|---|---|
| kişi | `harezmi` | dogum |
| kişi | `farabi` | duraklar, hami |
| kişi | `ibn-sina` | duraklar |
| kişi | `biruni` | duraklar |
| kişi | `gazali` | duraklar |
| kişi | `omer-hayyam` | duraklar |
| kişi | `nizamulmulk` | duraklar |
| kişi | `kasgarli-mahmud` | dogum, olum, duraklar |
| kişi | `yusuf-has-hacib` | dogum |
| kişi | `edip-ahmet-yukneki` | hami |
| kişi | `ahmet-yesevi` | duraklar, koken |
| kişi | `mevlana` | duraklar |
| kişi | `yunus-emre` | duraklar |
| kişi | `ahi-evran` | duraklar |
| kişi | `nasiruddin-tusi` | dogum, duraklar, hami |
| kişi | `kadizade-rumi` | dogum, duraklar |
| kişi | `ulug-bey` | dogum |
| kişi | `ali-kuscu` | duraklar |
| kişi | `ali-sir-nevai` | dogum, duraklar |
| kişi | `aksemseddin` | duraklar, koken |
| kişi | `molla-fenari` | dogum, duraklar |
| kişi | `piri-reis` | dogum, duraklar |
| kişi | `matrakci-nasuh` | duraklar |
| kişi | `mimar-sinan` | duraklar |
| kişi | `takiyuddin` | duraklar |
| kişi | `katip-celebi` | dogum, duraklar |
| kişi | `evliya-celebi` | dogum, duraklar |
| kişi | `fuzuli` | dogum, duraklar, koken |
| kişi | `baki` | duraklar, hami |
| kişi | `kindi` | duraklar, hami |
| kişi | `fergani` | duraklar |
| kişi | `cahiz` | dogum, duraklar, koken |
| kişi | `maturidi` | duraklar |
| kişi | `buhari` | duraklar, koken |
| kişi | `ebubekir-razi` | dogum, duraklar |
| kişi | `ibnul-heysem` | dogum, duraklar, hami |
| kişi | `battani` | dogum |
| kişi | `firdevsi` | dogum, duraklar |
| kişi | `beyhaki` | dogum, duraklar |
| kişi | `cuveyni` | dogum, duraklar |
| kişi | `zemahseri` | dogum, duraklar |
| kişi | `fahreddin-razi` | dogum, duraklar, hami |
| kişi | `necmeddin-kubra` | duraklar |
| kişi | `hakim-ata` | duraklar |
| kişi | `attar` | dogum |
| kişi | `nizami-gencevi` | dogum, hami |
| kişi | `merginani` | dogum |
| kişi | `omer-nesefi` | duraklar |
| kişi | `bahaeddin-veled` | dogum, olum, duraklar, hami |
| kişi | `sems-tebrizi` | duraklar |
| kişi | `sultan-veled` | dogum, olum, duraklar |
| kişi | `sadreddin-konevi` | duraklar |
| kişi | `ibnul-arabi` | dogum, duraklar |
| kişi | `necmeddin-daye` | duraklar |
| kişi | `ibn-bibi` | duraklar, hami |
| kişi | `ata-melik-cuveyni` | dogum, duraklar |
| kişi | `residuddin` | dogum, olum, koken, duraklar |
| kişi | `kutbuddin-sirazi` | duraklar |
| kişi | `ebu-hayyan` | dogum, duraklar, koken |
| kişi | `ibn-haldun` | dogum, duraklar, koken |
| kişi | `ibn-battuta` | dogum, duraklar, hami |
| kişi | `sadi-sirazi` | dogum, olum, duraklar |
| kişi | `ibn-rusd` | dogum, duraklar, hami |
| kişi | `asik-pasa` | duraklar |
| kişi | `gulsehri` | olum, duraklar |
| kişi | `kadi-burhaneddin` | dogum, duraklar, koken |
| kişi | `nesimi` | duraklar |
| kişi | `ahmedi` | dogum, duraklar, hami |
| kişi | `seyhi` | duraklar |
| kişi | `haci-pasa` | koken |
| kişi | `suleyman-celebi` | dogum, hami |
| kişi | `mercimek-ahmed` | duraklar, kisi_tdv_maddesi |
| kişi | `asikpasazade` | duraklar, hami |
| kişi | `molla-husrev` | koken, duraklar |
| kişi | `molla-gurani` | dogum, koken, duraklar |
| kişi | `hocazade` | duraklar |
| kişi | `teftazani` | dogum, duraklar |
| kişi | `curcani` | dogum |
| kişi | `kasi` | dogum, duraklar |
| kişi | `babur` | duraklar |
| kişi | `mirim-celebi` | duraklar |
| kişi | `kemalpasazade` | dogum, duraklar |
| kişi | `ebussuud` | dogum, duraklar |
| kişi | `taskoprizade` | hami |
| kişi | `kinalizade` | dogum, duraklar |
| kişi | `mustafa-ali` | duraklar, hami |
| kişi | `seydi-ali-reis` | dogum, duraklar |
| kişi | `nefi` | dogum, hami |
| kişi | `pecevi` | koken |
| kişi | `koci-bey` | koken, duraklar |
| kişi | `ebulgazi` | duraklar |
| kişi | `sai-mustafa-celebi` | duraklar |
| kişi | `tamgac-bugra-han` | tam_ad |
| kişi | `alparslan` | duraklar |
| kişi | `meliksah` | dogum, duraklar |
| kişi | `sencer` | dogum, olum, duraklar |
| kişi | `keykubad-1` | dogum |
| kişi | `gazan-han` | dogum |
| kişi | `timur` | dogum, duraklar |
| kişi | `murad-2` | dogum, olum, duraklar |
| kişi | `mehmed-2` | dogum, duraklar |
| kişi | `suleyman-1` | dogum, duraklar |
| kişi | `murad-3` | dogum, olum, duraklar |
| eser | `harezmi-hisab` | yil |
| eser | `harezmi-suretul-arz` | yil |
| eser | `harezmi-zic` | yil |
| eser | `farabi-ihsa` | yil, yazildigi_yer |
| eser | `farabi-medine` | yil, yazildigi_yer |
| eser | `farabi-musika` | yil, sunuldugu_kisi |
| eser | `ibn-sina-kanun` | yil |
| eser | `ibn-sina-sifa` | yil |
| eser | `ibn-sina-isarat` | yil |
| eser | `ibn-sina-danisname` | yil, ilk_olma |
| eser | `biruni-asar` | yil |
| eser | `biruni-tahdid` | yil |
| eser | `biruni-hind` | yil |
| eser | `biruni-kanun` | yil |
| eser | `biruni-tefhim` | yil, sunuldugu_kisi |
| eser | `biruni-saydele` | yil |
| eser | `gazali-ihya` | yil, yazildigi_yer |
| eser | `gazali-tehafut` | yil |
| eser | `gazali-munkiz` | yil, yazildigi_yer |
| eser | `gazali-nasihat` | yil, sunuldugu_kisi |
| eser | `hayyam-cebir` | yil, sunuldugu_kisi |
| eser | `siyasetname` | yazildigi_yer |
| eser | `cevahirun-nahv` | yil |
| eser | `atabetul-hakayik` | sunuldugu_kisi |
| eser | `mesnevi` | yil |
| eser | `risaletun-nushiyye` | yil |
| eser | `makalat-haci-bektas` | dil, konu |
| eser | `zic-i-ilhani` | yil, sunuldugu_kisi |
| eser | `ahlak-i-nasiri` | yil, sunuldugu_kisi, yazildigi_yer |
| eser | `tusi-tezkire` | yil |
| eser | `tusi-isarat-serhi` | yil |
| eser | `kadizade-mulahhas` | yil, sunuldugu_kisi |
| eser | `fethiyye` | yazildigi_yer |
| eser | `ali-kuscu-heye` | yil |
| eser | `serh-i-tecrid` | yil, sunuldugu_kisi, yazildigi_yer |
| eser | `serh-i-zic-ulug` | yil |
| eser | `muhakemetul-lugateyn` | ilk_olma |
| eser | `nevai-hamse` | yil, sunuldugu_kisi |
| eser | `mecalisun-nefais` | yil |
| eser | `nevai-mizan` | yil |
| eser | `maddetul-hayat` | konu, onemi |
| eser | `risaletun-nuriyye` | dil, konu |
| eser | `fusulul-bedayi` | yil, yazildigi_yer |
| eser | `fenari-isagoci` | konu |
| eser | `kitab-i-bahriye` | yazildigi_yer |
| eser | `beyan-i-menazil` | yil |
| eser | `umdetul-hisab` | yil, sunuldugu_kisi |
| eser | `cemalul-kuttab` | dil |
| eser | `sehzade-camii` | yil |
| eser | `suleymaniye` | yil |
| eser | `selimiye` | yil |
| eser | `sidretul-munteha` | yil, sunuldugu_kisi |
| eser | `kevakibud-durriyye` | yil, yazildigi_yer |
| eser | `turukus-seniyye` | yil, yazildigi_yer |
| eser | `cihannuma` | yil |
| eser | `tuhfetul-kibar` | yil, ilk_olma |
| eser | `mizanul-hak` | yil |
| eser | `dusturul-amel-katip` | yil |
| eser | `fuzuli-leyla` | yil, sunuldugu_kisi |
| eser | `fuzuli-hadika` | yil |
| eser | `sikayetname` | yil, sunuldugu_kisi |
| eser | `beng-u-bade` | yil, sunuldugu_kisi |
| eser | `baki-divan` | yil |
| eser | `kindi-felsefe-ula` | yil, sunuldugu_kisi |
| eser | `fergani-cevami` | yil |
| eser | `cevheri-sihah` | yil |
| eser | `fezailul-etrak` | yazildigi_yer |
| eser | `cahiz-hayevan` | yil |
| eser | `sahih-buhari` | yil |
| eser | `razi-havi` | yil |
| eser | `razi-cuderi` | onemi |
| eser | `kitabul-menazir` | yil |
| eser | `zicus-sabi` | yil |
| eser | `ibn-fadlan-risale` | yil, sunuldugu_kisi |
| eser | `sehname` | yil |
| eser | `tarih-i-beyhaki` | yil |
| eser | `el-giyasi` | sunuldugu_kisi |
| eser | `kessaf` | yil |
| eser | `mukaddimetul-edeb` | yil, yazildigi_yer |
| eser | `mefatihul-gayb` | yil, yazildigi_yer |
| eser | `hadikatul-hakika` | yil |
| eser | `mantikut-tayr` | yil, devlet |
| eser | `el-hidaye` | yil |
| eser | `maarif-bahaeddin` | konu |
| eser | `makalat-sems` | yil |
| eser | `ibtidaname` | yil |
| eser | `fususul-hikem` | yazildigi_yer |
| eser | `evamirul-alaiyye` | sunuldugu_kisi, yazildigi_yer |
| eser | `tarih-i-cihangusa` | yil, yazildigi_yer |
| eser | `durretut-tac` | yil, sunuldugu_kisi |
| eser | `mukaddime` | yil |
| eser | `ibn-battuta-rihle` | yil |
| eser | `bostan` | yil |
| eser | `tehafutut-tehafut` | yazildigi_yer |
| eser | `kadi-burhaneddin-divan` | yil |
| eser | `nesimi-divan` | devlet |
| eser | `iskendername-ahmedi` | ilk_olma |
| eser | `harname` | yil |
| eser | `husrev-u-sirin-seyhi` | yil, sunuldugu_kisi |
| eser | `vesiletun-necat` | yil |
| eser | `cerrahiyyetul-haniyye` | yazildigi_yer |
| eser | `mucerrebname` | yazildigi_yer |
| eser | `tevarih-asikpasazade` | yazildigi_yer |
| eser | `durerul-hukkam` | yil |
| eser | `gayetul-emani` | konu |
| eser | `tehafut-hocazade` | yil |
| eser | `serhul-akaid` | yil, devlet |
| eser | `serhul-mevakif` | yil, yazildigi_yer |
| eser | `miftahul-hisab` | yil, sunuldugu_kisi |
| eser | `risaletul-muhitiyye` | yil |
| eser | `dusturul-amel-mirim` | dil |
| eser | `tevarih-kemalpasazade` | yil, sunuldugu_kisi |
| eser | `nigaristan` | yil |
| eser | `maruzat` | dil |
| eser | `sekaik` | yil |
| eser | `nushatus-selatin` | yil, sunuldugu_kisi |
| eser | `miratul-memalik` | sunuldugu_kisi |
| eser | `siham-i-kaza` | yil |
| eser | `tarih-i-pecevi` | yil |
| eser | `koci-bey-risalesi` | yil |
| eser | `secere-i-terakime` | yil |
| eser | `secere-i-turk` | yil |
| eser | `dede-korkut` | yil, devlet |
