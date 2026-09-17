function pen = deMarrePenetration(threat)
%DEMARREPENETRATION Modifiye De Marre denklemi ile gerekli RHA-esdeger kalinlik.
%   pen = DEMARREPENETRATION(threat) verilen kinetik tehdidi (mermi/sarapnel)
%   SIFIR PENETRASYON ile durdurmak icin gereken RHA-esdeger zirh kalinligini
%   (e_RHA, mm) hesaplar. Poncelet/De Marre ailesinden, mühendislik on-tasarim
%   asamasinda yaygin kullanilan basitlestirilmis form:
%
%       e_RHA [mm] = K_DM * sqrt(M_p[kg]) * V_i[m/s]^1.5 / D_p[mm]^0.75
%
%   K_DM (penetrator sinifina bagli ampirik katsayi), veri setindeki
%   "Mühimmat (5.56-155)" sayfasindaki gercek penetrasyon referanslari
%   kullanilarak KALIBRE EDILMISTIR. Ornek kalibrasyon (7.62x51mm AP M61,
%   9.5 g cekirdek, ~800 m/s @100m, RHA penetrasyonu ~14mm):
%       K_DM = 14 / (sqrt(0.0095) * 800^1.5 / 7.62^0.75) = 0.029
%
%   ONEMLI: Bu, dogrusal-olmayan penetrasyon fizigini (adiabatik kayma,
%   hidrodinamik rejim gecisi vb.) basitlestiren bir MÜHENDISLIK
%   YAKLASIMIDIR; AUTODYN/LS-DYNA hidrokod simulasyonlari ve V50 atis
%   testleri ile dogrulanmalidir.
%
%   Cikti pen struct: e_RHA_req_mm, K_DM, penetratorClass, designMargin

% Penetrator sinifina gore kalibre edilmis De Marre katsayilari [mm,kg,m/s birimlerinde]
K_DM_table = struct( ...
    'Soft',                  0.018, ...   % Kursun/kursun cekirdek (yumusak, deforme olur)
    'Hardened_Steel',        0.029, ...   % API/AP celik cekirdek (M61 verisiyle kalibre)
    'Tungsten_Carbide',      0.036, ...   % Tungsten karbur cekirdek (ufalanmaz, sert)
    'Tungsten_APFSDS_Sabot', 0.045 );     % Tungsten alt kalibreli ok/sabot (en agresif)

if isfield(threat, 'penetratorClass') && isfield(K_DM_table, threat.penetratorClass)
    K_DM = K_DM_table.(threat.penetratorClass);
    penClass = threat.penetratorClass;
else
    K_DM = K_DM_table.Hardened_Steel;   % Muhafazakar varsayilan
    penClass = 'Hardened_Steel (varsayilan)';
end

% Tasarim guvenlik payi: V50 -> V01 (guvenli/kesin-durdurma hizi) farkini
% temsil eder. Veri setindeki V50 tablosunda (Seviye 1) (940-880)/940 = %6.4
% oraninda bir marj gozlemlenmistir; muhafazakar olmasi icin %15 kullanilir.
designMargin = 1.15;

m_kg = threat.mass_g / 1000;
D_mm = threat.caliber_mm;
V_i = threat.v_impact_ms;

e_RHA_req_mm = designMargin * K_DM * sqrt(m_kg) * V_i^1.5 / D_mm^0.75;

pen.e_RHA_req_mm = e_RHA_req_mm;
pen.K_DM = K_DM;
pen.penetratorClass = penClass;
pen.designMargin = designMargin;

end
