import pandas as pd
import numpy as np

# ANSI Renk Kodları
G = '\033[92m'  # Yeşil (Güvenli Alım)
Y = '\033[93m'  # Sarı (Riskli/Tut)
R = '\033[91m'  # Kırmızı (Sat/Zarar)
LR = '\033[1;31m' # Açık Kırmızı (Kritik/Uzak Dur)
RESET = '\033[0m'

def calculate_trading_signals(file_list):
    print("Analiz başlatılıyor...")
    try:
        # Dosyaları tek tek oku
        dataframes = []
        for f in file_list:
            temp_df = pd.read_excel(f)
            temp_df.columns = temp_df.columns.str.strip()
            dataframes.append(temp_df)
        
        # Hatalı olan 'df = dataframes' yerine doğru birleştirme:
        df_final = dataframes[0]
        for i in range(1, len(dataframes)):
            df_final = pd.merge(df_final, dataframes[i], on='Şirket', how='outer')
            
    except Exception as e:
        print(f"HATA: Veriler birleştirilemedi: {e}")
        return

    results = []

    for _, row in df_final.iterrows():
        try:
            def to_f(col):
                val = row.get(col, 0)
                try: return float(val) if pd.notnull(val) else 0.0
                except: return 0.0

            sirket = str(row.get('Şirket', 'N/A'))
            fiyat = to_f('Fiyat')
            pddd = to_f('PD/DD')
            fk = to_f('F/K')
            net_marj = to_f('Net Kar Marjı')
            borc_favok = to_f('Net Borç/FAVÖK')

            if fiyat <= 0: continue

            # --- ANALİTİK KARAR MEKANİZMASI ---
            stop_loss = fiyat * 0.95    # %5 Standart Stop
            take_profit = fiyat * 1.15  # %15 Hedef
            color = RESET
            tavsiye = "İZLE"

            # KURAL 1: GÜVENLİ RASYONEL ALIM (Yeşil)
            if 0 < pddd < 2.5 and 0 < fk < 15 and net_marj > 10:
                color = G
                tavsiye = "GÜVENLİ AL"
            
            # KURAL 2: RİSKLİ / BEKLE (Sarı)
            elif 2.5 <= pddd < 6 or 15 <= fk < 35:
                color = Y
                tavsiye = "RİSKLİ / TUT"
                stop_loss = fiyat * 0.97 # Sıkı Stop
            
            # KURAL 3: SAT / UZAK DUR (Kırmızı)
            elif pddd >= 6 or fk >= 35 or net_marj <= 0 or borc_favok > 6:
                color = R
                tavsiye = "SAT / ZARAR"
                stop_loss = fiyat # Anında Çıkış
            
            # KURAL 4: KRİTİK VERİ ANOMALİSİ (Açık Kırmızı)
            if pddd > 15 or abs(net_marj) > 10000:
                color = LR
                tavsiye = "KRİTİK / KAÇ"

            results.append({
                'line': f"{color}{sirket:<10} {fiyat:<10.2f} {tavsiye:<15} {stop_loss:<12.2f} {take_profit:<10.2f} {pddd:<8.2f} {fk:<8.2f}{RESET}",
                'pddd': pddd
            })
        except:
            continue

    # Başlık Yazdır
    print(f"\n{'Şirket':<10} {'Fiyat':<10} {'Tavsiye':<15} {'Stop-Loss':<12} {'Hedef':<10} {'PD/DD':<8} {'FK':<8}")
    print("-" * 85)
    
    # PD/DD oranına göre sıralayarak listele
    results.sort(key=lambda x: x['pddd'])
    for r in results:
        print(r['line'])

# Dosya yolları
file_paths = [
    r"C:\Users\info\Downloads\fintables_hisse_senetleri.xlsx",
    r"C:\Users\info\Downloads\fintables_hisse_senetleri (1).xlsx",
    r"C:\Users\info\Downloads\fintables_hisse_senetleri (2).xlsx",
    r"C:\Users\info\Downloads\fintables_hisse_senetleri (3).xlsx",
    r"C:\Users\info\Downloads\fintables_hisse_senetleri (4).xlsx",
    r"C:\Users\info\Downloads\fintables_hisse_senetleri (5).xlsx",
    r"C:\Users\info\Downloads\fintables_hisse_senetleri (6).xlsx",
    r"C:\Users\info\Downloads\fintables_hisse_senetleri (7).xlsx"
]

calculate_trading_signals(file_paths)
