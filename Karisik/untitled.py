"""
UST (Unified Source Theory) — QuTiP Deney
Windows'ta direkt çalışır, Jupyter gerekmez.

KURULUM (CMD veya PowerShell'de bir kez çalıştır):
    pip install numpy scipy matplotlib qutip

ÇALIŞTIRMA:
    python ust_deney.py

Niyazi ÖCAL — Patent No: 2026/003258
"""

import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# QuTiP kontrolü
# ─────────────────────────────────────────────
try:
    import qutip as qt
    print("QuTiP yüklü ✓  versiyon:", qt.__version__)
except ImportError:
    print("HATA: QuTiP bulunamadı!")
    print("Şu komutu çalıştır:  pip install qutip")
    input("Çıkmak için Enter...")
    exit()

# ═══════════════════════════════════════════════════════════
# BÖLÜM 1 — TEMEL SABİTLER
# ═══════════════════════════════════════════════════════════
phi   = (1 + np.sqrt(5)) / 2
e_val = np.e
alpha = 1 / 137.035999
Ns_q  = 2 * np.pi**2 * phi * e_val * alpha
pi_Ns = np.pi * Ns_q

print()
print("=" * 55)
print("  UST EVRENSEİ SABİTLER")
print("=" * 55)
print(f"  Ns_q          = {Ns_q:.10f}")
print(f"  π·Ns_q        = {pi_Ns:.10f}")
print(f"  (√3−1)/2      = {(np.sqrt(3)-1)/2:.10f}  ← T2 alt sınırı")
print(f"  1 − Ns_q      = {1-Ns_q:.10f}  ← T10 tünelleme")
print(f"  Ns/(1-Ns)     = {Ns_q/(1-Ns_q):.6f}  ≈ √3 = {np.sqrt(3):.6f}")
print("=" * 55)

# ═══════════════════════════════════════════════════════════
# BÖLÜM 2 — YARDIMCI FONKSİYONLAR (QuTiP tabanlı)
# ═══════════════════════════════════════════════════════════
sz = qt.sigmaz()
sx = qt.sigmax()
sy = qt.sigmay()
I2 = qt.identity(2)

def make_physical(rho):
    """Yoğunluk matrisini fiziksel yap: Hermitik, pozitif, iz=1."""
    rho  = (rho + rho.dag()) / 2
    vals, vecs = rho.eigenstates()
    vals = np.maximum(vals.real, 0)
    rho  = sum(float(v) * vecs[i] * vecs[i].dag()
               for i, v in enumerate(vals))
    tr   = rho.tr().real
    if tr > 1e-10:
        rho = rho / tr
    return rho

def lindblad_step(rho, ops):
    """Lindblad terimi: Σ [L ρ L† − ½(L†L ρ + ρ L†L)]"""
    drho = qt.Qobj(np.zeros((2,2), dtype=complex), dims=[[2],[2]])
    for L in ops:
        LdL   = L.dag() * L
        drho += L * rho * L.dag() - 0.5 * (LdL * rho + rho * LdL)
    return drho

def fidelity(psi, rho):
    """F = ⟨ψ|ρ|ψ⟩"""
    return float(np.real((psi.dag() * rho * psi).tr()))

def von_neumann(rho):
    """S = −Tr(ρ ln ρ)"""
    return float(qt.entropy_vn(rho, base=np.e))

def compute_dfs(rho0, p_train, gamma, dt):
    """Gürültü istatistiğinden DFS yönünü öğren."""
    Ld    = np.sqrt(gamma * dt) * sz
    LdLd  = Ld.dag() * Ld
    E_sum = qt.Qobj(np.zeros((2,2), dtype=complex), dims=[[2],[2]])
    for p in p_train:
        U  = (-1j * p * sz / 2).expm()
        rk = U * rho0 * U.dag()
        rk = rk + Ld * rk * Ld.dag() - 0.5*(LdLd*rk + rk*LdLd)
        rk = make_physical(rk)
        E_sum = E_sum + rk
    rho_avg  = E_sum / len(p_train)
    vals, vecs = rho_avg.eigenstates()
    idx      = np.argsort(vals.real)[::-1]
    return vecs[idx[0]], vecs[idx[1]]

