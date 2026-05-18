import numpy as np
import os
import re

print("UST v5 – RA Minimizasyonu (Kütle ve Hacim Dahil)")
print("="*70)

# --- UST SABİTLERİ ---
Nb  = 0.6335446
Nm  = 0.63353522
RA  = Nb - Nm
Ccb = 1.0 - Nb
TOm = np.exp(-2*np.pi*Nb*Ccb)

print(f"Nb = {Nb}")
print(f"Nm = {Nm}")
print(f"RA = Nb-Nm = {RA:.8f}")
print(f"Ccb = {Ccb}")
print(f"TOm = {TOm:.8f}")

# --- CIF OKUMA ---
def parse_cif(path):
    data = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if "_cell_length_a" in line:
                data['a'] = float(re.findall(r"[\d\.]+", line)[0])
            elif "_cell_length_b" in line:
                data['b'] = float(re.findall(r"[\d\.]+", line)[0])
            elif "_cell_length_c" in line:
                data['c'] = float(re.findall(r"[\d\.]+", line)[0])
            elif "_cell_volume" in line:
                data['V'] = float(re.findall(r"[\d\.]+", line)[0])
            elif "_exptl_crystal_density_diffrn" in line:
                data['rho'] = float(re.findall(r"[\d\.]+", line)[0])
    return data

# --- DOSYALAR ---
files = {
    "D_RAO": r"C:\AtlasTest\adg8274_Data_S1.cif",
    "L_RAO": r"C:\AtlasTest\adg8274_Data_S2.cif",
    "DX_RAO": r"C:\AtlasTest\adg8274_Data_S3.cif"
}

data = {}
for key, path in files.items():
    if os.path.exists(path):
        data[key] = parse_cif(path)
    else:
        print(f"HATA: {path} bulunamadı")

# --- KÜTLE ÇEKİM ETKİSİ VE ΔV RA İLİŞKİSİ ---
print("\n" + "="*70)
print("D/L HACİM FARKI VE RA ETKİSİ")
print("-"*70)

V_D = data['D_RAO']['V']
V_L = data['L_RAO']['V']
rho_D = data['D_RAO']['rho']
rho_L = data['L_RAO']['rho']

# Kütle farkı
m_D = V_D * rho_D
m_L = V_L * rho_L
delta_m = m_D - m_L

# Hacim farkı
delta_V = V_D - V_L

# RA etkisi
RA_impact = delta_V / RA if RA != 0 else np.nan
RA_mass_impact = delta_m / RA if RA != 0 else np.nan

print(f"V_D       = {V_D} Å³")
print(f"V_L       = {V_L} Å³")
print(f"ΔV_D-L    = {delta_V:.6f} Å³")
print(f"ρ_D       = {rho_D} g/cm³")
print(f"ρ_L       = {rho_L} g/cm³")
print(f"m_D       = {m_D:.6f}")
print(f"m_L       = {m_L:.6f}")
print(f"Δm_D-L    = {delta_m:.6f}")
print(f"RA         = {RA:.8f}")
print(f"ΔV / RA   = {RA_impact:.2f} Å³ per RA unit")
print(f"Δm / RA   = {RA_mass_impact:.2f} mass unit per RA unit")

# --- KAFES PARAMETRELERİ ---
a_D = data['D_RAO']['a']
b_D = data['D_RAO']['b']
c_D = data['D_RAO']['c']

print("\nKafes Oranları (D_RAO):")
print(f"a/c = {a_D/c_D:.6f}")
print(f"b/c = {b_D/c_D:.6f}")

# --- GENEL SONUÇ ---
print("\n" + "="*70)
print("GENEL YORUM")
print("-"*70)
print("• RA = Nb-Nm kristal asimetrisinin mikroskopik ölçüsü")
print("• ΔV / RA ve Δm / RA → blueprint-manifest gap etkisini gösterir")
print("• Küçük RA → küçük hacim ve kütle farkı → yüksek simetri")
print("• B ekseni asimetrisi RA’dan kaynaklanabilir")
print("• XAO ile hacim/kütle artışı RA etkisiyle karşılaştırılabilir")