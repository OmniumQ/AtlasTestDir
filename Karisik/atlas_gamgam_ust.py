"""
CERN ATLAS Open Data — GamGam (diphoton) kanalı
UST v5 T11 Testi — Doğru değişkenlerle
"""

import uproot
import numpy as np

# ── UST sabitleri ─────────────────────────────────────────────────────
N_b  = 0.63354460
N_m  = 0.63353522
Cc_b = 1 - N_b
Cc_m = 1 - N_m
T_Om = np.exp(-2 * np.pi * N_b * Cc_b)
T11_theory = (N_m / Cc_m) * (1 + N_b * N_m / (2 * np.pi))

print("=" * 65)
print("UST v5 — CERN ATLAS GamGam T11 Testi")
print(f"T11 teorik = {T11_theory:.6f}")
print("=" * 65)

# ── Dosya ─────────────────────────────────────────────────────────────
path = r"C:\AtlasTest\data_A.GamGam.root"
f    = uproot.open(path)
tree = f["mini;1"]

# Mevcut değişkenleri göster
print("\nMevcut değişkenler:")
keys = tree.keys()
for k in sorted(keys):
    print(f"  {k}")

# ── Test her değişken üzerinde ────────────────────────────────────────
print("\n" + "=" * 65)
print("TÜM DEĞİŞKENLER ÜZERİNDE T11 TESTİ")
print("=" * 65)
print(f"{'Değişken':<35} {'pQ':>12} {'pC':>12} {'Oran':>10} {'Δ%':>8}")
print("-" * 80)

results = {}
for key in sorted(keys):
    try:
        data = tree[key].array(library="np")
        # Sadece sayısal ve pozitif değerler
        data = data[np.isfinite(data)]
        if len(data) < 100:
            continue
        if data.dtype.kind not in ['f', 'i', 'u']:
            continue

        # Sadece pozitif değerlerle (enerji/momentum)
        data_pos = data[data > 0]
        if len(data_pos) < 100:
            continue

        pQ = np.percentile(data_pos, N_b * 100)
        pC = np.percentile(data_pos, Cc_b * 100)

        if pC < 1e-6:
            continue

        ratio = pQ / pC
        delta = abs(ratio - T11_theory) / T11_theory * 100
        results[key] = {'pQ': pQ, 'pC': pC, 'ratio': ratio,
                        'delta': delta, 'n': len(data_pos)}

        flag = "✓✓✓" if delta < 1 else "✓✓" if delta < 3 else \
               "✓" if delta < 10 else "—"
        print(f"  {key:<33} {pQ:>12.2f} {pC:>12.2f} "
              f"{ratio:>10.6f} {delta:>7.3f}% {flag}")

    except Exception:
        continue

# En iyi sonuçlar
print("\n" + "=" * 65)
print("EN İYİ SONUÇLAR (Δ% sıralı)")
print("=" * 65)
for key, r in sorted(results.items(), key=lambda x: x[1]['delta'])[:10]:
    flag = "✓✓✓" if r['delta']<1 else "✓✓" if r['delta']<3 else "✓" if r['delta']<10 else "—"
    print(f"  {key:<35} oran={r['ratio']:.6f}  "
          f"Δ%={r['delta']:.4f}%  n={r['n']}  {flag}")

# ── ONL üç bölge testi (met_et üzerinde) ─────────────────────────────
print("\n" + "=" * 65)
print("ONL ÜÇ BÖLGE TESTİ — met_et")
print("=" * 65)
met = tree["met_et"].array(library="np")
met = met[met > 0]

thr_tom = np.percentile(met, T_Om * 100)
thr_nb  = np.percentile(met, N_b  * 100)

f_c  = np.sum(met <= thr_tom) / len(met)
f_om = np.sum((met > thr_tom) & (met <= thr_nb)) / len(met)
f_q  = np.sum(met > thr_nb) / len(met)

print(f"  N toplam: {len(met)}")
print(f"  Channel C  beklenen={T_Om:.6f}  ölçülen={f_c:.6f}  "
      f"Δ%={abs(f_c-T_Om)/T_Om*100:.4f}%")
print(f"  0-Element  beklenen={N_b-T_Om:.6f}  ölçülen={f_om:.6f}  "
      f"Δ%={abs(f_om-(N_b-T_Om))/(N_b-T_Om)*100:.4f}%")
print(f"  Channel Q  beklenen={Cc_b:.6f}  ölçülen={f_q:.6f}  "
      f"Δ%={abs(f_q-Cc_b)/Cc_b*100:.4f}%")
print(f"  Toplam: {f_c+f_om+f_q:.6f}")
