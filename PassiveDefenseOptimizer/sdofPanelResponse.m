function sdof = sdofPanelResponse(blast, structLayer, AD_total_kg_m2, panelSpan_m)
%SDOFPANELRESPONSE Tek Serbestlik Dereceli (SDOF) elasto-plastik panel tepkisi.
%   sdof = SDOFPANELRESPONSE(blast, structLayer, AD_total_kg_m2, panelSpan_m)
%   basitlestirilmis Biggs/UFC 3-340-02 SDOF metodolojisiyle, blast yukü
%   altinda tek yonlu (basit mesnetli) yapisal panelin (UHPC veya metal
%   destek katmani) sunek tepkisini hesaplar.
%
%   Yontem (1 m genislikte serit / birim genislik yaklasimi, b=1m):
%     1) Plastik moment kapasitesi:      M_p = sigma_flex * (t^2/4)
%     2) Ultimate (plastik) yayilma yuku: w_ult = 8*M_p / L^2   -> R_u [Pa]
%     3) Elastik egilme rijitligi:        k = 384*E*I / (5*L^4), I=t^3/12
%     4) Elastik sinir deplasman:         X_el = R_u / k
%     5) Dogal frekans:                   wn = sqrt(k / (AD_total))
%     6) Yuk suresi orani td/Tn ile rejim (impulsif/dinamik/yari-statik)
%     7) Impulsif enerji dengesi ile maksimum deplasman ve suneklik talebi:
%          v0 = i_r / AD_total  (yansiyan impuls / birim alan kutlesi)
%          KE = 0.5*AD_total*v0^2
%          X_max = X_el/2 + KE/R_u   (elasto-plastik enerji dengesi)
%          mu_demand = X_max / X_el
%
%   Girdi:
%     blast           - blastLoad.m ciktisi (Pr_kPa, iso_kPa_ms, Pso_kPa)
%     structLayer     - materials struct elemani (yapisal/sunek katman: UHPC/Metal)
%     AD_total_kg_m2  - Panelin TOPLAM alan yogunlugu (tum katmanlarin kutlesi, atalet icin)
%     panelSpan_m     - Panel acikligi (mesnetler arasi mesafe) [m]
%
%   Cikti sdof struct: Tn_s, td_Tn_ratio, regime, X_el_m, X_max_m,
%   mu_demand, mu_allow, BFS_limit_m, survives (bool), failureReason

t_struct_m = structLayer.thickness_mm / 1000;
sigma_flex_Pa = structLayer.sigma_y_MPa * 1e6;
E_Pa = structLayer.E_GPa * 1e9;
mu_allow = structLayer.mu_allow;

BFS_limit_m = 0.044;   % NIJ/veri seti Arka Yuzey Cokmesi (BFS) kritik esigi = 44 mm

if t_struct_m <= 0
    sdof.survives = false;
    sdof.failureReason = 'Yapisal (sunek) katman kalinligi sifir - blast yuku tasiyamaz.';
    sdof.mu_demand = Inf; sdof.mu_allow = mu_allow; sdof.X_max_m = Inf; sdof.X_el_m = 0;
    sdof.Tn_s = NaN; sdof.td_Tn_ratio = NaN; sdof.regime = 'N/A'; sdof.BFS_limit_m = BFS_limit_m;
    return;
end

L = panelSpan_m;

% --- Plastik / elastik kapasite (birim genislik, b = 1 m) ---
Z_p = t_struct_m^2 / 4;
M_p = sigma_flex_Pa * Z_p;          % [N*m] (birim genislikte)
w_ult = 8 * M_p / L^2;              % [N/m] -> b=1m icin sayisal olarak R_u [Pa]
R_u_Pa = w_ult;

I_sect = t_struct_m^3 / 12;         % [m^4] (birim genislikte, m^3/m)
k_stiff = 384 * E_Pa * I_sect / (5 * L^4);   % [Pa] (birim genislikte)

X_el_m = R_u_Pa / k_stiff;

% --- Dogal frekans ve rejim tayini ---
omega_n = sqrt(k_stiff / AD_total_kg_m2);   % [rad/s]
Tn_s = 2*pi / omega_n;
td_s = blast.td_ms / 1000;
td_Tn_ratio = td_s / Tn_s;

if td_Tn_ratio < 0.1
    regime = 'Impulsif';
elseif td_Tn_ratio > 10
    regime = 'Yari-Statik';
else
    regime = 'Dinamik (Genel)';
end

% --- Yansiyan impuls (basitlestirilmis: iso * Pr/Pso reflection katsayisi) ---
reflectionFactor = blast.Pr_kPa / max(blast.Pso_kPa, eps);
i_r_Pa_s = (blast.iso_kPa_ms * reflectionFactor);   % kPa*ms == Pa*s (sayisal olarak esdeger)

v0 = i_r_Pa_s / AD_total_kg_m2;     % [m/s] - panele kazandirilan baslangic hizi
KE_per_area = 0.5 * AD_total_kg_m2 * v0^2;   % [J/m^2]

X_max_m = X_el_m/2 + KE_per_area / R_u_Pa;
mu_demand = X_max_m / X_el_m;

survives = (mu_demand <= mu_allow) && (X_max_m <= BFS_limit_m);

if ~survives
    if mu_demand > mu_allow
        failureReason = sprintf('Suneklik talebi asildi: mu=%.2f > mu_izin=%.2f', mu_demand, mu_allow);
    else
        failureReason = sprintf('Arka yuzey deplasmani BFS esigini asti: %.1f mm > 44 mm', X_max_m*1000);
    end
else
    failureReason = '';
end

sdof.Tn_s = Tn_s;
sdof.td_Tn_ratio = td_Tn_ratio;
sdof.regime = regime;
sdof.X_el_m = X_el_m;
sdof.X_max_m = X_max_m;
sdof.mu_demand = mu_demand;
sdof.mu_allow = mu_allow;
sdof.BFS_limit_m = BFS_limit_m;
sdof.survives = survives;
sdof.failureReason = failureReason;
sdof.R_u_kPa = R_u_Pa / 1000;

end