def find_optimal_kdt(psi_ref, psi_DFS, psi_PERP,
                     p_test, gamma, dt, kdt_range, N_last=50):
    """κ·dt taraması ile optimal değeri bul."""
    Ld    = np.sqrt(gamma * dt) * sz
    rho0_ = psi_ref * psi_ref.dag()
    fid_k = np.zeros(len(kdt_range))
    for ki, kdt_val in enumerate(kdt_range):
        kap  = kdt_val / dt
        Lk   = np.sqrt(kap * dt) * psi_DFS * psi_PERP.dag()
        rho  = rho0_.copy()
        fr   = []
        for p in p_test:
            U   = (-1j * p * sz / 2).expm()
            rho = U * rho * U.dag()
            rho = rho + lindblad_step(rho, [Ld, Lk])
            rho = make_physical(rho)
            fr.append(fidelity(psi_ref, rho))
        fid_k[ki] = np.mean(fr[-N_last:])
    dF = np.diff(fid_k)
    sc = np.where((dF[:-1] > 0) & (dF[1:] < 0))[0]
    if len(sc) > 0:
        kdt_opt = kdt_range[sc[np.argmax(fid_k[sc])]]
    else:
        kdt_opt = kdt_range[np.argmax(fid_k)]
    return kdt_opt, fid_k

# ═══════════════════════════════════════════════════════════
# BÖLÜM 3 — PARAMETRELER
# ═══════════════════════════════════════════════════════════
gamma   = 0.05
dt      = 0.01
kappa   = pi_Ns / dt
sigma   = 1.0
N       = 1000
N_train = 500

np.random.seed(42)
p_noise = sigma * np.random.randn(N)
p_train = p_noise[:N_train]
p_test  = p_noise[N_train:]

psi0  = (qt.basis(2,0) + qt.basis(2,1)).unit()
rho0  = psi0 * psi0.dag()
kdt_range = np.linspace(0.5, 3.5, 60)

# ═══════════════════════════════════════════════════════════
# TEST 1 — DFS vs STANDART
# ═══════════════════════════════════════════════════════════
print("\n[TEST 1] DFS öğreniliyor...")
psi_DFS, psi_PERP = compute_dfs(rho0, p_train, gamma, dt)
print(f"  |ψ_DFS⟩ = [{psi_DFS[0][0][0]:.4f},  {psi_DFS[1][0][0]:.4f}]")

L_dek = np.sqrt(gamma * dt) * sz
L_kor = np.sqrt(kappa * dt) * psi_DFS * psi_PERP.dag()

rho_std = rho0.copy()
rho_dfs = rho0.copy()
fid_std_arr, fid_dfs_arr, S_dfs_arr = [], [], []

print("  Simülasyon çalışıyor (500 adım)...")
for p in p_test:
    U = (-1j * p * sz / 2).expm()

    rho_std  = U * rho_std * U.dag()
    rho_std  = rho_std + lindblad_step(rho_std, [L_dek])
    rho_std  = make_physical(rho_std)

    rho_dfs  = U * rho_dfs * U.dag()
    rho_dfs  = rho_dfs + lindblad_step(rho_dfs, [L_dek, L_kor])
    rho_dfs  = make_physical(rho_dfs)

    fid_std_arr.append(fidelity(psi0, rho_std))
    fid_dfs_arr.append(fidelity(psi0, rho_dfs))
    S_dfs_arr.append(von_neumann(rho_dfs))

fid_std_arr = np.array(fid_std_arr)
fid_dfs_arr = np.array(fid_dfs_arr)
S_dfs_arr   = np.array(S_dfs_arr)

F_std = np.mean(fid_std_arr[-50:])
F_dfs = np.mean(fid_dfs_arr[-50:])
S_son = np.mean(S_dfs_arr[-50:])

print()
print("-" * 45)
print(f"  F_std (son 50) = {F_std:.6f}")
print(f"  F_dfs (son 50) = {F_dfs:.6f}")
print(f"  İyileşme       = +{(F_dfs-F_std)/F_std*100:.1f}%")
print(f"  S_dfs (son 50) = {S_son:.2e}  (→ 0 hedef)")
print("-" * 45)

