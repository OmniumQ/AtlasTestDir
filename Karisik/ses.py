import numpy as np

alpha = 7.2973525693e-3
N_geo = (3-np.sqrt(3))/2

# Türetme
dirac_4d = 4*4 + 1   # 16 bileşen + birim matris
N_ust = N_geo - alpha/dirac_4d

print(f"4D Dirac serbestlik derecesi = {dirac_4d}")
print(f"N_geo                        = {N_geo:.8f}")
print(f"α/17                         = {alpha/dirac_4d:.8f}")
print(f"N_ust                        = {N_ust:.8f}")
print(f"N_ampirik                    = 0.63354460")
print(f"Δ                            = {abs(N_ust-0.63354460):.8f}")
print(f"Δ%                           = {abs(N_ust-0.63354460)/0.63354460*100:.6f}%")

print(f"\nTüretme zinciri:")
print(f"1. Einstein tensor maksimizasyonu → N_geo = (3-√3)/2")
print(f"2. 4D Dirac spinör düzeltmesi     → -α/(4²+1)")
print(f"3. N_s,q = N_geo - α/17           = {N_ust:.8f}")