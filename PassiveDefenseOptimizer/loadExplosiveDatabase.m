function explosives = loadExplosiveDatabase()
%LOADEXPLOSIVEDATABASE Patlayici madde veritabani (TNT esdegerlik icin).
%   explosives = LOADEXPLOSIVEDATABASE() her patlayici sinifi icin yogunluk,
%   detonasyon hizi, Chapman-Jouguet basinci ve TNT Esdegerlik (RE) Faktorunu
%   struct array olarak dondurur.
%
%   Kaynak: Veri seti "Temel ve Karisim Patlayicilar" sayfasi
%   (UFC 3-340-02, LLNL Explosives Handbook, Cooper - Explosives Engineering).

explosives = struct('name', {}, 'rho', {}, 'VoD_ms', {}, 'CJ_pressure_GPa', {}, ...
    'RE_factor', {}, 'source', {});

names        = {'TNT (Referans)', 'RDX (Siklonit)', 'HMX (Oktojen)', 'PETN', ...
                 'C-4 (%91 RDX)', 'Comp-B', 'ANFO'};
rho          = [1.63, 1.76, 1.89, 1.76, 1.59, 1.71, 0.84] * 1000;   % kg/m^3
VoD          = [6900, 8750, 9100, 8400, 8090, 8050, 4500];          % m/s
CJ           = [19.0, 34.0, 39.0, 31.4, 25.7, 29.0, 6.0];           % GPa
RE           = [1.00, 1.60, 1.70, 1.66, 1.34, 1.33, 0.80];          % TNT esdegerlik faktoru
source       = {'UFC 3-340-02 / Cooper Tablo 19.1', 'LLNL Explosives Handbook / UFC 3-340-02', ...
                 'Gibbs & Popolato, LASL', 'Cooper, Explosives Engineering', ...
                 'US Army FM 3-34.214', 'UFC 3-340-02 / GICHD', 'US Army FM 3-34.214'};

for i = 1:numel(names)
    explosives(i).name = names{i};
    explosives(i).rho = rho(i);
    explosives(i).VoD_ms = VoD(i);
    explosives(i).CJ_pressure_GPa = CJ(i);
    explosives(i).RE_factor = RE(i);
    explosives(i).source = source{i};
end

end
