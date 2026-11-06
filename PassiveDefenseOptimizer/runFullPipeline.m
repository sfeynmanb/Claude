function out = runFullPipeline(threat, panelSpan_m, materials, explosives, scaledTable, damageTable)
%RUNFULLPIPELINE Tehdit girdisinden optimum tasarima kadar tum hesap hattini calistirir.
%   out = RUNFULLPIPELINE(threat, panelSpan_m, materials, explosives, scaledTable, damageTable)
%   STANAG siniflandirmasi, kinetik enerji metrikleri, De Marre penetrasyon
%   gereksinimi, patlama yuku ve pasif savunma optimizasyonunu tek bir
%   cagri ile calistirir. main_PassiveDefenseOptimizer.m (komut satiri) ve
%   PassiveDefenseOptimizerApp.m (etkilesimli uygulama) tarafindan ORTAK
%   olarak kullanilir; boylece hesaplama mantigi tek bir yerde tutulur.
%
%   Veritabani argumanlari (materials, explosives, scaledTable, damageTable)
%   opsiyoneldir; verilmezse ilgili loadXxxDatabase() fonksiyonlari ile
%   otomatik yuklenir (tekrarli cagrilarda performans icin disaridan
%   yuklenip gecirilmesi onerilir).
%
%   Cikti 'out' struct alanlari:
%     threat, stanagLevel, marginNote, keMetrics, penInfo, blast,
%     optimum_design, searchTrace, reportStr, elapsed_s

if nargin < 3 || isempty(materials),   materials = loadMaterialDatabase();     end
if nargin < 4 || isempty(explosives),  explosives = loadExplosiveDatabase();   end
if nargin < 5 || isempty(scaledTable), scaledTable = loadBlastScaledDistanceTable(); end
if nargin < 6 || isempty(damageTable), damageTable = loadDamageThresholdTable(); end

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

t0 = tic;
[optimum_design, searchTrace] = optimizePassiveDefense(threat, materials, blast, penInfo, panelSpan_m);
elapsed_s = toc(t0);

reportStr = printDesignReport(threat, stanagLevel, marginNote, blast, keMetrics, penInfo, optimum_design);

out.threat = threat;
out.stanagLevel = stanagLevel;
out.marginNote = marginNote;
out.keMetrics = keMetrics;
out.penInfo = penInfo;
out.blast = blast;
out.optimum_design = optimum_design;
out.searchTrace = searchTrace;
out.reportStr = reportStr;
out.elapsed_s = elapsed_s;
out.materials = materials;
out.scaledTable = scaledTable;
out.damageTable = damageTable;

end
