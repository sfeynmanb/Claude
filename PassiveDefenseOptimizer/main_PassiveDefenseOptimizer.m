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
materials   = loadMaterialDatabase();
explosives  = loadExplosiveDatabase();
scaledTable = loadBlastScaledDistanceTable();
damageTable = loadDamageThresholdTable();

[stanagLevel, ~, marginNote] = classifyThreatSTANAG(threat);

keMetrics = struct('E_k_J', NaN, 'SD_kg_m2', NaN, 'E_d_J_m2', NaN);
penInfo   = struct('e_RHA_req_mm', 0, 'K_DM', NaN, 'penetratorClass', '-', 'designMargin', NaN);
if ~strcmpi(threat.type, 'HE')
    keMetrics = kineticEnergyMetrics(threat);
    penInfo   = deMarrePenetration(threat);
end

blast = struct('Z', NaN, 'Pso_kPa', NaN, 'Pr_kPa', NaN, 'td_ms', NaN, ...
    'iso_kPa_ms', NaN, 'isExtrapolated', false, 'W_TNT_kg', NaN, 'R_m', NaN);
if strcmpi(threat.type, 'HE') || strcmpi(threat.type, 'HE_FRAG')
    W_TNT = computeTNTEquivalent(threat.explosiveMass_kg, threat.explosiveType, explosives);
    blast = blastLoad(W_TNT, threat.standoff_R_m, scaledTable);
end

fprintf('Optimizasyon calisiyor (izgara taramasi), lutfen bekleyin...\n');
tic;
[optimum_design, searchTrace] = optimizePassiveDefense(threat, materials, blast, penInfo, panelSpan_m);
fprintf('Optimizasyon tamamlandi (%.1f s, %d aday degerlendirildi).\n', toc, numel(searchTrace));

%% ============================ RAPOR VE GORSELLESTIRME ============================
printDesignReport(threat, stanagLevel, marginNote, blast, keMetrics, penInfo, optimum_design);

plotResults(threat, searchTrace, optimum_design, scaledTable, damageTable);
