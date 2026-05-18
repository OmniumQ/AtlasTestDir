import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

# Dosya yolu (Kendi sisteminize göre güncelleyin)
dosya_yolu = r"C:\AtlasTest\20250102_20250402_0_9.0_20_187.txt"

# UST (Birleşik Kaynak Teorisi) Sabitleri
N_sq = 0.63354460 # Evrensel Dinamik Denge Sabiti
pi_N_sq = np.pi * N_sq # 1.990339... (Sistem stabilizasyon fazı)

def ust_mekansal_ve_zamansal_tahmin(dosya):
    print("Kandilli verisi okunuyor ve UST Mekansal/Zamansal Modeline uyarlanıyor...\n")
    try:
        # Sütun kaymalarını önleyen güvenli okuma şablonu
        kendi_kolonlarimiz = ['No', 'Deprem_Kodu', 'Tarih', 'Saat', 'Enlem', 'Boylam', 'Derinlik', 'xM', 'MD', 'ML', 'Mw', 'Ms', 'Mb', 'Tip']
        df = pd.read_csv(dosya, sep=r'\s+', skiprows=1, usecols=range(14), names=kendi_kolonlarimiz, on_bad_lines='skip', low_memory=False)
        
        # Zaman hesaplaması
        df['Zaman'] = pd.to_datetime(df['Tarih'] + ' ' + df['Saat'], format='%Y.%m.%d %H:%M:%S.%f', errors='coerce')
        
        # Enlem ve Boylamı güvenli sayısal değerlere (float) dönüştürme
        df['Enlem'] = pd.to_numeric(df['Enlem'], errors='coerce')
        df['Boylam'] = pd.to_numeric(df['Boylam'], errors='coerce')
        
        # Hatalı/Boş verileri temizleyip kronolojik sıraya dizme
        df = df.dropna(subset=['Zaman', 'Enlem', 'Boylam']).sort_values('Zaman').reset_index(drop=True)
        df['dt_saniye'] = df['Zaman'].diff().dt.total_seconds()
        
        # --- ZAMAN TAHMİNİ (S=0 Entropi Sıfırlaması) ---
        ortalama_dt = df['dt_saniye'].mean()
        aktif_ufuk_suresi = ortalama_dt * N_sq
        
        son_deprem = df.iloc[-1]
        son_deprem_zamani = son_deprem['Zaman']
        
        tahmini_zaman_erken = son_deprem_zamani + timedelta(seconds=aktif_ufuk_suresi)
        tahmini_zaman_ana = son_deprem_zamani + timedelta(seconds=ortalama_dt)

        # --- KONUM TAHMİNİ (Non-Markovian Stres Merkezi) ---
        # UST mantığına göre sistem hafızayı (stresi) son olaylar dizisinde biriktirir.
        # Bu yüzden son 15 olayın (kümelenmenin) coğrafi merkezini hedef alıyoruz.
        son_olaylar = df.tail(15)
        hedef_enlem = son_olaylar['Enlem'].mean()
        hedef_boylam = son_olaylar['Boylam'].mean()

        print("--- UST Deterministik Zaman ve Konum Analizi ---")
        print(f"Sistem Faz Sabiti (pi * N_sq)   : {pi_N_sq:.6f}")
        print(f"Sistemdeki Son Kayıtlı Olay     : {son_deprem_zamani} | Enlem: {son_deprem['Enlem']:.4f}, Boylam: {son_deprem['Boylam']:.4f}\n")
        
        print("-> UST ZAMAN TAHMİNİ:")
        print(f"   1. Erken Yankı (N_sq Kırılma Eşiği) : {tahmini_zaman_erken}")
        print(f"   2. Tam Döngü (S=0 Ana Boşalım Anı)  : {tahmini_zaman_ana}\n")
        
        print("-> UST KONUM TAHMİNİ (Aktif Hafıza Birikim Merkezi):")
        print(f"   Tahmini Enlem  : {hedef_enlem:.4f}")
        print(f"   Tahmini Boylam : {hedef_boylam:.4f}\n")

        # --- GÖRSELLEŞTİRME (Coğrafi Dağılım) ---
        plt.figure(figsize=(10, 6))
        
        # Tüm geçmiş depremleri soluk mavi ile çiz (X ekseni Boylam, Y ekseni Enlem)
        plt.scatter(df['Boylam'], df['Enlem'], alpha=0.2, s=10, c='blue', label='Tarihsel Arka Plan (Kanal C İzi)')
        
        # Son 15 depremi turuncu ile belirgin çiz (Aktif stres bölgesi)
        plt.scatter(son_olaylar['Boylam'], son_olaylar['Enlem'], alpha=0.8, s=40, c='orange', label='Son 15 Olay (Aktif Hafıza Kümesi)')
        
        # UST tahmin noktasını dev bir kırmızı X ile işaretle
        plt.scatter([hedef_boylam], [hedef_enlem], color='red', marker='X', s=200, label='Tahmini Boşalım Merkezi (S=0)')
        
        plt.title('UST Modeli: Non-Markovian Stres Birikimi ve Olası Deprem Konumu')
        plt.xlabel('Boylam (Longitude)')
        plt.ylabel('Enlem (Latitude)')
        plt.legend(loc='upper right')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()

    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")

# Fonksiyonu çalıştır
ust_mekansal_ve_zamansal_tahmin(dosya_yolu)