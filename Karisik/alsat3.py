import pandas as pd
import numpy as np
import math

# --- STANDART ANSI RENKLERİ ---
YESIL = '\033[92m'    # GÜVENLİ (RASYONEL)
SARI = '\033[93m'     # RİSKLİ (İZLEME)
KIRMIZI = '\033[91m'  # TEHLİKE (SAT)
A_KIRMIZI = '\033[1;31m' # BALON (HALLUCINATION)
GRI = '\033[90m'      # VERİ YETERSİZ
RESET = '\033[0m'

def calculate_ust_quantum_signals(file_list):
    print(f"{YESIL}Spec(Z) Hiyerarşik Zaman-Mekan Analizi Başlatıldı...{RESET}")
    
    try:
        dataframes = [pd.read_excel(f) for f in file_list]
        for df in dataframes: df.columns = df.columns.str.strip()
        
        main_df = dataframes[0]
        for i in range(1, len(dataframes)):
            main_df = pd.merge(main_df, dataframes[i], on='Şirket', how='outer')
    except Exception as e:
        print(f"HATA: Dosya entegrasyonu başarısız: {e}")
        return

    results = []
    # Sabitler
    ALPHA = 1 / 137
    PHI = (1 + 5**0.5) / 2
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]

    for _, row in main_df.iterrows():
        try:
            def val(col):
                v = row.get(col, 0)
                return float(v) if pd.notnull(v) and isinstance(v, (int, float)) else 0.0

            # 1. TEMEL VERİLER (KNOWLEDGE BASE)
            isim = str(row.get('Şirket', 'Bilinmiyor'))
            fiyat = val('Fiyat')
            pddd = val('PD/DD')
            fk = val('F/K')
            net_marj = val('Net Kar Marjı')
            ozkaynak_kar = val('Özkaynak Karlılığı')
            borc_favok = val('Net Borç/FAVÖK')
            hacim = val('Hacim')

            # 2. TARİHSEL VERİLER (FIBONACCI CURRICULUM)
            getiri_1y = val('Getiri % (Son 1 yıl)')
            getiri_3y = val('Getiri % (Son 3 yıl)')
            getiri_5y = val('Getiri % (Son 5 yıl)')
            
            # Fibonacci ağırlıklı tarihsel momentum hesaplama
            # Uzun vade (5y) daha temel bir "asal" kabul edilir
            momentum_score = (getiri_1y * 1 + getiri_3y * 3 + getiri_5y * 8) / 12

            # 3. p-ADİK TUTARLILIK (ULTRAMETRIC CHECK)
            # Fact A: PD/DD, Fact B: Özkaynak Karlılığı, Fact C: Kar Marjı
            # d(A,C) <= max(d(A,B), d(B,C)) kuralı finansal rasyolara uygulanır
            d_AB = abs(pddd - (ozkaynak_kar / 100))
            d_BC = abs((ozkaynak_kar / 100) - (net_marj / 100))
            d_AC = abs(pddd - (net_marj / 100))
            
            is_consistent = d_AC <= max(d_AB, d_BC)

            # 4. AL-SAT STRATEJİSİ (SPEC-Z Karar Mekanizması)
            ust_score = (net_marj * PHI) / (pddd + 0.1) + (ALPHA * np.log10(hacim + 1))
            
            # Statü ve Renk Belirleme
            color = RESET
            tavsiye = "BEKLE"
            stop_loss = fiyat * (1 - (1/PHI**2)) # %38.2 Stop
            hedef = fiyat * PHI                  # %161.8 Hedef

            # GÜVENLİ ALIM ŞARTI
            if is_consistent and 0 < pddd < 3 and fk < 20 and net_marj > 5:
                color = YESIL
                tavsiye = "GÜVENLİ AL"
            
            # RİSKLİ / BALON ŞARTI
            elif pddd > 10 or not is_consistent:
                color = A_KIRMIZI
                tavsiye = "BALON / UZAK DUR"
                stop_loss = fiyat
            
            # ZARAR EDEN / SORUNLU
            elif net_marj <= 0 or ozkaynak_kar <= 0:
                color = KIRMIZI
                tavsiye = "OPERASYONEL ZARAR"
            
            # BELİRSİZ / RİSKLİ
            elif 3 <= pddd < 7:
                color = SARI
                tavsiye = "RİSKLİ / İZLE"
            
            results.append({
                'line': f"{color}{isim:<10} {fiyat:<8.2f} {tavsiye:<18} {stop_loss:<10.2f} {hedef:<10.2f} {pddd:<8.2f} {fk:<8.2f} {round(momentum_score,1):<10}{RESET}",
                'score': ust_score
            })
        except: continue

    # Başlık ve Çıktı
    print(f"\n{'Şirket':<10} {'Fiyat':<8} {'Tavsiye':<18} {'Stop':<10} {'Hedef':<10} {'PD/DD':<8} {'FK':<8} {'Momentum':<10}")
    print("-" * 100)
    results.sort(key=lambda x: x['score'], reverse=True)
    for r in results: print(r['line'])

# Dosya yolları
file_paths = [fr"C:\Users\info\Downloads\fintables_hisse_senetleri{s}.xlsx" for s in ["", " (1)", " (2)", " (3)", " (4)", " (5)", " (6)", " (7)"]]

calculate_ust_quantum_signals(file_paths)
