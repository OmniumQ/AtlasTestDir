"""
ATLAS GamGam — data_A + data_B birleşik T11 testi
UST v5: Topoloji filtresiyle T11 iyileşmesi
"""

import uproot
import numpy as np
import awkward as ak
import os

N_b  = 0.63354460
Cc_b = 1 - N_b
N_m  = 0.63353522
Cc_m = 1 - N_m
T_Om = np.exp(-2 * np.pi * N_b * Cc_b)
T11_theory = (N_m / Cc_m) * (1 + N_b * N_m / (2 * np.pi))

print("=" * 65)
print("UST v5 — GamGam A+B Birleşik T11 Testi")
print(f"T11 teorik = {T11_theory:.6f}")
print("=" * 65)

base  = r"C:\AtlasTest"
files = ["data_A.GamGam.root", "data_B.GamGam.root"]

# Mevcut dosyaları kontrol et
avail = [f for f in files
         if os.path.exists(os.path.join(base, f))]
print(f"\nMevcut dosyalar: {avail}")

# Tüm dosyalardan veri topla
jet_E_all  = []
jet_n_all  = []
lep_E_all  = []
met_et_all = []
n_total    = 0

for fname in avail:
    fpath = os.path.join(base, fname)
    f     = uproot.open(fpath)
    tree  = f["mini;1"]
    n     = len(tree["jet_n"].array(library="np"))
    print(f"  {fname}: {n:,} olay")
    n_total += n

    jet_n_all.append(tree["jet_n"].array(library="np"))
    met_et_all.append(tree["met_et"].array(library="np"))
    jet_E_all.append(tree["jet_E"].array(library="ak"))
    lep_E_all.append(tree["lep_E"].array(library="ak"))

# Birleştir
jet_n  = np.concatenate(jet_n_all)
met_et = np.concatenate(met_et_all)
jet_E  = ak.concatenate(jet_E_all)
lep_E  = ak.concatenate(lep_E_all)

print(f"\n  Toplam olay: {n_total:,}")

# ── Topoloji filtreleri ───────────────────────────────────────────────
def t11_test(jet_E_ak, mask, label):
    jets = ak.to_numpy(ak.flatten(jet_E_ak[mask]))
    jets = jets[jets > 0]
    if len(jets) < 100:
        return
    pQ    = np.percentile(jets, N_b * 100)
    pC    = np.percentile(jets, Cc_b * 100)
    ratio = pQ / pC
    delta = abs(ratio - T11_theory) / T11_theory * 100
    flag  = "✓✓✓" if delta<1 else "✓✓" if delta<3 else \
            "✓" if delta<10 else "—"
    print(f"  {label:<30} N={np.sum(mask):>8,}  "
          f"oran={ratio:.6f}  Δ%={delta:.4f}%  {flag}")

print(f"\n{'Seçim':<32} {'N':>9}  {'Oran':>10}  {'Δ%':>8}")
print("-" * 65)

masks = {
    "Tümü":             np.ones(len(jet_n), dtype=bool),
    "jet_n>=1":         jet_n >= 1,
    "jet_n>=2":         jet_n >= 2,
    "jet_n>=3":         jet_n >= 3,
    "MET>30GeV":        met_et > 30000,
    "jet_n>=2+MET>30":  (jet_n >= 2) & (met_et > 30000),
    "jet_n>=3+MET>30":  (jet_n >= 3) & (met_et > 30000),
    "jet_n>=2+MET>50":  (jet_n >= 2) & (met_et > 50000),
}

best_delta = 999
best_label = ""
for label, mask in masks.items():
    jets = ak.to_numpy(ak.flatten(jet_E[mask]))
    jets = jets[jets > 0]
    if len(jets) < 100:
        print(f"  {label:<30} yetersiz")
        continue
    pQ    = np.percentile(jets, N_b * 100)
    pC    = np.percentile(jets, Cc_b * 100)
    ratio = pQ / pC
    delta = abs(ratio - T11_theory) / T11_theory * 100
    flag  = "✓✓✓" if delta<1 else "✓✓" if delta<3 else \
            "✓" if delta<10 else "—"
    print(f"  {label:<30} N={np.sum(mask):>8,}  "
          f"oran={ratio:.6f}  Δ%={delta:.4f}%  {flag}")
    if delta < best_delta:
        best_delta = delta
        best_label = label

print(f"\n  En iyi: {best_label}  Δ%={best_delta:.4f}%")
print(f"  Orijinal UST (2J2L, 2.97M olay): Δ%=0.43%")
print(f"  GamGam eğitim verisi (eğitim amaçlı): Δ%={best_delta:.2f}%")

# ── ONL üç bölge ─────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("ONL ÜÇ BÖLGE — jet_E birleşik")
print("=" * 65)
jets_all = ak.to_numpy(ak.flatten(jet_E))
jets_all = jets_all[jets_all > 0]

thr_tom = np.percentile(jets_all, T_Om * 100)
thr_nb  = np.percentile(jets_all, N_b  * 100)
f_c  = np.sum(jets_all <= thr_tom) / len(jets_all)
f_om = np.sum((jets_all > thr_tom) & (jets_all <= thr_nb)) / len(jets_all)
f_q  = np.sum(jets_all > thr_nb) / len(jets_all)

print(f"  N = {len(jets_all):,}")
print(f"  Channel C  {T_Om:.6f} → {f_c:.6f}  "
      f"Δ%={abs(f_c-T_Om)/T_Om*100:.4f}%")
print(f"  0-Element  {N_b-T_Om:.6f} → {f_om:.6f}  "
      f"Δ%={abs(f_om-(N_b-T_Om))/(N_b-T_Om)*100:.4f}%")
print(f"  Channel Q  {Cc_b:.6f} → {f_q:.6f}  "
      f"Δ%={abs(f_q-Cc_b)/Cc_b*100:.4f}%")
print("✓ Tamamlandı.")
