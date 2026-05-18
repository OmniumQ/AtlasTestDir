% UST_Universal_Timeline_Simulation.m
% Unified Source Theory (UST) v5 - Cosmological Timeline & Phase Inversion
% Simulates the universe's timeline from the last Big Bang to the next 
% Channel Inversion, mapped to UST Universal Time (T32) and Cyclic Cosmology (T25).

clear; clc; close all;

% --- 1. UST v5 Ontological Constants ---
N_b  = 0.63354460;       % Channel Q (Active Observable Sector / Blueprint)
C_cb = 0.36645540;       % Channel C (Frozen Gravitational Background)
T_Om = 0.23252885;       % WKB Tunnel Amplitude (Conserved across cycles)

% --- 2. Cosmological Time Mapping (T32) ---
% Standard Empirical Time (SI units - Gyr)
Current_Age_SI = 13.8;   % Standard model current age
t_H_SI_Gyr     = 14.5;   % Standard Hubble expansion macro-limit

% UST Universal Time Conversion (1 UST-sec = N_b * 1 SI-sec)
Current_Age_UST = Current_Age_SI * N_b;     % Current Age in UST Time: ~8.7429 Gyr
t_H_UST_Gyr     = t_H_SI_Gyr * N_b;         % Universal Time Anchor: ~9.1919 Gyr

% Inversion Threshold (T25)
% The universe undergoes Channel Inversion when Channel Q decays via T_Om 
% and reaches equilibrium with Channel C (0.5 threshold).
Inversion_Time_UST = t_H_UST_Gyr + (T_Om * t_H_UST_Gyr); % Projected limit

% --- 3. Phase Evolution Vectors ---
% Simulating cosmic progression from t = 0 to post-inversion
time_vector_UST = linspace(0, Inversion_Time_UST * 1.2, 2000); 

% Cosine decay mapping from N_b to C_cb
% Frequency is scaled so that Q(t) crosses 0.5 at Inversion_Time_UST
freq = pi / (2 * Inversion_Time_UST); 
Amplitude = N_b - 0.5;

Q_evolution = 0.5 + Amplitude * cos(freq * time_vector_UST);
C_evolution = 0.5 - Amplitude * cos(freq * time_vector_UST);

% --- 4. Advanced Visualization ---
fig = figure('Name', 'UST v5: Universal Timeline & Channel Inversion');

% Main Plot: Channel Q vs Channel C Evolution
plot(time_vector_UST, Q_evolution, 'LineWidth', 3, 'Color', [0.1 0.5 0.8], ...
    'DisplayName', 'Channel Q (Active Universe)'); hold on;
plot(time_vector_UST, C_evolution, 'LineWidth', 3, 'Color', [0.8 0.2 0.2], ...
    'DisplayName', 'Channel C (Frozen Background)');

% Shaded Tunneling Region (Information Leakage via T_Om)
fill_x = [time_vector_UST, fliplr(time_vector_UST)];
fill_y = [Q_evolution, fliplr(C_evolution)];
fill(fill_x, fill_y, [0.8 0.8 0.8], 'FaceAlpha', 0.3, 'EdgeColor', 'none', ...
    'DisplayName', 'T_{Om} Tunnelling Leakage');

% --- Annotations & Markers ---

% A. Big Bang (Start)
plot(0, N_b, 'ks', 'MarkerSize', 10, 'MarkerFaceColor', 'k', 'HandleVisibility', 'off');
text(0.2, N_b, 'Big Bang (t=0)\nChannel Q max', 'FontSize', 10, 'FontWeight', 'bold');

% B. Current Cosmic Epoch (Mapped to UST Time)
plot(Current_Age_UST, interp1(time_vector_UST, Q_evolution, Current_Age_UST), ...
    'wo', 'MarkerSize', 10, 'MarkerFaceColor', 'b', 'MarkerEdgeColor', 'k', ...
    'DisplayName', sprintf('Current Epoch (%.2f UST-Gyr)', Current_Age_UST));
xline(Current_Age_UST, '--b', 'Alpha', 0.5, 'HandleVisibility', 'off');

% C. Hubble Macro-Limit Anchor
xline(t_H_UST_Gyr, '--m', 'Alpha', 0.5, 'HandleVisibility', 'off');
plot(t_H_UST_Gyr, interp1(time_vector_UST, Q_evolution, t_H_UST_Gyr), ...
    'md', 'MarkerSize', 8, 'MarkerFaceColor', 'm', ...
    'DisplayName', sprintf('Hubble Anchor (%.3f UST-Gyr)', t_H_UST_Gyr));

% D. Channel Inversion (The Next Big Bang)
plot(Inversion_Time_UST, 0.5, 'r*', 'MarkerSize', 14, 'MarkerFaceColor', 'r', ...
    'DisplayName', 'Channel Inversion (S=0, Next Big Bang)');
xline(Inversion_Time_UST, '-.k', 'LineWidth', 2, 'HandleVisibility', 'off');
text(Inversion_Time_UST + 0.2, 0.52, 'PHASE TRANSITION\nQ=C=0.5', ...
    'FontSize', 11, 'FontWeight', 'bold', 'Color', 'r');

% Formatting
xlabel('UST Universal Time (Gyr)', 'FontWeight', 'bold', 'FontSize', 12);
ylabel('Ontological Weight (Ns)', 'FontWeight', 'bold', 'FontSize', 12);
title('UST v5: Cosmological Timeline - From Big Bang to Next Channel Inversion', ...
      'FontWeight', 'bold', 'FontSize', 15);
legend('Location', 'southwest', 'FontSize', 11);
grid on;
ylim([0.3 0.7]);
xlim([-0.5 Inversion_Time_UST * 1.1]);

% Execute & Display Console Output
fprintf('--- UST v5 Cosmological Timeline Analysis ---\n');
fprintf('Big Bang (Start)         : 0.000 UST-Gyr\n');
fprintf('Current Age (SI)         : %.3f Gyr\n', Current_Age_SI);
fprintf('Current Age (UST Time)   : %.3f UST-Gyr\n', Current_Age_UST);
fprintf('Hubble Anchor Limit      : %.3f UST-Gyr\n', t_H_UST_Gyr);
fprintf('Next Channel Inversion   : %.3f UST-Gyr\n', Inversion_Time_UST);
fprintf('Inversion Mechanism      : Deterministic phase shift at Channel Q = Channel C = 0.5\n');
Analitik Yorum ve Operasyonel Çıktılar: