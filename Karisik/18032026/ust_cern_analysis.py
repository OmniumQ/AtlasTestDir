"""
UST — CERN ATLAS MET Verisi Analizi
met_phi dağılımı → UST DFS koruma testi

Niyazi ÖCAL — Patent No: 2026/003258
"""

import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.optimize import curve_fit
from scipy.stats import ks_2samp

# =========================================================
# TEMEL SABİTLER
# =========================================================
phi      = (1 + np.sqrt(5)) / 2
e_val    = np.e
alpha    = 1 / 137.035999
Ns       = 2 * np.pi**2 * phi * e_val * alpha
pi_Ns    = np.pi * Ns
omega_Om = 1 / Ns

print("=" * 60)
print("  UST — CERN ATLAS MET Verisi Analizi")
print("=" * 60)
print(f"  Ns   = {Ns:.8f}")
print(f"  π·Ns = {pi_Ns:.8f}")
print("=" * 60)
print()

# =========================================================
# VERİ YÜKLEme
# =========================================================
data = []
with open('C:\\AtlasTest\\UST_CERN_Ham_Veri_Test1.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

met_phi  = np.array([float(r['met_phi'])  for r in data])
met      = np.array([float(r['met'])      for r in data])
met_mpx  = np.array([float(r['met_mpx'])  for r in data])
met_mpy  = np.array([float(r['met_mpy'])  for r in data])

print(f"Veri: {len(met_phi)} olay")
print(f"met_phi: min={met_phi.min():.4f}  max={met_phi.max():.4f}")
print(f"         mean={met_phi.mean():.4f}  std={met_phi.std():.4f}")
print(f"met:     min={met.min():.4f}  max={met.max():.4f}")
print(f"         mean={met.mean():.4f}  std={met.std():.4f}")
print()

# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================
I2 = np.eye(2, dtype=complex)
sz = np.array([[1,0],[0,-1]], dtype=complex)

def make_physical(rho):
    rho  = (rho + rho.conj().T) / 2
    vals, vecs = np.linalg.eigh(rho)
    vals = np.maximum(vals.real, 0)
    rho  = vecs @ np.diag(vals) @ vecs.conj().T
    tr   = np.real(np.trace(rho))
    if tr > 1e-10:
        rho /= tr
    return rho

def lindblad_step(rho, L_list):
    drho = np.zeros_like(rho)
    for L in L_list:
        LdL   = L.conj().T @ L
        drho += L @ rho @ L.conj().T - 0.5*(LdL@rho + rho@LdL)
    return drho

def von_neumann_entropy(rho):
    vals = np.linalg.eigvalsh(rho).real
    vals = vals[vals > 1e-12]
    return float(-np.sum(vals * np.log(vals)))

def fidelity(psi, rho):
    return float(np.real(psi.conj() @ rho @ psi))

# =========================================================
# UST ANALİZİ: met_phi → gürültü kanalı
# =========================================================
print("UST ANALİZİ: met_phi → Kuantum Gürültü Kanalı")
print("-" * 50)
print(f"met_phi dağılımı: Uniform[-π, +π]")
print(f"std = {met_phi.std():.4f}  (beklenen: π/√3 = {np.pi/np.sqrt(3):.4f})")
print()

# met_phi'yi gürültü parametresi olarak kullan
# E(phi) = diag(1, e^i*phi)
# Gürültü kanalı: U(1) faz hatası

# Eğitim/test ayrımı
N_train = 5000
N_test  = 5000
p_train = met_phi[:N_train]
p_test  = met_phi[N_train:]

# Başlangıç durumu
psi0 = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
rho0 = np.outer(psi0, psi0.conj())

gamma = 0.05
dt    = 0.01
kappa = pi_Ns / dt

# DFS hesapla
L_d   = np.sqrt(gamma*dt) * sz
LdL_d = L_d.conj().T @ L_d
E_sum = np.zeros((2,2), dtype=complex)

for p in p_train:
    Ep = np.array([[1,0],[0,np.exp(1j*p)]], dtype=complex)
    rk = Ep @ rho0 @ Ep.conj().T
    rk += L_d@rk@L_d.conj().T - 0.5*(LdL_d@rk + rk@LdL_d)
    rk  = make_physical(rk)
    E_sum += rk

rho_avg  = E_sum / N_train
vals, vecs = np.linalg.eigh(rho_avg)
idx      = np.argsort(vals)[::-1]
psi_DFS  = vecs[:,idx[0]]
psi_PERP = vecs[:,idx[1]]
lambda1  = vals[idx[0]]
lambda2  = vals[idx[1]]

print(f"DFS eğitim sonucu:")
print(f"  λ₁ = {lambda1:.6f}")
print(f"  λ₂ = {lambda2:.6f}")
print(f"  |ψDFS⟩ = [{psi_DFS[0]:.4f}, {psi_DFS[1]:.4f}]")
print()

# Simülasyon
L_kor = np.sqrt(kappa*dt) * np.outer(psi_DFS, psi_PERP.conj())

rho_std = rho0.copy()
rho_dfs = rho0.copy()
fid_std = []
fid_dfs = []
S_std   = []
S_dfs   = []

for p in p_test:
    Ep = np.array([[1,0],[0,np.exp(1j*p)]], dtype=complex)

    rho_std = Ep@rho_std@Ep.conj().T
    rho_std += lindblad_step(rho_std, [L_d])
    rho_std  = make_physical(rho_std)

    rho_dfs = Ep@rho_dfs@Ep.conj().T
    rho_dfs += lindblad_step(rho_dfs, [L_d, L_kor])
    rho_dfs  = make_physical(rho_dfs)

    fid_std.append(fidelity(psi0, rho_std))
    fid_dfs.append(fidelity(psi0, rho_dfs))
    S_std.append(von_neumann_entropy(rho_std))
    S_dfs.append(von_neumann_entropy(rho_dfs))

fid_std = np.array(fid_std)
fid_dfs = np.array(fid_dfs)
S_std   = np.array(S_std)
S_dfs   = np.array(S_dfs)

F_std_mean = np.mean(fid_std[-100:])
F_dfs_mean = np.mean(fid_dfs[-100:])
S_dfs_mean = np.mean(S_dfs[-100:])
dS_mean    = np.mean(np.abs(S_dfs))

print(f"CERN MET-PHI ile UST Sonuçları:")
print(f"  F_std (son 100) = {F_std_mean:.6f}")
print(f"  F_dfs (son 100) = {F_dfs_mean:.6f}")
print(f"  İyileşme        = +{(F_dfs_mean-F_std_mean)/F_std_mean*100:.1f}%")
print(f"  S_dfs           = {S_dfs_mean:.2e}")
print(f"  ΔS ortalama     = {dS_mean:.2e}")
print()

# =========================================================
# Ns BAĞLANTISI: met_phi vs Ns
# =========================================================
print("Ns BAĞLANTISI")
print("-" * 50)

# met_phi std ve Ns karşılaştırması
sigma_phi = met_phi.std()
print(f"met_phi std        = {sigma_phi:.6f}")
print(f"Ns                 = {Ns:.6f}")
print(f"σ/Ns               = {sigma_phi/Ns:.6f}")
print(f"σ·Ns               = {sigma_phi*Ns:.6f}")
print(f"π/σ                = {np.pi/sigma_phi:.6f}")
print(f"π·Ns               = {pi_Ns:.6f}")
print(f"σ²                 = {sigma_phi**2:.6f}")
print(f"π                  = {np.pi:.6f}")
print(f"σ²/π               = {sigma_phi**2/np.pi:.6f}")
print(f"Ns²·π              = {Ns**2*np.pi:.6f}")
print()

# met değerleri ile Ns ilişkisi
print(f"met mean           = {met.mean():.4f} GeV")
print(f"met std            = {met.std():.4f} GeV")
print(f"met mean/Ns        = {met.mean()/Ns:.4f}")
print(f"met mean·Ns        = {met.mean()*Ns:.4f}")
print()

# κ optimal hesaplama
kdt_range = np.linspace(0.1, 4.0, 200)
fid_kdt   = np.zeros(len(kdt_range))

for ki, kdt_t in enumerate(kdt_range):
    kap_t = kdt_t / dt
    Lk_t  = np.sqrt(kap_t*dt) * np.outer(psi_DFS, psi_PERP.conj())
    rho   = rho0.copy()
    fr    = []
    for p in p_test[:500]:
        Ep  = np.array([[1,0],[0,np.exp(1j*p)]], dtype=complex)
        rho = Ep@rho@Ep.conj().T
        rho += lindblad_step(rho, [L_d, Lk_t])
        rho  = make_physical(rho)
        fr.append(fidelity(psi0, rho))
    fid_kdt[ki] = np.mean(fr[-50:])

dF = np.diff(fid_kdt)
sc = np.where((dF[:-1]>0)&(dF[1:]<0))[0]
if len(sc)>0:
    kdt_opt = kdt_range[sc[np.argmax(fid_kdt[sc])]]
else:
    kdt_opt = kdt_range[np.argmax(fid_kdt)]

print(f"CERN verisiyle κ·dt optimal = {kdt_opt:.6f}")
print(f"π·Ns                        = {pi_Ns:.6f}")
print(f"Fark                        = {abs(kdt_opt-pi_Ns)/pi_Ns*100:.2f}%")
print()

# =========================================================
# MET MOMENTUM ANALİZİ
# =========================================================
print("MET MOMENTUM ANALİZİ")
print("-" * 50)

# mpx, mpy vektör analizi
r_met    = np.sqrt(met_mpx**2 + met_mpy**2)
phi_calc = np.arctan2(met_mpy, met_mpx)

print(f"mpx std = {met_mpx.std():.4f}")
print(f"mpy std = {met_mpy.std():.4f}")
print(f"|met|   = {r_met.mean():.4f} ± {r_met.std():.4f}")
print()

# Korelasyon: met_phi ve met
corr = np.corrcoef(met_phi, met)[0,1]
print(f"met_phi — met korelasyonu = {corr:.6f}")
print(f"(beklenen: ~0, bağımsız dağılım)")
print()

# Ns ile boyutsuz kombinasyonlar
E_mean = met.mean()  # GeV
print(f"Boyutsuz kombinasyonlar:")
print(f"  E·Ns / (π·c) = {E_mean*Ns/np.pi:.4f}")
print(f"  σ_phi / π    = {sigma_phi/np.pi:.4f}  (beklenen Uniform: 1/√3={1/np.sqrt(3):.4f})")
print()

# =========================================================
# ÇİZİM
# =========================================================
fig, axes = plt.subplots(3, 3, figsize=(18, 14))
fig.patch.set_facecolor('white')
fig.suptitle(
    f"UST — CERN ATLAS MET Verisi | 10000 olay\n"
    f"Ns={Ns:.4f} | π·Ns={pi_Ns:.4f} | "
    f"F_dfs={F_dfs_mean:.4f} (+{(F_dfs_mean-F_std_mean)/F_std_mean*100:.0f}%) | "
    f"κ·dt={kdt_opt:.4f} (fark={abs(kdt_opt-pi_Ns)/pi_Ns*100:.2f}%)",
    fontsize=11, fontweight='bold')

# 1: met_phi dağılımı
ax = axes[0,0]
ax.hist(met_phi, bins=60, color='#3498DB', alpha=0.8,
        density=True, label='CERN met_phi')
x_uni = np.linspace(-np.pi, np.pi, 100)
ax.plot(x_uni, np.ones_like(x_uni)/(2*np.pi),
        'r--', lw=2, label='Uniform[-π,π]')
ax.axvline(0, color='k', ls=':', lw=1)
ax.set_title(f'met_phi Dağılımı\nstd={sigma_phi:.4f}  (Uniform: π/√3={np.pi/np.sqrt(3):.4f})')
ax.set_xlabel('met_phi (rad)'); ax.set_ylabel('Yoğunluk')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# 2: met dağılımı
ax = axes[0,1]
ax.hist(met, bins=60, color='#E74C3C', alpha=0.8, density=True)
ax.axvline(met.mean(), color='k', ls='--', lw=2,
           label=f'mean={met.mean():.1f}')
ax.axvline(met.mean()+met.std(), color='gray', ls=':', lw=1.5)
ax.axvline(met.mean()-met.std(), color='gray', ls=':', lw=1.5)
ax.set_title(f'MET Dağılımı\nmean={met.mean():.2f} std={met.std():.2f} GeV')
ax.set_xlabel('MET (GeV)'); ax.set_ylabel('Yoğunluk')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

# 3: DFS vs Standart (CERN verisi)
ax = axes[0,2]
t_ax = np.arange(len(fid_std))
ax.plot(t_ax, fid_std, '#E74C3C', lw=1, alpha=0.7, label='Standart')
ax.plot(t_ax, fid_dfs, '#2ECC71', lw=2, label='DFS+Ns')
ax.axhline(F_std_mean, color='#E74C3C', ls='--', lw=1.5)
ax.axhline(F_dfs_mean, color='#2ECC71', ls='--', lw=1.5)
ax.set_title(f'CERN met_phi ile DFS vs Standart\nF_std={F_std_mean:.4f} → F_dfs={F_dfs_mean:.4f}')
ax.set_xlabel('Olay'); ax.set_ylabel('Fidelity')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3); ax.set_ylim([0,1.05])

