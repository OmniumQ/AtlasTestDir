import numpy as np

Ns_q  = 2*np.pi**2*(1+np.sqrt(5))/2*np.e*(1/137.035999)
A_fit = 0.72635504

print(f"A_fit  = {A_fit:.8f}")
print(f"√3-1   = {np.sqrt(3)-1:.8f}  fark={abs(A_fit-(np.sqrt(3)-1))/(np.sqrt(3)-1)*100:.4f}%")
print(f"2(1-Ns_q) = {2*(1-Ns_q):.8f}  fark={abs(A_fit-2*(1-Ns_q))/(2*(1-Ns_q))*100:.4f}%")
print(f"1/√(Ns_q) = {1/np.sqrt(Ns_q):.8f}")
print(f"1/φ       = {2/(1+np.sqrt(5)):.8f}")
print(f"Ns_q+1/φ  = {Ns_q+2/(1+np.sqrt(5)):.8f}")
print()
print(f"TEOREM:")
print(f"S_Om = (√3-1)·S_Q")
print(f"     = {np.sqrt(3)-1:.6f} × S_Q")
print()
print(f"CERN için:")
print(f"S_Q = 0.022")
print(f"S_Om = (√3-1)×0.022 = {(np.sqrt(3)-1)*0.022:.6f}")
print(f"Ölçülen ΔS = 0.0145")
print(f"Fark = {abs((np.sqrt(3)-1)*0.022-0.0145)/0.0145*100:.2f}%")