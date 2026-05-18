

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
import numpy as np

Ns_q     = 0.63354460
kappa_dt = np.pi * Ns_q   # 1.990339
sim      = AerSimulator()

fid_std, fid_ust = [], []

# 10,000 ATLAS olayına karşılık 500 gürültü seviyesi
noise_levels = np.linspace(0.01, 0.5, 500)

for p in noise_levels:
    # Standart QM
    qc = QuantumCircuit(1)
    qc.rx(p * np.pi, 0)
    qc.save_statevector()
    sv = sim.run(transpile(qc, sim)).result().get_statevector()
    fid_std.append(float(abs(sv[0])**2))

    # UST kilitli
    qc2 = QuantumCircuit(1)
    qc2.rx(p * np.pi, 0)
    qc2.rx(-kappa_dt * p * np.pi, 0)
    qc2.save_statevector()
    sv2 = sim.run(transpile(qc2, sim)).result().get_statevector()
    fid_ust.append(float(abs(sv2[0])**2))

F_std = np.mean(fid_std)
F_ust = np.mean(fid_ust)
print(f"F_std (standart QM)  : {F_std:.4f}  (beklenen ~0.4999)")
print(f"F_ust (UST kilitli)  : {F_ust:.4f}  (beklenen ~0.9913)")
print(f"İyileştirme          : +%{(F_ust/F_std-1)*100:.1f}")
print(f"kappa_dt             : {kappa_dt:.6f}")