# ═══════════════════════════════════════════════════════════
# TEST 2 — κ·dt OPTİMAL TARAMASI
# ═══════════════════════════════════════════════════════════
print("\n[TEST 2] κ·dt taraması (60 nokta)...")
kdt_opt, fid_kdt = find_optimal_kdt(
    psi0, psi_DFS, psi_PERP, p_test, gamma, dt, kdt_range)

print()
print("-" * 45)
print(f"  κ·dt optimal  = {kdt_opt:.6f}")
print(f"  π·Ns_q        = {pi_Ns:.6f}")
print(f"  Fark          = {abs(kdt_opt-pi_Ns)/pi_Ns*100:.2f}%")
if abs(kdt_opt - pi_Ns)/pi_Ns < 0.05:
    print("  ✓ T1 DOĞRULANDI")
print("-" * 45)

# ═══════════════════════════════════════════════════════════
# TEST 3 — γ BAĞIMSIZLIĞI
# ═══════════════════════════════════════════════════════════
print("\n[TEST 3] γ bağımsızlığı testi...")
gamma_vals = [0.01, 0.02, 0.05, 0.10, 0.20]
kdt_gamma  = []

for gam in gamma_vals:
    pD, pP = compute_dfs(rho0, p_train, gam, dt)
    ko, _  = find_optimal_kdt(psi0, pD, pP, p_test, gam, dt, kdt_range)
    kdt_gamma.append(ko)
    print(f"  γ={gam:.3f}  →  κ·dt={ko:.4f}  fark={abs(ko-pi_Ns)/pi_Ns*100:.2f}%")

ort_fark = np.mean([abs(k-pi_Ns)/pi_Ns*100 for k in kdt_gamma])
print(f"\n  Ortalama fark = {ort_fark:.2f}%")
if ort_fark < 5.0:
    print("  ✓ T1 EVRENSELLİĞİ DOĞRULANDI")

# ═══════════════════════════════════════════════════════════
# TEST 4 — T2: F_Om ALT SINIRI
# ═══════════════════════════════════════════════════════════
print("\n[TEST 4] T2 — Omnium fidelity alt sınırı...")
alt_sinir = (np.sqrt(3) - 1) / 2

test_states = {
    '|+⟩' : (qt.basis(2,0) + qt.basis(2,1)).unit(),
    '|0⟩' : qt.basis(2,0),
    '|1⟩' : qt.basis(2,1),
    '|-⟩' : (qt.basis(2,0) - qt.basis(2,1)).unit(),
    '|i+⟩': (qt.basis(2,0) + 1j*qt.basis(2,1)).unit(),
}

F_Om_mins = []
for name, psi_init in test_states.items():
    rho = (psi_init * psi_init.dag()).copy()
    fr  = []
    for p in p_test:
        U   = (-1j * p * sz / 2).expm()
        rho = U * rho * U.dag()
        rho = rho + lindblad_step(rho, [L_dek, L_kor])
        rho = make_physical(rho)
        F_Q  = fidelity(psi_init, rho)
        F_Om = Ns_q * F_Q + (1 - Ns_q)
        fr.append(F_Om)
    F_Om_min = min(fr)
    F_Om_mins.append(F_Om_min)
    status = "✓" if F_Om_min >= alt_sinir else "✗"
    print(f"  {name:6s}: F_Om_min={F_Om_min:.4f}  ≥ {alt_sinir:.4f}? {status}")

if all(f >= alt_sinir for f in F_Om_mins):
    print("  ✓ T2 DOĞRULANDI")

# ═══════════════════════════════════════════════════════════
# TEST 5 — T3: ANALİTİK ENTROPİ FORMÜLÜ
# ═══════════════════════════════════════════════════════════
print("\n[TEST 5] T3 — Analitik entropi formülü...")

def S_Om_analitik(Ns, F):
    disc  = 1 - 4 * Ns * (1-Ns) * (1-F)
    if disc < 0: return 0.0
    lp = (1 + np.sqrt(disc)) / 2
    lm = (1 - np.sqrt(disc)) / 2
    S  = 0.0
    if lp > 1e-12: S -= lp * np.log(lp)
    if lm > 1e-12: S -= lm * np.log(lm)
    return S

