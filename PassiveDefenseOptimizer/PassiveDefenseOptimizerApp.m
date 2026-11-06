function PassiveDefenseOptimizerApp()
%PASSIVEDEFENSEOPTIMIZERAPP Pasif Savunma Optimizasyonu - Etkilesimli Uygulama.
%   PASSIVEDEFENSEOPTIMIZERAPP() tehdit parametrelerini girmek, hazir STANAG
%   senaryolarindan secim yapmak, optimizasyonu calistirmak ve sonuc
%   raporu ile grafikleri TEK bir pencerede gormek icin etkilesimli bir
%   MATLAB uygulamasi acar.
%
%   Bu uygulama, mevcut komut-satiri aracinin (main_PassiveDefenseOptimizer.m)
%   TUM hesaplama mantigini aynen kullanir (runFullPipeline.m uzerinden);
%   burada sadece bir grafik arayuz (GUI) katmani eklenmistir. Fizik/
%   optimizasyon kodunda hicbir degisiklik yapilmamistir.
%
%   Gereksinim: MATLAB R2016b veya sonrasi (uifigure/App Designer bilesenleri).
%
%   Kullanim:
%       PassiveDefenseOptimizerApp
%
%   Ya da main_PassiveDefenseOptimizer.m ile ayni klasorde iken sadece
%   komut penceresine PassiveDefenseOptimizerApp yazip calistirabilirsiniz.

addpath(fileparts(mfilename('fullpath')));

% ---------------------------------------------------------------
% Veritabanlarini BIR KEZ yukle (her "Hesapla" tiklamasinda tekrar
% yuklenmesin diye uygulama omrunce bellekte tutulur).
% ---------------------------------------------------------------
materials   = loadMaterialDatabase();
explosives  = loadExplosiveDatabase();
scaledTable = loadBlastScaledDistanceTable();
damageTable = loadDamageThresholdTable();
presets     = loadThreatPresetDatabase();

% =================================================================
%                         ANA PENCERE VE DUZEN
% =================================================================
fig = uifigure('Name', 'Pasif Savunma Optimizasyonu - Etkilesimli Uygulama', ...
    'Position', [60 50 1340 860]);

mainGrid = uigridlayout(fig, [1 2]);
mainGrid.ColumnWidth = {380, '1x'};
mainGrid.RowHeight = {'1x'};
mainGrid.Padding = [10 10 10 10];
mainGrid.ColumnSpacing = 10;

% ----------------------- SOL PANEL: GIRDILER -----------------------
leftPanel = uipanel(mainGrid, 'Title', 'Tehdit Profili ve Parametreler', 'FontWeight', 'bold');
leftPanel.Layout.Row = 1; leftPanel.Layout.Column = 1;

formGrid = uigridlayout(leftPanel, [16 2]);
formGrid.ColumnWidth = {160, '1x'};
formGrid.RowHeight = {26,26,8,26,26,26,26,8,26,26,26,8,26,38,30,'1x'};
formGrid.RowSpacing = 6;

r = 1;
lbl = uilabel(formGrid, 'Text', 'Hazir STANAG Senaryosu', 'FontWeight', 'bold');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
presetItems = [{'Ozel (Manuel Giris)'}, arrayfun(@(p) sprintf('Seviye %d - %s', p.level, p.name), presets, 'UniformOutput', false)];
presetItemsData = [0, 1:numel(presets)];
presetDropdown = uidropdown(formGrid, 'Items', presetItems, 'ItemsData', presetItemsData, 'Value', 0);
presetDropdown.Layout.Row = r; presetDropdown.Layout.Column = 2;
r = r + 1;

lbl = uilabel(formGrid, 'Text', 'Tehdit Tipi', 'FontWeight', 'bold');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
threatTypeDropdown = uidropdown(formGrid, ...
    'Items', {'Kinetik Enerji (KE) - Zirh Delici', 'Patlayici / Blast (HE)', 'Kombine (HE + Sarapnel)'}, ...
    'ItemsData', {'KE', 'HE', 'HE_FRAG'}, 'Value', 'HE_FRAG');
threatTypeDropdown.Layout.Row = r; threatTypeDropdown.Layout.Column = 2;
r = r + 1;

r = r + 1; % bosluk satiri

lbl = uilabel(formGrid, 'Text', 'Kalibre [mm]');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
caliberField = uieditfield(formGrid, 'numeric', 'Limits', [0 Inf], 'Value', 7.62);
caliberField.Layout.Row = r; caliberField.Layout.Column = 2;
r = r + 1;

