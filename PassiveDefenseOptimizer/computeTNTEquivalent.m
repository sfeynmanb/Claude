function [W_TNT, matchedExplosive] = computeTNTEquivalent(mass_kg, explosiveName, explosives)
%COMPUTETNTEQUIVALENT Patlayici kutlesini TNT esdegerine cevirir.
%   [W_TNT, matchedExplosive] = COMPUTETNTEQUIVALENT(mass_kg, explosiveName, explosives)
%   W_TNT = mass_kg * RE_factor  (RE Faktoru = Relative Effectiveness,
%   TNT'ye gore agirlikca esdeger patlayici enerjisi orani).
%
%   explosiveName bos birakilirsa veya veritabaninda bulunamazsa, RE=1.00
%   (dogrudan TNT) varsayilir ve kullaniciya bilgi notu birakilir.

if nargin < 3 || isempty(explosives)
    explosives = loadExplosiveDatabase();
end

matchedExplosive = [];
RE = 1.00;

if ~isempty(explosiveName)
    names = {explosives.name};
    idx = find(~cellfun('isempty', strfind(lower(names), lower(explosiveName))), 1);
    if ~isempty(idx)
        matchedExplosive = explosives(idx);
        RE = matchedExplosive.RE_factor;
    end
end

W_TNT = mass_kg * RE;

end
