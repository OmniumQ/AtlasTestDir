% UST_Cosmological_Analysis.m
% Unified Source Theory (UST) v5 - Cosmological Parameters and Visualizations
% This script computes and visualizes dark sector dynamics, ONL architecture,
% Hubble tension resolution, and Von Neumann entropy based on UST v5 matrices.

clear; clc; close all;

% 1. Core UST v5 Ontological Constants
N_b = 0.63354460; % Channel Q (Blueprint / Active Observable Sector)
C_cb = 1 - N_b;   % Channel C (Frozen Gravitational Background) -> 0.36645540
T_Om = exp(-2 * pi * N_b * C_cb); % WKB Tunnel Amplitude (T10) -> 0.23252885

% 2. ONL (Omnium Number Line) 3-Region Partition
f_C = T_Om;               % Channel C (Frozen) fraction
f_Om = N_b - T_Om;        % 0-Element (Omnium) transition gap
f_Q = C_cb;               % Channel Q (Active) fraction

% 3. Cosmological Budget (Dark Energy & Dark Matter) - Theorem 5
phi = (1 + sqrt(5)) / 2;  % Golden ratio
Omega_DM_obs = 0.265;     % Planck 2018 Dark Matter
% Dark Energy determined deterministically by Channel C pressure via log-spiral filter
Omega_Lambda_UST = N_b + (Omega_DM_obs / (phi * pi)); % -> 0.685677
Omega_Lambda_obs = 0.6850; % Planck 2018 Dark Energy Observation

% 4. Hubble Tension Resolution - Theorem 23
H0_Planck = 67.4; % km/s/Mpc (Channel C frozen background measurement)
H0_Local = 73.0;  % km/s/Mpc (Channel Q active sector measurement)
Hubble_Ratio_UST = 1 + (N_b * (C_cb^2)); % T23 Equation -> 1.085078
Hubble_Ratio_Obs = H0_Local / H0_Planck; % -> 1.083086

% 5. Visualizations
fig = figure('Name', 'UST v5 Cosmological Matrix');

% Subplot 1: ONL 3-Region Partition
subplot(2, 2, 1);
pie_data = [f_C, f_Om, f_Q];
labels = {sprintf('Channel C (Frozen)\n%.4f', f_C), ...
          sprintf('0-Element (Omnium)\n%.4f', f_Om), ...
          sprintf('Channel Q (Active)\n%.4f', f_Q)};
p = pie(pie_data, labels);
title('ONL 3-Region Partition (Sum = 1.0)', 'FontWeight', 'bold');
colormap([0.2 0.2 0.2; 0.8 0.6 0.2; 0.2 0.6 0.8]); % Gray, Gold, Blue

% Subplot 2: Dark Energy Comparison (T5)
subplot(2, 2, 2);
bar_data = [Omega_Lambda_UST, Omega_Lambda_obs];
b = bar(bar_data, 'FaceColor', 'flat');
b.CData(1,:) = [0.2 0.6 0.8]; % UST Prediction
b.CData(2,:) = [0.8 0.3 0.3]; % Planck Observation
set(gca, 'XTick', 1:2, 'XTickLabel', {'UST Predicted (T5)', 'Planck 2018 Obs.'});
ylim([0.67 0.69]);
ylabel('\Omega_\Lambda (Dark Energy Density)');
title(sprintf('Dark Energy Deterministic Bound\n\\Omega_\\Lambda = N_b + \\Omega_{DM} / (\\phi \\pi) | \\Delta%%: 0.10%%'));
grid on;

% Subplot 3: Hubble Tension Resolution (T23)
subplot(2, 2, 3);
h_data = [Hubble_Ratio_UST, Hubble_Ratio_Obs];
bh = bar(h_data, 'FaceColor', 'flat');
bh.CData(1,:) = [0.2 0.6 0.8];
bh.CData(2,:) = [0.8 0.3 0.3];
set(gca, 'XTick', 1:2, 'XTickLabel', {'UST Predicted', 'Observed (Local/Planck)'});
ylim([1.07 1.09]);
ylabel('H_0 Ratio');
title(sprintf('Hubble Tension Asymmetry\nH_{local}/H_{Planck} = 1 + N_b \\cdot C_{cb}^2 | \\Delta%%: 0.18%%'));
grid on;

% Subplot 4: Omnium Entropy vs Fidelity (T3)
subplot(2, 2, 4);
% Fidelity ranges from the deterministic lower bound to 1
F_bound = (sqrt(3) - 1) / 2; % ~0.366
F = linspace(F_bound, 1, 500); 

% Eigenvalues for Von Neumann entropy calculation
discriminant = 1 - 4 * N_b * C_cb * (1 - F);
discriminant(discriminant < 0) = 0; % Stabilize floating point limits
lambda_plus = (1 + sqrt(discriminant)) / 2;
lambda_minus = (1 - sqrt(discriminant)) / 2;

% Handle natural log of zero limits
lambda_minus(lambda_minus == 0) = eps;

% Von Neumann Entropy formulation
S_Om = -lambda_plus .* log(lambda_plus) - lambda_minus .* log(lambda_minus);

plot(F, S_Om, 'LineWidth', 2.5, 'Color', [0.2 0.8 0.4]);
xlabel('Aslına Uygunluk / Fidelity (F)');
ylabel('Von Neumann Entropy (S_{Om})');
title('Omnium Entropy & Unitary Evolution (T3)');
xline(1, '--r', 'S=0 Target (Hardware Alignment)', 'LabelVerticalAlignment', 'bottom');
grid on;

% Execution Complete
disp('UST v5 Matrix Analysis Successfully Executed.');