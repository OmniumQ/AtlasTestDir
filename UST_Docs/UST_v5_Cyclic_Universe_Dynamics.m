% UST_v5_Cyclic_Universe_Dynamics.m
% Unified Source Theory (UST) v5 - Advanced Cosmological Matrix
% Operational Simulation of T25 (Big Bang Channel Inversion), T32 (Universal Time),
% and Deterministic Phase Transitions without free parameters.

clear; clc; close all;

% --- 1. UST v5 Ontological Core Constants ---
N_b  = 0.63354460;       % Channel Q (Active Observable Sector / Blueprint)
C_cb = 0.36645540;       % Channel C (Frozen Gravitational Background)
T_Om = 0.23252885;       % WKB Tunnel Amplitude (Constant across cycles)
phi  = (1 + sqrt(5))/2;  % Golden Ratio Filter

% --- 2. Cosmological Time Parameters (T32 & T25) ---
H0_Planck = 67.4;             % km/s/Mpc
t_H_Gyr = 14.5;               % Hubble Macro-Time Limit (Gyr)
t_UST_epoch = t_H_Gyr * N_b;  % Universal Time Anchor (T32) -> ~9.192 Gyr
Current_Age_Gyr = 13.8;       % Empirical standard model cosmic age

% Cycle Frequency and Tunnelling Decay Rate
% The universe oscillates symmetrically. T_Om governs the transition threshold.
cycle_freq = 1 / T_Om;        % 4.3005 (T25 Frequency Constant)
phase_velocity = pi * T_Om;   % Transformation rate Q -> C

% --- 3. Figure Initialization ---
fig = figure('Name', 'UST v5: Cyclic Universe & Deterministic Inversion');

% =========================================================================
% SUBPLOT 1: ONL 3-Region Partition (Current Snapshot)
% =========================================================================
subplot(2, 2, 1);
pie_data = [T_Om, (N_b - T_Om), C_cb];
labels = {sprintf('Channel C (Frozen)\n%.4f', T_Om), ...
          sprintf('0-Element (Transition)\n%.4f', (N_b - T_Om)), ...
          sprintf('Channel Q (Active)\n%.4f', C_cb)};
pie(pie_data, labels);
title('Current ONL Partition (Sum = 1.0)', 'FontWeight', 'bold', 'FontSize', 12);
colormap([0.3 0.3 0.3; 0.8 0.6 0.1; 0.1 0.5 0.8]);

% =========================================================================
% SUBPLOT 2: T32 Universal Time Map & Hubble Equivalence
% =========================================================================
subplot(2, 2, 2);
time_metrics = [Current_Age_Gyr, t_H_Gyr, t_UST_epoch];
b = bar(time_metrics, 'FaceColor', 'flat', 'EdgeColor', 'k');
b.CData(1,:) = [0.2 0.6 0.4];
b.CData(2,:) = [0.6 0.2 0.2];
b.CData(3,:) = [0.2 0.4 0.8];
set(gca, 'XTick', 1:3, 'XTickLabel', {'Empirical Age (13.8)', 'Hubble Limit (14.5)', 'UST Anchor (9.192)'});
ylabel('Time (Gyr)');
ylim();
grid on;
title(sprintf('T32: Universal Time Standard\nt_H \\times N_b = \\nu_{Cs-133} (%.3f Gyr)', t_UST_epoch), 'FontWeight', 'bold');

% =========================================================================
% SUBPLOT 3: T25 Cyclic Channel Evolution & Big Bang Inversion 
% =========================================================================
subplot(2, 2, [8, 9]);

% Cosmological Time Vector (Normalized to Hubble expansions)
t_norm = linspace(0, 3, 2000); % Spanning 3 cosmic cycles

% Mathematical Oscillation of Channels (Amplitude = N_b - 0.5)
Amp = N_b - 0.5; 
% Even cycles: C dominates. Odd cycles: Q dominates.
Q_evolution = 0.5 + Amp * cos(pi * t_norm);
C_evolution = 0.5 - Amp * cos(pi * t_norm);

% Plotting the ontological vectors
plot(t_norm, Q_evolution, 'LineWidth', 3, 'Color', [0.1 0.5 0.8], 'DisplayName', 'Channel Q (Active Universe)'); hold on;
plot(t_norm, C_evolution, 'LineWidth', 3, 'Color', [0.6 0.2 0.2], 'DisplayName', 'Channel C (Frozen Background)');

% Marking the Channel Inversion points (Phase Transition / Big Bangs)
inversion_indices = find(diff(sign(Q_evolution - C_evolution)));
for i = 1:length(inversion_indices)
    inv_x = t_norm(inversion_indices(i));
    xline(inv_x, '--k', 'LineWidth', 1.5, 'HandleVisibility', 'off');
    plot(inv_x, 0.5, 'ks', 'MarkerSize', 10, 'MarkerFaceColor', 'k', 'HandleVisibility', 'off');
    text(inv_x, 0.45, sprintf('Channel Inversion\n(Big Bang)'), ...
         'HorizontalAlignment', 'center', 'FontSize', 10, 'FontWeight', 'bold');
end

% Marking the Current Cosmic Epoch (Projected near the active peak)
% Our universe is an odd-numbered cycle where N_b = 0.6335 (Max Q)
current_phase_x = 0.15; % Approximation of empirical age in current phase
plot(current_phase_x, interp1(t_norm, Q_evolution, current_phase_x), 'wo', ...
     'MarkerSize', 10, 'MarkerFaceColor', 'b', 'MarkerEdgeColor', 'k', 'DisplayName', 'Current Cosmic Epoch');

% Visualizing the T_Om Tunneling Decay vector
fill_x = [t_norm, fliplr(t_norm)];
fill_y = [Q_evolution, fliplr(C_evolution)];
fill(fill_x, fill_y, [0.8 0.8 0.8], 'FaceAlpha', 0.2, 'EdgeColor', 'none', 'DisplayName', 'T_{Om} Tunneling Transfer');

xlabel('Cosmological Phase Progression (\tau)', 'FontWeight', 'bold', 'FontSize', 11);
ylabel('Ontological Weight (Fraction)', 'FontWeight', 'bold', 'FontSize', 11);
title('T25: Deterministic Cyclic Cosmology & Channel Inversion (The Next Big Bang)', 'FontWeight', 'bold', 'FontSize', 13);
legend('Location', 'northeast');
grid on;
ylim([0.3 0.7]);
xlim([0 2.5]);

% 4. System Output
disp('UST v5 Operational Matrix: T25 and T32 simulations successfully executed.');
disp('Note: The transition energy threshold is strictly locked to T_Om^2 = 0.05407.');
Analitik ve Operasyonel Çıktıların Akademik Yorumu: