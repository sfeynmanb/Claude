function blast = blastLoad(W_TNT_kg, R_m, scaledTable)
%BLASTLOAD Kingery-Bulmash/CONWEP tabanli patlama yukü hesaplayicisi.
%   blast = BLASTLOAD(W_TNT_kg, R_m, scaledTable) serbest hava patlamasi
%   icin olceklendirilmis mesafe Z = R / W^(1/3) hesaplar ve embedded
%   Kingery-Bulmash tablosu uzerinde LOG-LOG interpolasyon yaparak;
%   gelen asiri basinc (Pso), yansiyan asiri basinc (Pr), pozitif faz
%   suresi (td) ve gelen impulsu (iso) dondurur.
%
%   Cikti struct alanlari:
%     Z, Pso_kPa, Pr_kPa, td_ms, iso_kPa_ms, isExtrapolated (bool)
%
%   Not: Tablo araligi disina (Z<0.5 veya Z>10) dusen durumlarda
%   ekstrapolasyon yapilir ve isExtrapolated=true isaretlenir; sonuclar
%   dikkatli yorumlanmalidir (yakin-alan asiri basinclari yuksek
%   belirsizlik icerir, CONWEP/AUTODYN ile dogrulanmalidir).

if nargin < 3 || isempty(scaledTable)
    scaledTable = loadBlastScaledDistanceTable();
end

Z = R_m / (W_TNT_kg)^(1/3);

logZ = log(scaledTable.Z);
isExtrap = (Z < scaledTable.Z(1)) || (Z > scaledTable.Z(end));

Pso = exp(interp1(logZ, log(scaledTable.Pso), log(Z), 'linear', 'extrap'));
Pr  = exp(interp1(logZ, log(scaledTable.Pr),  log(Z), 'linear', 'extrap'));
td  = exp(interp1(logZ, log(scaledTable.td),  log(Z), 'linear', 'extrap'));
iso = exp(interp1(logZ, log(scaledTable.iso), log(Z), 'linear', 'extrap'));

blast.Z = Z;
blast.Pso_kPa = Pso;
blast.Pr_kPa = Pr;
blast.td_ms = td;
blast.iso_kPa_ms = iso;
blast.isExtrapolated = isExtrap;
blast.W_TNT_kg = W_TNT_kg;
blast.R_m = R_m;

end
