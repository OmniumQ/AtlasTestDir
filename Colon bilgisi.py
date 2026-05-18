import os
import pandas as pd
from astropy.io.votable import parse

# ============================
# 1) VOT dosyasını DataFrame'e çeviren fonksiyon (HATA ÇÖZÜLDÜ)
# ============================
def load_vot_to_df(path):
    vot = parse(path)
    table = vot.get_first_table()
    data = table.array

    # Masked array → normal array
    data = data.filled(None)

    df = pd.DataFrame(data)
    return df

# ============================
# 2) Klasör yolu
# ============================
folder = r"C:\\AtlasTest\\"

# ============================
# 3) Dosya eşleşmeleri
# ============================
files = {
    "mer":  "c53c4270-22cc-11f1-8a0e-e8ebd3edb7d7-TPDR-result.vot",
    "phz":  "c5f0d03b-22cd-11f1-8a0e-e8ebd3edb7d7-TPDR-result.vot",
    "phys": "4e5e59de-22ce-11f1-8a0e-e8ebd3edb7d7-TPDR-result.vot",
    "cls":  "64b8b3bf-22ce-11f1-8a0e-e8ebd3edb7d7-TPDR-result.vot"
}

# ============================
# 4) Her tabloyu yükle
# ============================
df_mer  = load_vot_to_df(os.path.join(folder, files["mer"]))
df_phz  = load_vot_to_df(os.path.join(folder, files["phz"]))
df_phys = load_vot_to_df(os.path.join(folder, files["phys"]))
df_cls  = load_vot_to_df(os.path.join(folder, files["cls"]))

# ============================
# 5) object_id üzerinden birleştir
# ============================
df = df_mer
df = df.merge(df_phz,  on="object_id", how="left")
df = df.merge(df_phys, on="object_id", how="left")
df = df.merge(df_cls,  on="object_id", how="left")

# ============================
# 6) Sonuç
# ============================
print("Birleştirme tamamlandı!")
print("Toplam satır:", len(df))
print("Toplam kolon:", len(df.columns))
print(df.head())