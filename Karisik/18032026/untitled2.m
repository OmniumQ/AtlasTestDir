% =========================================================================
% GENİŞLETİLMİŞ OMNİUM: φ·e·α·c·h·G·kB KATILIMI
% Her sabitin κ_optimal üzerindeki etkisi
% =========================================================================
clear; clc; close all;

% Temel sabitler
alpha = 1/137.035999;
phi   = (1+sqrt(5))/2;
e_val = exp(1);
c_val = 299792458;
hbar  = 1.054571817e-34;
h_val = 6.62607015e-34;
G_val = 6.674e-11;
kB    = 1.380649e-23;
mp    = 1.672623e-27;

% Planck birimleri
lp = sqrt(hbar*G_val/c_val^3);
tp = sqrt(hbar*G_val/c_val^5);
Ep = sqrt(hbar*c_val^5/G_val);
Tp = Ep/kB;

% Gravitasyonel ince yapı sabiti
alpha_G = G_val*mp^2/(hbar*c_val);

% Boyutsuz Ns (simülasyonda kullanılan)
Ns    = 2*pi^2*phi*e_val*alpha;
pi_Ns = pi*Ns;

% Ns_tam (tüm sabitlerle)
Ns_tam = pi*phi*e_val*alpha*c_val*h_val*G_val*kB;

fprintf('=== GENİŞLETİLMİŞ OMNİUM ANALİZİ ===\n');
fprintf('Ns (boyutsuz) = %.8f\n', Ns);
fprintf('Ns_tam        = %.4e\n', Ns_tam);
fprintf('\nPlanck birimleri:\n');
fprintf('lp = %.4e m\n', lp);
fprintf('tp = %.4e s\n', tp);
fprintf('Ep = %.4e J\n', Ep);
fprintf('Tp = %.4e K\n', Tp);
fprintf('\nBoyutsuz oranlar:\n');
fprintf('α        = %.6e\n', alpha);
fprintf('αG       = %.6e\n', alpha_G);
fprintf('αG/α     = %.6e\n', alpha_G/alpha);
fprintf('kB/Ep    = %.6e\n', kB/Ep);
fprintf('ℏ/Ep·tp  = %.6f\n', hbar/(Ep*tp));

% =========================================================
% OMNİUM FREKANS MODELLERİ
% Her sabitin ω_Om'a katkısı
% =========================================================
fprintf('\n=== OMNİUM FREKANS MODELLERİ ===\n');

% Model 1: Temel (mevcut)
omega_1 = 1/Ns;

% Model 2: + gravitasyonel katkı
omega_2 = 1/Ns * (1 + alpha_G/alpha);

% Model 3: + termal katkı (oda sıcaklığı T=300K)
T_room  = 300;
beta_kB = kB*T_room/Ep;
omega_3 = 1/Ns * (1 + beta_kB);

% Model 4: Ns_tam tabanlı (boyutlu → boyutsuz)
% Ns_tam/Ns = c·h·G·kB (boyutlu faktör)
% Planck birimlerinde c=h=G=kB=1 → Ns_tam/Ns = 1
% Ama gerçek değerlerde:
ratio   = Ns_tam/Ns;
omega_4 = 1/Ns * abs(ratio)^(1/4);  % 4. kök ile ölçekle

% Model 5: Gravitasyonel Ns
Ns_G    = 2*pi^2*phi*e_val*alpha_G;
omega_5 = 1/Ns + 1/Ns_G;  % EM + gravitasyonel

% Model 6: Harmonik ortalama
omega_6 = 2/(1/omega_1 + 1/abs(1/Ns_G));

fprintf('Model 1 (temel):     ω_Om = %.8f  κ·dt = %.6f\n',...
        omega_1, pi*Ns*omega_1/omega_1);
fprintf('Model 2 (+αG/α):     ω_Om = %.8f  κ·dt = %.6f\n',...
        omega_2, pi/omega_2);
fprintf('Model 3 (+kB·T/Ep):  ω_Om = %.8f  κ·dt = %.6f\n',...
        omega_3, pi/omega_3);
fprintf('Model 4 (Ns_tam):    ω_Om = %.8e  κ·dt = %.6e\n',...
        omega_4, pi/omega_4);
fprintf('Model 5 (EM+Grav):   ω_Om = %.8f  κ·dt = %.6f\n',...
        omega_5, pi/omega_5);

% =========================================================
% SİMÜLASYON: Her model için κ·dt testi
% Sadece güvenilir iki nokta: θ=0 ve θ=π/4
% =========================================================
dt      = 0.01;
sigma   = 1.0;
Nt      = 2000;
N_train = 1000;

gamma_faz = 0.05;
T1 = 2.0; T2 = 1.0;

sz = [1,0; 0,-1];
sm = [0,0; 1,0];

L_faz = sqrt(gamma_faz*dt)*sz;
L_T1  = sqrt(dt/T1)*sm;
coeff = max(dt/(2*T2)-dt/(4*T1),0);
L_T2  = sqrt(coeff)*sz;
LdL_faz = L_faz'*L_faz;
LdL_T1  = L_T1'*L_T1;
LdL_T2  = L_T2'*L_T2;

