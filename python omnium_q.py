#!/usr/bin/env python3
# rigorous_dm_omnium_spectrum_pipeline.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from astropy.io import votable
from scipy.optimize import minimize
import sympy as sp
import os

# ============================================================
# 0) KULLANICI AYARLARI
# ============================================================

# Birden fazla Euclid alanı / dosyası:
EUCLID_FILES = [
    # ('etiket', 'dosya_yolu', 'tip')
    # tip: 'vot' veya 'csv'
    ('field_1', 'C:\\AtlasTest\\82996c50-220d-11f1-8a0e-e8ebd3edb7d7-TPDR-result.vot', 'vot'),
    ('field_2', 'C:\\AtlasTest\\82996c50-220d-11f1-8a0e-e8ebd3edb7d7-TPDR-result.vot', 'vot'),
    # örnek: ('field_3', 'euclid_field3.csv', 'csv'),
]

# Filtre parametreleri
MIN_FLUX = 0.0
MIN_SEG_AREA = 5
DET_QUALITY_GOOD = 0
POINT_LIKE_MAX = 0.5

ENTROPY_BINS = 100
BOOTSTRAP_N = 300  # çok büyütürsen yavaşlar

# Teorik hedef Omnium
TARGET_TOM = -0.00042925603348728  # -alpha/17 gibi

# a2 spektrum taraması için parametre aralıkları
H_VALUES = [0.5, 1.0, 2.0]      # örnek Hubble ölçekleri
XI_VALUES = [0.0, 0.1, 0.2]     # eğrilik bağlanması
M2_VALUES = [0.0, 0.01, 0.1]    # kütle karesi

OUTPUT_SUMMARY = "rigorous_dm_omnium_spectrum_summary.csv"
PLOT_DIR = "rigorous_plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# ============================================================
# 1) YARDIMCI FONKSİYONLAR
# ============================================================

def load_euclid_table(path, ftype='vot'):
    if ftype == 'vot':
        vot = votable.parse(path)
        table = vot.get_first_table().to_table(use_names_over_ids=True)
        df = table.to_pandas()
    elif ftype == 'csv':
        df = pd.read_csv(path)
    else:
        raise ValueError("file_type 'vot' veya 'csv' olmalı.")
    return df

def shannon_entropy(arr, bins=100):
    hist, edges = np.histogram(arr, bins=bins, density=True)
    p = hist * np.diff(edges)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def bootstrap_entropy(arr, bins=100, nboot=300):
    n = len(arr)
    boots = []
    for _ in range(nboot):
        sample = np.random.choice(arr, size=n, replace=True)
        boots.append(shannon_entropy(sample, bins=bins))
    boots = np.array(boots)
    return np.percentile(boots, [16, 50, 84])

# a2 genel sembolik ifade (bir kez kur)
R0_sym, c1_sym, c2_sym = sp.symbols('R0 c1 c2', real=True)
alpha_sym, beta_sym = sp.symbols('alpha beta', real=True)

a2_expr = (
    - (R0_sym**2 * c1_sym) / 180
    + (R0_sym**2 * c2_sym) / 180
    + (R0_sym**2) / 72
    + (R0_sym * (R0_sym*alpha_sym + beta_sym)) / 6
    + ((R0_sym*alpha_sym + beta_sym)**2) / 2
)
a2_expr = sp.simplify(a2_expr)

def compute_a2(H_val, xi_val, m2_val):
    # de Sitter örneği:
    # R0 = 12 H^2
    # Ricci^2 = (1/4) R0^2
    # Riemann^2 = (1/6) R0^2
    R0_val = 12 * H_val**2
    c1_val = 1/4
    c2_val = 1/6
    alpha_val = xi_val
    beta_val = m2_val
    return float(a2_expr.subs({
        R0_sym: R0_val,
        c1_sym: c1_val,
        c2_sym: c2_val,
        alpha_sym: alpha_val,
        beta_sym: beta_val
    }).evalf())

def fit_Tom_linear(R_value, target_Tom):
    def model(params, r):
        a, b = params
        return a * r + b
    def loss(params):
        return (model(params, R_value) - target_Tom)**2
    res = minimize(loss, x0=[0.0, 0.0])
    a_fit, b_fit = res.x
    Tom_pred = a_fit * R_value + b_fit
    return a_fit, b_fit, Tom_pred

# ============================================================
# 2) ANA DÖNGÜ: TÜM EUCLID ALANLARI
# ============================================================

all_rows = []

