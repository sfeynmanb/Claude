function ke = kineticEnergyMetrics(threat)
%KINETICENERGYMETRICS Kinetik tehdit icin enerji/kesit metriklerini hesaplar.
%   ke = KINETICENERGYMETRICS(threat) mermi/sarapnel kutlesi, hizi ve
%   capindan; Kinetik Enerji, Kesit Alani, Kesit Yogunlugu (Sectional
%   Density) ve Enerji Yogunlugunu hesaplar (veri setindeki FSP sayfasi
%   ile ayni tanimlar: E_k=0.5*m*v^2, A=pi*r^2, SD=m/A, E_d=E_k/A).

m_kg = threat.mass_g / 1000;
D_m = threat.caliber_mm / 1000;

ke.E_k_J = 0.5 * m_kg * threat.v_impact_ms^2;
ke.A_p_m2 = pi * (D_m/2)^2;
ke.SD_kg_m2 = m_kg / ke.A_p_m2;
ke.E_d_J_m2 = ke.E_k_J / ke.A_p_m2;

end
