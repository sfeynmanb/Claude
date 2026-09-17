function V_r = residualVelocityLambertJonas(V_i, V_bl)
%RESIDUALVELOCITYLAMBERTJONAS Lambert-Jonas kalan hiz (residual velocity) modeli.
%   V_r = RESIDUALVELOCITYLAMBERTJONAS(V_i, V_bl) carpma hizi V_i, balistik
%   limit hizi V_bl icin, THOR ailesi ampirik denklemlerinin yaygin
%   kullanilan basitlestirilmis formu ile kalan (perforasyon sonrasi) hizi
%   hesaplar:
%
%       V_r = (V_i^p - V_bl^p)^(1/p),   V_i > V_bl icin
%       V_r = 0,                        V_i <= V_bl icin  (perforasyon yok)
%
%   p=2 (Lambert-Jonas'in normal darbe icin onerdigi tipik deger) ve A=1
%   (near-normal impact) varsayilir. Bu, "gerekli penetrasyon derinligi"
%   yerine dogrudan raporlama/teshis amaciyla kullanilir (bkz. printDesignReport.m).

p = 2;

if V_i <= V_bl
    V_r = 0;
else
    V_r = (V_i^p - V_bl^p)^(1/p);
end

end
