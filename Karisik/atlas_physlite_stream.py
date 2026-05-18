"""
ATLAS DAOD_PHYSLITE — HTTPS Stream Erişimi
İndirme gerektirmez, xrootd gerektirmez
Sadece: pip install uproot awkward fsspec aiohttp zstandard

DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI (CC0)
Bilimsel yayına uygun veri
"""

import numpy as np

# ── UST sabitleri ─────────────────────────────────────────────────────
N_b  = 0.63354460
Cc_b = 1 - N_b
N_m  = 0.63353522
Cc_m = 1 - N_m
T_Om = np.exp(-2 * np.pi * N_b * Cc_b)
T11  = (N_m / Cc_m) * (1 + N_b * N_m / (2 * np.pi))

print("=" * 65)
print("ATLAS PHYSLITE — HTTPS Stream + UST T11 Testi")
print(f"T11 teorik = {T11:.6f}")
print(f"DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI (CC0)")
print("=" * 65)

# ── Paket kontrolü ────────────────────────────────────────────────────
import subprocess, sys

def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           pkg, "-q"])

for pkg in ["uproot", "awkward", "fsspec", "aiohttp", "zstandard"]:
    try:
        __import__(pkg.replace("-","_"))
    except ImportError:
        print(f"Kuruluyor: {pkg}")
        install(pkg)

import uproot
import awkward as ak

# ── HTTPS ile doğrudan CERN EOS erişimi ──────────────────────────────
# Bu URL'ler indirme gerektirmez — stream okuma yapar
# 2016 data, Run 310781 (en küçük run)

urls_2016 = [
    "simplecache::https://opendata.cern.ch/eos/opendata/atlas/rucio/"
    "data16_13TeV/00310781/DAOD_PHYSLITE.29004645._000001.pool.root.1",
    "simplecache::https://opendata.cern.ch/eos/opendata/atlas/rucio/"
    "data16_13TeV/00310781/DAOD_PHYSLITE.29004645._000002.pool.root.1",
]

# MC ttbar (bilinen T11 uyumu için referans)
urls_mc = [
    "simplecache::https://opendata.cern.ch/eos/opendata/atlas/rucio/"
    "mc20_13TeV/DAOD_PHYSLITE.37620644._000012.pool.root.1",
]

def test_url(url, label, n_max=100000):
    """Tek dosyadan jet_pt okuyup T11 ve ONL testi yap"""
    print(f"\n  [{label}]")
    print(f"  URL: ...{url[-60:]}")

    try:
        f = uproot.open(url, timeout=60)
        tree = f["CollectionTree"]

        # Mevcut branch'leri tara
        branches = tree.keys()
        jet_branches = [b for b in branches
                        if "jet" in b.lower() and
                        ("pt" in b.lower() or "_pt" in b.lower())]
        met_branches = [b for b in branches
                        if "met" in b.lower() or "MET" in b]

        print(f"  Toplam branch: {len(branches)}")
        print(f"  Jet PT branch'leri: {jet_branches[:5]}")
        print(f"  MET branch'leri: {met_branches[:5]}")

        # Jet PT oku
        jet_pt_branch = None
        for b in ["AntiKt4EMPFlowJetsAuxDyn.pt",
                  "AntiKt4EMTopoJetsAuxDyn.pt",
                  "HLT_xAOD__JetContainer_a4tcemsubjesFS.pt"]:
            if b in branches:
                jet_pt_branch = b
                break

        if jet_pt_branch is None:
            # Tüm branch listesini göster
            print(f"  Branch listesi (ilk 50):")
            for b in list(branches)[:50]:
                print(f"    {b}")
            return None

        print(f"  Jet PT branch: {jet_pt_branch}")

        # Veriyi oku
        data = tree[jet_pt_branch].array(library="ak",
                                          entry_stop=n_max)
        flat = ak.to_numpy(ak.flatten(data))
        flat = flat[flat > 0]

        print(f"  Jet PT N={len(flat):,}")
        print(f"  PT ort={flat.mean():.1f} MeV  max={flat.max():.1f} MeV")

        # T11 testi
        pQ = np.percentile(flat, N_b * 100)
        pC = np.percentile(flat, Cc_b * 100)
        ratio = pQ / pC
        delta = abs(ratio - T11) / T11 * 100
        flag  = "✓✓✓" if delta<1 else "✓✓" if delta<3 else "✓" if delta<10 else "—"

        print(f"\n  T11 testi (jet_pt):")
        print(f"  pQ={pQ:.2f}  pC={pC:.2f}  oran={ratio:.6f}")
        print(f"  T11 teorik={T11:.6f}  Δ%={delta:.4f}%  {flag}")

        # ONL üç bölge
        thr_tom = np.percentile(flat, T_Om * 100)
        thr_nb  = np.percentile(flat, N_b  * 100)
        f_c  = np.sum(flat <= thr_tom) / len(flat)
        f_om = np.sum((flat > thr_tom) & (flat <= thr_nb)) / len(flat)
        f_q  = np.sum(flat > thr_nb) / len(flat)

        print(f"\n  ONL üç bölge (jet_pt):")
        print(f"  Channel C  {T_Om:.6f} → {f_c:.6f}  "
              f"Δ%={abs(f_c-T_Om)/T_Om*100:.4f}%")
        print(f"  0-Element  {N_b-T_Om:.6f} → {f_om:.6f}  "
              f"Δ%={abs(f_om-(N_b-T_Om))/(N_b-T_Om)*100:.4f}%")
        print(f"  Channel Q  {Cc_b:.6f} → {f_q:.6f}  "
              f"Δ%={abs(f_q-Cc_b)/Cc_b*100:.4f}%")

        return {'ratio': ratio, 'delta': delta, 'n': len(flat)}

    except Exception as e:
        print(f"  HATA: {e}")
        return None

# ── Test çalıştır ─────────────────────────────────────────────────────
print("\n[1] MC ttbar referans dosyası")
for url in urls_mc:
    result = test_url(url, "MC ttbar", n_max=50000)
    if result:
        break

print("\n[2] 2016 gerçek veri")
for url in urls_2016:
    result = test_url(url, "data16 Run310781", n_max=50000)
    if result:
        break

print("\n" + "=" * 65)
print("Makale referansı:")
print("ATLAS Collaboration (2024).")
print("DAOD_PHYSLITE format 2015-2016 Open Data for Research.")
print("CERN Open Data Portal.")
print("DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI")
print("=" * 65)
