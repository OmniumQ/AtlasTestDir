"""
ATLAS MC Metadata — Tam Analiz
Nb, Nm, RA, 17 faktörü dahil tüm testler
"""

import numpy as np
import pandas as pd

# ── UST sabitleri ─────────────────────────────────────────────────────
N_b  = 0.63354460
N_m  = 0.63353522
RA   = N_b - N_m       # = 9.38e-6
Cc_b = 1 - N_b
Cc_m = 1 - N_m
T_Om = np.exp(-2 * np.pi * N_b * Cc_b)
T11  = (N_m / Cc_m) * (1 + N_b * N_m / (2 * np.pi))
alpha = 1 / 137.036
a17   = alpha / 17
N_geo = (3 - np.sqrt(3)) / 2

print("=" * 70)
print("UST v5 — ATLAS MC Metadata Tam Analiz")
print(f"N_b={N_b}  N_m={N_m}  RA={RA:.4e}")
print("=" * 70)

# ── CSV oku ───────────────────────────────────────────────────────────
path = r"C:\AtlasTest\GamGam\mc_metadata.csv"
df = pd.read_csv(path)

print(f"\nToplam satır: {len(df)}")
print(f"Sütunlar: {list(df.columns)}")
print(f"\n{df.to_string(max_rows=30)}")

# ── Numerik sütunları bul ──────────────────────────────────────────────
num_cols = ['crossSection_pb', 'genFiltEff', 'kFactor',
            'nEvents', 'sumOfWeights', 'sumOfWeightsSquared']
num_cols = [c for c in num_cols if c in df.columns]

print("\n" + "=" * 70)
print("NUMERIK SÜTUN İSTATİSTİKLERİ")
print("=" * 70)
for col in num_cols:
    vals = pd.to_numeric(df[col], errors='coerce').dropna()
    if len(vals) == 0:
        continue
    print(f"\n  [{col}]  n={len(vals)}")
    print(f"  min={vals.min():.6g}  max={vals.max():.6g}  "
          f"mean={vals.mean():.6g}  std={vals.std():.6g}")

# ── CrossSection UST testleri ──────────────────────────────────────────
print("\n" + "=" * 70)
print("CROSS SECTION — UST T11 ve ONL TESTLERİ")
print("=" * 70)

if 'crossSection_pb' in df.columns:
    sigma = pd.to_numeric(df['crossSection_pb'], errors='coerce').dropna()
    sigma_pos = sigma[sigma > 0].values

    print(f"\n  Tüm cross section değerleri:")
    for i, (idx, row) in enumerate(df.iterrows()):
        s = pd.to_numeric(row.get('crossSection_pb', 0), errors='coerce')
        if pd.notna(s) and s > 0:
            name = row.get('physics_short', str(row.get('dataset_number',i)))[:45]
            print(f"  {name:<45} σ={s:.6g} pb")

    print(f"\n  --- T11 yüzdelik oranı ---")
    pQ = np.percentile(sigma_pos, N_b * 100)
    pC = np.percentile(sigma_pos, Cc_b * 100)
    pQ_m = np.percentile(sigma_pos, N_m * 100)
    pC_m = np.percentile(sigma_pos, Cc_m * 100)

    r_nb = pQ / pC
    r_nm = pQ_m / pC_m
    d_nb = abs(r_nb - T11) / T11 * 100
    d_nm = abs(r_nm - T11) / T11 * 100

    print(f"  Nb: pQ={pQ:.6g}  pC={pC:.6g}  oran={r_nb:.6f}  Δ%={d_nb:.4f}%")
    print(f"  Nm: pQ={pQ_m:.6g}  pC={pC_m:.6g}  oran={r_nm:.6f}  Δ%={d_nm:.4f}%")
    print(f"  Kazanan: {'Nb' if d_nb < d_nm else 'Nm'}  "
          f"fark={abs(d_nb-d_nm):.6f}%  RA={RA:.4e}")

    print(f"\n  --- ONL üç bölge ---")
    thr_tom = np.percentile(sigma_pos, T_Om * 100)
    thr_nb  = np.percentile(sigma_pos, N_b * 100)
    f_c  = np.sum(sigma_pos <= thr_tom) / len(sigma_pos)
    f_om = np.sum((sigma_pos > thr_tom) & (sigma_pos <= thr_nb)) / len(sigma_pos)
    f_q  = np.sum(sigma_pos > thr_nb) / len(sigma_pos)
    print(f"  N={len(sigma_pos)}")
    print(f"  Channel C  beklenen={T_Om:.6f}  ölçülen={f_c:.6f}  "
          f"Δ%={abs(f_c-T_Om)/T_Om*100:.4f}%")
    print(f"  0-Element  beklenen={N_b-T_Om:.6f}  ölçülen={f_om:.6f}  "
          f"Δ%={abs(f_om-(N_b-T_Om))/(N_b-T_Om)*100:.4f}%")
    print(f"  Channel Q  beklenen={Cc_b:.6f}  ölçülen={f_q:.6f}  "
          f"Δ%={abs(f_q-Cc_b)/Cc_b*100:.4f}%")

    # ── 17 faktörü: tüm çiftler ────────────────────────────────────────
    print(f"\n  --- σ oranları → 17 kontrolü ---")
    names = []
    for idx, row in df.iterrows():
        s = pd.to_numeric(row.get('crossSection_pb',0), errors='coerce')
        if pd.notna(s) and s > 0:
            names.append((row.get('physics_short','?')[:30], s))

    print(f"  {'σ_i / σ_j':<40} {'Oran':>10} {'Δ%_17':>8} {'Δ%_T11':>8}")
    print("  " + "-" * 65)
    hits_17 = []
    hits_t11 = []
    for i in range(len(names)):
        for j in range(len(names)):
            if i == j:
                continue
            ni, si = names[i]
            nj, sj = names[j]
            if si <= 0 or sj <= 0:
                continue
            r = si / sj
            d17  = abs(r - 17) / 17 * 100
            dt11 = abs(r - T11) / T11 * 100
            if d17 < 5:
                hits_17.append((ni, nj, r, d17))
                flag = "✓✓✓" if d17<1 else "✓✓" if d17<3 else "✓"
                print(f"  {ni[:25]}/{nj[:25]:<30} {r:>10.4f} "
                      f"{d17:>7.3f}% {flag}")
            elif dt11 < 5:
                hits_t11.append((ni, nj, r, dt11))
                flag = "✓✓✓" if dt11<1 else "✓✓"
                print(f"  {ni[:25]}/{nj[:25]:<30} {r:>10.4f} "
                      f"{'—':>8} {dt11:>7.3f}% {flag}")

    print(f"\n  17'ye yakın oran sayısı : {len(hits_17)}")
    print(f"  T11'e yakın oran sayısı: {len(hits_t11)}")

