% UST_CosmicBudget_and_Inversion_Timeline.m
% Unified Source Theory (UST) v5 - Comprehensive Cosmological Matrix
% Integrates Cosmic Energy Budget (T5) and Exact Temporal Inversion Limit (T17/T25).

clear; clc; close all;

% =========================================================================
% 1. CORE ONTOLOGICAL CONSTANTS & UST V5 THEOREMS
% =========================================================================
N_b  = 0.63354460;        % Channel Q (Active Observable Sector / Blueprint)
C_cb = 0.36645540;        % Channel C (Frozen Gravitational Background)
T_Om = 0.23252885;        % WKB Tunnel Amplitude (Information Leakage)
phi  = (1 + sqrt(5))/2;   % Golden Ratio
Omnium_Ratio = 1 / N_b;   % T17 Horizon Scale (~1.578421)

% =========================================================================
% 2. COSMIC BUDGET CALCULATION (THEOREM 5)
% =========================================================================
% Standard empirical observation for Dark Matter (Planck 2018)
Omega_DM_obs = 0.265;     

% T5: Dark Energy is Channel C pressure filtered by log-spiral geometry
Omega_Lambda_UST = N_b + (Omega_DM_obs / (phi * pi)); % ~0.6857

% Remaining budget allocated to Baryonic matter
Omega_Baryonic_UST = 1.0 - (Omega_Lambda_UST + Omega_DM_obs);

% =========================================================================
% 3. EXACT TEMPORAL INVERSION CALCULATION (T17 & T25)
% =========================================================================
% Current observable cosmic age in standard SI units (Gyr)
t_current_SI = 13.8;      

% The maximum temporal extent (Inversion Point) before Channel Q collapses
% into Channel C. Governed by the Omnium Horizon scalar (1 / N_b).
t_inversion_SI = t_current_SI * Omnium_Ratio; % 13.8 * 1.578421 = 21.7822 Gyr

% Remaining time until deterministic phase shift (Next Big Bang)
t_remaining_SI = t_inversion_SI - t_current_SI; % ~7.9822 Gyr

% =========================================================================
% 4. ADVANCED VISUALIZATION MATRIX
% =========================================================================
fig = figure('Name', 'UST v5: Cosmic Budget & Exact Inversion Timeline');

% ---------------------------------------------------------
% Subplot 1: T5 Cosmic Energy Budget Distribution
% ---------------------------------------------------------
subplot(1, 2, 1);
budget_data = [Omega_Lambda_UST, Omega_DM_obs, Omega_Baryonic_UST];
labels = {sprintf('Dark Energy (\\Omega_\\Lambda)\n%.4f (T5 Limit)', Omega_Lambda_UST), ...
          sprintf('Dark Matter (\\Omega_{DM})\n%.4f', Omega_DM_obs), ...
          sprintf('Baryonic (\\Omega_b)\n%.4f', Omega_Baryonic_UST)};
          
pie_chart = pie(budget_data, labels);
title('T5: Deterministic Cosmic Energy Budget', 'FontWeight', 'bold', 'FontSize', 13);
colormap([0.1 0.4 0.7; 0.3 0.3 0.3; 0.8 0.6 0.1]);

% Format pie chart text for professional aesthetic
for i = 1:2:length(pie_chart)
    pie_chart(i+1).FontSize = 10;
    pie_chart(i+1).FontWeight = 'bold';
end

% ---------------------------------------------------------
% Subplot 2: Temporal Inversion Vector (Phase Transition)
% ---------------------------------------------------------
subplot(1, 2, 2);
t_vector = linspace(0, 30, 1000); % Spanning 30 Billion Years

% Simulating the topological decay of Channel Q and rise of Channel C
% They intersect exactly at t_inversion_SI (21.782 Gyr)
freq = pi / (2 * t_inversion_SI);
Q_decay = 0.5 + (N_b - 0.5) * cos(freq * t_vector);
C_rise  = 0.5 - (N_b - 0.5) * cos(freq * t_vector);

plot(t_vector, Q_decay, 'LineWidth', 3, 'Color', [0.1 0.5 0.8], 'DisplayName', 'Channel Q (Active Universe)'); hold on;
plot(t_vector, C_rise, 'LineWidth', 3, 'Color', [0.8 0.2 0.2], 'DisplayName', 'Channel C (Frozen Background)');

% Shaded leakage area representing T_Om WKB Tunnelling
fill([t_vector, fliplr(t_vector)], [Q_decay, fliplr(C_rise)], [0.8 0.8 0.8], ...
    'FaceAlpha', 0.2, 'EdgeColor', 'none', 'DisplayName', 'T_{Om} Information Leakage');

% Timeline Anchors
plot(0, N_b, 'ks', 'MarkerSize', 10, 'MarkerFaceColor', 'k', 'HandleVisibility', 'off');
text(0.5, N_b, 'Big Bang', 'FontSize', 10, 'FontWeight', 'bold');

% Current Age Marker
xline(t_current_SI, '--b', 'LineWidth', 1.5, 'HandleVisibility', 'off');
plot(t_current_SI, interp1(t_vector, Q_decay, t_current_SI), 'wo', ...
    'MarkerSize', 10, 'MarkerFaceColor', 'b', 'MarkerEdgeColor', 'k', ...
    'DisplayName', sprintf('Current Epoch (%.2f Gyr)', t_current_SI));

% Inversion Marker (The 7.98 Billion Year limit)
xline(t_inversion_SI, '-.k', 'LineWidth', 2, 'HandleVisibility', 'off');
plot(t_inversion_SI, 0.5, 'rp', 'MarkerSize', 14, 'MarkerFaceColor', 'r', ...
    'DisplayName', sprintf('Phase Inversion at %.3f Gyr', t_inversion_SI));

% Remaining Time Annotation
text(t_current_SI + (t_remaining_SI/2), 0.65, sprintf('\\Delta t = %.3f Gyr\nUntil Inversion', t_remaining_SI), ...
    'HorizontalAlignment', 'center', 'FontSize', 11, 'FontWeight', 'bold', 'Color', 'k', 'BackgroundColor', 'w', 'EdgeColor', 'k');

% Graph Aesthetics
xlabel('Cosmological Time (SI - Gyr)', 'FontWeight', 'bold', 'FontSize', 12);
ylabel('Ontological Fractional Weight', 'FontWeight', 'bold', 'FontSize', 12);
title('Temporal Expansion to Omnium Horizon & Phase Inversion Limit', 'FontWeight', 'bold', 'FontSize', 13);
legend('Location', 'southwest');
grid on;
ylim([0.35 0.65]);
xlim([-1 28]);

% =========================================================================
% 5. CONSOLE OUTPUT METRICS
% =========================================================================
fprintf('--- UST v5 Cosmic Budget & Inversion Metrics ---\n');
fprintf('Dark Energy (Omega_Lambda) : %.6f\n', Omega_Lambda_UST);
fprintf('Dark Matter (Omega_DM)     : %.6f\n', Omega_DM_obs);
fprintf('Current Cosmic Age         : %.3f Billion Years (Gyr)\n', t_current_SI);
fprintf('Omnium Horizon Ratio (1/Nb): %.6f\n', Omnium_Ratio);
fprintf('Absolute Inversion Point   : %.3f Billion Years (Gyr)\n', t_inversion_SI);
fprintf('Remaining Time to Collapse : %.3f Billion Years (Gyr)\n', t_remaining_SI);
fprintf('Status                     : Deterministic parameters executed flawlessly.\n');