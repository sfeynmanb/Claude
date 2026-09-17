function D = loadDamageThresholdTable()
%LOADDAMAGETHRESHOLDTABLE Biyolojik ve strukturel hasar esik degerleri.
%   D = LOADDAMAGETHRESHOLDTABLE() asiri basinc esiklerine karsi gelen
%   hasar olasiligi seviyelerini dondurur. "Mesafe (Z) vs Hasar Olasiligi"
%   grafiginde referans cizgileri olarak kullanilir.
%
%   Kaynak: Veri seti "Biyolojik - Hasar Matrisi" sayfasi (UFC 3-340-02,
%   Bowen Egrisi, ASCE Blast, ACI 349).

D.label = {'Kulak Zari Yirtilmasi (Esik)', 'Kulak Zari Yirtilmasi (Kritik)', ...
           'Akciger Hasari (Barotravma)', '%99 Olumcul Esik', ...
           'Tugla/Blok Duvar Yikilmasi', 'Betonarme Yuzey Parcalanmasi'};
D.Pcrit_kPa = [35, 100, 250, 450, 60, 200];
D.pLethalFraction = [0.01, 0.50, 0.90, 0.99, NaN, NaN];  % Bowen egrisi yaklasik olasilik

end
