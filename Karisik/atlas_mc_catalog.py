"""
ATLAS MC Katalog — UST v5 Cross Section Analizi
CSV verisindeki cross section oranlarını UST sabitleriyle karşılaştır
"""

import numpy as np

# ── UST sabitleri ─────────────────────────────────────────────────────
N_b  = 0.63354460
N_m  = 0.63353522
Cc_b = 1 - N_b
T_Om = np.exp(-2 * np.pi * N_b * Cc_b)
T11_theory = (N_m/(1-N_m)) * (1 + N_b*N_m/(2*np.pi))
alpha = 1/137.036
a17   = alpha/17

print("=" * 65)
print("UST v5 — ATLAS MC Katalog Cross Section Analizi")
print("=" * 65)

# ── Katalog verileri ──────────────────────────────────────────────────
datasets = {
    # BSM sinyaller
    301204: {'name': "Z'→ee",        'sigma': 0.001762,  'n': 20000},
    301209: {'name': "Z'→μμ",        'sigma': 0.0017718, 'n': 20000},
    301243: {'name': "W'→eν",        'sigma': 0.011414,  'n': 8000},
    301247: {'name': "W'→μν",        'sigma': 0.011432,  'n': 20000},
    301333: {'name': "Z'→tt̄",       'sigma': 0.0050843, 'n': 30000},
    301826: {'name': "W'→qq",        'sigma': 0.10318,   'n': 10000},
    301928: {'name': "Z'→bb̄",       'sigma': 0.007024,  'n': 10000},
    # SM diphoton (arka plan)
    302520: {'name': "γγ (55-100)",   'sigma': 85.503,    'n': 2642000},
    302521: {'name': "γγ (100-160)",  'sigma': 18.282,    'n': 642000},
    302522: {'name': "γγ (160-250)",  'sigma': 5.028,     'n': 200000},
}

# ── Cross section değerleri ───────────────────────────────────────────
print("\n[1] Diphoton Cross Section Oranları")
print("-" * 50)
sig_A = datasets[302520]['sigma']  # 85.503
sig_B = datasets[302521]['sigma']  # 18.282
sig_C = datasets[302522]['sigma']  # 5.028

print(f"  σ(55-100)   = {sig_A:.3f} pb")
print(f"  σ(100-160)  = {sig_B:.3f} pb")
print(f"  σ(160-250)  = {sig_C:.3f} pb")

r_AB = sig_A / sig_B
r_BC = sig_B / sig_C
r_AC = sig_A / sig_C

print(f"\n  σ_A/σ_B = {sig_A}/{sig_B} = {r_AB:.4f}")
print(f"  σ_B/σ_C = {sig_B}/{sig_C} = {r_BC:.4f}")
print(f"  σ_A/σ_C = {sig_A}/{sig_C} = {r_AC:.4f}")

# UST karşılaştırması
print(f"\n  UST sabit karşılaştırması:")
for name, val in [
    ("17",        17),
    ("1/a17",     1/a17),
    ("1/T_Om",    1/T_Om),
    ("N_b/Cc_b",  N_b/Cc_b),
    ("T11",       T11_theory),
    ("κ2=2πNb",   2*np.pi*N_b),
]:
    d = abs(r_AC - val) / val * 100
    flag = "✓✓✓" if d<1 else "✓✓" if d<3 else "✓" if d<10 else "—"
    print(f"  σ_A/σ_C vs {name:<12} = {val:.4f}  "
          f"Δ% = {d:.4f}%  {flag}")

# ── Z' ve W' lepton universality ─────────────────────────────────────
print("\n[2] Z' Lepton Universality (ee vs μμ)")
print("-" * 50)
r_ee_mm = datasets[301209]['sigma'] / datasets[301204]['sigma']
print(f"  σ(Z'→μμ)/σ(Z'→ee) = {r_ee_mm:.6f}")
print(f"  Beklenen (lepton univ.) = 1.000000")
print(f"  Δ% = {abs(r_ee_mm-1)*100:.4f}%")
print(f"  N_m/N_b = {N_m/N_b:.8f}  Δ% = {abs(N_m/N_b-1)*100:.6f}%")

print("\n[3] W' Lepton Universality (eν vs μν)")
print("-" * 50)
r_enu_munu = datasets[301247]['sigma'] / datasets[301243]['sigma']
print(f"  σ(W'→μν)/σ(W'→eν) = {r_enu_munu:.6f}")
print(f"  Δ% from 1.0 = {abs(r_enu_munu-1)*100:.4f}%")

# ── nEvents oranları ─────────────────────────────────────────────────
print("\n[4] nEvents Oranları")
print("-" * 50)
n_vals = [d['n'] for d in datasets.values()]
n_arr  = np.array(n_vals)

for name, target in [
    ("N_b",   N_b),
    ("Cc_b",  Cc_b),
    ("T_Om",  T_Om),
    ("N_b/Cc_b", N_b/Cc_b),
]:
    pQ = np.percentile(n_arr, N_b * 100)
    pC = np.percentile(n_arr, Cc_b * 100)
    if pC > 0:
        ratio = pQ / pC
        delta = abs(ratio - T11_theory) / T11_theory * 100
        print(f"  nEvents pQ/pC = {pQ:.0f}/{pC:.0f} = {ratio:.4f}  "
              f"T11 Δ% = {delta:.4f}%")
    break

# ── Genlik verimliliği (genFiltEff) oranı ────────────────────────────
print("\n[5] Diphoton genFiltEff Analizi")
print("-" * 50)
effs = {
    302520: 0.42178,
    302521: 0.44191,
    302522: 0.42736,
}
print(f"  55-100 GeV: {effs[302520]}")
print(f"  100-160GeV: {effs[302521]}")
print(f"  160-250GeV: {effs[302522]}")
mean_eff = np.mean(list(effs.values()))
print(f"  Ortalama verimlilik: {mean_eff:.5f}")

for name, val in [
    ("Cc_b",  Cc_b),
    ("T_Om",  T_Om),
    ("N_b/2", N_b/2),
    ("sqrt(Cc_b)", np.sqrt(Cc_b)),
]:
    d = abs(mean_eff - val) / val * 100
    flag = "✓✓✓" if d<1 else "✓✓" if d<3 else "✓" if d<10 else "—"
    print(f"  Ort verimlilik vs {name:<15} = {val:.5f}  "
          f"Δ% = {d:.4f}%  {flag}")

# ── Ana sonuç ─────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("ÖZET")
print("=" * 65)
print(f"  σ(γγ 55-100) / σ(γγ 160-250) = {r_AC:.4f}")
print(f"  17 (1/a2 DOF)                 = 17.0000")
print(f"  Δ%                            = {abs(r_AC-17)/17*100:.4f}%")
print()
print(f"  YORUMLAMA:")
print(f"  Diphoton cross section skalası 3 kütle bandında")
print(f"  17× faktörü ile ölçekleniyor.")
print(f"  UST'de 17 = DOF = Cl(1,3) + ONL boundary normal")
print(f"  Bu tesadüf mü yoksa yapısal mı → araştırılmalı")
print()
print(f"  NOT: Bu MC simülasyon katalog verisi.")
print(f"  Gerçek veri ile doğrulama gerekli.")
print("✓ Tamamlandı.")
