clear; clc; close all;

% --- 1. UST EVRENSEL SABİTLERİ (Mühürleme Katmanı) ---
Ns_q = 0.63354460;   % Master Register (Blueprint)
a2   = 1/17;         % Seeley-DeWitt Spektral Tahliye Valfi
Vb   = 1.195461;     % Harmonik Dişli Oranı (Laminar Senkronizasyon)

% --- 2. SİMÜLASYON PARAMETRELERİ ---
L  = 2*pi;           % Manifold Uzunluğu
Nx = 256;            % Uzaysal Çözünürlük (DOF Kontrolü)
dx = L/Nx;
x  = linspace(0, L, Nx);
dt = 0.0002;         % DÜZELTME: Kararlılık için zaman adımı küçültüldü (CFL Şartı)
T_final = 2.0;       % Toplam Gözlem Süresi
nu = 0.02;           % Klasik Kinematik Viskozite

% --- 3. BAŞLANGIÇ KOŞULU (Enerji Girişi) ---
u_std = sin(x); 
u_ust = sin(x); 

% --- 4. NUMERİK İTERASYON (Zaman Serisi) ---
steps = round(T_final/dt);
history_std = zeros(steps, Nx);
history_ust = zeros(steps, Nx);

for t = 1:steps
    % --- A. STANDART FİZİK (Navier-Stokes Sektörü) ---
    % DÜZELTME: Patlamayı önlemek için merkezi fark yerine upwind_diff kullanıldı
    du_std = -u_std .* upwind_diff(u_std, dx) + nu * second_diff(u_std, dx);
    u_std = u_std + du_std * dt;
    
    % --- B. UST v5 FİZİĞİ (Topolojik Mühürleme Sektörü) ---
    u_eff = u_ust * Ns_q; 
    du_ust = -u_eff .* upwind_diff(u_ust, dx) + (nu + a2) * second_diff(u_ust, dx);
    u_ust = u_ust + du_ust * dt;
    
    % Kayıt
    history_std(t, :) = u_std;
    history_ust(t, :) = u_ust;
end

% --- 5. RASYONEL ANALİZ VE VİZÜALİZASYON ---
figure('Color', 'w', 'Name', 'UST v5 vs Düzeltilmiş Standart Fizik');

% Zaman ekseni görselleştirmesi için seyrekleştirme adımı (Grafik kasmasını önler)
plot_stride = max(1, round(steps/50)); 
t_indices = 1:plot_stride:steps;

subplot(2,1,1);
waterfall(x, t_indices, history_std(t_indices, :));
title('STANDART NAVIER-STOKES (Upwind ve Düşük dt ile Kararlı kılınan Akış)');
xlabel('Uzay (Manifold)'); ylabel('Zaman Adımı'); zlabel('Hız (u)');
view(10, 45); colormap('hot');

subplot(2,1,2);
waterfall(x, t_indices, history_ust(t_indices, :));
title(['UST v5 MÜHÜRLÜ AKIŞ (Yüksek Difüzyonlu Sönümlenme - Ns,q=', num2str(Ns_q), ')']);
xlabel('Uzay (Manifold)'); ylabel('Zaman Adımı'); zlabel('Hız (u)');
view(10, 45); colormap('winter');

% --- NUMERİK TÜREV FONKSİYONLARI ---

function du = upwind_diff(u, dx)
    % DÜZELTME: Akış yönüne göre türev alarak şok bölgelerindeki patlamayı engeller
    u_pos = max(u, 0);
    u_neg = min(u, 0);
    
    % Geri ve İleri farklar (Periyodik sınır şartları korunarak)
    back_diff = (u - circshift(u, 1)) / dx;
    fwd_diff  = (circshift(u, -1) - u) / dx;
    
    du = u_pos .* back_diff + u_neg .* fwd_diff;
end

function d2u = second_diff(u, dx)
    d2u = (circshift(u,-1) - 2*u + circshift(u,1)) / (dx^2);
end
