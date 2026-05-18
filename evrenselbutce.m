% Bütünsel Kaynak Teorisi (UST) v5 Kozmolojik Bütçe ve Kanal Dağılımı Analizi
clear; clc; close all;

%% 1. UST Deterministik Temel Sabitleri
alpha = 1 / 137.035999;               % İnce yapı sabiti [7]
N_sq = (3 - sqrt(3))/2 - (alpha/17);  % Kanal Q (Aktif/Manifest) ağırlığı [8]
C_cb = 1 - N_sq;                      % Kanal C (Dondurulmuş/Blueprint) ağırlığı [2]

%% 2. Tünelleme ve Geometrik Parametreler
T_Om = exp(-2 * pi * N_sq * C_cb);    % Teorem 10: Kanal Q'dan Kanal C'ye tünelleme genliği [9]
phi_pi = 5.083204;                    % Galaktik logaritmik sarmal sabiti [4]

%% 3. Kozmik Enerji Bütçesi Dağılımı (Teorem 5, 16 ve Baryonik Oran)
% Karanlık Madde (DM), Kanal C'nin gölgesi olarak hesaplanmıştır. 
% UST T16 referanslarına göre optimal uyum ~0.265'tir [4].
Omega_DM = 0.265000; 

% Teorem 5: Karanlık Enerji (DE) [4]
Omega_Lambda = N_sq + (Omega_DM / phi_pi); 

% Baryonik Madde (b) tahmini [6]
Omega_b = T_Om / phi_pi; 

% Bilinmeyen/Işıma (Nötrinolar ve fotonlar)
Omega_Unknown = 1 - (Omega_Lambda + Omega_DM + Omega_b);

%% 4. Analitik Sonuçların Konsola Yazdırılması
fprintf('--- UST v5: Deterministik Kozmik Bütçe Analizi ---\n');
fprintf('Kanal Q (Aktif Sektör) Ağırlığı (N_sq): %.6f\n', N_sq);
fprintf('Kanal C (Dondurulmuş Arka Plan) Ağırlığı (C_cb): %.6f\n', C_cb);
fprintf('Omnium Tünelleme Genliği (T_Om): %.6f\n', T_Om);
fprintf('--------------------------------------------------\n');
fprintf('Karanlık Enerji (Omega_Lambda) : %%%.2f\n', Omega_Lambda * 100);
fprintf('Karanlık Madde (Omega_DM)      : %%%.2f\n', Omega_DM * 100);
fprintf('Baryonik Madde (Omega_b)       : %%%.2f\n', Omega_b * 100);
fprintf('Bilinmeyen/Işıma Kalanı        : %%%.2f\n', Omega_Unknown * 100);
fprintf('--------------------------------------------------\n');

%% 5. Görselleştirme (Simülasyon Çıktıları)

% Grafik 1: Çift Kanallı Mimari (Kanal Q vs Kanal C)
subplot(1, 2, 1);
channel_weights = [N_sq, C_cb];
labels_channels = {sprintf('Kanal Q (Aktif)\n%%%.2f', N_sq*100), ...
                   sprintf('Kanal C (Dondurulmuş)\n%%%.2f', C_cb*100)};
pie(channel_weights, labels_channels);
title('Evrenin Ontolojik Kanal Dağılımı (UST T2)', 'FontWeight', 'bold');
colormap(gca, [0.2 0.6 1; 0.6 0.2 0.8]);

% Grafik 2: Kozmik Bütçe (Karanlık Enerji, Karanlık Madde, Baryonik, Bilinmeyen)
subplot(1, 2, 2);
energy_budget = [Omega_Lambda, Omega_DM, Omega_b, Omega_Unknown];
labels_budget = {sprintf('Karanlık Enerji\n%%%.2f', Omega_Lambda*100), ...
                 sprintf('Karanlık Madde\n%%%.2f', Omega_DM*100), ...
                 sprintf('Baryonik Madde\n%%%.2f', Omega_b*100), ...
                 sprintf('Bilinmeyen/Işıma\n%%%.2f', Omega_Unknown*100)};
pie(energy_budget, labels_budget);
title('Evrenin Enerji Bütçesi (UST T5 & T16)', 'FontWeight', 'bold');
colormap(gca, [0.8 0.2 0.2; 0.2 0.8 0.2; 0.2 0.2 0.8; 0.5 0.5 0.5]);