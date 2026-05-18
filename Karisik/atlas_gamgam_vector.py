"""
ATLAS GamGam — Vektör değişkenler düzleştirme
jet_E, photon_E, photon_pt, lep_E üzerinde T11 testi
"""

import uproot
import numpy as np
import awkward as ak

N_b  = 0.63354460
Cc_b = 1 - N_b
N_m  = 0.63353522
Cc_m = 1 - N_m
T_Om = np.exp(-2 * np.pi * N_b * Cc_b)
T11_theory = (N_m / Cc_m) * (1 + N_b * N_m / (2 * np.pi))

print("=" * 65)
print("UST v5 — GamGam Vektör Değişken T11 Testi")
print(f"T11 teorik = {T11_theory:.6f}")
print("=" * 65)

path = r"C:\AtlasTest\data_A.GamGam.root"
f    = uproot.open(path)
tree = f["mini;1"]

# Düzleştirilecek değişkenler
vector_vars = [
    "jet_E", "jet_pt",
    "photon_E", "photon_pt",
    "lep_E", "lep_pt",
    "tau_E", "tau_pt",
    "largeRjet_E", "largeRjet_pt",
]

print(f"\n{'Değişken':<25} {'N':>10} {'pQ':>14} {'pC':>14} "
      f"{'Oran':>10} {'Δ%':>8}")
print("-" * 85)

results = {}
for var in vector_vars:
    try:
        raw  = tree[var].array(library="ak")
        flat = ak.to_numpy(ak.flatten(raw))
        flat = flat[np.isfinite(flat) & (flat > 0)]
        if len(flat) < 100:
            continue

        pQ    = np.percentile(flat, N_b * 100)
        pC    = np.percentile(flat, Cc_b * 100)
        ratio = pQ / pC
        delta = abs(ratio - T11_theory) / T11_theory * 100
        results[var] = {'pQ':pQ,'pC':pC,'ratio':ratio,
                        'delta':delta,'n':len(flat)}

        flag = "✓✓✓" if delta<1 else "✓✓" if delta<3 else \
               "✓" if delta<10 else "—"
        print(f"  {var:<23} {len(flat):>10,} {pQ:>14.2f} {pC:>14.2f} "
              f"{ratio:>10.6f} {delta:>7.3f}% {flag}")
    except Exception as e:
        print(f"  {var:<23} HATA: {e}")

print("\n" + "=" * 65)
print("EN İYİ SONUÇ")
print("=" * 65)
if results:
    best = min(results, key=lambda k: results[k]['delta'])
    r = results[best]
    print(f"  Değişken : {best}")
    print(f"  N        : {r['n']:,}")
    print(f"  pQ       : {r['pQ']:.4f}")
    print(f"  pC       : {r['pC']:.4f}")
    print(f"  Oran     : {r['ratio']:.6f}")
    print(f"  Teorik   : {T11_theory:.6f}")
    print(f"  Δ%       : {r['delta']:.4f}%")

# ── Nm ile de test et ─────────────────────────────────────────────────
print("\n" + "=" * 65)
print("Nb vs Nm KARŞILAŞTIRMASI — En iyi değişken")
print("=" * 65)
if results:
    best_var = min(results, key=lambda k: results[k]['delta'])
    raw  = tree[best_var].array(library="ak")
    flat = ak.to_numpy(ak.flatten(raw))
    flat = flat[flat > 0]

    pQ_nb = np.percentile(flat, N_b * 100)
    pC_nb = np.percentile(flat, Cc_b * 100)
    pQ_nm = np.percentile(flat, N_m * 100)
    pC_nm = np.percentile(flat, Cc_m * 100)

    r_nb = pQ_nb / pC_nb
    r_nm = pQ_nm / pC_nm

    d_nb = abs(r_nb - T11_theory) / T11_theory * 100
    d_nm = abs(r_nm - T11_theory) / T11_theory * 100

    print(f"  {best_var} üzerinde:")
    print(f"  Nb eşiği  : pQ={pQ_nb:.2f}  pC={pC_nb:.2f}  "
          f"oran={r_nb:.6f}  Δ%={d_nb:.4f}%")
    print(f"  Nm eşiği  : pQ={pQ_nm:.2f}  pC={pC_nm:.2f}  "
          f"oran={r_nm:.6f}  Δ%={d_nm:.4f}%")
    winner = "Nb" if d_nb < d_nm else "Nm"
    print(f"  Kazanan   : {winner}  (fark={abs(d_nb-d_nm):.6f}%)")
    print(f"  RA = {N_b-N_m:.4e}")