for label, path, ftype in EUCLID_FILES:
    print(f"\n=== Processing {label} ({path}) ===")
    df = load_euclid_table(path, ftype)
    n_total = len(df)
    print("Toplam satır:", n_total)

    # Filtreler
    df = df.dropna(subset=['ellipticity'])

    if 'flux_detection_total' in df.columns:
        df = df[df['flux_detection_total'] > MIN_FLUX]

    if 'segmentation_area' in df.columns:
        df = df[df['segmentation_area'] >= MIN_SEG_AREA]

    if 'det_quality_flag' in df.columns:
        df = df[df['det_quality_flag'] == DET_QUALITY_GOOD]

    if 'point_like_prob' in df.columns:
        df = df[df['point_like_prob'] < POINT_LIKE_MAX]

    n_after = len(df)
    print("Filtre sonrası satır:", n_after)

    if n_after == 0:
        print("Uygun veri yok, atlanıyor.")
        continue

    # Eliptiklik KDE + entropi
    e = df['ellipticity'].to_numpy()
    kde = gaussian_kde(e, bw_method='scott')
    xs = np.linspace(0, 1, 2000)
    kde_vals = kde(xs)
    peak = xs[np.argmax(kde_vals)]

    S_total = shannon_entropy(e, bins=ENTROPY_BINS)
    S_CI = bootstrap_entropy(e, bins=ENTROPY_BINS, nboot=BOOTSTRAP_N)

    print(f"KDE peak (ellipticity) = {peak:.6f}")
    print(f"Shannon entropy (ellipticity) = {S_total:.6f}")
    print("Entropy CI (16,50,84) =", S_CI)

    # DM / DE proxy (flux medyan)
    if 'flux_detection_total' not in df.columns:
        print("flux_detection_total yok, DM/DE ayrımı yapılamıyor, atlanıyor.")
        continue

    flux = df['flux_detection_total'].to_numpy()
    flux_med = np.median(flux)

    mask_DM = flux > flux_med
    mask_DE = flux <= flux_med

    e_DM = df.loc[mask_DM, 'ellipticity'].to_numpy()
    e_DE = df.loc[mask_DE, 'ellipticity'].to_numpy()

    S_DM = shannon_entropy(e_DM, bins=ENTROPY_BINS)
    S_DE = shannon_entropy(e_DE, bins=ENTROPY_BINS)
    R_value = S_DM / S_DE if S_DE != 0 else np.nan

    print(f"S_DM = {S_DM:.6f}, S_DE = {S_DE:.6f}, R = {R_value:.6f}")

    # Omnium lineer fit
    if not np.isnan(R_value):
        a_fit, b_fit, Tom_pred = fit_Tom_linear(R_value, TARGET_TOM)
        print("Best-fit (a,b) =", a_fit, b_fit)
        print("Predicted T_Om =", Tom_pred)
    else:
        a_fit = b_fit = Tom_pred = np.nan
        print("R NaN; T_Om fit atlanıyor.")

    # Bu alan için spektrum taraması (a2)
    spectrum_rows = []
    for H_val in H_VALUES:
        for xi_val in XI_VALUES:
            for m2_val in M2_VALUES:
                a2_val = compute_a2(H_val, xi_val, m2_val)
                spectrum_rows.append({
                    'field': label,
                    'H': H_val,
                    'xi': xi_val,
                    'm2': m2_val,
                    'a2': a2_val
                })

    spectrum_df = pd.DataFrame(spectrum_rows)
    spectrum_df.to_csv(os.path.join(PLOT_DIR, f"{label}_a2_spectrum.csv"), index=False)

    # DM–Omnium grafiği (bu alan için)
    R_grid = np.linspace(R_value - 0.01, R_value + 0.01, 200)
    Tom_grid = a_fit * R_grid + b_fit

    plt.figure(figsize=(7,5))
    plt.plot(R_grid, Tom_grid, label="Linear model", color="blue")
    plt.scatter([R_value], [Tom_pred], color="red", label="Euclid point", s=60)
    plt.axhline(TARGET_TOM, color="green", linestyle="--", label="Theoretical target")
    plt.xlabel("R = S_DM / S_DE")
    plt.ylabel("T_Om")
    plt.title(f"DM–Omnium Relation ({label})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, f"{label}_dm_omnium.png"), dpi=200)
    plt.close()

    # Özet satırı
    row = {
        'field': label,
        'n_total': int(n_total),
        'n_after': int(n_after),
        'kde_peak_ellipticity': float(peak),
        'S_total': float(S_total),
        'S_CI_16': float(S_CI[0]),
        'S_CI_50': float(S_CI[1]),
        'S_CI_84': float(S_CI[2]),
        'S_DM': float(S_DM),
        'S_DE': float(S_DE),
        'R': float(R_value),
        'flux_median': float(flux_med),
        'target_Tom': float(TARGET_TOM),
        'a_fit': float(a_fit),
        'b_fit': float(b_fit),
        'Tom_pred': float(Tom_pred)
    }
    all_rows.append(row)

# ============================================================
# 3) TÜM ALANLARIN ÖZETİ
# ============================================================

if all_rows:
    summary_df = pd.DataFrame(all_rows)
    summary_df.to_csv(OUTPUT_SUMMARY, index=False)
    print(f"\nGlobal summary saved to {OUTPUT_SUMMARY}")
else:
    print("\nHiç alan işlenemedi; özet oluşturulmadı.")