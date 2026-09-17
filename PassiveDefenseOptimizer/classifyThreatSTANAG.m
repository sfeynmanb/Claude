function [levelStr, matchedPreset, marginNote] = classifyThreatSTANAG(threat)
%CLASSIFYTHREATSTANAG Tehdidi STANAG 4569 Seviye 1-6 ile eslestirir.
%   [levelStr, matchedPreset, marginNote] = CLASSIFYTHREATSTANAG(threat)
%   Kinetik enerjili (KE) tehditler icin kinetik enerjiyi (E_k) STANAG
%   presetleriyle karsilastirarak, tehdidi karsilayabilecek EN DUSUK
%   (ve dolayisiyla tasarim icin yeterli/muhafazakar) seviyeyi bulur.
%   HE/Blast tehditler icin ise dogrudan "IED / Topcu Mühimmati Sarapnel
%   Etkisi" olarak etiketlenir (STANAG 4569 KE tablosu ile birebir
%   eslesmez; blast etkisi ayri degerlendirilir, bkz. blastLoad.m).
%
%   Girdi threat struct alanlari (bkz. main script):
%     threat.type  - 'KE' | 'HE' | 'HE_FRAG'
%     threat.mass_g, threat.v_impact_ms  (KE / HE_FRAG icin)

presets = loadThreatPresetDatabase();
matchedPreset = [];
marginNote = '';

if strcmpi(threat.type, 'HE')
    levelStr = 'IED / Topcu-Havan Mühimmati (Blast Etkisi Baskin)';
    return;
end

% KE veya HE_FRAG (sarapnel/parca) icin kinetik enerji tabanli siniflandirma
m_kg = threat.mass_g / 1000;
E_k = 0.5 * m_kg * threat.v_impact_ms^2;

levels = [presets.level];
KEs = [presets.KE_J];

% Her seviyenin o seviyedeki maksimum referans KE degeri (muhafazakar sinir)
uniqLevels = unique(levels);
levelMaxKE = zeros(size(uniqLevels));
for k = 1:numel(uniqLevels)
    levelMaxKE(k) = max(KEs(levels == uniqLevels(k)));
end

idx = find(E_k <= levelMaxKE, 1, 'first');
if isempty(idx)
    levelStr = sprintf('Seviye 6 Ustu (Ozel Tehdit, E_k=%.0f J)', E_k);
    marginNote = 'Tehdit STANAG 4569 Seviye 6 sinirlarinin uzerinde; ozel muhendislik incelemesi gerekir.';
else
    levelStr = sprintf('Seviye %d', uniqLevels(idx));
    % En yakin (esdeger) preseti referans olarak bul
    candidateIdx = find(levels == uniqLevels(idx));
    [~, closest] = min(abs(KEs(candidateIdx) - E_k));
    matchedPreset = presets(candidateIdx(closest));
    marginNote = sprintf('Tasarim KE = %.0f J; STANAG Seviye %d referans esik = %.0f J.', ...
        E_k, uniqLevels(idx), levelMaxKE(idx));
end

end
