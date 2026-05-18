import uproot
import pandas as pd

file_path = r"C:\AtlasTest\ODEO_FEB2025_v0_2J2LMET30_data16_periodL.2J2LMET30.root"

with uproot.open(file_path) as f:
    print("Dosya içeriği:")
    for key in f.keys():
        print(" -", key)

    # İlk TTree'yi otomatik seç
    tree_name = None
    for key, obj in f.items():
        if isinstance(obj, uproot.behaviors.TTree.TTree):
            tree_name = key
            break

    if tree_name is None:
        raise ValueError("Dosyada TTree bulunamadı.")

    print(f"\nSeçilen tree: {tree_name}")

    tree = f[tree_name]

    # Kolon adları
    columns = tree.keys()
    print("\nKolon adları:")
    for col in columns:
        print(col)

    # İlk 10 satır
    df = tree.arrays(library="pd").head(10)

    print("\nİlk 10 satır:")
    print(df)