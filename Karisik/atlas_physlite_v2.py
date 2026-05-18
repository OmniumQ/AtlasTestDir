"""
ATLAS DAOD_PHYSLITE — Doğru Erişim Yöntemi
cernopendata-client ile dosya URL'leri + uproot stream

Kurulum:
pip install cernopendata-client uproot==5.1.2 awkward==2.5.0 zstandard

DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI (CC0)
"""

import numpy as np
import subprocess, sys, os

# ── UST sabitleri ─────────────────────────────────────────────────────
N_b  = 0.63354460
Cc_b = 1 - N_b
N_m  = 0.63353522
Cc_m = 1 - N_m
T_Om = np.exp(-2 * np.pi * N_b * Cc_b)
T11  = (N_m / Cc_m) * (1 + N_b * N_m / (2 * np.pi))

print("=" * 65)
print("ATLAS PHYSLITE — Doğru Erişim + UST T11 Testi")
print(f"T11 teorik = {T11:.6f}")
print("=" * 65)

# ── Paket kur ─────────────────────────────────────────────────────────
for pkg in ["cernopendata_client", "uproot", "awkward", "zstandard"]:
    try:
        __import__(pkg.replace("-","_"))
        print(f"✓ {pkg}")
    except ImportError:
        print(f"Kuruluyor: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                               pkg.replace("_","-"), "-q"])

import uproot
import awkward as ak

# ── Yöntem A: cernopendata-client ile URL bul ─────────────────────────
print("\n[A] cernopendata-client ile dosya URL'leri")
print("-" * 50)

try:
    import cernopendata_client as cod

    # 2016 data record ID = 80001
    # Birkaç dosya URL'i al
    print("  Record 80001 dosya listesi alınıyor...")
    files = cod.get_file_locations(recid=80001,
                                   protocol="http",
                                   limit=5)
    print(f"  Bulunan dosyalar:")
    for f in files[:5]:
        print(f"    {f}")

    # İlk dosyayı aç
    if files:
        test_url = files[0]
        print(f"\n  Açılıyor: {test_url[:80]}...")

        f_root = uproot.open(test_url, timeout=60)
        print(f"  Anahtarlar: {list(f_root.keys())[:5]}")

        tree = f_root["CollectionTree"]
        branches = tree.keys()
        print(f"  Branch sayısı: {len(branches)}")
        print(f"  İlk 20 branch:")
        for b in list(branches)[:20]:
            print(f"    {b}")

except Exception as e:
    print(f"  cernopendata-client hatası: {e}")

# ── Yöntem B: Bilinen HTTP URL formatı ───────────────────────────────
print("\n[B] Bilinen HTTP URL ile doğrudan erişim")
print("-" * 50)

# Resmi tutorial'dan alınan URL formatı:
# http://opendata.cern.ch/eos/opendata/atlas/rucio/...
known_urls = [
    # MC ttbar (tutorial'dan alındı)
    "http://opendata.cern.ch/eos/opendata/atlas/rucio/"
    "mc20_13TeV/DAOD_PHYSLITE.37620644._000012.pool.root.1",

    # 2016 data (Run 310781 - en küçük run)
    "http://opendata.cern.ch/eos/opendata/atlas/rucio/"
    "data16_13TeV/DAOD_PHYSLITE.29004645._000001.pool.root.1",
]

for url in known_urls:
    label = "MC" if "mc20" in url else "data16"
    print(f"\n  [{label}] {url[-60:]}")
    try:
        f = uproot.open(url, timeout=60)
        tree = f["CollectionTree"]
        branches = tree.keys()
        print(f"  ✓ Bağlantı başarılı! Branch: {len(branches)}")

        # Jet branch'leri bul
        jet_pt = None
        for b in branches:
            if ("Jet" in b or "jet" in b) and "pt" in b.lower():
                jet_pt = b
                break

        if jet_pt:
            print(f"  Jet PT branch: {jet_pt}")
            data = tree[jet_pt].array(library="ak", entry_stop=10000)
            flat = ak.to_numpy(ak.flatten(data))
            flat = flat[flat > 0]

            pQ    = np.percentile(flat, N_b * 100)
            pC    = np.percentile(flat, Cc_b * 100)
            ratio = pQ / pC
            delta = abs(ratio - T11) / T11 * 100
            flag  = "✓✓✓" if delta<1 else "✓✓" if delta<3 else "✓"

            print(f"  N={len(flat):,}  T11={ratio:.6f}  Δ%={delta:.4f}% {flag}")

    except Exception as e:
        print(f"  HATA: {type(e).__name__}: {str(e)[:100]}")

# ── Yöntem C: Küçük test dosyası doğrudan indir ───────────────────────
print("\n[C] Küçük dosya indir (~birkaç MB)")
print("-" * 50)
print("  Aşağıdaki komutu çalıştırın (cmd'de):")
print()
print("  curl -O http://opendata.cern.ch/eos/opendata/atlas/rucio/"
      "mc20_13TeV/DAOD_PHYSLITE.37620644._000012.pool.root.1")
print()
print("  Sonra bu scripti tekrar çalıştırın")
print("  Dosya C:\\AtlasTest\\DAOD_PHYSLITE_mc.root olarak kaydedin")

# ── Yöntem D: Yerel dosya varsa test et ──────────────────────────────
local_files = [
    r"C:\AtlasTest\DAOD_PHYSLITE_mc.root",
    r"C:\AtlasTest\DAOD_PHYSLITE_data16.root",
]

print("\n[D] Yerel dosya testi")
print("-" * 50)
for local in local_files:
    if os.path.exists(local):
        print(f"  Bulundu: {local}")
        try:
            f = uproot.open(local)
            tree = f["CollectionTree"]
            branches = tree.keys()
            print(f"  Branch: {len(branches)}")

            # Jet PT bul ve test et
            for b in branches:
                if "Jet" in b and "pt" in b.lower():
                    data = tree[b].array(library="ak", entry_stop=50000)
                    flat = ak.to_numpy(ak.flatten(data))
                    flat = flat[flat > 0]
                    pQ = np.percentile(flat, N_b * 100)
                    pC = np.percentile(flat, Cc_b * 100)
                    ratio = pQ / pC
                    delta = abs(ratio - T11) / T11 * 100
                    flag  = "✓✓✓" if delta<1 else "✓✓" if delta<3 else "✓"
                    print(f"  {b}: T11={ratio:.6f} Δ%={delta:.4f}% {flag}")
                    break
        except Exception as e:
            print(f"  HATA: {e}")
    else:
        print(f"  Yok: {local}")
