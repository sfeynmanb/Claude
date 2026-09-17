function printDesignReport(threat, stanagLevel, marginNote, blast, keMetrics, penInfo, optimum_design)
%PRINTDESIGNREPORT Command Window'da ozet tasarim raporu basar.

sep = repmat('=', 1, 72);
fprintf('\n%s\n', sep);
fprintf(' PASIF SAVUNMA COZUMU OPTIMIZASYONU VE ESLESTIRME RAPORU\n');
fprintf('%s\n', sep);

fprintf('\n[1] TEHDIT SINIFLANDIRMASI\n');
fprintf('    STANAG 4569 Karsiligi : %s\n', stanagLevel);
if ~isempty(marginNote)
    fprintf('    Not                   : %s\n', marginNote);
end
fprintf('    Tehdit Tipi           : %s\n', threat.type);

if ~strcmpi(threat.type, 'HE')
    fprintf('\n[2] KINETIK ENERJI METRIKLERI\n');
    fprintf('    Carpma Hizi           : %.1f m/s\n', threat.v_impact_ms);
    fprintf('    Mermi/Sarapnel Kutlesi: %.2f g\n', threat.mass_g);
    fprintf('    Kinetik Enerji (E_k)  : %.0f J\n', keMetrics.E_k_J);
    fprintf('    Kesit Yogunlugu (SD)  : %.2f kg/m^2\n', keMetrics.SD_kg_m2);
    fprintf('    Enerji Yogunlugu (E_d): %.2f J/mm^2\n', keMetrics.E_d_J_m2/1e6);
    fprintf('    Penetrator Sinifi     : %s (K_DM=%.3f)\n', penInfo.penetratorClass, penInfo.K_DM);
    fprintf('    Gerekli RHA-Esdeger   : %.1f mm (tasarim marji x%.2f dahil)\n', ...
        penInfo.e_RHA_req_mm, penInfo.designMargin);
end

if strcmpi(threat.type, 'HE') || strcmpi(threat.type, 'HE_FRAG')
    fprintf('\n[3] PATLAMA (BLAST) YUKU\n');
    fprintf('    TNT Esdegeri (W)      : %.2f kg\n', blast.W_TNT_kg);
    fprintf('    Patlama Mesafesi (R)  : %.2f m\n', blast.R_m);
    fprintf('    Olceklendirilmis Mesafe Z : %.3f m/kg^(1/3)\n', blast.Z);
    fprintf('    Gelen Asiri Basinc Pso: %.1f kPa\n', blast.Pso_kPa);
    fprintf('    Yansiyan Asiri Basinc Pr : %.1f kPa\n', blast.Pr_kPa);
    fprintf('    Pozitif Faz Suresi (td): %.2f ms\n', blast.td_ms);
    fprintf('    Gelen Impuls (iso)    : %.1f kPa*ms\n', blast.iso_kPa_ms);
    if blast.isExtrapolated
        fprintf('    [!] UYARI: Z, referans tablo araligi disinda -> sonuclar EKSTRAPOLE edilmistir.\n');
    end
end

fprintf('\n[4] OPTIMUM PASIF SAVUNMA DIZILIMI\n');
if isempty(optimum_design)
    fprintf('    Aranan uzayda gecerli tasarim bulunamadi. Arama araligini genisletin.\n');
else
    d = optimum_design.design;
    if isfield(d, 'ceramicMat') && ~isempty(d.ceramicMat) && d.t_ceramic_mm > 0
        fprintf('    - Seramik (On Yuz)    : %.1f mm  [%s]\n', d.t_ceramic_mm, d.ceramicMat.name);
    end
    if isfield(d, 'uhpcMat') && ~isempty(d.uhpcMat) && d.t_uhpc_mm > 0
        fprintf('    - UHPC (Yapisal)      : %.1f mm  [%s]\n', d.t_uhpc_mm, d.uhpcMat.name);
    end
    if isfield(d, 'compositeMat') && ~isempty(d.compositeMat) && d.t_composite_mm > 0
        fprintf('    - Kompozit (Arka/Spall): %.1f mm  [%s]\n', d.t_composite_mm, d.compositeMat.name);
    end
    if isfield(d, 'metalMat') && ~isempty(d.metalMat) && d.t_metal_mm > 0
        fprintf('    - Metal (Destek)      : %.1f mm  [%s]\n', d.t_metal_mm, d.metalMat.name);
    end
    if isfield(d, 'soilMat') && ~isempty(d.soilMat) && d.t_soil_m > 0
        fprintf('    - Toprak Bariyer      : %.2f m   [%s]\n', d.t_soil_m, d.soilMat.name);
    end

    fprintf('\n    Toplam Alan Yogunlugu (Areal Density) : %.1f kg/m^2\n', optimum_design.AD_total_kg_m2);
    fprintf('    Lojistik Zorluk Indeksi (1-10)        : %.2f\n', optimum_design.logisticScore);
    fprintf('    Fizibilite                            : %s\n', ternary(optimum_design.feasible, 'SAGLANIYOR', 'SAGLANMIYOR'));

    if ~strcmpi(threat.type, 'HE')
        fprintf('    KE Korunma Marji                      : %.1f%% (RHA-esd. %.1f kg/m^2 saglandi / %.1f kg/m^2 gerekli)\n', ...
            optimum_design.keDetail.margin_pct, optimum_design.keDetail.AD_RHA_equiv_kg_m2, optimum_design.keDetail.AD_RHA_req_kg_m2);
    end
    if ~isempty(optimum_design.blastDetail)
        bd = optimum_design.blastDetail;
        fprintf('    SDOF Rejimi                           : %s (td/Tn=%.2f)\n', bd.regime, bd.td_Tn_ratio);
        fprintf('    Suneklik Talebi / Izni (mu)            : %.2f / %.2f\n', bd.mu_demand, bd.mu_allow);
        fprintf('    Arka Yuzey Deplasmani (BFS)            : %.1f mm  (Esik: %.0f mm)\n', bd.X_max_m*1000, bd.BFS_limit_m*1000);
    end
end

fprintf('\n%s\n', sep);
fprintf(' NOT: Bu program bir ON-ANALIZ / ELEME araci olup, sonuclar LS-DYNA veya\n');
fprintf(' AUTODYN gibi hidrokod simulasyonlari ve fiziksel STANAG 4569 atis\n');
fprintf(' testleri ile dogrulanmadan nihai tasarim onayi icin kullanilmamalidir.\n');
fprintf('%s\n\n', sep);

end

function s = ternary(cond, a, b)
if cond
    s = a;
else
    s = b;
end
end