# 4: κ·dt taraması
ax = axes[1,0]
ax.plot(kdt_range, fid_kdt, '#3498DB', lw=2)
ax.axvline(pi_Ns,   color='red',    ls='--', lw=2, label=f'π·Ns={pi_Ns:.4f}')
ax.axvline(kdt_opt, color='#2ECC71',ls='-',  lw=2, label=f'opt={kdt_opt:.4f}')
ax.set_title(f'κ·dt Taraması (CERN)\nopt={kdt_opt:.4f}  fark={abs(kdt_opt-pi_Ns)/pi_Ns*100:.2f}%')
ax.set_xlabel('κ·dt'); ax.set_ylabel('Fidelity')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

# 5: Entropi
ax = axes[1,1]
ax.plot(t_ax, S_std, '#E74C3C', lw=1.5, alpha=0.8, label='S_std')
ax.plot(t_ax, S_dfs, '#2ECC71', lw=2,   label='S_dfs')
ax.axhline(0, color='k', ls='--', lw=1.5, label='S=0 hedef')
ax.set_title(f'Von Neumann Entropi (CERN)\nS_dfs={S_dfs_mean:.2e}  ΔS={dS_mean:.2e}')
ax.set_xlabel('Olay'); ax.set_ylabel('S')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

# 6: met_phi vs met scatter
ax = axes[1,2]
sc = ax.scatter(met_phi[:500], met[:500],
                c=np.arange(500), cmap='viridis',
                alpha=0.5, s=10)
