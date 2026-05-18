
% =========================================================================
% BÜTÜNSEL KAYNAK TEORİSİ (UST) v5 - ADIM 1 SİMÜLASYONU
% Kesintili (Geçersiz) vs Sürekli (Geçerli) Ağ Bağlantısallığı Karşılaştırması
% =========================================================================

% 1. UST v5 Evrensel Sabitleri
T_Om = 0.23252885; % Kanal C / Dondurulmuş Arka Plan Sınırı
N_b  = 0.63354460; % Kanal Q / Aktif Enformasyon Akışı Sınırı

% 2. GEÇERSİZ VERİ SİMÜLASYONU (s01_dataset3corticalParc.dlabel.nii benzeri)
% Özellikler: Dışarıdan kümelenmiş, 16 benzersiz değer, kesintili
N_invalid = 81924;
data_invalid = randi( N_invalid, 1); 

% 3. GEÇERLİ VERİ SİMÜLASYONU (tfMRI_ALLTASKS_cohensd.dscalar.nii benzeri)
% Özellikler: Ham, sürekli dağılım (mu=0.016221, sigma=0.525782)
N_valid = 7850252;
mu = 0.016221;
sigma = 0.525782;
data_valid = mu + sigma * randn(N_valid, 1);

% 4. GRAFİKSEL GÖSTERİM (FİGÜR OLUŞTURMA)
fig = figure('Name', 'UST v5 Falsifikasyon Spektrumu');

% --- Alt Grafik 1: Geçersiz Kesintili Veri ---
subplot(1, 2, 1);
histogram(data_invalid, 'BinEdges', -0.5:15.5, 'FaceColor', [0.7 0.3 0.3]);
title('GEÇERSİZ VERİ (Dışarıdan Etiketlenmiş Parcellation)');
subtitle('UST Adım 1 Uygulanamaz: Süreklilik Yok');
xlabel('Kategorik Bölge Numaraları (0 - 15)');
ylabel('Düğüm (Node) Frekansı');
grid on;
ax = gca; ax.FontSize = 10;
text(7.5, max(ylim)*0.5, 'YÜZDELİK DİLİM HESAPLANAMAZ', 'HorizontalAlignment', 'center', 'BackgroundColor', 'w', 'Color', 'r', 'FontWeight', 'bold');

% --- Alt Grafik 2: Geçerli Sürekli Veri (Yığışımlı Dağılım - CDF) ---
subplot(1, 2, 2);
h = cdfplot(data_valid);
set(h, 'LineWidth', 2, 'Color', 'k');
title('GEÇERLİ VERİ (Sürekli fMRI BOLD Matrisi)');
subtitle('ONL Üç Bölgeli Bölümleme (Kanal C, 0-Element, Kanal Q)');
xlabel('Fiziksel Aktivasyon Büyüklüğü (Cohen''s d)');
ylabel('Yığışımlı Ağ Olasılığı (CDF)');
hold on;
grid on;

% UST Yüzdelik Dilim (Percentile) Eşiklerinin Hesaplanması ve Çizilmesi
thr_TOm = prctile(data_valid, T_Om * 100);
thr_Nb = prctile(data_valid, N_b * 100);

yline(T_Om, '--b', sprintf('Kanal C Sınırı (T_{Om} = %.4f)', T_Om), 'LineWidth', 1.5, 'LabelHorizontalAlignment', 'left');
yline(N_b, '--r', sprintf('Kanal Q Sınırı (N_b = %.4f)', N_b), 'LineWidth', 1.5, 'LabelHorizontalAlignment', 'left');

xline(thr_TOm, ':b', sprintf('%.3f d', thr_TOm), 'LineWidth', 1.5, 'LabelVerticalAlignment', 'bottom');
xline(thr_Nb, ':r', sprintf('%.3f d', thr_Nb), 'LineWidth', 1.5, 'LabelVerticalAlignment', 'bottom');

% Bölgelerin Renklendirilmesi (Arka Plan Yamaları)
ylims = ylim; xlims = xlim;
patch([xlims(1) thr_TOm thr_TOm xlims(1)], [0 0 T_Om T_Om], 'b', 'FaceAlpha', 0.1, 'EdgeColor', 'none');
patch([thr_TOm thr_Nb thr_Nb thr_TOm], [T_Om T_Om N_b N_b], 'g', 'FaceAlpha', 0.1, 'EdgeColor', 'none');
patch([thr_Nb xlims(2) xlims(2) thr_Nb], [N_b N_b 1 1], 'r', 'FaceAlpha', 0.1, 'EdgeColor', 'none');

% Açıklamalar
text(thr_TOm/2 + xlims(1)/2, T_Om/2, 'Kanal C (Dondurulmuş)', 'HorizontalAlignment', 'center', 'FontSize', 9);
text((thr_TOm + thr_Nb)/2, (T_Om + N_b)/2, '0-Element (Omnium)', 'HorizontalAlignment', 'center', 'FontSize', 9, 'FontWeight', 'bold');
text((thr_Nb + xlims(2))/2, (N_b + 1)/2, 'Kanal Q (Aktif Akış)', 'HorizontalAlignment', 'center', 'FontSize', 9);

ax2 = gca; ax2.FontSize = 10;
hold off;
