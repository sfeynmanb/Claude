function reportStr = printDesignReport(threat, stanagLevel, marginNote, blast, keMetrics, penInfo, optimum_design)
%PRINTDESIGNREPORT Ozet tasarim raporunu olusturur, Command Window'a basar
%ve metni (string) olarak dondurur.
%   reportStr = PRINTDESIGNREPORT(...) hem fprintf ile konsola yazar hem de
%   ayni metni bir char array olarak geri dondurur; bu sayede interaktif
%   uygulama (PassiveDefenseOptimizerApp.m) ayni raporu bir metin kutusunda
%   (uitextarea) gosterebilir.

sep = repmat('=', 1, 72);
L = {};
L{end+1} = sprintf('%s', sep);
L{end+1} = sprintf(' PASIF SAVUNMA COZUMU OPTIMIZASYONU VE ESLESTIRME RAPORU');
L{end+1} = sprintf('%s', sep);
L{end+1} = '';

L{end+1} = sprintf('[1] TEHDIT SINIFLANDIRMASI');
L{end+1} = sprintf('    STANAG 4569 Karsiligi : %s', stanagLevel);
if ~isempty(marginNote)
    L{end+1} = sprintf('    Not                   : %s', marginNote);
end
L{end+1} = sprintf('    Tehdit Tipi           : %s', threat.type);

if ~strcmpi(threat.type, 'HE')
    L{end+1} = '';
    L{end+1} = sprintf('[2] KINETIK ENERJI METRIKLERI');
    L{end+1} = sprintf('    Carpma Hizi           : %.1f m/s', threat.v_impact_ms);
    L{end+1} = sprintf('    Mermi/Sarapnel Kutlesi: %.2f g', threat.mass_g);
    L{end+1} = sprintf('    Kinetik Enerji (E_k)  : %.0f J', keMetrics.E_k_J);
    L{end+1} = sprintf('    Kesit Yogunlugu (SD)  : %.2f kg/m^2', keMetrics.SD_kg_m2);
    L{end+1} = sprintf('    Enerji Yogunlugu (E_d): %.2f J/mm^2', keMetrics.E_d_J_m2/1e6);
    L{end+1} = sprintf('    Penetrator Sinifi     : %s (K_DM=%.3f)', penInfo.penetratorClass, penInfo.K_DM);
    L{end+1} = sprintf('    Gerekli RHA-Esdeger   : %.1f mm (tasarim marji x%.2f dahil)', ...
        penInfo.e_RHA_req_mm, penInfo.designMargin);
end

if strcmpi(threat.type, 'HE') || strcmpi(threat.type, 'HE_FRAG')
    L{end+1} = '';
    L{end+1} = sprintf('[3] PATLAMA (BLAST) YUKU');
    L{end+1} = sprintf('    TNT Esdegeri (W)      : %.2f kg', blast.W_TNT_kg);
    L{end+1} = sprintf('    Patlama Mesafesi (R)  : %.2f m', blast.R_m);
    L{end+1} = sprintf('    Olceklendirilmis Mesafe Z : %.3f m/kg^(1/3)', blast.Z);
    L{end+1} = sprintf('    Gelen Asiri Basinc Pso: %.1f kPa', blast.Pso_kPa);
    L{end+1} = sprintf('    Yansiyan Asiri Basinc Pr : %.1f kPa', blast.Pr_kPa);
    L{end+1} = sprintf('    Pozitif Faz Suresi (td): %.2f ms', blast.td_ms);
    L{end+1} = sprintf('    Gelen Impuls (iso)    : %.1f kPa*ms', blast.iso_kPa_ms);
    if blast.isExtrapolated
        L{end+1} = sprintf('    [!] UYARI: Z, referans tablo araligi disinda -> sonuclar EKSTRAPOLE edilmistir.');
    end
end

