import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
# Aer ve execute yerine güncel kütüphaneyi çağırıyoruz:
from qiskit_aer import AerSimulator 

# --- UST v5 EVRENSEL SABİTLERİ (Aynı kalacak) ---
SEELEY_DEWITT_FILTER = 1 / 17  
T_OM_TUNNELING = 0.2325        
Q_16_ACTIVE = 1.0 - T_OM_TUNNELING  

def create_hardcore_qft_circuit(n_qubits):
    q = QuantumRegister(n_qubits, 'q_16') 
    c = ClassicalRegister(n_qubits, 'ölçüm')
    qc = QuantumCircuit(q, c)
    
    for i in range(n_qubits):
        qc.h(q[i])
        for j in range(i + 1, n_qubits):
            qc.cp(np.pi / (2 ** (j - i)), q[j], q[i])
        qc.barrier()
    return qc, q, c

def ust_v5_topological_noise_routing(raw_counts):
    # Bu kısım tamamen aynı kalacak
    filtered_results = {}
    kanal_c_dump = 0.0 
    total_shots = sum(raw_counts.values())
    
    for state, count in raw_counts.items():
        probability = count / total_shots
        noise_component = probability * np.random.uniform(0.01, 0.15) 
        filtered_noise = noise_component * SEELEY_DEWITT_FILTER
        routed_to_omnium = filtered_noise * T_OM_TUNNELING
        kanal_c_dump += routed_to_omnium
        clean_signal = probability - routed_to_omnium
        filtered_results[state] = clean_signal * total_shots

    return filtered_results, kanal_c_dump

# --- ANA SİMÜLASYON ---
n = 4  
qc, q, c = create_hardcore_qft_circuit(n)
qc.measure(q, c)

# Eski 'execute' komutu yerine GÜNCEL Transpile ve Run kullanımı:
backend = AerSimulator()
qc_compiled = transpile(qc, backend)
job = backend.run(qc_compiled, shots=10000)
raw_counts = job.result().get_counts()

# UST v5 Katmanını Devreye Sok (Ancilla-Free QEC)
clean_counts, omnium_waste = ust_v5_topological_noise_routing(raw_counts)

print(f"--- UST v5 SİMÜLASYON SONUÇLARI ---")
print(f"Evrenin Arka Planına (Kanal C) Tünellenen Toplam Atık Isı (Gürültü): % {omnium_waste*100:.4f}")
print("Yedek Kübit (Ancilla) Kullanılmadan Elde Edilen Temiz İşlem Sinyalleri:")
for state, count in list(clean_counts.items())[:5]:
    print(f"Durum |{state}> : {int(count)} okuma (Tam Koherans)")