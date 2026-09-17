function materials = loadMaterialDatabase()
%LOADMATERIALDATABASE Pasif savunma malzeme mikro-veritabani.
%   materials = LOADMATERIALDATABASE() STANAG 4569 pasif zirh tasarimi
%   icin kullanilan temel malzeme siniflarini (Seramik, Kompozit, UHPC,
%   Metal, Toprak) fiziksel/mekanik ozellikleriyle birlikte struct array
%   olarak dondurur.
%
%   Alanlar:
%     name          - Malzeme adi
%     class         - 'Seramik' | 'Kompozit' | 'UHPC' | 'Metal' | 'Toprak'
%     rho           - Yogunluk [kg/m^3]
%     E_GPa         - Elastisite modulu [GPa]
%     sigma_y_MPa   - Akma/basinc/cekme dayanimi [MPa] (SDOF egilme kapasitesi icin)
%     mu_allow      - Izin verilen suneklik orani (ductility ratio), SDOF kontrolu
%     E_mat         - RHA'ya gore Kutlesel Balistik Verimlilik Katsayisi [-]
%                     (E_mat=1 => RHA ile ayni performans/kg; E_mat>1 => RHA'dan
%                     daha hafif ayni korumayi saglar). Bkz. fonksiyon ici notlar.
%     logisticIndex - Goreceli lojistik/kurulum zorlugu (1=kolay .. 10=zor)
%     source        - Veri kaynagi / kalibrasyon notu
%
%   Kaynak: "Balistik ve Patlama Data Seti" (Zirh Malzeme Parametre sayfasi,
%   Johnson-Cook / JH-2 tipi parametreler) + acik literatur tipik degerleri
%   (UHPC, Kompozit, Toprak icin - veri setinde ayri sayfa olmadigindan).
%
%   ONEMLI: E_mat, mu_allow ve logisticIndex degerleri, on-analiz / eleme
%   (screening) amacli MUHENDISLIK YAKLASIMLARIDIR. Nihai tasarim dogrulamasi
%   LS-DYNA / AUTODYN gibi sonlu elemanlar hidrokod simulasyonlari ve fiziksel
%   atis testleri (V50) ile yapilmalidir.

materials = struct('name', {}, 'class', {}, 'rho', {}, 'E_GPa', {}, ...
    'sigma_y_MPa', {}, 'mu_allow', {}, 'E_mat', {}, 'logisticIndex', {}, 'source', {});

i = 0;

% ---------------------------------------------------------------
% METAL SINIFI (Zirh Malzeme Parametre sayfasi - Johnson-Cook)
% ---------------------------------------------------------------
i = i + 1;
materials(i).name = 'RHA (MIL-A-12560)';
materials(i).class = 'Metal';
materials(i).rho = 7850;
materials(i).E_GPa = 210;
materials(i).sigma_y_MPa = 792.0;
materials(i).mu_allow = 10;
materials(i).E_mat = 1.00;               % Referans malzeme
materials(i).logisticIndex = 5;
materials(i).source = 'Veri seti: Zirh Malzeme Parametre (Johnson-Cook A=792 MPa)';

i = i + 1;
materials(i).name = 'AR500 (Hardox)';
materials(i).class = 'Metal';
materials(i).rho = 7850;
materials(i).E_GPa = 210;
materials(i).sigma_y_MPa = 1250.0;
materials(i).mu_allow = 8;
materials(i).E_mat = 1.08;               % Yuksek sertlik -> RHA'ya kiyasla hafif ustunluk
materials(i).logisticIndex = 5;
materials(i).source = 'Veri seti: Zirh Malzeme Parametre (Johnson-Cook A=1250 MPa)';

i = i + 1;
materials(i).name = 'Aluminyum Al 5083-H131';
materials(i).class = 'Metal';
materials(i).rho = 2660;
materials(i).E_GPa = 71;
materials(i).sigma_y_MPa = 167.0;
materials(i).mu_allow = 8;
materials(i).E_mat = 0.75;               % Dusuk yogunluk avantaji, orta balistik verim
materials(i).logisticIndex = 4;
materials(i).source = 'Veri seti: Zirh Malzeme Parametre (Johnson-Cook A=167 MPa)';

i = i + 1;
materials(i).name = 'Titanyum Ti-6Al-4V';
materials(i).class = 'Metal';
materials(i).rho = 4430;
materials(i).E_GPa = 114;
materials(i).sigma_y_MPa = 1098.0;
materials(i).mu_allow = 6;
materials(i).E_mat = 1.45;
materials(i).logisticIndex = 7;
materials(i).source = 'Veri seti: Zirh Malzeme Parametre (Johnson-Cook A=1098 MPa)';

