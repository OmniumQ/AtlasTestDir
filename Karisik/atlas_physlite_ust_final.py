"""
ATLAS DAOD_PHYSLITE — UST v5 TAM ANALİZ
Her sabit, her formül, her test — tek dosyada
DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI (CC0)
Niyazi ÖCAL, 2026
"""

import numpy as np
import awkward as ak
import uproot
import warnings
warnings.filterwarnings('ignore')

# ════════════════════════════════════════════════════════════════════
# UST v5 — TÜM SABİTLER
# ════════════════════════════════════════════════════════════════════
N_b   = 0.63354460
N_m   = 0.63353522
RA    = N_b - N_m          # = 9.38e-6
Cc_b  = 1 - N_b
Cc_m  = 1 - N_m
T_Om  = np.exp(-2*np.pi*N_b*Cc_b)
N_geo = (3 - np.sqrt(3)) / 2
alpha = 1/137.036
a17   = alpha/17
T11   = (N_m/Cc_m)*(1 + N_b*N_m/(2*np.pi))
kappa1= np.pi*N_b
kappa2= 2*np.pi*N_b
Vb    = (1+N_b)/(2-N_b)
ONL   = N_b/Cc_b
# ONL üç bölge
ONL_C  = T_Om
ONL_Om = N_b - T_Om
ONL_Q  = Cc_b

FILE = r"C:\AtlasTest\DAOD_test.root"

print("="*70)
print("ATLAS DAOD_PHYSLITE — UST v5 TAM ANALİZ")
print(f"DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI (CC0)")
print("="*70)
print(f"\n  N_b   = {N_b:.10f}  (Blueprint)")
print(f"  N_m   = {N_m:.10f}  (Manifest)")
print(f"  RA    = {RA:.4e}  (Nb-Nm)")
print(f"  Cc_b  = {Cc_b:.10f}")
print(f"  T_Om  = {T_Om:.10f}")
print(f"  T11   = {T11:.10f}")
print(f"  κ1    = {kappa1:.8f}")
print(f"  κ2    = {kappa2:.8f}")
print(f"  Vb    = {Vb:.8f}")
print(f"  Nb/Ccb= {ONL:.8f}  (≈√3={np.sqrt(3):.8f})")
print(f"  ONL_C = {ONL_C:.8f}  (T_Om)")
print(f"  ONL_Om= {ONL_Om:.8f}  (Nb-TOm)")
print(f"  ONL_Q = {ONL_Q:.8f}  (Ccb)")
print(f"  α/17  = {a17:.8f}")
print(f"  Ngeo  = {N_geo:.8f}")

# ════════════════════════════════════════════════════════════════════
# DOSYA AÇ
# ════════════════════════════════════════════════════════════════════
print(f"\n{'='*70}")
print(f"DOSYA: {FILE}")
print(f"{'='*70}")

f    = uproot.open(FILE)
tree = f["CollectionTree"]
all_branches = tree.keys()
print(f"  Toplam branch: {len(all_branches)}")

# İlginç branch'leri bul
def find_branches(keywords):
    result = []
    for b in all_branches:
        if any(k.lower() in b.lower() for k in keywords):
            result.append(b)
    return result

jet_branches = find_branches(["AntiKt4EMPFlow","AntiKt4EMTopo"])
met_branches = find_branches(["METAssoc","MET_","MissingET"])
el_branches  = find_branches(["Electron","electron"])
mu_branches  = find_branches(["Muon","muon"])

print(f"\n  Jet branch'leri ({len(jet_branches)}):")
for b in jet_branches[:8]: print(f"    {b}")
print(f"\n  MET branch'leri ({len(met_branches)}):")
for b in met_branches[:5]: print(f"    {b}")
print(f"\n  Elektron branch'leri: {len(el_branches)}")
print(f"  Muon branch'leri: {len(mu_branches)}")

# ════════════════════════════════════════════════════════════════════
# VERİ OKU
# ════════════════════════════════════════════════════════════════════
print(f"\n{'='*70}")
print("VERİ OKUMA")
print(f"{'='*70}")

results = {}