lbl = uilabel(formGrid, 'Text', 'Mermi/Sarapnel Kutlesi [g]');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
massField = uieditfield(formGrid, 'numeric', 'Limits', [0 Inf], 'Value', 9.7);
massField.Layout.Row = r; massField.Layout.Column = 2;
r = r + 1;

lbl = uilabel(formGrid, 'Text', 'Carpma Hizi [m/s]');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
velocityField = uieditfield(formGrid, 'numeric', 'Limits', [0 Inf], 'Value', 930);
velocityField.Layout.Row = r; velocityField.Layout.Column = 2;
r = r + 1;

lbl = uilabel(formGrid, 'Text', 'Penetrator Sinifi');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
penClassDropdown = uidropdown(formGrid, ...
    'Items', {'Yumusak (Kursun Cekirdek)', 'Sertlestirilmis Celik (API/AP)', ...
               'Tungsten Karbur (AP)', 'Tungsten APFSDS / Sabot'}, ...
    'ItemsData', {'Soft', 'Hardened_Steel', 'Tungsten_Carbide', 'Tungsten_APFSDS_Sabot'}, ...
    'Value', 'Tungsten_Carbide');
penClassDropdown.Layout.Row = r; penClassDropdown.Layout.Column = 2;
r = r + 1;

r = r + 1; % bosluk satiri

lbl = uilabel(formGrid, 'Text', 'Patlayici Kutlesi - NEW [kg]');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
explMassField = uieditfield(formGrid, 'numeric', 'Limits', [0 Inf], 'Value', 10.8);
explMassField.Layout.Row = r; explMassField.Layout.Column = 2;
r = r + 1;

lbl = uilabel(formGrid, 'Text', 'Patlayici Turu');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
explTypeDropdown = uidropdown(formGrid, 'Items', {explosives.name}, 'ItemsData', {explosives.name}, ...
    'Value', 'TNT (Referans)');
explTypeDropdown.Layout.Row = r; explTypeDropdown.Layout.Column = 2;
r = r + 1;

lbl = uilabel(formGrid, 'Text', 'Patlama Mesafesi - R [m]');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
standoffField = uieditfield(formGrid, 'numeric', 'Limits', [0 Inf], 'Value', 5.0);
standoffField.Layout.Row = r; standoffField.Layout.Column = 2;
r = r + 1;

r = r + 1; % bosluk satiri

lbl = uilabel(formGrid, 'Text', 'Panel Acikligi - L [m]');
lbl.Layout.Row = r; lbl.Layout.Column = 1;
panelSpanField = uieditfield(formGrid, 'numeric', 'Limits', [0.1 Inf], 'Value', 1.2);
panelSpanField.Layout.Row = r; panelSpanField.Layout.Column = 2;
r = r + 1;

runButton = uibutton(formGrid, 'Text', 'HESAPLA / OPTIMIZE ET', 'FontWeight', 'bold', ...
    'BackgroundColor', [0.10 0.45 0.20], 'FontColor', [1 1 1]);
runButton.Layout.Row = r; runButton.Layout.Column = [1 2];
r = r + 1;

statusLabel = uilabel(formGrid, 'Text', 'Hazir. Parametreleri girin ve hesaplayin.', ...
    'FontAngle', 'italic', 'WordWrap', 'on');
statusLabel.Layout.Row = r; statusLabel.Layout.Column = [1 2];

% ----------------------- SAG PANEL: SONUCLAR (SEKMELER) -----------------------
tabGroup = uitabgroup(mainGrid);
tabGroup.Layout.Row = 1; tabGroup.Layout.Column = 2;

reportTab = uitab(tabGroup, 'Title', 'Rapor');
reportGrid = uigridlayout(reportTab, [1 1]);
reportTextArea = uitextarea(reportGrid, 'Editable', 'off', 'FontName', 'Consolas', 'FontSize', 12);
reportTextArea.Value = {'Sonuc raporu burada gosterilecektir.', '', ...
    'Soldaki parametreleri girip "HESAPLA / OPTIMIZE ET" dugmesine basin.'};

plotsTab = uitab(tabGroup, 'Title', 'Grafikler');
plotsGrid = uigridlayout(plotsTab, [2 2]);
ax1 = uiaxes(plotsGrid); ax1.Layout.Row = 1; ax1.Layout.Column = 1;
ax2 = uiaxes(plotsGrid); ax2.Layout.Row = 1; ax2.Layout.Column = 2;
ax3 = uiaxes(plotsGrid); ax3.Layout.Row = 2; ax3.Layout.Column = 1;
ax4 = uiaxes(plotsGrid); ax4.Layout.Row = 2; ax4.Layout.Column = 2;
title(ax1, 'Pareto Front'); title(ax2, 'Kalinlik vs Beka');
title(ax3, 'Mesafe vs Basinc'); title(ax4, 'Mesafe vs Hasar Olasiligi');

