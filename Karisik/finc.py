import pandas as pd
import numpy as np

# Standart ANSI Renk Kodları
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
LIGHT_RED = '\033[1;31m'
GRAY = '\033[90m'
RESET = '\033[0m'

def calculate_full_raw_analysis(file_list):
    print("Sistem Başlatıldı: Dosyalar okunuyor...")
    try:
        dataframes = []
        for f in file_list:
            df_temp = pd.read_excel(f)
            df_temp.columns = df_temp.columns.str.strip()
            dataframes.append(df_temp)
            print(f"Okundu: {f.split('\\')[-1]}")
            
        df = dataframes[0]
        for i in range(1, len(dataframes)):
            df = pd.merge(df, dataframes[i], on='Şirket', how='outer')
    except Exception as e:
        print(f"HATA: Dosya okuma veya birleştirme başarısız: {e}")
        return

    results = []
    ALPHA = 1 / 137

    for index, row in df.iterrows():
        try:
            def to_float(val):
                if pd.isna(val) or val == '': return 0.0
                try: return float(val)
                except: return 0.0

            # --- ÇIPLAK VERİLER ---
            sirket = str(row.get('Şirket', 'Bilinmiyor'))
            pddd = to_float(row.get('PD/DD', 1))
            fk = to_float(row.get('F/K', 0))
            net_marj = to_float(row.get('Net Kar Marjı', 0))
            borc_favok = to_float(row.get('Net Borç/FAVÖK', 0))
            hacim = to_float(row.get('Hacim', 1))
            
            # Fibonacci Büyüme
            growth = [
                to_float(row.get('Satışlar Dğş %', 0)),
                to_float(row.get('Brüt Kar Dğş %', 0)),
                to_float(row.get('FAVÖK Dğş %', 0)),
                to_float(row.get('Net Kar Dğş %', 0))
            ]
            w = [1, 2, 3, 5]
            weighted_growth = sum(wi * gi for wi, gi in zip(w, growth)) / sum(w)

            # Skor (Hiçbir sınırlama yok)
            fk_factor = np.log(fk + 2) if fk > 0 else 15
            quality_score = (net_marj / fk_factor) + (ALPHA * np.log10(hacim + 1))
            final_score = quality_score * (weighted_growth / 100)

            # --- ANALİTİK RENK KATEGORİLERİ ---
            color = RESET
            label = "BELİRSİZ"

            if pddd > 15 or abs(net_marj) > 10000 or borc_favok > 20:
                color = LIGHT_RED
                label = "UZAK DUR (KRİTİK)"
            elif pddd > 8 or net_marj < 0 or fk > 100:
                color = RED
                label = "SORUNLU / PAHALI"
            elif 4 < pddd <= 8 or 3 < borc_favok <= 6:
                color = YELLOW
                label = "RİSKLİ"
            elif 0 < pddd <= 4 and net_marj > 0 and 0 < fk < 30:
                color = GREEN
                label = "RASYONEL"
            else:
                color = GRAY
                label = "GRİ ALAN"

            results.append({
                'text': f"{color}{sirket:<10} {final_score:<15.2f} {label:<20} {net_marj:<12.2f} {weighted_growth:<12.2f} {fk:<10.2f} {pddd:<10.2f}{RESET}",
                'score': final_score
            })
        except Exception as e:
            continue

    # Skora göre sırala
    results.sort(key=lambda x: x['score'], reverse=True)

    # Başlık
    print("\n" + "="*90)
    print(f"{'Şirket':<10} {'UST_SKOR':<15} {'DURUM':<20} {'MARJ_%':<12} {'BÜYÜME_%':<12} {'FK':<10} {'PD_DD':<10}")
    print("="*90)

    for r in results:
        print(r['text'])

# Dosya yolları (Listeyi kontrol et!)
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

calculate_full_raw_analysis(file_paths)
