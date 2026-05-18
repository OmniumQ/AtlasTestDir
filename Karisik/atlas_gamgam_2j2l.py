"""
ATLAS GamGam — 2J2L Topoloji Seçimi + T11 Testi
jet_n >= 2, lep_n >= 2, met_et > 30000 MeV filtresi
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
print("UST v5 — GamGam: 2J2L Topoloji Seçimi")
print(f"T11 teorik = {T11_theory:.6f}")
print("=" * 65)

path = r"C:\AtlasTest\data_A.GamGam.root"
f    = uproot.open(path)
tree = f["mini;1"]

# Tüm gerekli değişkenleri oku
jet_n   = tree["jet_n"].array(library="np")
lep_n   = tree["lep_n"].array(library="np")
met_et  = tree["met_et"].array(library="np")
jet_E   = tree["jet_E"].array(library="ak")
lep_E   = tree["lep_E"].array(library="ak")

print(f"\n  Toplam olay: {len(jet_n):,}")
print(f"\n  Olay topolojileri:")
print(f"  jet_n=0: {np.sum(jet_n==0):,}")
print(f"  jet_n=1: {np.sum(jet_n==1):,}")
print(f"  jet_n=2: {np.sum(jet_n==2):,}")
print(f"  jet_n>=2: {np.sum(jet_n>=2):,}")
print(f"  lep_n=0: {np.sum(lep_n==0):,}")
print(f"  lep_n=1: {np.sum(lep_n==1):,}")
print(f"  lep_n=2: {np.sum(lep_n==2):,}")
print(f"  met_et>30GeV: {np.sum(met_et>30000):,}")

# ── Farklı seçimler ───────────────────────────────────────────────────
selections = {
    "Tümü":             np.ones(len(jet_n), dtype=bool),
    "jet_n>=1":         jet_n >= 1,
    "jet_n>=2":         jet_n >= 2,
    "met_et>30GeV":     met_et > 30000,
    "jet_n>=2+MET>30":  (jet_n >= 2) & (met_et > 30000),
    "lep_n>=1":         lep_n >= 1,
    "lep_n>=2":         lep_n >= 2,
}

print(f"\n{'Seçim':<25} {'N':>10} {'jet_E oran':>12} {'Δ%':>8}")
print("-" * 60)

for sel_name, mask in selections.items():
    try:
        # jet_E bu maske ile
        jet_E_sel = ak.flatten(jet_E[mask])
        jet_E_arr = ak.to_numpy(jet_E_sel)
        jet_E_arr = jet_E_arr[jet_E_arr > 0]

        if len(jet_E_arr) < 50:
            print(f"  {sel_name:<23} {np.sum(mask):>10,}  yetersiz veri")
            continue

        pQ    = np.percentile(jet_E_arr, N_b * 100)
        pC    = np.percentile(jet_E_arr, Cc_b * 100)
        ratio = pQ / pC
        delta = abs(ratio - T11_theory) / T11_theory * 100
        flag  = "✓✓✓" if delta<1 else "✓✓" if delta<3 else \
                "✓" if delta<10 else "—"
        print(f"  {sel_name:<23} {np.sum(mask):>10,} "
              f"{ratio:>12.6f} {delta:>7.3f}% {flag}")
    except Exception as e:
        print(f"  {sel_name:<23} HATA: {e}")

# ── En iyi seçimde ONL testi ──────────────────────────────────────────
print("\n" + "=" * 65)
print("ONL ÜÇ BÖLGE — jet_E (tüm olaylar, düzleştirilmiş)")
print("=" * 65)

jet_E_all = ak.to_numpy(ak.flatten(jet_E))
jet_E_all = jet_E_all[jet_E_all > 0]

thr_tom = np.percentile(jet_E_all, T_Om * 100)
thr_nb  = np.percentile(jet_E_all, N_b * 100)
f_c  = np.sum(jet_E_all <= thr_tom) / len(jet_E_all)
f_om = np.sum((jet_E_all > thr_tom) & (jet_E_all <= thr_nb)) / len(jet_E_all)
f_q  = np.sum(jet_E_all > thr_nb) / len(jet_E_all)

print(f"  N = {len(jet_E_all):,}")
print(f"  Channel C  beklenen={T_Om:.6f}  ölçülen={f_c:.6f}  "
      f"Δ%={abs(f_c-T_Om)/T_Om*100:.4f}%")
print(f"  0-Element  beklenen={N_b-T_Om:.6f}  ölçülen={f_om:.6f}  "
      f"Δ%={abs(f_om-(N_b-T_Om))/(N_b-T_Om)*100:.4f}%")
print(f"  Channel Q  beklenen={Cc_b:.6f}  ölçülen={f_q:.6f}  "
      f"Δ%={abs(f_q-Cc_b)/Cc_b*100:.4f}%")

# ── Nb vs Nm jet_E üzerinde ───────────────────────────────────────────
print("\n" + "=" * 65)
print("Nb vs Nm — jet_E")
print("=" * 65)
pQ_nb = np.percentile(jet_E_all, N_b * 100)
pC_nb = np.percentile(jet_E_all, Cc_b * 100)
pQ_nm = np.percentile(jet_E_all, N_m * 100)
pC_nm = np.percentile(jet_E_all, Cc_m * 100)
r_nb  = pQ_nb / pC_nb
r_nm  = pQ_nm / pC_nm
d_nb  = abs(r_nb - T11_theory) / T11_theory * 100
d_nm  = abs(r_nm - T11_theory) / T11_theory * 100
print(f"  Nb: oran={r_nb:.6f}  Δ%={d_nb:.4f}%")
print(f"  Nm: oran={r_nm:.6f}  Δ%={d_nm:.4f}%")
print(f"  Kazanan: {'Nb' if d_nb<d_nm else 'Nm'}  "
      f"fark={abs(d_nb-d_nm):.6f}%")
print(f"  RA = {N_b-N_m:.4e}")
print("✓ Tamamlandı.")
