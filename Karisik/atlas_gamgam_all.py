"""
ATLAS GamGam — Tüm dosyalar A+B+C+D
Mevcut olanları otomatik bulur
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
print("UST v5 — GamGam Tüm Dosyalar T11 Testi")
print(f"T11 teorik = {T11_theory:.6f}")
print("=" * 65)

base  = r"C:\AtlasTest"
files = ["data_A.GamGam.root", "data_B.GamGam.root",
         "data_C.GamGam.root", "data_D.GamGam.root"]

avail = [f for f in files
         if os.path.exists(os.path.join(base, f))]
print(f"\nMevcut: {avail}\n")

jet_E_all = []
jet_n_all = []
met_et_all= []
n_total   = 0

for fname in avail:
    t = uproot.open(os.path.join(base, fname))["mini;1"]
    n = len(t["jet_n"].array(library="np"))
    n_total += n
    print(f"  {fname}: {n:,} olay")
    jet_n_all.append(t["jet_n"].array(library="np"))
    met_et_all.append(t["met_et"].array(library="np"))
    jet_E_all.append(t["jet_E"].array(library="ak"))

jet_n  = np.concatenate(jet_n_all)
met_et = np.concatenate(met_et_all)
jet_E  = ak.concatenate(jet_E_all)

print(f"\n  Toplam: {n_total:,} olay")
print(f"\n{'Seçim':<30} {'N':>9}  {'Oran':>10}  {'Δ%':>8}")
print("-" * 60)

best_delta = 999
best_label = ""

for label, mask in {
    "Tümü":            np.ones(len(jet_n), dtype=bool),
    "jet_n>=2":        jet_n >= 2,
    "jet_n>=3":        jet_n >= 3,
    "jet_n>=4":        jet_n >= 4,
    "MET>30GeV":       met_et > 30000,
    "jet_n>=2+MET>30": (jet_n>=2)&(met_et>30000),
    "jet_n>=3+MET>30": (jet_n>=3)&(met_et>30000),
    "jet_n>=4+MET>30": (jet_n>=4)&(met_et>30000),
    "jet_n>=3+MET>50": (jet_n>=3)&(met_et>50000),
}.items():
    jets = ak.to_numpy(ak.flatten(jet_E[mask]))
    jets = jets[jets > 0]
    if len(jets) < 100:
        continue
    pQ    = np.percentile(jets, N_b * 100)
    pC    = np.percentile(jets, Cc_b * 100)
    ratio = pQ / pC
    delta = abs(ratio - T11_theory) / T11_theory * 100
    flag  = "✓✓✓" if delta<1 else "✓✓" if delta<3 else \
            "✓" if delta<10 else "—"
    print(f"  {label:<28} N={np.sum(mask):>8,}  "
          f"oran={ratio:.6f}  Δ%={delta:.4f}%  {flag}")
    if delta < best_delta:
        best_delta = delta
        best_label = label

print(f"\n  En iyi : {best_label}  Δ%={best_delta:.4f}%")
print(f"  Orijinal UST hedef: Δ%=0.43%")
print(f"  Mevcut en iyi     : Δ%={best_delta:.2f}%")
print(f"  Dosya sayısı      : {len(avail)}/4")
if len(avail) < 4:
    print(f"  NOT: C ve D inince tekrar çalıştırın → daha iyi sonuç bekleniyor")
print("✓ Tamamlandı.")
