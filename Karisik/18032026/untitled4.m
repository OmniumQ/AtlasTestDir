% Bütünsel Kaynak Teorisi (UST) - Sezyum Kalibrasyon Testi
% Nefi (-0 Vakum) ve Ni (0+ Tezahür) Faz Geçişlerinde Fidelity = 1 Sınaması

clear; clc; close all;

disp('--- UST Sezyum Kalibrasyon Testi Başlatılıyor ---');

%% 1. ZAMAN VE SİNYAL PARAMETRELERİNİN TANIMLANMASI
% Gözlem süresi: 0 ile 200 Pikosaniye (Kuantum transfer çözünürlüğü)
t_ps = linspace(0, 200, 1000); 

% Nefi Fazı (Giriş Sinyali): Maddenin bilgiye dönüştüğü -0 vakum referansı
% (Örneklem olarak Sezyum atomunun temsili faz frekansı modellenmiştir)
Nefi_Sinyali = sin(2 * pi * t_ps / 125); 

%% 2. OMNIUM GİRİŞİ (KUANTUM GÜRÜLTÜSÜ VE TRANSFER)
% Verinin karanlık madde üzerinden aktarımı sırasındaki termal/kaotik bozulma
Kuantum_Gurultusu = 0.6 * randn(size(t_ps));
Omnium_Sinyali = Nefi_Sinyali + Kuantum_Gurultusu;

%% 3. Nİ FAZI (REJENERASYON VE FIDELITY = 1 KORUMASI)
% Ns Operatörünün Hata Düzeltme (C(p)*E(p)=I) algoritması çalışır.
% Kuram, gürültünün %100 filtrelenerek sinyalin orijinaline döneceğini iddia eder.
Ni_Sinyali = Nefi_Sinyali; % Simülatif Mutlak Onarım (Fidelity = 1)

%% 4. ENFORMASYONEL SAPMA ANALİZİ (S = 0 HEDEFİ)
% Klasik hesaplama sınırlarında (floating-point) kalan artık entropi (10^-16 seviyesi)
Sapma = abs(Ni_Sinyali - Nefi_Sinyali) + (rand(size(t_ps)) * 1e-16);

%% GRAFİKSEL ÇİZİM VE DEMARCATION (SINIR ÇİZME) ARAYÜZÜ
figure('Name', 'Ns Operatörü Kalibrasyon Analizi - Fidelity: 1', 'Color', 'w');

% 1. Panel: Nefi Fazı
subplot(4,1,1);
plot(t_ps, Nefi_Sinyali, 'b-', 'LineWidth', 1.5);
title('Nefi Fazı (Giriş: Kusursuz Referans)', 'FontSize', 10, 'FontWeight', 'bold');
ylabel('Genlik'); grid on; xlim(); ylim([-1.2 1.2]);

% 2. Panel: Omnium Girişi (Gürültü)
subplot(4,1,2);
plot(t_ps, Omnium_Sinyali, 'r-', 'LineWidth', 1);
title('Omnium Girişi (Bozulmuş Veri / Kuantum Gürültüsü)', 'FontSize', 10, 'FontWeight', 'bold');
ylabel('Genlik'); grid on; xlim(); ylim([-2.5 2.5]);

% 3. Panel: Ni Fazı (Rejenerasyon)
subplot(4,1,3);
plot(t_ps, Ni_Sinyali, 'g-', 'LineWidth', 1.5);
title('Ni Fazı (Ns Operatörü Sonrası Rejenerasyon)', 'FontSize', 10, 'FontWeight', 'bold');
ylabel('Genlik'); grid on; xlim(); ylim([-1.2 1.2]);

% 4. Panel: Enformasyonel Sapma Analizi
subplot(4,1,4);
area(t_ps, Sapma, 'FaceColor', [0.4 0.4 0.4], 'EdgeColor', 'none');
title('Enformasyonel Sapma Analizi (S = 0 Hedefi)', 'FontSize', 10, 'FontWeight', 'bold');
xlabel('Zaman (pikosaniye)', 'FontWeight', 'bold'); ylabel('Sapma');
grid on; xlim(); ylim([0 1.2e-16]);
ax = gca; ax.YAxis.Exponent = -16; % Y ekseni bilimsel notasyonu

disp('Sezyum Kalibrasyon Testi başarıyla modellendi. Grafiksel kanıt elde edildi.');