function plotResults(threat, searchTrace, optimum_design, scaledTable, damageTable, axesHandles)
%PLOTRESULTS Pareto Front, Kalinlik-Beka ve Mesafe-Hasar Olasiligi grafiklerini uretir.
%   PLOTRESULTS(threat, searchTrace, optimum_design, scaledTable, damageTable)
%   kendi figurunu acip 2x2 duzeninde ciziyor (komut satiri kullanimi).
%
%   PLOTRESULTS(..., axesHandles) var olan 4 adet eksen tutamacina (ornegin
%   bir uifigure icindeki 4 uiaxes) cizim yapar; yeni figur ACMAZ. Bu,
%   PassiveDefenseOptimizerApp.m tarafindan grafikleri uygulama penceresi
%   icine gommek icin kullanilir. axesHandles = [ax1 ax2 ax3 ax4].
%
%   Panel duzeni (her iki modda da ayni):
%     (1) Pareto Front       : Alan Yogunlugu (kg/m^2) - Skor, fizibil/degil.
%     (2) Kalinlik vs Beka    : Birincil katman kalinligi vs toplam alan yogunlugu.
%     (3) Z vs Asiri Basinc   : (yalniz HE/HE_FRAG) veya KE icin Kalan Hiz grafigi.
%     (4) Z vs Hasar Olasiligi: (yalniz HE/HE_FRAG) veya KE icin bos/bilgi notu.

if nargin < 6 || isempty(axesHandles)
    figure('Name', 'Pasif Savunma Optimizasyonu - Sonuc Grafikleri', 'Position', [100 100 1000 760]);
    ax1 = subplot(2,2,1); ax2 = subplot(2,2,2); ax3 = subplot(2,2,3); ax4 = subplot(2,2,4);
else
    ax1 = axesHandles(1); ax2 = axesHandles(2); ax3 = axesHandles(3); ax4 = axesHandles(4);
    cla(ax1); cla(ax2); cla(ax3); cla(ax4);
end

% ---------------- Panel 1: Pareto Front (Alan Yogunlugu vs Skor) ----------------
AD = [searchTrace.AD_total];
sc = [searchTrace.score];
feas = logical([searchTrace.feasible]);

hold(ax1, 'on');
if any(~feas)
    scatter(ax1, AD(~feas), sc(~feas), 10, [0.85 0.33 0.10], 'filled');
end
if any(feas)
    scatter(ax1, AD(feas), sc(feas), 14, [0.10 0.60 0.20], 'filled');
end
if ~isempty(optimum_design)
    plot(ax1, optimum_design.AD_total_kg_m2, optimum_design.score, 'kp', ...
        'MarkerSize', 16, 'MarkerFaceColor', [1 0.84 0]);
end
xlabel(ax1, 'Toplam Alan Yogunlugu - Areal Density [kg/m^2]');
ylabel(ax1, 'Skor (dusuk = daha iyi)');
title(ax1, 'Pareto Front: Agirlik vs Uygunluk Skoru');
legend(ax1, {'Fizibil Degil', 'Fizibil (Sart Saglaniyor)', 'Secilen Optimum'}, 'Location', 'northeast');
grid(ax1, 'on'); box(ax1, 'on'); hold(ax1, 'off');

% ---------------- Panel 2: Kalinlik vs Beka ----------------
t1 = [searchTrace.t1];
[t1s, idxSort] = sort(t1);
hold(ax2, 'on');
scatter(ax2, t1s(~feas(idxSort)), AD(idxSort(~feas(idxSort))), 8, [0.85 0.33 0.10], 'filled');
scatter(ax2, t1s(feas(idxSort)), AD(idxSort(feas(idxSort))), 8, [0.10 0.60 0.20], 'filled');
if strcmpi(threat.type, 'HE')
    xlabel(ax2, 'Birincil Katman Kalinligi (UHPC) [mm]');
else
    xlabel(ax2, 'Birincil Katman Kalinligi (Seramik) [mm]');
end
ylabel(ax2, 'Toplam Alan Yogunlugu [kg/m^2]');
title(ax2, 'Kalinlik vs Beka (Yesil = Sart Saglaniyor)');
grid(ax2, 'on'); box(ax2, 'on'); hold(ax2, 'off');

% ---------------- Panel 3 & 4: Z vs Basinc / Hasar Olasiligi (HE, HE_FRAG) ----------------
if strcmpi(threat.type, 'HE') || strcmpi(threat.type, 'HE_FRAG')
    Zsweep = linspace(scaledTable.Z(1), scaledTable.Z(end), 200);
    Psweep = exp(interp1(log(scaledTable.Z), log(scaledTable.Pso), log(Zsweep), 'linear', 'extrap'));

    semilogy(ax3, Zsweep, Psweep, 'b-', 'LineWidth', 1.8);
    xlabel(ax3, 'Olceklendirilmis Mesafe Z = R / W^{1/3} [m/kg^{1/3}]');
    ylabel(ax3, 'Gelen Asiri Basinc P_{so} [kPa]');
    title(ax3, 'Mesafe (Z) vs Asiri Basinc (Kingery-Bulmash)');
    grid(ax3, 'on');

    validIdx = ~isnan(damageTable.pLethalFraction);
    Pcrit = damageTable.Pcrit_kPa(validIdx);
    pLeth = damageTable.pLethalFraction(validIdx);
    [Pcrit, order] = sort(Pcrit);
    pLeth = pLeth(order);
    pInterp = interp1(Pcrit, pLeth, Psweep, 'linear', 'extrap');
    pInterp = min(max(pInterp, 0), 1);
    plot(ax4, Zsweep, pInterp, 'r-', 'LineWidth', 1.8);
    xlabel(ax4, 'Olceklendirilmis Mesafe Z = R / W^{1/3} [m/kg^{1/3}]');
    ylabel(ax4, 'Yaklasik Olumcul Hasar Olasiligi [-]');
    ylim(ax4, [0 1]);
    title(ax4, 'Mesafe (Z) vs Hasar Olasiligi (Bowen Egrisi Yaklasimi)');
    grid(ax4, 'on');
else
    % KE tehdit: Carpma Hizi - Kalan Hiz (Lambert-Jonas) marj grafigi (ax3 icine)
    V_bl_sweep = linspace(0.5*threat.v_impact_ms, 1.5*threat.v_impact_ms, 100);
    Vr_sweep = arrayfun(@(vbl) residualVelocityLambertJonas(threat.v_impact_ms, vbl), V_bl_sweep);

    hold(ax3, 'on');
    plot(ax3, V_bl_sweep, Vr_sweep, 'm-', 'LineWidth', 1.8);
    plot(ax3, V_bl_sweep, zeros(size(V_bl_sweep)), 'k:');
    xlabel(ax3, 'Varsayimsal Balistik Limit Hizi V_{bl} [m/s]');
    ylabel(ax3, 'Kalan Hiz V_r (Lambert-Jonas) [m/s]');
    title(ax3, sprintf('Carpma Hizi (%.0f m/s) icin Kalan Hiz Duyarliligi', threat.v_impact_ms));
    grid(ax3, 'on'); box(ax3, 'on'); hold(ax3, 'off');

    text(ax4, 0.5, 0.5, 'KE tehdidinde kullanilmaz (yalniz HE / HE\_FRAG)', ...
        'HorizontalAlignment', 'center', 'Units', 'normalized');
    set(ax4, 'XTick', [], 'YTick', []);
    title(ax4, 'Mesafe (Z) vs Hasar Olasiligi');
end

end