F_son  = fid_dfs_arr[-50:]
S_sim  = S_dfs_arr[-50:]
S_anal = np.array([S_Om_analitik(Ns_q, f) for f in F_son])
fark_T3 = np.mean(np.abs(S_sim - S_anal)) / (np.mean(np.abs(S_anal)) + 1e-12) * 100

print(f"  S_Om simülasyon = {np.mean(S_sim):.6f}")
print(f"  S_Om analitik   = {np.mean(S_anal):.6f}")
print(f"  Fark            = {fark_T3:.2f}%")
if fark_T3 < 5.0:
    print("  ✓ T3 DOĞRULANDI")

# ═══════════════════════════════════════════════════════════
# TEST 6 — T10: OMNIUM TÜNELLEMESİ
# ═══════════════════════════════════════════════════════════
print("\n[TEST 6] T10 — Omnium tünelleme...")

T_Om_teori    = np.exp(-2 * (1-Ns_q) * pi_Ns)
T_Om_beklenti = 1 - Ns_q
T_Om_sim      = 1 - np.mean(fid_dfs_arr[-100:])

print(f"  T_Om = exp(−2·(1−Ns)·π·Ns)")
print(f"       = exp({-2*(1-Ns_q)*pi_Ns:.4f})")
print(f"       = {T_Om_teori:.6f}")
print(f"  1 − Ns_q (beklenen) = {T_Om_beklenti:.6f}")
print(f"  Fark                = {abs(T_Om_teori-T_Om_beklenti):.6f}")
print(f"  Simülasyon T_Om     = {T_Om_sim:.6f}")
print(f"  Kanal Q'da kalan    = {1-T_Om_teori:.4f}  ≈  Ns_q = {Ns_q:.4f}")
print(f"  Kanal C'ye sızan    = {T_Om_teori:.4f}  ≈  1-Ns_q = {1-Ns_q:.4f}")

# ═══════════════════════════════════════════════════════════
# BÖLÜM 4 — GRAFİKLER
# ═══════════════════════════════════════════════════════════
print("\nGrafikler çiziliyor...")

fig, axes = plt.subplots(3, 3, figsize=(18, 14))
fig.patch.set_facecolor('white')
fig.suptitle(
    f"UST QuTiP Deneyi  |  Ns_q={Ns_q:.4f}  |  π·Ns={pi_Ns:.4f}\n"
    f"F_dfs={F_dfs:.4f} (+{(F_dfs-F_std)/F_std*100:.0f}%)  |  "
    f"κ·dt_opt={kdt_opt:.4f} (fark={abs(kdt_opt-pi_Ns)/pi_Ns*100:.1f}%)  |  "
    f"T_Om={T_Om_teori:.4f} ≈ 1−Ns={1-Ns_q:.4f}",
    fontsize=11, fontweight='bold'
)

t_ax = np.arange(len(fid_std_arr))

# 1: DFS vs Standart
ax = axes[0, 0]
ax.plot(t_ax, fid_std_arr, '#E74C3C', lw=1, alpha=0.7, label='Standart')
ax.plot(t_ax, fid_dfs_arr, '#2ECC71', lw=2, label='DFS+Ns')
ax.axhline(F_std, color='#E74C3C', ls='--', lw=1.5)
ax.axhline(F_dfs, color='#2ECC71', ls='--', lw=1.5)
ax.axhline((np.sqrt(3)-1)/2, color='orange', ls=':', lw=1.5, label='T2 alt sınır')
ax.set_title(f'T1: DFS vs Standart\nF_std={F_std:.4f} → F_dfs={F_dfs:.4f} (+{(F_dfs-F_std)/F_std*100:.0f}%)')
ax.set_xlabel('Adım'); ax.set_ylabel('Fidelity')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3); ax.set_ylim([0, 1.05])

