function [optimum_design, searchTrace] = optimizePassiveDefense(threat, materials, blast, penInfo, panelSpan_m)
%OPTIMIZEPASSIVEDEFENSE Pasif savunma konfigurasyonu optimizasyonu (COK KATMANLI).
%   [optimum_design, searchTrace] = OPTIMIZEPASSIVEDEFENSE(threat, materials, blast, penInfo, panelSpan_m)
%
%   Tehdit tipine gore aktif katman kumesini secer ve KABA -> INCE (coarse-to-fine)
%   sezgisel izgara (grid) taramasi ile, evaluateDesign.m icindeki SARTLARI
%   (penetrasyon=0 ve/veya SDOF suneklik+BFS siniri) saglayan, MINIMUM
%   agirlikli skora (alan yogunlugu + lojistik zorluk) sahip dizilimi bulur.
%
%   Eger kullanicinin MATLAB kurulumunda Optimization Toolbox mevcutsa
%   (fmincon), kaba tarama sonucunu baslangic noktasi olarak kullanarak
%   surekli degiskenlerde ince ayar (yerel iyilestirme) yapilir. Toolbox
%   yoksa sonuc, sezgisel izgara taramasindan dogrudan alinir (govde algoritma).
%
%   searchTrace: gorsellestirme icin taranan tum adaylarin (AD_total, score,
%   feasible, degisken degerleri) kaydini icerir.

materialsByClass = @(cls) materials(strcmp({materials.class}, cls));
ceramicCandidates   = materialsByClass('Seramik');
compositeCandidates = materialsByClass('Kompozit');
uhpcCandidates       = materialsByClass('UHPC');
metalCandidates      = materialsByClass('Metal');
metalCandidates      = metalCandidates(ismember({metalCandidates.name}, {'RHA (MIL-A-12560)', 'AR500 (Hardox)'}));
soilCandidates        = materialsByClass('Toprak');

weights = struct('w_weight', 1.0, 'w_logistic', 0.15);

bestResult = [];
searchTrace = struct('t1', {}, 't2', {}, 't3', {}, 't4', {}, 'AD_total', {}, 'score', {}, 'feasible', {});

switch upper(threat.type)
    case 'KE'
        % Degiskenler: seramik (on yuz), kompozit (arka/spall), metal (yapisal destek)
        ceramicRange   = 0:2:30;   % mm
        compositeRange = 0:2:25;   % mm
        metalRange     = 0:2:16;   % mm

        for ci = 1:numel(ceramicCandidates)
            for mi = 1:numel(metalCandidates)
                for tc = ceramicRange
                    for tcomp = compositeRange
                        for tm = metalRange
                            design = makeDesign(ceramicCandidates(ci), tc, compositeCandidates(1), tcomp, ...
                                [], 0, metalCandidates(mi), tm, [], 0);
                            res = evaluateDesign(threat, design, materials, blast, penInfo, panelSpan_m, weights);
                            searchTrace(end+1) = struct('t1', tc, 't2', tcomp, 't3', tm, 't4', NaN, ...
                                'AD_total', res.AD_total_kg_m2, 'score', res.score, 'feasible', res.feasible); %#ok<AGROW>
                            bestResult = keepBest(bestResult, res);
                        end
                    end
                end
            end
        end
        % Ince tarama: en iyi kaba sonuc etrafinda +-2 adim, 0.5mm cozunurlukle
        bestResult = refineAroundBest(bestResult, threat, materials, blast, penInfo, panelSpan_m, weights, ...
            {'t_ceramic_mm', 't_composite_mm', 't_metal_mm'}, [0.5, 0.5, 0.5], [4, 4, 4]);

    case 'HE'
        % Degiskenler: UHPC (yapisal/blast), kompozit (spall-liner), toprak (standoff/sonumleme)
        uhpcRange      = 0:15:225;   % mm
        compositeRange = 0:2:20;     % mm
        soilRange      = 0:0.15:1.5; % m

        for tu = uhpcRange
            for tcomp = compositeRange
                for ts = soilRange
                    design = makeDesign([], 0, compositeCandidates(1), tcomp, ...
                        uhpcCandidates(1), tu, [], 0, soilCandidates(1), ts);
                    res = evaluateDesign(threat, design, materials, blast, penInfo, panelSpan_m, weights);
                    searchTrace(end+1) = struct('t1', tu, 't2', tcomp, 't3', ts, 't4', NaN, ...
                        'AD_total', res.AD_total_kg_m2, 'score', res.score, 'feasible', res.feasible); %#ok<AGROW>
                    bestResult = keepBest(bestResult, res);
                end
            end
        end
        bestResult = refineAroundBest(bestResult, threat, materials, blast, penInfo, panelSpan_m, weights, ...
            {'t_uhpc_mm', 't_composite_mm', 't_soil_m'}, [3, 0.5, 0.03], [15, 2, 0.15]);

    case 'HE_FRAG'
        % Kombine tehdit: seramik + UHPC + kompozit + toprak (dort degiskenli, kaba izgara)
        ceramicRange   = 0:5:25;    % mm
        uhpcRange      = 0:25:200;  % mm
        compositeRange = 0:4:20;    % mm
        soilRange      = 0:0.3:1.2; % m

        for ci = 1:numel(ceramicCandidates)
            for tc = ceramicRange
                for tu = uhpcRange
                    for tcomp = compositeRange
                        for ts = soilRange
                            design = makeDesign(ceramicCandidates(ci), tc, compositeCandidates(1), tcomp, ...
                                uhpcCandidates(1), tu, [], 0, soilCandidates(1), ts);
                            res = evaluateDesign(threat, design, materials, blast, penInfo, panelSpan_m, weights);
                            searchTrace(end+1) = struct('t1', tc, 't2', tu, 't3', tcomp, 't4', ts, ...
                                'AD_total', res.AD_total_kg_m2, 'score', res.score, 'feasible', res.feasible); %#ok<AGROW>
                            bestResult = keepBest(bestResult, res);
                        end
                    end
                end
            end
        end
        bestResult = refineAroundBest(bestResult, threat, materials, blast, penInfo, panelSpan_m, weights, ...
            {'t_ceramic_mm', 't_uhpc_mm', 't_composite_mm', 't_soil_m'}, [1, 5, 1, 0.05], [5, 25, 4, 0.3]);

    otherwise
        error('optimizePassiveDefense:UnknownThreatType', ...
            'threat.type ''KE'', ''HE'' veya ''HE_FRAG'' olmalidir.');