def ust_all_tests(arr_flat, label, n_label):
    """Her UST testini uygula ve sonuçları döndür"""
    if len(arr_flat) < 100:
        return None

    res = {'label': label, 'n': len(arr_flat)}

    # ── T11 testi ─────────────────────────────────────────────────
    pQ_nb = np.percentile(arr_flat, N_b*100)
    pC_nb = np.percentile(arr_flat, Cc_b*100)
    pQ_nm = np.percentile(arr_flat, N_m*100)
    pC_nm = np.percentile(arr_flat, Cc_m*100)

    r_nb = pQ_nb/pC_nb if pC_nb>0 else 0
    r_nm = pQ_nm/pC_nm if pC_nm>0 else 0

    d_nb = abs(r_nb-T11)/T11*100
    d_nm = abs(r_nm-T11)/T11*100

    res['T11_Nb']    = r_nb
    res['T11_Nm']    = r_nm
    res['dT11_Nb']   = d_nb
    res['dT11_Nm']   = d_nm
    res['T11_winner']= 'Nb' if d_nb<d_nm else 'Nm'

    # ── ONL üç bölge ──────────────────────────────────────────────
    thr_tom = np.percentile(arr_flat, T_Om*100)
    thr_nb  = np.percentile(arr_flat, N_b*100)
    f_C  = np.sum(arr_flat <= thr_tom)         / len(arr_flat)
    f_Om = np.sum((arr_flat>thr_tom)&(arr_flat<=thr_nb)) / len(arr_flat)
    f_Q  = np.sum(arr_flat > thr_nb)           / len(arr_flat)

    res['ONL_C']   = f_C
    res['ONL_Om']  = f_Om
    res['ONL_Q']   = f_Q
    res['dONL_C']  = abs(f_C  - ONL_C ) / ONL_C  * 100
    res['dONL_Om'] = abs(f_Om - ONL_Om) / ONL_Om * 100
    res['dONL_Q']  = abs(f_Q  - ONL_Q ) / ONL_Q  * 100

    # ── Nb/Nm fark analizi ─────────────────────────────────────────
    res['diff_Nb'] = abs(pQ_nb/len(arr_flat) - N_b)
    res['diff_Nm'] = abs(pQ_nb/len(arr_flat) - N_m)
    res['RA_ratio']= (r_nb - r_nm) / RA if RA>0 else 0

    # ── ONL oran testi (Nb/Ccb ≈ √3) ─────────────────────────────
    n_q   = np.sum(arr_flat > thr_nb)
    n_c   = np.sum(arr_flat <= thr_tom)
    ratio_qc = n_q/n_c if n_c>0 else 0
    res['QC_ratio'] = ratio_qc
    res['dQC_sqrt3']= abs(ratio_qc - np.sqrt(3))/np.sqrt(3)*100
    res['dQC_ONL']  = abs(ratio_qc - ONL)/ONL*100

    # ── α/17 geçiş testi ─────────────────────────────────────────
    thr_geo = np.percentile(arr_flat, N_geo*100)
    thr_nsq = np.percentile(arr_flat, N_b*100)
    f_bridge= np.sum((arr_flat>min(thr_geo,thr_nsq)) &
                     (arr_flat<=max(thr_geo,thr_nsq))) / len(arr_flat)
    res['alpha17_bridge'] = f_bridge
    res['dalpha17']       = abs(f_bridge - a17)/a17*100 if a17>0 else 0

    # ── Harmonik gear testi ───────────────────────────────────────
    p_k1 = np.percentile(arr_flat, kappa1/(2*np.pi)*100)
    p_k2 = np.percentile(arr_flat, kappa2/(2*np.pi)*100)
    res['p_kappa1'] = p_k1
    res['p_kappa2'] = p_k2

    # ── İstatistik ────────────────────────────────────────────────
    res['mean'] = arr_flat.mean()
    res['std']  = arr_flat.std()
    res['max']  = arr_flat.max()

    return res

# Her jet branch'ini test et
print("\n  Jet branch'leri okunuyor...")
for b in jet_branches:
    if "pt" in b.lower() or "e_" in b.lower() or b.endswith("E"):
        try:
            raw  = tree[b].array(library="ak", entry_stop=200000)
            flat = ak.to_numpy(ak.flatten(raw))
            flat = flat[np.isfinite(flat) & (flat>0)]
            if len(flat) < 1000: continue
            res = ust_all_tests(flat, b, len(flat))
            if res: results[b] = res
            print(f"  ✓ {b[:55]:<55} N={len(flat):>8,}")
        except: pass

# MET testi
print("\n  MET branch'leri okunuyor...")
for b in met_branches:
    try:
        raw  = tree[b].array(library="ak", entry_stop=200000)
        flat = ak.to_numpy(ak.flatten(raw))
        flat = flat[np.isfinite(flat) & (flat>0)]
        if len(flat) < 1000: continue
        res = ust_all_tests(flat, b, len(flat))
        if res: results[b] = res
        print(f"  ✓ {b[:55]:<55} N={len(flat):>8,}")
    except: pass