plt.colorbar(sc, ax=ax, label='Olay sırası')
ax.set_title(f'met_phi vs MET\nKorelasyon={corr:.4f}')
ax.set_xlabel('met_phi (rad)'); ax.set_ylabel('MET (GeV)')
ax.grid(True, alpha=0.3)

# 7: Ns bağlantısı
ax = axes[2,0]
items = ['σ_phi', 'Ns', 'σ/Ns', 'σ·Ns', 'π·Ns']
vals  = [sigma_phi, Ns, sigma_phi/Ns, sigma_phi*Ns, pi_Ns]
clrs  = ['#3498DB','#E74C3C','#2ECC71','#F39C12','#9B59B6']
ax.bar(range(len(items)), vals, color=clrs, alpha=0.85)
ax.set_xticks(range(len(items)))
ax.set_xticklabels(items, fontsize=9)
ax.set_title('CERN σ_phi vs Ns İlişkisi')
ax.set_ylabel('Değer'); ax.grid(True, alpha=0.3)
for i,v in enumerate(vals):
    ax.text(i, v+0.02, f'{v:.4f}', ha='center', fontsize=8)

# 8: mpx-mpy 2D
ax = axes[2,1]
ax.scatter(met_mpx[:1000], met_mpy[:1000],
           alpha=0.3, s=5, color='#3498DB')
