import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

# =========================================
# GPU BACKEND
# =========================================
try:
    backend = AerSimulator(method='statevector', device='GPU')
    # test
    test_qc = QuantumCircuit(2)
    test_qc.h(0)
    test_qc.measure_all()
    backend.run(transpile(test_qc, backend), shots=10).result()
    print("✅ GPU backend aktif (cuStateVec)")
except Exception as e:
    print(f"⚠️  GPU kullanılamıyor: {e}")
    print("→ CPU statevector'a geçiliyor")
    backend = AerSimulator(method='statevector', device='CPU')

# =========================================
# PARAMETRELER
# =========================================
NS = 0.6335
SHOTS = 8192
REPEATS = 20
SEED = 42
np.random.seed(SEED)

N_QUBITS = 5
phase_estimates = np.array([0.09, 0.14, -0.11, 0.06, -0.08], dtype=float)
DIFFICULTY = 10.0

NOISE_LEVELS = [0.005, 0.01, 0.03, 0.05, 0.08, 0.12, 0.18, 0.25]
KAPPA_MIN, KAPPA_MAX, KAPPA_STEPS = 0.05, 3.0, 200

# =========================================
# DEVRE
# =========================================
def build_ghz(qc, n):
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)

def build_inverse_ghz(qc, n):
    for i in reversed(range(n - 1)):
        qc.cx(i, i + 1)
    qc.h(0)

def make_circuit(kappa, true_phases, noisy_estimates):
    qc = QuantumCircuit(N_QUBITS, N_QUBITS)
    build_ghz(qc, N_QUBITS)
    for q, p in enumerate(true_phases):
        qc.rz(p * DIFFICULTY, q)
    for q, p_hat in enumerate(noisy_estimates):
        qc.rz(-(p_hat / kappa) * DIFFICULTY, q)
    build_inverse_ghz(qc, N_QUBITS)
    qc.measure(range(N_QUBITS), range(N_QUBITS))
    return qc

# =========================================
# DOĞRU LS
# =========================================
def kappa_ls(phi_true, phi_hat):
    num = np.dot(phi_true, phi_hat)
    den = np.dot(phi_hat, phi_hat)
    if abs(num) < 1e-12:
        return np.inf
    return den / num

# =========================================
# GHZ BRANCH
# =========================================
def kappa_branches(phi_true, phi_hat, difficulty, m_values=range(-4, 5)):
    s_true = np.sum(phi_true)
    s_hat  = np.sum(phi_hat)
    out = []
    for m in m_values:
        denom = s_true - (2 * np.pi * m / difficulty)
        if abs(denom) > 1e-12:
            k = s_hat / denom
            if k > 0:
                out.append((m, k))
    return out

# =========================================
# TEK NOISE ANALİZİ — TÜM DEVRELERİ TOPLU GÖNDER
# =========================================
def analyze_noise(noise_std):
    rng = np.random.default_rng(SEED + int(noise_std * 10000))
    kappas = np.linspace(KAPPA_MIN, KAPPA_MAX, KAPPA_STEPS)
    phi_true = phase_estimates / NS

    all_estimates = [
        phase_estimates + rng.normal(0, noise_std, size=len(phase_estimates))
        for _ in range(REPEATS)
    ]

    # 🔥 Tüm devreleri tek seferde toplu gönder
    circuits, labels = [], []
    for k in kappas:
        for r, est in enumerate(all_estimates):
            circuits.append(make_circuit(k, phi_true, est))
            labels.append((k, r))

    tqcs = transpile(
        circuits, backend=backend,
        optimization_level=1,
        seed_transpiler=SEED
    )

    job = backend.run(tqcs, shots=SHOTS, seed_simulator=SEED)
    result = job.result()

    zero = "0" * N_QUBITS
    per_kappa = {float(k): [] for k in kappas}

    for i, (k, r) in enumerate(labels):
        counts = result.get_counts(i)
        p0 = counts.get(zero, 0) / SHOTS
        per_kappa[float(k)].append(p0)

    # GHZ optimum
    summary = [(k, np.mean(v)) for k, v in per_kappa.items()]
    kappa_star = max(summary, key=lambda x: x[1])[0]
    p0_max     = max(summary, key=lambda x: x[1])[1]

    # Residual norm optimum (klasik, hızlı)
    residuals = []
    for k in kappas:
        vals = [np.linalg.norm(phi_true - est / k) for est in all_estimates]
        residuals.append((k, np.mean(vals)))
    kappa_res = min(residuals, key=lambda x: x[1])[0]

    # LS prediction
    kappa_ls_mean = float(np.mean([kappa_ls(phi_true, est) for est in all_estimates]))

    # Branch prediction
    branch_vals = []
    for est in all_estimates:
        br = kappa_branches(phi_true, est, DIFFICULTY)
        if br:
            branch_vals.append(br[0][1])
    kappa_branch = float(np.mean(branch_vals)) if branch_vals else np.nan

    return {
        "noise"       : noise_std,
        "kappa_star"  : kappa_star,
        "kappa_res"   : kappa_res,
        "kappa_ls"    : kappa_ls_mean,
        "kappa_branch": kappa_branch,
        "p0"          : p0_max,
        "summary"     : summary,
    }

