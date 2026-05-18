import pandas as pd
import numpy as np
import math

# --- UST Sabitleri ---
ALPHA = 1 / 137
PHI = (1 + math.sqrt(5)) / 2
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]

# --- Renk Kodları ---
G = '\033[92m'  # Rasyonel Alım (Consistent)
Y = '\033[93m'  # Belirsizlik (Uncertainty)
R = '\033[91m'  # Tutarsızlık (Inconsistent)
LR = '\033[1;31m' # Hallucination (Kritik Tehlike)
RESET = '\033[0m'

def p_adic_norm(value, p):
    """v_p(x) değerlemesi üzerinden p-adik norm hesaplar"""
    if value == 0: return 0
    # Finansal basitleştirme: Değer p'ye ne kadar bölünürse norm o kadar küçülür
    try:
        v_p = math.floor(math.log(abs(value), p)) if abs(value) > 1 else 0
        return p**(-v_p)
    except: return 1

def ultrametric_consistency_check(pd_dd, fk, net_marj):
    """d(A,C) <= max(d(A,B), d(B,C)) prensibiyle finansal tutarlılık kontrolü"""
    # Mesafe tanımları (Normalize edilmiş farklar)
    d_AB = abs(pd_dd - (fk / 10 if fk > 0 else 100))
    d_BC = abs((fk / 10 if fk > 0 else 100) - (net_marj / 10))
    d_AC = abs(pd_dd - (net_marj / 10))
    
    return d_AC <= max(d_AB, d_BC)

def spec_z_engine(file_paths):
    print(f"{G}UST Spec(Z) Quantum Analysis Engine Starting...{RESET}")
    
    try:
        dfs = [pd.read_excel(f) for f in file_paths]
        for df in dfs: df.columns = df.columns.str.strip()
        final_df = dfs[0]
        for next_df in dfs[1:]:
            final_df = pd.merge(final_df, next_df, on='Şirket', how='outer')
    except Exception as e:
        print(f"{R}Hata: Veri birleştirme başarısız: {e}{RESET}")
        return

    results = []

    for _, row in final_df.iterrows():
        try:
            def get_f(col):
                v = row.get(col, 0)
                return float(v) if pd.notnull(v) and isinstance(v, (int, float)) else 0.0

            name = str(row.get('Şirket', 'UNK'))
            price = get_f('Fiyat')
            pddd = get_f('PD/DD')
            fk = get_f('F/K')
            net_m = get_f('Net Kar Marjı')
            hacim = get_f('Hacim')
            borc_f = get_f('Net Borç/FAVÖK')

            if price <= 0: continue

            # 1. p-Adik Certainty (16 Head Asal Kanalı)
            # Her asal sayı farklı bir p-adik bakış açısı sunar
            certainties = [p_adic_norm(net_m if net_m != 0 else 0.01, p) for p in PRIMES]
            max_certainty = max(certainties)

            # 2. Ultrametric Consistency (Hallucination Detection)
            is_consistent = ultrametric_consistency_check(pddd, fk, net_m)
            
            # 3. Fibonacci Weighted Growth (Momentum)
            growth_vals = [get_f('Satışlar Dğş %'), get_f('Brüt Kar Dğş %'), get_f('FAVÖK Dğş %'), get_f('Net Kar Dğş %')]
            fib_steps = [1, 1, 2, 3] # Fibonacci serisi
            momentum = sum(w * g for w, g in zip(fib_steps, growth_vals)) / sum(fib_steps)

            # 4. Optimal Coupling (Loss/Score Function)
            # Score = Knowledge_Score + Alpha * Language_Score (Hacim/Duyarlılık)
            knowledge_score = (net_m * PHI) / (pddd + 1)
            language_score = math.log10(hacim + 1)
            ust_score = knowledge_score + (ALPHA * language_score)

            # --- KARAR MEKANİZMASI ---
            color = RESET
            signal = "GRİ ALAN"
            stop_loss = price * (1 - (1/PHI**2)) # Fibonacci bazlı dinamik stop (%38.2)
            target = price * (1 + (1/PHI))       # Fibonacci bazlı hedef (%61.8)

            if is_consistent and ust_score > 10 and net_m > 0:
                color = G
                signal = "UST GÜVENLİ AL"
            elif not is_consistent:
                if pddd > 10:
                    color = LR
                    signal = "HİERARCHİCAL ERROR (BALON)"
                    stop_loss = price # Anında çıkış
                else:
                    color = R
                    signal = "TUTARSIZ VERİ (SAT)"
            elif max_certainty < 0.5:
                color = Y
                signal = "YÜKSEK BELİRSİZLİK"

            results.append({
                'line': f"{color}{name:<10} {price:<8.2f} {signal:<25} {stop_loss:<10.2f} {target:<10.2f} {ust_score:<10.2f}{RESET}",
                'score': ust_score
            })
        except: continue

    # Çıktı
    print(f"\n{'Şirket':<10} {'Fiyat':<8} {'Sinyal / Durum':<25} {'Stop':<10} {'Hedef':<10} {'UST_Score':<10}")
    print("-" * 95)
    results.sort(key=lambda x: x['score'], reverse=True)
    for r in results: print(r['line'])

# Dosya yollarını Excel (xlsx) olarak tanımla
file_paths = [fr"C:\Users\info\Downloads\fintables_hisse_senetleri{suffix}.xlsx" 
              for suffix in ["", " (1)", " (2)", " (3)", " (4)", " (5)", " (6)", " (7)"]]

spec_z_engine(file_paths)
