function presets = loadThreatPresetDatabase()
%LOADTHREATPRESETDATABASE STANAG 4569 Seviye 1-6 mühimmat referans tablosu.
%   presets = LOADTHREATPRESETDATABASE() AEP-55 Vol.1 tabanli STANAG 4569
%   kinetik enerjili (KE) tehdit siniflandirma tablosunu dondurur. Kullanici
%   girdisini siniflandirmak (classifyThreatSTANAG.m) ve varsayilan
%   caliber/hiz/kutle degerlerini doldurmak icin kullanilir.
%
%   penetratorClass alani deMarrePenetration.m icindeki K_DM katsayi
%   secimini belirler:
%     'Soft'                 - Kursun/kursun cekirdek
%     'Hardened_Steel'       - Sertlestirilmis celik zirh delici (API/AP)
%     'Tungsten_Carbide'     - Tungsten karbur cekirdek (AP)
%     'Tungsten_APFSDS_Sabot'- Tungsten alt kalibreli zirh delici (APDS/APFSDS)
%
%   Kaynak: Veri seti "Mühimmat - STANAG" sayfasi.

presets = struct('level', {}, 'name', {}, 'coreMaterial', {}, 'penetratorClass', {}, ...
    'mass_g', {}, 'v_nominal_ms', {}, 'KE_J', {}, 'caliber_mm', {}, 'note', {});

i = 0;
i = i + 1;
presets(i).level = 1; presets(i).name = '5.56x45mm SS109 / M855';
presets(i).coreMaterial = 'Kursun-Celik Penetrator'; presets(i).penetratorClass = 'Soft';
presets(i).mass_g = 4.00; presets(i).v_nominal_ms = 900; presets(i).KE_J = 1620;
presets(i).caliber_mm = 5.56;
presets(i).note = 'AEP-55 Vol 1. Beton yuzeyde lokalize ufalanma (spalling).';

i = i + 1; presets(i).level = 1; presets(i).name = '7.62x51mm NATO Ball M80';
presets(i).coreMaterial = 'Kursun Cekirdek'; presets(i).penetratorClass = 'Soft';
presets(i).mass_g = 9.5; presets(i).v_nominal_ms = 833; presets(i).KE_J = 3235;
presets(i).caliber_mm = 7.62;
presets(i).note = 'AEP-55 Vol 1. Genis yuzeyli mikro-catlak olusumu.';

i = i + 1; presets(i).level = 2; presets(i).name = '7.62x39mm API BZ';
presets(i).coreMaterial = 'Celik Zirh Delici'; presets(i).penetratorClass = 'Hardened_Steel';
presets(i).mass_g = 7.9; presets(i).v_nominal_ms = 695; presets(i).KE_J = 1877;
presets(i).caliber_mm = 7.62;
presets(i).note = 'AEP-55 Vol 1. Celik cekirdek beton matrisinde kesme gerilmesi.';

i = i + 1; presets(i).level = 3; presets(i).name = '7.62x51mm AP (M61/FFV)';
presets(i).coreMaterial = 'Tungsten Karbur (WC)'; presets(i).penetratorClass = 'Tungsten_Carbide';
presets(i).mass_g = 9.7; presets(i).v_nominal_ms = 930; presets(i).KE_J = 3633;
presets(i).caliber_mm = 7.62;
presets(i).note = 'AEP-55 Vol 1. Asiri sert cekirdek, standart betonari deler (punching shear).';

i = i + 1; presets(i).level = 3; presets(i).name = '7.62x54Rmm B32 API';
presets(i).coreMaterial = 'Celik Zirh Delici'; presets(i).penetratorClass = 'Hardened_Steel';
presets(i).mass_g = 9.6; presets(i).v_nominal_ms = 860; presets(i).KE_J = 3846;
presets(i).caliber_mm = 7.62;
presets(i).note = 'GOST R 50744-95 / AEP-55. Maksimum Seviye 3 enerjisi.';

i = i + 1; presets(i).level = 4; presets(i).name = '14.5x114mm API B32';
presets(i).coreMaterial = 'Celik Zirh Delici'; presets(i).penetratorClass = 'Hardened_Steel';
presets(i).mass_g = 64.00; presets(i).v_nominal_ms = 911; presets(i).KE_J = 26558;
presets(i).caliber_mm = 14.5;
presets(i).note = 'AEP-55 Vol 1. Ciddi makro-yapisal tahribat, panellerde egilme.';

i = i + 1; presets(i).level = 5; presets(i).name = '25x137mm APDS-T';
presets(i).coreMaterial = 'Tungsten Penetrator'; presets(i).penetratorClass = 'Tungsten_APFSDS_Sabot';
presets(i).mass_g = 150.00; presets(i).v_nominal_ms = 1258; presets(i).KE_J = 118688;
presets(i).caliber_mm = 25;
presets(i).note = 'AEP-55 Vol 1. Sabot muhimmat, hidrodinamik isleme baslar.';

i = i + 1; presets(i).level = 6; presets(i).name = '30x173mm APFSDS-T';
presets(i).coreMaterial = 'Tungsten Ok'; presets(i).penetratorClass = 'Tungsten_APFSDS_Sabot';
presets(i).mass_g = 235.00; presets(i).v_nominal_ms = 1620; presets(i).KE_J = 308367;
presets(i).caliber_mm = 30;
presets(i).note = 'AEP-55 Vol 1. Hipersonik penetrasyon, sivil muhendislik sinirlarinin ustunde.';

end