% ---------------------------------------------------------------
% SERAMIK SINIFI (Zirh Malzeme Parametre sayfasi - JH-2 tipi)
% ---------------------------------------------------------------
i = i + 1;
materials(i).name = 'Silisyum Karbur (SiC)';
materials(i).class = 'Seramik';
materials(i).rho = 3210;
materials(i).E_GPa = 410;                % Tipik SiC elastisite modulu (literatur)
materials(i).sigma_y_MPa = 0;            % Gevrek malzeme: SDOF egilme kapasitesine katkisi ihmal
materials(i).mu_allow = 1;               % Gevrek -> sunek deformasyon kapasitesi yok
materials(i).E_mat = 5.50;               % Kompozit destekli sert-yuz (hard-face) verimliligi
materials(i).logisticIndex = 6;
materials(i).source = 'Veri seti: Zirh Malzeme Parametre (HEL=11.7 GPa, JH-2)';

i = i + 1;
materials(i).name = 'Alumina (Al2O3 %99.5)';
materials(i).class = 'Seramik';
materials(i).rho = 3890;
materials(i).E_GPa = 300;
materials(i).sigma_y_MPa = 0;
materials(i).mu_allow = 1;
materials(i).E_mat = 3.00;
materials(i).logisticIndex = 5;
materials(i).source = 'Veri seti: Zirh Malzeme Parametre (HEL=6.57 GPa, JH-2)';

i = i + 1;
materials(i).name = 'Bor Karbur (B4C)';
materials(i).class = 'Seramik';
materials(i).rho = 2510;
materials(i).E_GPa = 460;
materials(i).sigma_y_MPa = 0;
materials(i).mu_allow = 1;
materials(i).E_mat = 6.50;               % En hafif/en verimli seramik (hava platformlari)
materials(i).logisticIndex = 8;          % Kirilgan + pahali + tedarik kisitli
materials(i).source = 'Veri seti: Zirh Malzeme Parametre (HEL=18.0 GPa, JH-2)';

% ---------------------------------------------------------------
% KOMPOZIT SINIFI (literatur tipik degerleri - veri setinde ayri
% sayfa yok; BFS sayfasindaki "Spall-Liner Aramid/Kevlar" notuyla uyumlu)
% ---------------------------------------------------------------
i = i + 1;
materials(i).name = 'Aramid/Kevlar Kompozit (UD laminat)';
materials(i).class = 'Kompozit';
materials(i).rho = 1230;
materials(i).E_GPa = 30;                 % Lif dogrultusunda efektif modul (tipik)
materials(i).sigma_y_MPa = 600;          % Cekme/membran kapasitesi (tipik, literatur)
materials(i).mu_allow = 6;               % Yuksek suneklik / enerji sonumleme
materials(i).E_mat = 2.20;
materials(i).logisticIndex = 2;          % Hafif, esnek, kolay nakliye/montaj
materials(i).source = 'Literatur tipik deger (aramid balistik laminat, UHMWPE benzeri)';

% ---------------------------------------------------------------
% UHPC SINIFI (Siper Sunumu / literatur tipik degerleri)
% ---------------------------------------------------------------
i = i + 1;
materials(i).name = 'UHPC (Ultra Yuksek Performansli Beton)';
materials(i).class = 'UHPC';
materials(i).rho = 2500;
materials(i).E_GPa = 45;
materials(i).sigma_y_MPa = 20;           % Lifli UHPC catlak-sonrasi egilme (flexural) kapasitesi
materials(i).mu_allow = 3;
materials(i).E_mat = 0.40;               % KE karsisinda dusuk verim; asil rolu blast/spall direnci
materials(i).logisticIndex = 8;          % Agir, kalip/kur gerektirir (veya prefabrik nakliyesi zor)
materials(i).source = 'Basinc dayanimi >150 MPa (kullanici spesi); flexural literatur tipik deger';

% ---------------------------------------------------------------
% TOPRAK SINIFI (mevzi tahkimati / standoff bariyer)
% ---------------------------------------------------------------
i = i + 1;
materials(i).name = 'Sikistirilmis Toprak/Kum Bariyer';
materials(i).class = 'Toprak';
materials(i).rho = 1900;
materials(i).E_GPa = 0.05;
materials(i).sigma_y_MPa = 0;            % Yapisal (sunek) SDOF elemani olarak modellenmez
materials(i).mu_allow = 1;
materials(i).E_mat = 0.05;               % KE karsisinda ihmal edilebilir; asil rolu patlama sonumleme
materials(i).logisticIndex = 5;          % Hacimce buyuk, makine/is gucu bagimli
materials(i).source = 'Literatur tipik deger (mevzi tahkimati, dolgu toprak/kum)';

end