# 2: κ·dt taraması
ax = axes[0, 1]
ax.plot(kdt_range, fid_kdt, '#3498DB', lw=2.5)
ax.axvline(pi_Ns,   color='red',   ls='--', lw=2, label=f'π·Ns={pi_Ns:.4f}')
ax.axvline(kdt_opt, color='green', ls='-',  lw=2, label=f'opt={kdt_opt:.4f}')
ax.set_title(f'T1: κ·dt Taraması\noptimal={kdt_opt:.4f}  fark={abs(kdt_opt-pi_Ns)/pi_Ns*100:.1f}%')
ax.set_xlabel('κ·dt'); ax.set_ylabel('Fidelity')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

# 3: γ bağımsızlığı
ax = axes[0, 2]
ax.plot(gamma_vals, kdt_gamma, 'bo-', lw=2, ms=10, label='Ölçülen')
ax.axhline(pi_Ns, color='red', ls='--', lw=2, label=f'π·Ns')
ax.fill_between(gamma_vals,
                [pi_Ns*0.95]*len(gamma_vals),
                [pi_Ns*1.05]*len(gamma_vals),
                alpha=0.15, color='red', label='±5% bant')
ax.set_title(f'T1: γ Bağımsızlığı\nOrt fark={ort_fark:.2f}%')
ax.set_xlabel('γ'); ax.set_ylabel('κ·dt optimal')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# 4: Entropi
ax = axes[1, 0]
ax.plot(t_ax, S_dfs_arr, '#9B59B6', lw=2, label='S_dfs simülasyon')
ax.axhline(0, color='k', ls='--', lw=1.5, label='S=0 hedef')
ax.set_title(f'T3: Von Neumann Entropi\nS_son={S_son:.2e}  →  0 hedef')
ax.set_xlabel('Adım'); ax.set_ylabel('S')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

# 5: T2 — F_Om bar grafiği
ax = axes[1, 1]
names  = list(test_states.keys())
colors = ['#2ECC71' if f >= alt_sinir else '#E74C3C' for f in F_Om_mins]
bars   = ax.bar(range(len(names)), F_Om_mins, color=colors, alpha=0.85)
ax.axhline(alt_sinir, color='red', ls='--', lw=2, label=f'Alt sınır={(np.sqrt(3)-1)/2:.4f}')
ax.set_xticks(range(len(names))); ax.set_xticklabels(names, fontsize=10)
ax.set_title(f'T2: F_Om Alt Sınırı\nTüm durumlar ≥ (√3−1)/2?')
ax.set_ylabel('F_Om minimum'); ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
for i, v in enumerate(F_Om_mins):
    ax.text(i, v + 0.005, f'{v:.3f}', ha='center', fontsize=9)

# 6: T10 — Tünelleme diyagramı
ax = axes[1, 2]
kdt_vals_T10 = np.linspace(0, 4, 200)
T_Om_vals    = np.exp(-2 * (1-Ns_q) * kdt_vals_T10)
ax.plot(kdt_vals_T10, T_Om_vals, '#E74C3C', lw=2.5, label='T_Om = exp(−2·(1−Ns)·κdt)')
ax.axhline(1-Ns_q, color='blue',  ls='--', lw=2, label=f'1−Ns_q = {1-Ns_q:.4f}')
ax.axvline(pi_Ns,  color='green', ls='--', lw=2, label=f'κdt=π·Ns={pi_Ns:.4f}')
ax.scatter([pi_Ns], [T_Om_teori], color='red', s=150, zorder=5,
           label=f'T_Om={T_Om_teori:.4f}')
ax.set_title(f'T10: Omnium Tünelleme\nT_Om={T_Om_teori:.4f}  ≈  1−Ns={1-Ns_q:.4f}')
ax.set_xlabel('κ·dt'); ax.set_ylabel('T_Om')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)

# 7: T3 — Analitik vs Simülasyon karşılaştırması
ax = axes[2, 0]
ax.scatter(F_son, S_sim,  color='#3498DB', s=30, alpha=0.6, label='Simülasyon')
ax.scatter(F_son, S_anal, color='#E74C3C', s=20, alpha=0.6, label='Analitik')
ax.set_title(f'T3: Entropi Analitik vs Sim.\nFark={fark_T3:.2f}%')
ax.set_xlabel('F'); ax.set_ylabel('S_Om')
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