# =========================================
# ANA TEST
# =========================================
def run_full_test():
    print(f"\n{'noise':>8} | {'κ_GHZ':>7} | {'κ_res':>7} | "
          f"{'κ_LS':>7} | {'κ_branch':>9} | {'P0':>6}")
    print("-" * 70)

    results = []
    for n in NOISE_LEVELS:
        r = analyze_noise(n)
        results.append(r)
        print(f"{r['noise']:>8.4f} | {r['kappa_star']:>7.3f} | {r['kappa_res']:>7.3f} | "
              f"{r['kappa_ls']:>7.3f} | {r['kappa_branch']:>9.3f} | {r['p0']:>6.3f}")

    return results

# =========================================
# YORUM
# =========================================
def interpret(results):
    print("\n=== FİZİKSEL YORUM ===")

    diffs_res = [abs(r["kappa_res"] - NS) for r in results]
    diffs_ls  = [abs(r["kappa_ls"]  - NS) for r in results]
    mean_res  = np.mean(diffs_res)
    mean_ls   = np.mean(diffs_ls)

    print(f"κ_res  vs Ns → ort fark: {mean_res:.4f}")
    print(f"κ_LS   vs Ns → ort fark: {mean_ls:.4f}")

    print("\nNoise bazlı GHZ vs Residual farkı:")
    for r in results:
        delta = abs(r["kappa_star"] - r["kappa_res"])
        flag  = "⚠️ branch sapması" if delta > 0.15 else "✅ tutarlı"
        print(f"  noise={r['noise']:.3f} → Δ(GHZ-res)={delta:.3f}  {flag}")

    print("\n--- KARAR ---")
    if mean_res < 0.05:
        print("✅ GÜÇLÜ: κ_res ≈ Ns → UST fiziksel optimum")
        print("   GHZ sapması branch artefaktı, teori sağlam")
    elif mean_res < 0.12:
        print("⚠️  ORTA: Trend var ama sapma büyük, model revize edilmeli")
    else:
        print("❌ KANIT YOK: Ns fiziksel optimum değil")

# =========================================
# PLOT
# =========================================
def plot(results):
    noise  = [r["noise"]        for r in results]
    ghz    = [r["kappa_star"]   for r in results]
    res    = [r["kappa_res"]    for r in results]
    ls     = [r["kappa_ls"]     for r in results]
    branch = [r["kappa_branch"] for r in results]

    fig, axs = plt.subplots(2, 1, figsize=(10, 10))

    axs[0].plot(noise, ghz,    'o-',  label='κ_GHZ (ölçüm)')
    axs[0].plot(noise, res,    's-',  label='κ_res (fiziksel)')
    axs[0].plot(noise, ls,     '^-',  label='κ_LS (matematiksel)')
    axs[0].plot(noise, branch, 'D--', label='κ_branch (GHZ dal)')
    axs[0].axhline(NS, linestyle='--', color='red', lw=2, label=f'Ns={NS}')
    axs[0].set_ylabel("Kappa")
    axs[0].set_title("Gerçek Fizik Testi: 4 Farklı κ Tanımı")
    axs[0].legend(fontsize=9)
    axs[0].grid(alpha=0.3)

    axs[1].plot(noise, [abs(r-NS) for r in res],  's-', label='|κ_res - Ns|')
    axs[1].plot(noise, [abs(r-NS) for r in ls],   '^-', label='|κ_LS  - Ns|')
    axs[1].axhline(0.05, linestyle='--', color='green',  label='eşik 0.05')
    axs[1].axhline(0.02, linestyle='--', color='blue',   label='eşik 0.02')
    axs[1].set_ylabel("|κ - Ns|")
    axs[1].set_xlabel("Noise Std")
    axs[1].set_title("Ns'den Sapma")
    axs[1].legend(fontsize=9)
    axs[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("ust_gercek_fizik.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Grafik kaydedildi: ust_gercek_fizik.png")

# =========================================
# MAIN
# =========================================
if __name__ == "__main__":
    print("🔥 GERÇEK FİZİK TESTİ (GPU) 🔥")
    print(f"Ns={NS} | Shots={SHOTS} | Repeats={REPEATS}")
    print(f"Toplam devre ≈ {len(NOISE_LEVELS)*KAPPA_STEPS*REPEATS:,}")

    results = run_full_test()
    interpret(results)
    plot(results)