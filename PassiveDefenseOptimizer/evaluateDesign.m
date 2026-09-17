function result = evaluateDesign(threat, design, materials, blast, penInfo, panelSpan_m, weights)
%EVALUATEDESIGN Aday pasif savunma dizilimini degerlendiren maliyet/skor fonksiyonu.
%   result = EVALUATEDESIGN(threat, design, materials, blast, penInfo, panelSpan_m, weights)
%
%   design struct alanlari (katman kalinliklari; kullanilmayanlar icin 0):
%     ceramicMat  (materials struct elemani veya [])   t_ceramic_mm
%     compositeMat                                      t_composite_mm
%     uhpcMat                                            t_uhpc_mm
%     metalMat                                           t_metal_mm
%     soilMat                                            t_soil_m
%
%   SARTLAR (kisitlar):
%     - KE / HE_FRAG tehdit: Penetrasyon = 0 (RHA-esdeger korumasi >= gerekli)
%     - HE / HE_FRAG tehdit: SDOF suneklik talebi <= izin verilen VE
%       arka yuzey deplasmani <= BFS esigi (44 mm)
%
%   MINIMIZE EDILEN DEGER: Agirlikli(Alan Yogunlugu, Lojistik Zorluk Indeksi)
%
%   Cikti result struct: feasible (bool), AD_total_kg_m2, logisticScore,
%   score (dusuk=iyi), keFeasible, blastFeasible, keDetail, blastDetail

if nargin < 7 || isempty(weights)
    weights = struct('w_weight', 1.0, 'w_logistic', 0.15);
end

layers = {'ceramicMat', 'compositeMat', 'uhpcMat', 'metalMat'};
thicknessFields = {'t_ceramic_mm', 't_composite_mm', 't_uhpc_mm', 't_metal_mm'};

AD_total = 0;
AD_RHA_equiv = 0;
logisticWeighted = 0;

for i = 1:numel(layers)
    matField = layers{i};
    tField = thicknessFields{i};
    if isfield(design, matField) && ~isempty(design.(matField)) && design.(tField) > 0
        mat = design.(matField);
        t_m = design.(tField) / 1000;
        AD_i = t_m * mat.rho;                 % kg/m^2
        AD_total = AD_total + AD_i;
        AD_RHA_equiv = AD_RHA_equiv + AD_i * mat.E_mat;
        logisticWeighted = logisticWeighted + AD_i * mat.logisticIndex;
    end
end

% Toprak bariyer (ayri birim: metre), agirliga dahil edilir, RHA-esdegerine
% ihmal edilebilir katkisi vardir (KE savunmasinda birincil rolu yok)
if isfield(design, 'soilMat') && ~isempty(design.soilMat) && design.t_soil_m > 0
    AD_soil = design.t_soil_m * design.soilMat.rho;
    AD_total = AD_total + AD_soil;
    AD_RHA_equiv = AD_RHA_equiv + AD_soil * design.soilMat.E_mat;
    logisticWeighted = logisticWeighted + AD_soil * design.soilMat.logisticIndex;
end

if AD_total > 0
    logisticScore = logisticWeighted / AD_total;   % Agirlikli ortalama lojistik zorluk
else
    logisticScore = 0;
end

% ------------------ KE / Penetrasyon Sarti ------------------
keFeasible = true;
keDetail = struct('AD_RHA_equiv_kg_m2', AD_RHA_equiv, 'AD_RHA_req_kg_m2', 0, 'margin_pct', NaN);
if ~strcmpi(threat.type, 'HE')
    rho_RHA = 7850;
    AD_RHA_req = rho_RHA * (penInfo.e_RHA_req_mm / 1000);
    keDetail.AD_RHA_req_kg_m2 = AD_RHA_req;
    keFeasible = AD_RHA_equiv >= AD_RHA_req;
    keDetail.margin_pct = 100 * (AD_RHA_equiv - AD_RHA_req) / max(AD_RHA_req, eps);
end

% ------------------ Blast / SDOF Sarti ------------------
blastFeasible = true;
blastDetail = [];
if strcmpi(threat.type, 'HE') || strcmpi(threat.type, 'HE_FRAG')
    % Toprak bariyer, patlama basinc/impulsunu zayiflatan bir "standoff/attenuation"
    % katmani olarak modellenir (SDOF yapisal elemani DEGILDIR).
    k_soil_atten = 0.6;   % [1/m], literatur tipik deger (sikistirilmis kum/toprak)
    t_soil = 0;
    if isfield(design, 'soilMat') && ~isempty(design.soilMat)
        t_soil = design.t_soil_m;
    end
    attenFactor = exp(-k_soil_atten * t_soil);

    blastAttenuated = blast;
    blastAttenuated.Pr_kPa = blast.Pr_kPa * attenFactor;
    blastAttenuated.Pso_kPa = blast.Pso_kPa * attenFactor;
    blastAttenuated.iso_kPa_ms = blast.iso_kPa_ms * attenFactor;

    % Yapisal (sunek) katman olarak UHPC (varsa) yoksa metal destek kullanilir
    if isfield(design, 'uhpcMat') && ~isempty(design.uhpcMat) && design.t_uhpc_mm > 0
        structLayer = design.uhpcMat;
        structLayer.thickness_mm = design.t_uhpc_mm;
    elseif isfield(design, 'metalMat') && ~isempty(design.metalMat) && design.t_metal_mm > 0
        structLayer = design.metalMat;
        structLayer.thickness_mm = design.t_metal_mm;
    else
        structLayer = struct('thickness_mm', 0, 'sigma_y_MPa', 0, 'E_GPa', 1, 'mu_allow', 1);
    end

    blastDetail = sdofPanelResponse(blastAttenuated, structLayer, AD_total, panelSpan_m);
    blastFeasible = blastDetail.survives;
end

feasible = keFeasible && blastFeasible;

score = weights.w_weight * AD_total + weights.w_logistic * logisticScore;
if ~feasible
    % Fizibil olmayan tasarimlari agir cezalandir (optimizer bu bolgeden uzaklasir)
    penalty = 0;
    if ~keFeasible
        penalty = penalty + max(0, keDetail.AD_RHA_req_kg_m2 - keDetail.AD_RHA_equiv_kg_m2) * 100;
    end
    if ~blastFeasible && ~isempty(blastDetail)
        penalty = penalty + max(0, blastDetail.mu_demand - blastDetail.mu_allow) * 500;
        penalty = penalty + max(0, blastDetail.X_max_m - blastDetail.BFS_limit_m) * 1e5;
    end
    score = score + 1e4 + penalty;
end

result.feasible = feasible;
result.AD_total_kg_m2 = AD_total;
result.AD_RHA_equiv_kg_m2 = AD_RHA_equiv;
result.logisticScore = logisticScore;
result.score = score;
result.keFeasible = keFeasible;
result.blastFeasible = blastFeasible;
result.keDetail = keDetail;
result.blastDetail = blastDetail;
result.design = design;

end