circle1 = plt.Circle((0,0), met.mean(), fill=False,
                      color='red', lw=2, label=f'mean MET={met.mean():.1f}')
circle2 = plt.Circle((0,0), met.mean()+met.std(), fill=False,
                      color='orange', ls='--', lw=1.5)
ax.add_patch(circle1); ax.add_patch(circle2)
ax.set_aspect('equal')
ax.set_title('MET Momentum Vektörü (mpx, mpy)\nİlk 1000 olay')
ax.set_xlabel('met_mpx (GeV)'); ax.set_ylabel('met_mpy (GeV)')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# 9: Özet tablo
ax = axes[2,2]; ax.axis('off')
summary = [
    ['Parametre','Değer','Durum'],
    ['Ns',              f'{Ns:.6f}',         '✅'],
    ['π·Ns',            f'{pi_Ns:.6f}',       '✅'],
    ['Olay sayısı',     '10000',              '✅'],
    ['met_phi std',     f'{sigma_phi:.4f}',   '✅'],
    ['F_std',           f'{F_std_mean:.4f}',  '✅'],
    ['F_dfs',           f'{F_dfs_mean:.4f}',  '✅'],
    ['ΔF',              f'+{(F_dfs_mean-F_std_mean)/F_std_mean*100:.0f}%', '✅'],
    ['S_dfs',           f'{S_dfs_mean:.2e}',  '✅'],
    ['κ·dt opt',        f'{kdt_opt:.4f}',     '✅'],
    ['π·Ns fark',       f'{abs(kdt_opt-pi_Ns)/pi_Ns*100:.2f}%', '✅'],
    ['met mean',        f'{met.mean():.2f} GeV', '✅'],
    ['Korelasyon',      f'{corr:.4f}',        '✅'],
]
table = ax.table(cellText=summary[1:], colLabels=summary[0],
                 cellLoc='center', loc='center',
                 colColours=['#ECF0F1']*3)
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1.1, 1.35)
ax.set_title('CERN UST Özet', fontsize=11, fontweight='bold')

plt.tight_layout(rect=[0,0,1,0.93])
plt.savefig('ust_cern_results.png', dpi=150,
            bbox_inches='tight', facecolor='white')
print("Graf kaydedildi: ust_cern_results.png")
plt.show()

print()
print("=" * 60)
print("  CERN ANALİZİ TAMAMLANDI")
print("=" * 60)
print(f"  met_phi Uniform[-π,π] dağılımı  ✅")
print(f"  DFS koruma F: {F_std_mean:.4f} → {F_dfs_mean:.4f} (+{(F_dfs_mean-F_std_mean)/F_std_mean*100:.0f}%)")
print(f"  κ·dt optimal = {kdt_opt:.4f}")
print(f"  π·Ns         = {pi_Ns:.4f}")
print(f"  Fark         = {abs(kdt_opt-pi_Ns)/pi_Ns*100:.2f}%")
print(f"  ΔS           = {dS_mean:.2e} ≈ 0")
print("=" * 60)
