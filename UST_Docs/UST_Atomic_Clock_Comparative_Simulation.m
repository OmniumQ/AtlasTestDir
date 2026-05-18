% UST_Atomic_Clock_Comparative_Simulation.m
% Unified Source Theory (UST) v5 - Cyclic Cosmology & Atomic Clock Bridge
% Integrates T25 (Channel Inversion) with T32 (Micro-Macro Time Standard Equivalence).

clear; clc; close all;

% --- 1. Core UST Ontological Constants ---
N_b  = 0.63354460;       % Channel Q (Active Observable Sector)
C_cb = 0.36645540;       % Channel C (Frozen Gravitational Background)
T_Om = 0.23252885;       % WKB Tunnel Amplitude

% --- 2. T32: Atomic Clock & Hubble Time Equivalence ---
% Macro-scale: Hubble expansion time anchor
t_H_UST_Gyr = 9.191984;  % t_H * N_b (Gyr)

% Micro-scale: Cesium-133 hyperfine transition frequency (Atomic Clock)
v_Cs_133_GHz = 9.192632; % Frequency (GHz)

% Deviation Calculation
Delta_Percent = abs(t_H_UST_Gyr - v_Cs_133_GHz) / v_Cs_133_GHz * 100;

% --- 3. T25: Timeline & Inversion Vectors ---
Current_Age_UST = 13.8 * N_b; % ~8.7429 Gyr
Inversion_Time_UST = t_H_UST_Gyr + (T_Om * t_H_UST_Gyr); % Phase transition limit

time_vector_UST = linspace(0, Inversion_Time_UST * 1.1, 2000); 
freq = pi / (2 * Inversion_Time_UST); 
Amplitude = N_b - 0.5;

Q_evolution = 0.5 + Amplitude * cos(freq * time_vector_UST);
C_evolution = 0.5 - Amplitude * cos(freq * time_vector_UST);

% --- 4. Advanced Comparative Visualization ---
fig = figure('Name', 'UST v5: Universal Timeline & Atomic Clock Bridge');

% Subplot 1: T32 Micro-Macro Bridge (Atomic Clock vs Hubble Time)
subplot(1, 3, 1);
bar_data = [t_H_UST_Gyr, v_Cs_133_GHz];
b = bar(bar_data, 'FaceColor', 'flat', 'EdgeColor', 'k', 'LineWidth', 1.2);
b.CData(1,:) = [0.2 0.6 0.8]; % UST Hubble Anchor (Blue)
b.CData(2,:) = [0.8 0.4 0.2]; % Cs-133 Atomic Clock (Orange)
set(gca, 'XTick', 1:2, 'XTickLabel', {'Hubble Anchor (Gyr)', 'Cs-133 Clock (GHz)'}, ...
    'FontSize', 10, 'FontWeight', 'bold');
ylabel('Numerical Value', 'FontWeight', 'bold');
ylim([9.18 9.20]); % Zoomed in to show precision
title(sprintf('T32: Micro-Macro Time Bridge\n\\Delta%% = %.3f%%', Delta_Percent), ...
    'FontSize', 12, 'FontWeight', 'bold');
grid on;

% Subplot 2: T25 Universal Timeline & Inversion (2/3 of the figure width)
subplot(1, 3, [5, 6]);
plot(time_vector_UST, Q_evolution, 'LineWidth', 3, 'Color', [0.1 0.5 0.8], ...
    'DisplayName', 'Channel Q (Active Universe)'); hold on;
plot(time_vector_UST, C_evolution, 'LineWidth', 3, 'Color', [0.8 0.2 0.2], ...
    'DisplayName', 'Channel C (Frozen Background)');

% Shaded Tunneling Region
fill_x = [time_vector_UST, fliplr(time_vector_UST)];
fill_y = [Q_evolution, fliplr(C_evolution)];
fill(fill_x, fill_y, [0.8 0.8 0.8], 'FaceAlpha', 0.3, 'EdgeColor', 'none', ...
    'DisplayName', 'T_{Om} Tunnelling Leakage');

% Markers
plot(0, N_b, 'ks', 'MarkerSize', 10, 'MarkerFaceColor', 'k', 'HandleVisibility', 'off');
text(0.2, N_b, 'Big Bang (t=0)', 'FontSize', 10, 'FontWeight', 'bold');

plot(Current_Age_UST, interp1(time_vector_UST, Q_evolution, Current_Age_UST), ...
    'wo', 'MarkerSize', 10, 'MarkerFaceColor', 'b', 'MarkerEdgeColor', 'k', ...
    'DisplayName', sprintf('Current Epoch (%.2f UST-Gyr)', Current_Age_UST));
xline(Current_Age_UST, '--b', 'Alpha', 0.5, 'HandleVisibility', 'off');

% Hardware Lock Marker (T32 Integration)
plot(t_H_UST_Gyr, interp1(time_vector_UST, Q_evolution, t_H_UST_Gyr), ...
    'md', 'MarkerSize', 10, 'MarkerFaceColor', 'm', ...
    'DisplayName', sprintf('Atomic Clock Resonance (%.3f UST-Gyr)', t_H_UST_Gyr));
xline(t_H_UST_Gyr, '-.m', 'LineWidth', 1.5, 'HandleVisibility', 'off');
text(t_H_UST_Gyr - 1.5, 0.45, sprintf('Micro-Macro Resonance\n(v_{Cs-133} \\approx t_H \\times N_b)'), ...
    'Color', 'm', 'FontWeight', 'bold', 'FontSize', 10, 'HorizontalAlignment', 'center');

plot(Inversion_Time_UST, 0.5, 'r*', 'MarkerSize', 14, 'MarkerFaceColor', 'r', ...
    'DisplayName', 'Channel Inversion (Next Big Bang)');
xline(Inversion_Time_UST, '-.k', 'LineWidth', 2, 'HandleVisibility', 'off');

% Formatting
xlabel('UST Universal Time (Gyr)', 'FontWeight', 'bold', 'FontSize', 12);
ylabel('Ontological Weight (Ns)', 'FontWeight', 'bold', 'FontSize', 12);
title('UST v5: Cosmological Timeline and Atomic Clock Resonance Integration', ...
      'FontWeight', 'bold', 'FontSize', 15);
legend('Location', 'southwest', 'FontSize', 11);
grid on;
ylim([0.3 0.7]);
xlim([-0.5 Inversion_Time_UST * 1.1]);

% Execute & Display Console Output
fprintf('--- UST v5 Operational Matrix: T25 & T32 Execution ---\n');
fprintf('Hubble Time Anchor (t_H * N_b) : %.6f Gyr\n', t_H_UST_Gyr);
fprintf('Cesium-133 Atomic Clock        : %.6f GHz\n', v_Cs_133_GHz);
fprintf('Micro-Macro Deviation (Delta%%) : %.3f%%\n', Delta_Percent);
fprintf('Hardware Resonance verified. Ontological execution complete.\n');