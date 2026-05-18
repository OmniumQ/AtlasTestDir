import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity, entropy
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error

# =========================
# Parametreler
# =========================
N_QUBITS = 5
ALPHA_UST = 0.6335
SEED = 42

np.random.seed(SEED)

# Örnek faz hataları (radyan)
TRUE_PHASES = np.array([0.12, -0.08, 0.15, -0.11, 0.07])

# Faz tahmin hatası: gerçek donanımda Ramsey vb. ile gelir
PHASE_EST_STD = 0.02

# Stokastik dephasing gürültüsü
PHASE_DAMP_1Q = 0.01
PHASE_DAMP_2Q = 0.02


# =========================
# Devre kurucular
# =========================
def build_ghz_circuit(n=N_QUBITS):
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    return qc


def add_phase_error(qc, phases):
    """Her kübite coherent faz hatası ekler."""
    for q, phi in enumerate(phases):
        qc.p(phi, q)
    return qc


def add_phase_correction(qc, phase_estimates, alpha):
    """C(phi) = exp(-i * alpha * phi_hat) düzeltmesi."""
    for q, phi_hat in enumerate(phase_estimates):
        qc.p(-alpha * phi_hat, q)
    return qc


# =========================
# Gürültü modeli
# =========================
def build_noise_model():
    noise_model = NoiseModel()

    # 1-kübit dephasing
    err_1q = phase_damping_error(PHASE_DAMP_1Q)

    # 2-kübit için iki tekil dephasing'i tensörlüyoruz
    err_2q = phase_damping_error(PHASE_DAMP_2Q).tensor(
        phase_damping_error(PHASE_DAMP_2Q)
    )

    noise_model.add_all_qubit_quantum_error(err_1q, ["h", "p"])
    noise_model.add_all_qubit_quantum_error(err_2q, ["cx"])

    return noise_model


# =========================
# Simülasyon
# =========================
def simulate_case(alpha, true_phases, phase_est_std, noise_model):
    """
    alpha=0.0      -> düzeltme yok
    alpha=1.0      -> tam düzeltme
    alpha=0.6335   -> UST düzeltme
    """
    qc = build_ghz_circuit()

    # Kontrollü coherent faz hatası ekle
    add_phase_error(qc, true_phases)

    # Faz tahmini (gerçekte bunu Ramsey / calibration çıkarır)
    phase_estimates = true_phases + np.random.normal(
        loc=0.0, scale=phase_est_std, size=len(true_phases)
    )

    # Düzeltme uygula
    add_phase_correction(qc, phase_estimates, alpha)

    # Density matrix kaydet
    qc.save_density_matrix()

    backend = AerSimulator(method="density_matrix", noise_model=noise_model)
    tqc = transpile(qc, backend)

    result = backend.run(tqc).result()
    rho = DensityMatrix(result.data(0)["density_matrix"])

    return rho, phase_estimates


# =========================
# Metrikler
# =========================
def purity(rho: DensityMatrix):
    return float(np.real(np.trace(rho.data @ rho.data)))


def compute_metrics(rho, ideal_dm):
    return {
        "fidelity": float(state_fidelity(rho, ideal_dm)),
        "global_entropy_bits": float(entropy(rho, base=2)),
        "purity": purity(rho),
    }


# =========================
# Ana çalıştırma
# =========================
def main():
    ideal_sv = Statevector.from_instruction(build_ghz_circuit())
    ideal_dm = DensityMatrix(ideal_sv)

    noise_model = build_noise_model()

    cases = {
        "NO_CORRECTION": 0.0,
        "FULL_CORRECTION": 1.0,
        "UST_CORRECTION_0.6335": ALPHA_UST,
    }

    print("\n=== 5-Qubit UST Phase Correction Experiment ===")
    print(f"True phases          : {TRUE_PHASES}")
    print(f"Phase est. std       : {PHASE_EST_STD}")
    print(f"UST alpha            : {ALPHA_UST}")
    print(f"1Q phase damping     : {PHASE_DAMP_1Q}")
    print(f"2Q phase damping     : {PHASE_DAMP_2Q}\n")

    for name, alpha in cases.items():
        rho, phase_estimates = simulate_case(
            alpha=alpha,
            true_phases=TRUE_PHASES,
            phase_est_std=PHASE_EST_STD,
            noise_model=noise_model,
        )

        metrics = compute_metrics(rho, ideal_dm)

        print(f"--- {name} ---")
        print(f"Estimated phases     : {np.round(phase_estimates, 5)}")
        print(f"Fidelity             : {metrics['fidelity']:.6f}")
        print(f"Global entropy (bits): {metrics['global_entropy_bits']:.6f}")
        print(f"Purity               : {metrics['purity']:.6f}")
        print()

    print("Yorum:")
    print("- Fidelity yukarı gidiyorsa düzeltme işe yarıyor.")
    print("- Global entropy 0'a yaklaşıyorsa S=0 hipotezi daha iyi korunuyor.")
    print("- Purity 1'e yaklaşıyorsa sistem daha az karışık hale geliyor.")


if __name__ == "__main__":
    main()