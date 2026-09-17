function plotResults(threat, searchTrace, optimum_design, scaledTable, damageTable)
%PLOTRESULTS Pareto Front, Kalinlik-Beka ve Mesafe-Hasar Olasiligi grafiklerini uretir.
%   PLOTRESULTS(threat, searchTrace, optimum_design, scaledTable, damageTable)
%   2x2 duzeninde bir figur olusturur:
%     (1) Pareto Front      : Taranan tum adaylarin Alan Yogunlugu (kg/m^2) -
%                              Skor uzayinda dagilimi (fizibil/fizibil-degil).
%     (2) Kalinlik vs Beka   : Birincil katman kalinligina karsi toplam alan
%                              yogunlugu ve penetrasyon/blast beka durumu.
%     (3) Z vs Asiri Basinc  : Olceklendirilmis mesafeye (Z) bagli gelen
%                              asiri basinc egrisi (yalniz HE/HE_FRAG).
%     (4) Z vs Hasar Olasiligi: Bowen egrisi tabanli yaklasik olumcul hasar
%                              olasiligi (yalniz HE/HE_FRAG).
%   KE tipi tehditlerde (3) ve (4) yerine Carpma Hizi - Kalan Hiz (Lambert-
%   Jonas) marj grafigi gosterilir.

figure('Name', 'Pasif Savunma Optimizasyonu - Sonuc Grafikleri', 'Position', [100 100 1000 760]);

% ---------------- Panel 1: Pareto Front (Alan Yogunlugu vs Skor) ----------------
subplot(2,2,1);
AD = [searchTrace.AD_total];
sc = [searchTrace.score];
feas = logical([searchTrace.feasible]);

hold on;
if any(~feas)
    scatter(AD(~feas), sc(~feas), 10, [0.85 0.33 0.10], 'filled');
end
if any(feas)
    scatter(AD(feas), sc(feas), 14, [0.10 0.60 0.20], 'filled');
end
if ~isempty(optimum_design)
    plot(optimum_design.AD_total_kg_m2, optimum_design.score, 'kp', ...
        'MarkerSize', 16, 'MarkerFaceColor', [1 0.84 0]);
end
xlabel('Toplam Alan Yogunlugu - Areal Density [kg/m^2]');
ylabel('Skor (dusuk = daha iyi)');
title('Pareto Front: Agirlik vs Uygunluk Skoru');
legend({'Fizibil Degil', 'Fizibil (Sart Saglaniyor)', 'Secilen Optimum'}, 'Location', 'northeast');
grid on; box on; hold off;

% ---------------- Panel 2: Kalinlik vs Beka ----------------
subplot(2,2,2);
t1 = [searchTrace.t1];
[t1s, idxSort] = sort(t1);
hold on;
scatter(t1s(~feas(idxSort)), AD(idxSort(~feas(idxSort))), 8, [0.85 0.33 0.10], 'filled');
scatter(t1s(feas(idxSort)), AD(idxSort(feas(idxSort))), 8, [0.10 0.60 0.20], 'filled');
if strcmpi(threat.type, 'HE')
    xlabel('Birincil Katman Kalinligi (UHPC) [mm]');
else
    xlabel('Birincil Katman Kalinligi (Seramik) [mm]');
end
ylabel('Toplam Alan Yogunlugu [kg/m^2]');
title('Kalinlik vs Beka (Yesil = Sart Saglaniyor)');
grid on; box on; hold off;

% ---------------- Panel 3 & 4: Z vs Basinc / Hasar Olasiligi (HE, HE_FRAG) ----------------
if strcmpi(threat.type, 'HE') || strcmpi(threat.type, 'HE_FRAG')
    Zsweep = linspace(scaledTable.Z(1), scaledTable.Z(end), 200);
    Psweep = exp(interp1(log(scaledTable.Z), log(scaledTable.Pso), log(Zsweep), 'linear', 'extrap'));

    subplot(2,2,3);
    semilogy(Zsweep, Psweep, 'b-', 'LineWidth', 1.8);
    xlabel('Olceklendirilmis Mesafe Z = R / W^{1/3} [m/kg^{1/3}]');
    ylabel('Gelen Asiri Basinc P_{so} [kPa]');
    title('Mesafe (Z) vs Asiri Basinc (Kingery-Bulmash)');
    grid on;

    subplot(2,2,4);
    validIdx = ~isnan(damageTable.pLethalFraction);
    Pcrit = damageTable.Pcrit_kPa(validIdx);
    pLeth = damageTable.pLethalFraction(validIdx);
    [Pcrit, order] = sort(Pcrit);
    pLeth = pLeth(order);
    pInterp = interp1(Pcrit, pLeth, Psweep, 'linear', 'extrap');
    pInterp = min(max(pInterp, 0), 1);
    plot(Zsweep, pInterp, 'r-', 'LineWidth', 1.8);
    xlabel('Olceklendirilmis Mesafe Z = R / W^{1/3} [m/kg^{1/3}]');
    ylabel('Yaklasik Olumcul Hasar Olasiligi [-]');
    ylim([0 1]);
    title('Mesafe (Z) vs Hasar Olasiligi (Bowen Egrisi Yaklasimi)');
    grid on;
else
    % KE tehdit: Carpma Hizi - Kalan Hiz (Lambert-Jonas) marj grafigi
    V_bl_sweep = linspace(0.5*threat.v_impact_ms, 1.5*threat.v_impact_ms, 100);
    % V_bl, sabit e_RHA_req icin K_DM'den geri cozulur (V_i yerine V_bl ekseni taranir)
    Vr_sweep = arrayfun(@(vbl) residualVelocityLambertJonas(threat.v_impact_ms, vbl), V_bl_sweep);

    subplot(2,2,[3 4]);
    plot(V_bl_sweep, Vr_sweep, 'm-', 'LineWidth', 1.8); hold on;
    plot(V_bl_sweep, zeros(size(V_bl_sweep)), 'k:');
    xlabel('Varsayimsal Balistik Limit Hizi V_{bl} [m/s]');
    ylabel('Kalan Hiz V_r (Lambert-Jonas) [m/s]');
    title(sprintf('Carpma Hizi (%.0f m/s) icin Kalan Hiz Duyarliligi', threat.v_impact_ms));
    grid on; box on; hold off;
end

end