end

optimum_design = bestResult;

% --- Opsiyonel: Optimization Toolbox mevcutsa fmincon ile yerel ince ayar ---
if license('test', 'Optimization_Toolbox') && exist('fmincon', 'file') == 2 && ~isempty(bestResult)
    try
        optimum_design = refineWithFmincon(optimum_design, threat, materials, blast, penInfo, panelSpan_m, weights);
    catch
        % fmincon basarisiz olursa sezgisel sonuc korunur (govde algoritma)
    end
end

end

% =====================================================================
function design = makeDesign(ceramicMat, t_ceramic, compositeMat, t_composite, ...
    uhpcMat, t_uhpc, metalMat, t_metal, soilMat, t_soil)
design.ceramicMat = ceramicMat;     design.t_ceramic_mm = t_ceramic;
design.compositeMat = compositeMat; design.t_composite_mm = t_composite;
design.uhpcMat = uhpcMat;           design.t_uhpc_mm = t_uhpc;
design.metalMat = metalMat;         design.t_metal_mm = t_metal;
design.soilMat = soilMat;           design.t_soil_m = t_soil;
end

% =====================================================================
function best = keepBest(best, candidate)
if isempty(best)
    best = candidate;
    return;
end
betterFeasible = candidate.feasible && (~best.feasible || candidate.score < best.score);
betterInfeasible = ~best.feasible && ~candidate.feasible && candidate.score < best.score;
if betterFeasible || betterInfeasible
    best = candidate;
end
end

% =====================================================================
function best = refineAroundBest(best, threat, materials, blast, penInfo, panelSpan_m, weights, ...
    fieldNames, fineStep, coarseHalfWindow)
%REFINEAROUNDBEST En iyi kaba sonuc etrafinda daha ince cozunurlukte yerel arama.
if isempty(best)
    return;
end
design0 = best.design;
ranges = cell(1, numel(fieldNames));
for k = 1:numel(fieldNames)
    center = design0.(fieldNames{k});
    lo = max(0, center - coarseHalfWindow(k));
    hi = center + coarseHalfWindow(k);
    ranges{k} = lo:fineStep(k):hi;
end

switch numel(fieldNames)
    case 3
        for a = ranges{1}
            for b = ranges{2}
                for c = ranges{3}
                    design = design0;
                    design.(fieldNames{1}) = a;
                    design.(fieldNames{2}) = b;
                    design.(fieldNames{3}) = c;
                    res = evaluateDesign(threat, design, materials, blast, penInfo, panelSpan_m, weights);
                    best = keepBest(best, res);
                end
            end
        end
    case 4
        for a = ranges{1}
            for b = ranges{2}
                for c = ranges{3}
                    for d = ranges{4}
                        design = design0;
                        design.(fieldNames{1}) = a;
                        design.(fieldNames{2}) = b;
                        design.(fieldNames{3}) = c;
                        design.(fieldNames{4}) = d;
                        res = evaluateDesign(threat, design, materials, blast, penInfo, panelSpan_m, weights);
                        best = keepBest(best, res);
                    end
                end
            end
        end
end
end

% =====================================================================
function optimum = refineWithFmincon(optimum, threat, materials, blast, penInfo, panelSpan_m, weights)
%REFINEWITHFMINCON Sezgisel sonucu, mevcutsa fmincon ile surekli uzayda ince ayar yapar.
design0 = optimum.design;

switch upper(threat.type)
    case 'KE'
        fields = {'t_ceramic_mm', 't_composite_mm', 't_metal_mm'};
        ub = [40, 35, 20];
    case 'HE'
        fields = {'t_uhpc_mm', 't_composite_mm', 't_soil_m'};
        ub = [250, 30, 2.0];
    otherwise
        fields = {'t_ceramic_mm', 't_uhpc_mm', 't_composite_mm', 't_soil_m'};
        ub = [30, 220, 25, 1.5];
end

x0 = zeros(1, numel(fields));
for k = 1:numel(fields)
    x0(k) = design0.(fields{k});
end

costFcn = @(x) localCost(x, fields, design0, threat, materials, blast, penInfo, panelSpan_m, weights);

opts = optimoptions('fmincon', 'Display', 'off');
lb = zeros(size(x0));
xOpt = fmincon(costFcn, x0, [], [], [], [], lb, ub, [], opts);

designOpt = design0;
for k = 1:numel(fields)
    designOpt.(fields{k}) = max(0, xOpt(k));
end
resOpt = evaluateDesign(threat, designOpt, materials, blast, penInfo, panelSpan_m, weights);

if resOpt.feasible && resOpt.score < optimum.score
    optimum = resOpt;
end
end

function c = localCost(x, fields, design0, threat, materials, blast, penInfo, panelSpan_m, weights)
design = design0;
for k = 1:numel(fields)
    design.(fields{k}) = max(0, x(k));
end
res = evaluateDesign(threat, design, materials, blast, penInfo, panelSpan_m, weights);
c = res.score;
end
