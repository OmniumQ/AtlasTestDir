"""
ATLAS DAOD_PHYSLITE — 65 TB Araştırma Verisi
UST v5 T11 Testi — Bilimsel yayına uygun (CC0)
DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI

Yöntem 1: atlasopenmagic paketi ile
Yöntem 2: uproot + XRootD ile

Önce: pip install atlasopenmagic
"""

import numpy as np

# ── UST sabitleri ─────────────────────────────────────────────────────
N_b  = 0.63354460
Cc_b = 1 - N_b
N_m  = 0.63353522
Cc_m = 1 - N_m
T_Om = np.exp(-2 * np.pi * N_b * Cc_b)
T11_theory = (N_m / Cc_m) * (1 + N_b * N_m / (2 * np.pi))

print("=" * 65)
print("ATLAS PHYSLITE 65TB — UST v5 T11 Testi")
print(f"T11 teorik = {T11_theory:.6f}")
print(f"DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI (CC0)")
print("=" * 65)

# ══════════════════════════════════════════════════════════════════════
# YÖNTEM 1: atlasopenmagic
# ══════════════════════════════════════════════════════════════════════
try:
    import atlasopenmagic as atom
    print("\n[Yöntem 1] atlasopenmagic kurulu ✓")

    # Mevcut veri setlerini listele
    print("\nMevcut veri setleri:")
    datasets = atom.list_datasets()
    for d in datasets[:10]:
        print(f"  {d}")

    # 2016 pp çarpışma verisini yükle
    print("\n2016 pp verisi yükleniyor...")
    ds = atom.open_dataset("data16_13TeV")

    # Jet ve MET değişkenlerini oku
    jets = ds["InDetTrackParticles"]
    print(f"Değişkenler: {ds.keys()[:20]}")

except ImportError:
    print("\natlasopenmagic kurulu değil.")
    print("Kurmak için: pip install atlasopenmagic")
    print("Yöntem 2'ye geçiliyor...")

# ══════════════════════════════════════════════════════════════════════
# YÖNTEM 2: uproot + XRootD doğrudan erişim
# ══════════════════════════════════════════════════════════════════════
try:
    import uproot

    print("\n[Yöntem 2] uproot ile XRootD erişimi")
    print("XRootD kurulu mu kontrol ediliyor...")

    # CERN EOS üzerinden doğrudan erişim
    # 2016 veri dosyası örneği
    base_url = "root://eospublic.cern.ch//eos/opendata/atlas/rucio/data16_13TeV"

    # Küçük bir dosya dene
    test_files = [
        "root://eospublic.cern.ch//eos/opendata/atlas/rucio/data16_13TeV/"
        "00302872/DAOD_PHYSLITE.29004645._000001.pool.root.1",
    ]

    print(f"\nTest dosyası açılıyor...")
    for f_url in test_files:
        try:
            f = uproot.open(f_url, timeout=30)
            print(f"✓ Bağlantı başarılı!")
            print(f"Anahtarlar: {list(f.keys())[:10]}")

            # Ana ağaç
            tree_name = "CollectionTree"
            if tree_name in f:
                tree = f[tree_name]
                print(f"Toplam branch: {len(tree.keys())}")
                print(f"Branch listesi (ilk 30):")
                for k in list(tree.keys())[:30]:
                    print(f"  {k}")
        except Exception as e:
            print(f"  Bağlantı hatası: {e}")
            print("  XRootD kurulu değil olabilir")
            print("  Kurmak için: pip install xrootd")

except ImportError:
    print("uproot kurulu değil: pip install uproot")

# ══════════════════════════════════════════════════════════════════════
# YÖNTEM 3: CERN SWAN / Binder (indirme gerektirmez)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 65)
print("YÖNTEM 3: Web tabanlı erişim (indirme gerektirmez)")
print("=" * 65)
print("""
  CERN SWAN (CERN hesabı gerekli):
  https://swan.cern.ch

  Binder (hesap gerektirmez):
  https://mybinder.org/v2/gh/atlas-outreach-data-tools/notebooks-collection-opendata/master

  GitHub (örnek notebook):
  https://github.com/atlas-outreach-data-tools/notebooks-collection-opendata

  ATLAS Open Data Tutorial:
  https://opendata.atlas.cern/docs/tutresearch/physlitetut
""")

print("=" * 65)
print("ÖNERİLEN SIRADAKI ADIMLAR")
print("=" * 65)
print("""
  1. pip install xrootd uproot awkward
  2. Bu scripti tekrar çalıştır (Yöntem 2 çalışacak)
  3. PHYSLITE branch'lerini gör
  4. jet_pt / jet_E / met_sumet branching bul
  5. UST T11 testi uygula (N_b ve Cc_b yüzdelikleri)
  6. ONL üç bölge testi uygula
  7. Sonuçları DOI ile makaleye ekle

  Makale referansı:
  ATLAS Collaboration (2024). DAOD_PHYSLITE format 2015-2016
  Open Data for Research. CERN Open Data Portal.
  DOI: 10.7483/OPENDATA.ATLAS.9HK7.P5SI
""")