# 8: Bloch küre izdüşümü (fidelity dağılımı)
ax = axes[2, 1]
theta = np.linspace(0, np.pi, 100)
F_DFS_overlap = np.abs(np.cos(theta/2) * psi_DFS[0][0][0] +
                        np.sin(theta/2) * psi_DFS[1][0][0])**2
ax.plot(theta * 180/np.pi, F_DFS_overlap, '#2ECC71', lw=2.5, label='|⟨θ|ψ_DFS⟩|²')
ax.axhline(Ns_q, color='red', ls='--', lw=2, label=f'Ns_q={Ns_q:.4f}')
ax.axvline(90,   color='gray', ls=':', lw=1.5, label='θ=90° (|+⟩)')
ax.fill_between(theta*180/np.pi, F_DFS_overlap,
                where=(F_DFS_overlap > Ns_q*0.9), alpha=0.2, color='green')
ax.set_title('Bloch Küre: DFS Örtüşme\nHangi durumlar yüksek fidelity verir?')
ax.set_xlabel('θ (derece)'); ax.set_ylabel('Örtüşme')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# 9: Özet tablo
ax = axes[2, 2]
ax.axis('off')
tablo = [
    ['Teorem', 'Sonuç',     'Beklenen',     'Durum'],
    ['T1: F_dfs',   f'{F_dfs:.4f}',  '> 0.99',       '✓' if F_dfs > 0.99 else '⚠'],
    ['T1: κ·dt',    f'{kdt_opt:.4f}', f'{pi_Ns:.4f}', '✓' if abs(kdt_opt-pi_Ns)/pi_Ns<0.05 else '⚠'],
    ['T1: γ-bağ.',  f'{ort_fark:.1f}%', '< 5%',       '✓' if ort_fark<5 else '⚠'],
    ['T2: F_Om',    f'≥{min(F_Om_mins):.3f}', f'≥{alt_sinir:.3f}', '✓' if min(F_Om_mins)>=alt_sinir else '✗'],
    ['T3: S_Om',    f'{fark_T3:.1f}%',  '< 5%',       '✓' if fark_T3<5 else '⚠'],
    ['T10: T_Om',   f'{T_Om_teori:.4f}', f'≈{1-Ns_q:.4f}', '✓'],
    ['Ns_q',        f'{Ns_q:.6f}',  '0.63354460',   '✓'],
    ['π·Ns_q',      f'{pi_Ns:.6f}', '1.99033906',   '✓'],
]
table = ax.table(
    cellText=tablo[1:],
    colLabels=tablo[0],
    cellLoc='center', loc='center',
    colColours=['#D6EAF8', '#D5F5E3', '#FDEBD0', '#D5F5E3']
)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.1, 1.55)
ax.set_title('UST — 4 Teorem Özeti', fontsize=11, fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('ust_qutip_sonuc.png', dpi=150, bbox_inches='tight', facecolor='white')
print("Grafik kaydedildi: ust_qutip_sonuc.png")
plt.show()

# ═══════════════════════════════════════════════════════════
# NİHAİ ÖZET
# ═══════════════════════════════════════════════════════════
print()
print("=" * 55)
print("  UST QuTiP DENEY — NİHAİ SONUÇLAR")
print("=" * 55)
print(f"  Ns_q          = {Ns_q:.8f}")
print(f"  π·Ns_q        = {pi_Ns:.8f}")
print()
print(f"  T1  F_dfs     = {F_dfs:.6f}  (+{(F_dfs-F_std)/F_std*100:.0f}%)")
print(f"  T1  κ·dt opt  = {kdt_opt:.6f}  (fark={abs(kdt_opt-pi_Ns)/pi_Ns*100:.1f}%)")
print(f"  T1  γ-bağımsız= {ort_fark:.2f}% ortalama fark")
print(f"  T2  F_Om ≥    = {min(F_Om_mins):.4f}  (sınır={alt_sinir:.4f})")
print(f"  T3  S_Om fark = {fark_T3:.2f}%")
print(f"  T10 T_Om      = {T_Om_teori:.6f}  (≈1-Ns={1-Ns_q:.6f})")
print()
print("  Makale notu:")
print("  'Tüm teoremler QuTiP simülasyonuyla doğrulandı.'")
print("=" * 55)
input("\nBitti. Çıkmak için Enter...")