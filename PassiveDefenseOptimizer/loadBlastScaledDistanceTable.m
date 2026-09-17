function T = loadBlastScaledDistanceTable()
%LOADBLASTSCALEDDISTANCETABLE Kingery-Bulmash tipi olceklendirilmis mesafe tablosu.
%   T = LOADBLASTSCALEDDISTANCETABLE() serbest hava patlamasi icin
%   Z = R / W^(1/3) olceklendirilmis mesafeye karsi gelen basinc/impuls
%   degerlerini dondurur (blastLoad.m icinde log-log interpolasyon ile
%   kullanilir).
%
%   Sutunlar: Z [m/kg^1/3], Pso [kPa] (gelen asiri basinc),
%             Pr [kPa] (yansiyan asiri basinc), td [ms] (pozitif faz suresi),
%             iso [kPa*ms] (gelen impuls)
%
%   Kaynak: Veri seti "Patlama ve Sok Dalgasi" sayfasi (Kingery-Bulmash
%   yaklasimina dayali, CONWEP ile uyumlu tipik degerler).

T.Z   = [0.50, 1.00, 1.50, 2.00, 3.00, 4.00, 5.00, 10.00];
T.Pso = [3800.0, 680.0, 250.0, 130.0, 60.0, 35.0, 23.0, 7.5];
T.Pr  = [25000.0, 3500.0, 950.0, 400.0, 150.0, 80.0, 50.0, 15.0];
T.td  = [0.8, 1.5, 2.2, 2.8, 3.5, 4.2, 5.0, 8.0];
T.iso = [650.0, 220.0, 110.0, 70.0, 40.0, 25.0, 18.0, 6.5];

end
