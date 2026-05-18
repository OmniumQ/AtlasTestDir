% Bütünsel Kaynak Teorisi (UST) - İleri Epistemolojik Sınır Testleri
% 1. Kaotik Geometrik Bozulma (3D Ns Yüzeyi)
% 2. S = 0 Entropi Termodinamik Hata Payı Sınaması

clear; clc; close all;

disp('--- UST İleri Çürütme Modelleri Başlatılıyor ---');

%% BÖLÜM 1: 3D NS YÜZEYİ VE KAOTİK GEOMETRİK BOZULMA
% Kuram, Makro (Kütleçekim-G) ve Mikro (Kuantum-h) evren sabitlerinin
% birbirlerinden bağımsız olmadığını, Ns operatörü altında pürüzsüz 
% bir topolojik manifold oluşturduğunu iddia eder.

% G ve h için normalize edilmiş rasyonel limitler (Faz Uzayı)
G_norm = linspace(0.1, 1, 50);
h_norm = linspace(0.1, 1, 50);
[G_grid, h_grid] = meshgrid(G_norm, h_norm);

% 1.A: İdeal Ns Yüzeyi (Gürültüsüz, Kusursuz Evrensel Uyum)
% Yüzey log(G*h) izdüşümü üzerinden hesaplanır
Ns_ideal = log10(G_grid .* h_grid) + 10; 

% 1.B: Kaotik Bozulma Sınırı (Kuantum Gürültüsü / Noise = 0.5)
% Sisteme yüksek entropi eklendiğinde yüzeyin ne kadar bozulacağı hesaplanır.
noise_level = 0.5;
Ns_kaotik = Ns_ideal + noise_level * randn(size(Ns_ideal));

% Çizim İşlemi (Figure 1)
figure('Name', 'UST Ns Operatörü: 3D Topoloji ve Kaotik Bozulma', 'Color', 'w');

subplot(1,2,1);
surf(G_grid, h_grid, Ns_ideal, 'EdgeColor', 'none');
title('Orijinal UST: Pürüzsüz Uyum (Ns Clean)', 'FontSize', 11, 'FontWeight', 'bold');
xlabel('Kütleçekim Sabiti Etkisi (G)'); ylabel('Planck Sabiti Etkisi (h)'); zlabel('log_{10}(Ns)');
colormap(jet); view(3); grid on;

subplot(1,2,2);
surf(G_grid, h_grid, Ns_kaotik, 'EdgeColor', 'none');
title('Kaotik UST: Geometrik Bozulma Sınırı', 'FontSize', 11, 'FontWeight', 'bold');
xlabel('Kütleçekim Sabiti Etkisi (G)'); ylabel('Planck Sabiti Etkisi (h)'); zlabel('log_{10}(Ns)');
view(3); grid on;

%% BÖLÜM 2: TERMOKİNETİK SINIR (S = 0 ENTROPİ SIFIRLANMASI)
% Madde ve enerjinin bilgi tabanlı dönüşümünde toplam entropi değişiminin sıfır 
% olması şart koşulur. Bu mutlak bir hiçlik değil, katı bir hata payına sahip simetridir.

% Kuramın Ampirik Verileri [1]
E_Giris = 9e16;               % Giriş Enerjisi Kapasitesi (Joule)
Hata_Payi = 4080156960000;    % Kabul edilebilir maksimum entropik sapma (4.08x10^12)
E_Cikis = E_Giris - Hata_Payi;% Yeniden inşa edilen enerji (Çıkış)

% Çizim İşlemi (Figure 2)
figure('Name', 'UST Termodinamik Sınır: S=0 Analizi', 'Color', 'w');
bar_handle = bar([2, 3], [E_Giris, E_Cikis], 0.5, 'FaceColor', [0.4660 0.6740 0.1880]);

% Grafiksel Parametreler
set(gca, 'XTick', [2, 3], 'XTickLabel', {'Giris Enerjisi', 'Cikis Enerjisi'}, 'FontSize', 11);
ylabel('Enerji Kapasitesi (J)', 'FontSize', 12);
title('S = 0 Analizi (Hata Payi: 4080156960000)', 'FontSize', 14, 'FontWeight', 'bold');
ylim([0 9e16]);
grid on;

disp('Simülasyonlar tamamlandı. 3D Manifold ve Termodinamik Sınır grafikleri yansıtıldı.');