dbTab = uitab(tabGroup, 'Title', 'Malzeme Veritabani');
dbGrid = uigridlayout(dbTab, [1 1]);
materialsTable = uitable(dbGrid, 'Data', struct2table(materials)); %#ok<NASGU>

% =================================================================
%                              CALLBACK'LER
% =================================================================
threatTypeDropdown.ValueChangedFcn = @(src, ~) onThreatTypeChanged();
presetDropdown.ValueChangedFcn = @(src, ~) onPresetChanged();
runButton.ButtonPushedFcn = @(src, ~) onRunButtonPushed();

onThreatTypeChanged();   % Baslangic etkinlik durumunu ayarla

    function onThreatTypeChanged()
        keFieldsOn = ismember(threatTypeDropdown.Value, {'KE', 'HE_FRAG'});
        heFieldsOn = ismember(threatTypeDropdown.Value, {'HE', 'HE_FRAG'});

        keEnable = onOff(keFieldsOn);
        heEnable = onOff(heFieldsOn);

        caliberField.Enable = keEnable;
        massField.Enable = keEnable;
        velocityField.Enable = keEnable;
        penClassDropdown.Enable = keEnable;

        explMassField.Enable = heEnable;
        explTypeDropdown.Enable = heEnable;
        standoffField.Enable = heEnable;
    end

    function onPresetChanged()
        idx = presetDropdown.Value;
        if idx == 0
            return;   % "Ozel (Manuel Giris)" - degisiklik yok
        end
        p = presets(idx);
        caliberField.Value = p.caliber_mm;
        massField.Value = p.mass_g;
        velocityField.Value = p.v_nominal_ms;
        penClassDropdown.Value = p.penetratorClass;
        threatTypeDropdown.Value = 'KE';
        onThreatTypeChanged();
        statusLabel.Text = sprintf('Preset yuklendi: %s. Gerekirse Tehdit Tipini degistirip devam edin.', p.name);
    end

    function onRunButtonPushed()
        threat = struct();
        threat.type = threatTypeDropdown.Value;
        threat.caliber_mm = caliberField.Value;
        threat.mass_g = massField.Value;
        threat.v_impact_ms = velocityField.Value;
        threat.penetratorClass = penClassDropdown.Value;
        threat.explosiveMass_kg = explMassField.Value;
        threat.explosiveType = explTypeDropdown.Value;
        threat.standoff_R_m = standoffField.Value;
        panelSpan_m = panelSpanField.Value;

        % --- Basit girdi dogrulamasi ---
        if ismember(threat.type, {'KE', 'HE_FRAG'}) && ...
                (threat.caliber_mm <= 0 || threat.mass_g <= 0 || threat.v_impact_ms <= 0)
            uialert(fig, 'Kalibre, kutle ve carpma hizi sifirdan buyuk olmalidir.', 'Girdi Hatasi');
            return;
        end
        if ismember(threat.type, {'HE', 'HE_FRAG'}) && ...
                (threat.explosiveMass_kg <= 0 || threat.standoff_R_m <= 0)
            uialert(fig, 'Patlayici kutlesi ve patlama mesafesi sifirdan buyuk olmalidir.', 'Girdi Hatasi');
            return;
        end

        runButton.Enable = 'off';
        statusLabel.Text = 'Optimizasyon calisiyor (izgara taramasi), lutfen bekleyin...';
        drawnow;

        try
            out = runFullPipeline(threat, panelSpan_m, materials, explosives, scaledTable, damageTable);

            reportTextArea.Value = strsplit(out.reportStr, sprintf('\n'));

            plotResults(out.threat, out.searchTrace, out.optimum_design, out.scaledTable, out.damageTable, ...
                [ax1 ax2 ax3 ax4]);

            if out.optimum_design.feasible
                feasText = 'SAGLANIYOR';
            else
                feasText = 'SAGLANMIYOR';
            end
            statusLabel.Text = sprintf('Tamamlandi: %.1f sn, %d aday degerlendirildi. Fizibilite: %s', ...
                out.elapsed_s, numel(out.searchTrace), feasText);

            tabGroup.SelectedTab = reportTab;
        catch ME
            statusLabel.Text = 'Hata olustu (asagidaki mesaja bakin).';
            uialert(fig, ME.message, 'Calistirma Hatasi');
        end

        runButton.Enable = 'on';
    end

    function s = onOff(cond)
        if cond
            s = 'on';
        else
            s = 'off';
        end
    end

end