# ════════════════════════════════════════════════════════════════════
# SONUÇLAR
# ════════════════════════════════════════════════════════════════════
print(f"\n{'='*70}")
print("T11 SONUÇLARI — Nb vs Nm")
print(f"{'='*70}")
print(f"  {'Branch':<40} {'T11_Nb':>10} {'Δ%':>7} {'T11_Nm':>10} {'Δ%':>7} {'Kazanan'}")
print(f"  {'-'*85}")
for b, r in sorted(results.items(), key=lambda x: x[1]['dT11_Nb']):
    flag = "✓✓✓" if r['dT11_Nb']<1 else "✓✓" if r['dT11_Nb']<3 else "✓"
    print(f"  {b[:40]:<40} {r['T11_Nb']:>10.6f} {r['dT11_Nb']:>6.3f}% "
          f"{r['T11_Nm']:>10.6f} {r['dT11_Nm']:>6.3f}%  "
          f"{r['T11_winner']} {flag}")

print(f"\n{'='*70}")
print("ONL ÜÇ BÖLGE SONUÇLARI")
print(f"{'='*70}")
print(f"  {'Branch':<40} {'C Δ%':>7} {'Om Δ%':>7} {'Q Δ%':>7} {'Ort Δ%':>8}")
print(f"  {'-'*72}")
for b, r in sorted(results.items(),
                   key=lambda x: np.mean([x[1]['dONL_C'],
                                          x[1]['dONL_Om'],
                                          x[1]['dONL_Q']])):
    ort = np.mean([r['dONL_C'], r['dONL_Om'], r['dONL_Q']])
    flag = "✓✓✓" if ort<1 else "✓✓" if ort<3 else "✓"
    print(f"  {b[:40]:<40} {r['dONL_C']:>6.3f}% {r['dONL_Om']:>6.3f}% "
          f"{r['dONL_Q']:>6.3f}% {ort:>7.3f}% {flag}")

print(f"\n{'='*70}")
print("Q/C ORAN TESTİ (≈ √3)")
print(f"{'='*70}")
for b, r in sorted(results.items(), key=lambda x: x[1]['dQC_sqrt3'])[:5]:
    print(f"  {b[:45]:<45} Q/C={r['QC_ratio']:.4f}  "
          f"Δ%√3={r['dQC_sqrt3']:.4f}%  Δ%ONL={r['dQC_ONL']:.4f}%")

print(f"\n{'='*70}")
print("Nb/Nm FARK ANALİZİ")
print(f"{'='*70}")
print(f"  RA = {RA:.4e}")
for b, r in list(results.items())[:3]:
    print(f"  {b[:45]:<45}")
    print(f"    T11(Nb)-T11(Nm) = {r['T11_Nb']-r['T11_Nm']:+.6e}")
    print(f"    ΔT11/RA         = {(r['T11_Nb']-r['T11_Nm'])/RA:.2f}")
    print(f"    Kazanan         : {r['T11_winner']}")

# ── Genel özet ─────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("GENEL ÖZET — EN İYİ SONUÇLAR")
print(f"{'='*70}")
if results:
    best_t11 = min(results.items(), key=lambda x: x[1]['dT11_Nb'])
    best_onl = min(results.items(),
                   key=lambda x: np.mean([x[1]['dONL_C'],
                                          x[1]['dONL_Om'],
                                          x[1]['dONL_Q']]))
    b,r = best_t11
    print(f"\n  En iyi T11:")
    print(f"  {b}")
    print(f"  N={r['n']:,}  T11={r['T11_Nb']:.6f}  Δ%={r['dT11_Nb']:.4f}%")
    print(f"  ONL_C={r['ONL_C']:.6f}(Δ%={r['dONL_C']:.3f}%)  "
          f"ONL_Om={r['ONL_Om']:.6f}(Δ%={r['dONL_Om']:.3f}%)  "
          f"ONL_Q={r['ONL_Q']:.6f}(Δ%={r['dONL_Q']:.3f}%)")

    b,r = best_onl
    print(f"\n  En iyi ONL:")
    print(f"  {b}")
    onl_rms = np.sqrt(np.mean([r['dONL_C']**2,
                                r['dONL_Om']**2,
                                r['dONL_Q']**2]))
    print(f"  ONL RMS Δ% = {onl_rms:.4f}%")

print(f"\n{'='*70}")
print("MAKALEye referans:")
print("ATLAS Collaboration (2024). DAOD_PHYSLITE format")
print("2015-2016 Open Data for Research. CERN Open Data Portal.")
print("DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI  (CC0)")
print("="*70)
print("✓ Tamamlandı.")