rng(42);
p_noise = sigma*randn(1,Nt);
p_train = p_noise(1:N_train);
p_test  = p_noise(N_train+1:end);

% Sadece iki güvenilir durum
psi_test = {[1;0], [1/sqrt(2);1/sqrt(2)]};
names_t  = {'|0⟩ (θ=0)', '|+⟩ (θ=π/4)'};
expected = [pi_Ns/2, pi_Ns];  % beklenen değerler

kdt_range = linspace(0.05, 4.0, 200);
kdt_opt   = zeros(2,1);
fid_curves= zeros(2, length(kdt_range));

fprintf('\n=== İKİ GÜVENİLİR NOKTA TESTİ ===\n');

for si = 1:2
    psi_s = psi_test{si}/norm(psi_test{si});
    rho_s = psi_s*psi_s';

    % DFS
    E_s = zeros(2,2);
    for k = 1:N_train
        p  = p_train(k);
        Ep = [1,0;0,exp(1i*p)];
        rk = Ep*rho_s*Ep';
        rk = rk+L_T1*rk*L_T1'-0.5*(LdL_T1*rk+rk*LdL_T1);
        rk = rk+L_T2*rk*L_T2'-0.5*(LdL_T2*rk+rk*LdL_T2);
        rk = rk+L_faz*rk*L_faz'-0.5*(LdL_faz*rk+rk*LdL_faz);
        rk = make_physical(rk);
        E_s = E_s+rk;
    end
    [Vs,Ds] = eig(E_s/N_train);
    [~,is2] = sort(real(diag(Ds)),'descend');
    psi_Ds  = Vs(:,is2(1));
    psi_Ps  = Vs(:,is2(2));

    % Tarama
    fid_list = zeros(1,length(kdt_range));
    for ki = 1:length(kdt_range)
        kap   = kdt_range(ki)/dt;
        L_kor = sqrt(kap*dt)*(psi_Ds*psi_Ps');
        LdL_k = L_kor'*L_kor;
        rho   = rho_s;
        fr    = zeros(1,N_train);
        for t = 1:N_train
            p  = p_test(t);
            Ep = [1,0;0,exp(1i*p)];
            rho= Ep*rho*Ep';
            rho= rho+L_T1*rho*L_T1'-0.5*(LdL_T1*rho+rho*LdL_T1);
            rho= rho+L_T2*rho*L_T2'-0.5*(LdL_T2*rho+rho*LdL_T2);
            rho= rho+L_faz*rho*L_faz'-0.5*(LdL_faz*rho+rho*LdL_faz);
            rho= rho+L_kor*rho*L_kor'-0.5*(LdL_k*rho+rho*LdL_k);
            rho= make_physical(rho);
            fr(t) = real(psi_s'*rho*psi_s);
        end
        fid_list(ki) = mean(fr(end-99:end));
    end
    fid_curves(si,:) = fid_list;

    % Gerçek maksimum
    dFdk = diff(fid_list);
    sc   = find(diff(sign(dFdk))<0);
    if ~isempty(sc)
        [~,best]   = max(fid_list(sc));
        kdt_opt(si)= kdt_range(sc(best));
    else
        [~,im]     = max(fid_list);
        kdt_opt(si)= kdt_range(im);
    end

    fprintf('\n%s:\n', names_t{si});
    fprintf('  Ölçülen κ·dt  = %.6f\n', kdt_opt(si));
    fprintf('  Beklenen      = %.6f\n', expected(si));
    fprintf('  Fark          = %.2f%%\n',...
            abs(kdt_opt(si)-expected(si))/pi_Ns*100);

    % Her model için tahmin
    fprintf('  Model tahminleri:\n');
    models_kdt = [pi/omega_1, pi/omega_2, ...
                  pi/omega_3, pi/omega_5];
    model_names= {'Temel(1/Ns)',...
                  '+αG/α','+ kB·T/Ep','EM+Grav'};
    if si==1  % |0⟩ için yarım
        models_kdt = models_kdt/2;
    end
    for mi = 1:4
        fark = abs(models_kdt(mi)-kdt_opt(si))/pi_Ns*100;
        marker = '';
        if fark<5,  marker=' ✓'; end
        if fark<2,  marker=' ✓✓'; end
        fprintf('    %-15s: %.6f  fark=%.2f%%%s\n',...
                model_names{mi}, models_kdt(mi), fark, marker);
    end
end

% =========================================================
% ÇİZİM
% =========================================================
figure('Name','Genişletilmiş Omnium','Color','w',...
       'Position',[30 30 1400 800]);

subplot(2,3,1:2);
plot(kdt_range, fid_curves(1,:),'b','LineWidth',2,...
     'DisplayName','|0⟩'); hold on;
plot(kdt_range, fid_curves(2,:),'r','LineWidth',2,...
     'DisplayName','|+⟩');
xline(kdt_opt(1),'b--','LineWidth',2,...
      'Label',sprintf('|0⟩ opt=%.4f',kdt_opt(1)));
xline(kdt_opt(2),'r--','LineWidth',2,...
      'Label',sprintf('|+⟩ opt=%.4f',kdt_opt(2)));
xline(pi_Ns,'k-','LineWidth',2,'Label','π·Ns');
xline(pi_Ns/2,'k--','LineWidth',1.5,'Label','π·Ns/2');
legend('Location','SouthEast');
title('İki Güvenilir Nokta: |0⟩ ve |+⟩');
xlabel('κ·dt'); ylabel('F'); grid on;

subplot(2,3,3);
% Sabit katkı analizi
sabit_names = {'α','α+αG','α+kB/Ep','α·φ','α·e','α·φ·e',...
               'α·π²','α·2π²','Ns=2π²φeα'};
sabit_vals  = [alpha, alpha+alpha_G, alpha+kB/Ep,               alpha*phi, alpha*e_val, alpha*phi*e_val,               alpha*pi^2, alpha*2*pi^2, Ns];
kdt_from_sabit = pi./sabit_vals;

bar(categorical(sabit_names), log10(kdt_from_sabit),...
    'FaceColor',[0.3 0.6 0.9]);
hold on;
yline(log10(pi_Ns),'r--','LineWidth',2,'Label','log(π·Ns)');
yline(log10(pi_Ns/2),'m--','LineWidth',1.5,'Label','log(π·Ns/2)');
title('π/sabit → κ·dt (log10)');
ylabel('log10(π/sabit)');
xtickangle(45); grid on;

subplot(2,3,4);
% Omnium enerji seviyeleri
n_levels = 0:5;
E_levels = n_levels * omega_1;  % ℏ=1
bar(n_levels, E_levels,'FaceColor',[0.2 0.7 0.4]);
hold on;
yline(pi_Ns/2,'r--','Label','π·Ns/2 = κ·dt(|0⟩)');
yline(pi_Ns,  'b--','Label','π·Ns   = κ·dt(|+⟩)');
title(sprintf('Omnium Enerji Seviyeleri\nω_{Om}=1/Ns=%.4f',omega_1));
xlabel('n'); ylabel('E_n = n·ω_{Om}'); grid on;

% π·Ns/2 ve π·Ns hangi enerji seviyesine karşılık?
n_half = pi_Ns/2 / omega_1;
n_full = pi_Ns   / omega_1;
fprintf('\n=== OMNİUM ENERJİ SEVİYELERİ ===\n');
fprintf('π·Ns/2 = %.4f → n = %.4f\n', pi_Ns/2, n_half);
fprintf('π·Ns   = %.4f → n = %.4f\n', pi_Ns,   n_full);
fprintf('→ n_half = π·Ns/(2·ω_Om) = π·Ns·Ns/2 = π·Ns²/2\n');
fprintf('→ n_full = π·Ns²\n');
fprintf('π·Ns²/2 = %.4f\n', pi*Ns^2/2);
fprintf('π·Ns²   = %.4f\n', pi*Ns^2);

subplot(2,3,5);
% c, h, G, kB ile ω_Om modifikasyonu
T_vals  = logspace(0, 10, 100);  % 1K → 10^10 K
omega_T = 1/Ns * (1 + kB*T_vals/Ep);
kdt_T   = pi./omega_T;
semilogx(T_vals, kdt_T,'b','LineWidth',2); hold on;
yline(pi_Ns,  'r--','Label','π·Ns (T=0)');
yline(pi_Ns/2,'m--','Label','π·Ns/2');
xline(T_room, 'k--','Label','T=300K');
xline(Tp,     'g--','Label','T_{Planck}');
title('Termal Katkı: κ·dt vs T');
xlabel('T (K)'); ylabel('κ·dt'); grid on;

subplot(2,3,6);
% GR katkısı: κ·dt vs kütle
M_vals   = logspace(-30, 30, 100);  % elektron → güneş
r_vals   = 1e-10*ones(size(M_vals)); % Bohr yarıçapı
phi_grav = G_val*M_vals./(r_vals*c_val^2);  % gravitasyonel potansiyel
omega_GR = 1/Ns * (1 + phi_grav);
kdt_GR   = pi./omega_GR;
semilogx(M_vals, kdt_GR,'r','LineWidth',2); hold on;
yline(pi_Ns,'b--','Label','π·Ns (M→0)');
xline(mp,'k--','Label','m_p');
title('GR Katkısı: κ·dt vs M');
xlabel('M (kg)'); ylabel('κ·dt'); grid on;

sgtitle(sprintf(['Genişletilmiş Omnium: φ·e·α·c·h·G·kB\n'...
                 'Ns=%.4f | ω_{Om}=%.4f | π·Ns=%.4f'],...
                Ns, omega_1, pi_Ns),...
        'FontSize',12,'FontWeight','bold');

function rho = make_physical(rho)
    rho = (rho+rho')/2;
    [V,D] = eig(rho);
    D = diag(max(real(diag(D)),0));
    rho = V*D*V';
    t = real(trace(rho));
    if t > 1e-10, rho = rho/t; end
end