# ── genFiltEff testleri ────────────────────────────────────────────────
print("\n" + "=" * 70)
print("genFiltEff — Nb/Nm/RA ANALİZİ")
print("=" * 70)

if 'genFiltEff' in df.columns:
    effs = pd.to_numeric(df['genFiltEff'], errors='coerce').dropna()
    effs = effs[effs > 0].values

    print(f"\n  Tüm genFiltEff değerleri: {effs}")
    print(f"  Ortalama: {effs.mean():.8f}")
    print(f"  Std:      {effs.std():.8f}")

    for name, val in [
        ("N_b",     N_b),
        ("N_m",     N_m),
        ("Cc_b",    Cc_b),
        ("T_Om",    T_Om),
        ("T11",     T11),
        ("a17",     a17),
        ("N_geo",   N_geo),
        ("0.43",    0.43),
        ("sqrt(Nb)",np.sqrt(N_b)),
    ]:
        d = abs(effs.mean() - val) / val * 100
        flag = "✓✓✓" if d<1 else "✓✓" if d<3 else "✓" if d<10 else "—"
        print(f"  Ort genFiltEff vs {name:<12} = {val:.8f}  "
              f"Δ%={d:.4f}%  {flag}")

    print(f"\n  Nb/Nm fark testi:")
    print(f"  |mean - N_b| = {abs(effs.mean()-N_b):.4e}")
    print(f"  |mean - N_m| = {abs(effs.mean()-N_m):.4e}")
    print(f"  RA           = {RA:.4e}")
    print(f"  Kazanan: {'N_b' if abs(effs.mean()-N_b) < abs(effs.mean()-N_m) else 'N_m'}")

# ── process sütunu analizi ────────────────────────────────────────────
print("\n" + "=" * 70)
print("PROCESS DAĞILIMI")
print("=" * 70)
if 'process' in df.columns:
    for proc in df['process'].unique():
        n = len(df[df['process']==proc])
        print(f"  {proc:<35} n={n}")

    n_bsm = len(df[df['keywords'].str.contains('BSM', na=False)])
    n_sm  = len(df[df['keywords'].str.contains("'SM'", na=False)])
    n_total_proc = len(df)
    print(f"\n  BSM süreçler: {n_bsm}  ({n_bsm/n_total_proc:.6f})")
    print(f"  SM  süreçler: {n_sm}   ({n_sm/n_total_proc:.6f})")
    print(f"  BSM/total beklenen Nb={N_b:.6f}  "
          f"Δ%={abs(n_bsm/n_total_proc-N_b)/N_b*100:.4f}%")

print("\n✓ Tamamlandı.")
