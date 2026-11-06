%% MAIN_PASSIVEDEFENSEOPTIMIZER
%  Pasif Savunma Cozumu Optimizasyonu ve Eslestirme - Ana Calistirma Betigi
%
%  Bu betik; kullanici tarafindan tanimlanan tehdit profiline (muhimmat
%  turu, patlayici esdeger kutlesi, carpma hizi, patlama mesafesi vb.)
%  gore, minimum agirlik / minimum lojistik yuk ve STANAG 4569 (Seviye 1-4)
%  standartlarinda maksimum beka (survivability) saglayan en optimum pasif
%  savunma konfigurasyonunu (UHPC kalinligi, Seramik-Kompozit-Metal
%  sandvic dizilimi, toprak bariyer vb.) hesaplar.
%
%  Bu arac; Ar-Ge ekibinin LS-DYNA / AUTODYN hidrokod simulasyonlarindan
%  once hizli bir muhendislik ON-ANALIZ / ELEME (screening) araci olarak
%  kullanmasi icin tasarlanmistir. Tum ampirik formuller ve malzeme
%  katsayilari, ilgili fonksiyon dosyalarinin ic dokumantasyonunda
%  kaynagiyla birlikte belirtilmistir.
%
%  Kullanim: Asagidaki "KULLANICI GIRDILERI" bolumunu tehdit senaryonuza
%  gore duzenleyip betigi calistirin (main_PassiveDefenseOptimizer).

clear; clc; close all;
addpath(fileparts(mfilename('fullpath')));

%% ============================ KULLANICI GIRDILERI ============================
% threat.type :
%   'KE'      -> Salt kinetik enerjili tehdit (zirh delici mermi/APFSDS)
%   'HE'      -> Salt patlayici/blast tehdidi (IED, gomulu mayin vb. - fragman onemsiz)
%   'HE_FRAG' -> Kombine tehdit (topcu/havan mermisi: blast + sarapnel/parca etkisi)
%
% ASAGIDAKI ORNEK SENARYO: 152/155mm sinifi topcu mermisi benzeri kombine
% tehdit (blast + STANAG Seviye 3 sarapnel enerjisi).

threat.type = 'HE_FRAG';

% --- Kinetik / Sarapnel Parametreleri (KE ve HE_FRAG icin kullanilir) ---
threat.caliber_mm      = 7.62;    % Kalibre [mm] (5.56, 7.62, 12.7, 14.5, 20, 25, 30 ...)
threat.mass_g           = 9.7;     % Mermi/sarapnel kutlesi [g]
threat.v_impact_ms      = 930;     % Carpma hizi [m/s]
threat.penetratorClass  = 'Tungsten_Carbide';  % 'Soft' | 'Hardened_Steel' | 'Tungsten_Carbide' | 'Tungsten_APFSDS_Sabot'

% --- Patlayici / Blast Parametreleri (HE ve HE_FRAG icin kullanilir) ---
threat.explosiveMass_kg = 10.8;    % Net patlayici kutlesi (NEW) [kg]
threat.explosiveType    = 'TNT';   % loadExplosiveDatabase() icindeki bir isimle eslesmeli
threat.standoff_R_m     = 5.0;     % Patlama mesafesi (standoff distance) [m]

% --- Yapisal Panel Geometrisi (SDOF blast analizi icin) ---
panelSpan_m = 1.2;    % Panel acikligi / mesnetler arasi mesafe [m]

%% ============================ HESAPLAMA HAT (PIPELINE) ============================
% Tum siniflandirma / fizik / optimizasyon mantigi runFullPipeline.m icinde
% tutulur; boylece bu komut-satiri betigi ile etkilesimli uygulama
% (PassiveDefenseOptimizerApp.m) AYNI hesaplama kodunu paylasir.
fprintf('Optimizasyon calisiyor (izgara taramasi), lutfen bekleyin...\n');
out = runFullPipeline(threat, panelSpan_m);
fprintf('Optimizasyon tamamlandi (%.1f s, %d aday degerlendirildi).\n', out.elapsed_s, numel(out.searchTrace));

%% ============================ GORSELLESTIRME ============================
% Rapor zaten runFullPipeline() icinde Command Window'a basildi (out.reportStr
% metin olarak da mevcuttur). Burada yalnizca grafikleri uretiyoruz.
plotResults(out.threat, out.searchTrace, out.optimum_design, out.scaledTable, out.damageTable);
