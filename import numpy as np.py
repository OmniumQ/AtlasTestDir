import numpy as np

psi = np.array([
    -0.27122+0.15332j, -0.02673-0.14806j, 0.03741+0.10883j, -0.01801+0.10074j,
    -0.22693-0.11653j, 0.03803+0.02042j, -0.13123+0.07262j, -0.04737-0.02123j,
    -0.00420+0.00629j, -0.08941-0.10106j, 0.12982+0.04848j, 0.15829-0.14142j,
    -0.12374-0.00771j, 0.04970-0.10152j, -0.01998-0.10731j, -0.03910+0.04677j,
    0.23958-0.15001j, 0.30364-0.12971j, 0.17418-0.00827j, 0.09520-0.10484j,
    -0.13265-0.01680j, 0.04237+0.10114j, 0.04694-0.12423j, 0.18530-0.10880j,
    0.07770-0.05834j, 0.05755-0.20962j, -0.05825-0.02281j, -0.18049+0.06493j,
    0.13292-0.07069j, 0.17982-0.18905j, 0.31937-0.10199j, 0.06652+0.00930j
])

probs = np.abs(psi)**2
total = np.sum(probs)

print(f"Total: {total:.6f}\n")
print("="*70)
print("UST FINAL TEST - MULTI-SCALE + ERROR CORRECTION")
print("="*70)

# ATLAS-LIGO correlation
atlas_ligo = sum(probs[i] for i in range(32) if ((i>>2)&1) == ((i>>3)&1))
print(f"\nATLAS-LIGO (q[2]=q[3]): {atlas_ligo:.4f} ({atlas_ligo*100:.1f}%)")
if atlas_ligo > 0.60:
    print("✅✅ STRONG")
    s1 = 30
elif atlas_ligo > 0.55:
    print("✅ MODERATE")
    s1 = 15
else:
    print("❌ WEAK")
    s1 = 0

# Micro-Macro
micro_macro = sum(probs[i] for i in range(32) if (i&1) == ((i>>4)&1))
print(f"\nMicro-Macro (q[0]=q[4]): {micro_macro:.4f} ({micro_macro*100:.1f}%)")
if micro_macro > 0.60:
    print("✅ EMERGENCE")
    s1 += 20
elif micro_macro > 0.55:
    print("⚠️ WEAK")
    s1 += 10

# Error correction
p0 = probs[0]
print(f"\n|00000⟩: {p0:.6f} ({p0*100:.2f}%)")
if p0 > 0.10:
    s2 = 25
elif p0 > 0.05:
    s2 = 10
else:
    s2 = 0

# Parity
even = sum(probs[i] for i in range(32) if bin(i).count('1')%2==0)
odd = sum(probs[i] for i in range(32) if bin(i).count('1')%2==1)
ratio = even/odd if odd>0 else 999
print(f"\nEven/Odd: {ratio:.2f}")

# 17-fold
p17 = probs[17] if 17<32 else 0
sig17 = probs[0] + p17
print(f"\nStates 0+17: {sig17:.4f} ({sig17*100:.1f}%)")
if sig17 > 0.15:
    s3 = 25
elif sig17 > 0.10:
    s3 = 10
else:
    s3 = 0

# p_ust test
p_ust_expected = 0.08521139
# Check if error correction visible
error_corr_signal = p0 / 0.03125  # vs uniform
print(f"\nError correction elevation: {error_corr_signal:.2f}x")

print("\n" + "="*70)
print("TOP 10 STATES")
print("="*70)
idx = np.argsort(probs)[::-1]
for i in range(10):
    j = idx[i]
    print(f"{i+1}. |{format(j,'05b')}⟩: {probs[j]:.6f} ({probs[j]*100:5.2f}%)")

total_score = s1 + s2 + s3
print("\n" + "="*70)
print(f"FINAL SCORE: {total_score}/100")
print("="*70)
print(f"  Cross-scale: {s1}/50")
print(f"  Error corr:  {s2}/25")
print(f"  17-fold:     {s3}/25")
print("="*70)

if total_score >= 75:
    print("\n✅✅✅ STRONG: UST universal!")
elif total_score >= 50:
    print("\n✅ MODERATE: Partial evidence")
elif total_score >= 25:
    print("\n⚠️ WEAK: Limited structure")
else:
    print("\n❌ NO evidence")
print("="*70)