L{end+1} = '';
L{end+1} = sprintf('[4] OPTIMUM PASIF SAVUNMA DIZILIMI');
if isempty(optimum_design)
    L{end+1} = sprintf('    Aranan uzayda gecerli tasarim bulunamadi. Arama araligini genisletin.');
else
    d = optimum_design.design;
    if isfield(d, 'ceramicMat') && ~isempty(d.ceramicMat) && d.t_ceramic_mm > 0
        L{end+1} = sprintf('    - Seramik (On Yuz)     : %.1f mm  [%s]', d.t_ceramic_mm, d.ceramicMat.name);
    end
    if isfield(d, 'uhpcMat') && ~isempty(d.uhpcMat) && d.t_uhpc_mm > 0
        L{end+1} = sprintf('    - UHPC (Yapisal)       : %.1f mm  [%s]', d.t_uhpc_mm, d.uhpcMat.name);
    end
    if isfield(d, 'compositeMat') && ~isempty(d.compositeMat) && d.t_composite_mm > 0
        L{end+1} = sprintf('    - Kompozit (Arka/Spall): %.1f mm  [%s]', d.t_composite_mm, d.compositeMat.name);
    end
    if isfield(d, 'metalMat') && ~isempty(d.metalMat) && d.t_metal_mm > 0
        L{end+1} = sprintf('    - Metal (Destek)       : %.1f mm  [%s]', d.t_metal_mm, d.metalMat.name);
    end
    if isfield(d, 'soilMat') && ~isempty(d.soilMat) && d.t_soil_m > 0
        L{end+1} = sprintf('    - Toprak Bariyer       : %.2f m   [%s]', d.t_soil_m, d.soilMat.name);
    end

    L{end+1} = '';
    L{end+1} = sprintf('    Toplam Alan Yogunlugu (Areal Density) : %.1f kg/m^2', optimum_design.AD_total_kg_m2);
    L{end+1} = sprintf('    Lojistik Zorluk Indeksi (1-10)        : %.2f', optimum_design.logisticScore);
    L{end+1} = sprintf('    Fizibilite                            : %s', ternary(optimum_design.feasible, 'SAGLANIYOR', 'SAGLANMIYOR'));

    if ~strcmpi(threat.type, 'HE')
        L{end+1} = sprintf('    KE Korunma Marji                      : %.1f%% (RHA-esd. %.1f kg/m^2 saglandi / %.1f kg/m^2 gerekli)', ...
            optimum_design.keDetail.margin_pct, optimum_design.keDetail.AD_RHA_equiv_kg_m2, optimum_design.keDetail.AD_RHA_req_kg_m2);
    end
    if ~isempty(optimum_design.blastDetail)
        bd = optimum_design.blastDetail;
        L{end+1} = sprintf('    SDOF Rejimi                           : %s (td/Tn=%.2f)', bd.regime, bd.td_Tn_ratio);
        L{end+1} = sprintf('    Suneklik Talebi / Izni (mu)            : %.2f / %.2f', bd.mu_demand, bd.mu_allow);
        L{end+1} = sprintf('    Arka Yuzey Deplasmani (BFS)            : %.1f mm  (Esik: %.0f mm)', bd.X_max_m*1000, bd.BFS_limit_m*1000);
    end
end

L{end+1} = '';
L{end+1} = sprintf('%s', sep);
L{end+1} = sprintf(' NOT: Bu program bir ON-ANALIZ / ELEME araci olup, sonuclar LS-DYNA veya');
L{end+1} = sprintf(' AUTODYN gibi hidrokod simulasyonlari ve fiziksel STANAG 4569 atis');
L{end+1} = sprintf(' testleri ile dogrulanmadan nihai tasarim onayi icin kullanilmamalidir.');
L{end+1} = sprintf('%s', sep);

reportStr = strjoin(L, sprintf('\n'));
fprintf('\n%s\n\n', reportStr);

end

function s = ternary(cond, a, b)
if cond
    s = a;
else
    s = b;
end
end
