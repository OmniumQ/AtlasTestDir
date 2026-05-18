import h5py
import numpy as np
import matplotlib.pyplot as plt

file_path = r"C:\AtlasTest\H-H1_GWOSC_O4a_16KHZ_R1-1368993792-4096.hdf5"
N_SQ = 0.63354460
CHANNEL_C = 1 - N_SQ

try:
    with h5py.File(file_path, 'r') as f:
        strain = np.nan_to_num(f['strain/Strain'][()])
        fs = 16384.0
        
        # 1. Zirve Bölgesine Odaklan (1078.75s - 1079.00s arası)
        start_sec, end_sec = 1078.70, 1079.10
        start_idx, end_idx = int(start_sec * fs), int(end_sec * fs)
        
        zoom_strain = strain[start_idx:end_idx]
        norm_zoom = np.abs(zoom_strain / np.max(np.abs(strain))) # Tüm dosyadaki max'a göre
        time_axis = np.linspace(start_sec, end_sec, len(zoom_strain))

        # 2. Tünelleme Kapılarının Tespiti (Kanal Q'nun Üzeri)
        gate_indices = np.where(norm_zoom > N_SQ)[0]
        
        # 3. GÖRSELLEŞTİRME: KAPILARIN İÇİ
        plt.figure(figsize=(15, 8))
        plt.plot(time_axis, norm_zoom, color='blue', linewidth=1.5, label='Spacetime Flow')
        plt.fill_between(time_axis, N_SQ, norm_zoom, where=(norm_zoom > N_SQ), 
                         color='red', alpha=0.4, label='Tunneling Gates (Open)')
        
        plt.axhline(y=N_SQ, color='red', linestyle='--', label=f'N_sq (0.6335)')
        plt.axhline(y=CHANNEL_C, color='green', linestyle='-.', label=f'Channel C (0.3665)')
        
        plt.title("UST Tünelleme Kapıları: Zaman-Mekan Yırtılma Analizi", fontsize=14)
        plt.xlabel("Hassas Zaman (Saniye)", fontsize=12)
        plt.ylabel("Kanal Enerji Seviyesi", fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.15)

        # 4. KAPASİTE HESABI
        if len(gate_indices) > 0:
            total_open_time = len(gate_indices) / fs
            gate_count = len(np.split(gate_indices, np.where(np.diff(gate_indices) != 1)[0] + 1))
            print(f"\n--- UST KAPASİTE RAPORU ---")
            print(f"Tespit Edilen Tünelleme Kapısı Sayısı: {gate_count}")
            print(f"Toplam Kapı Açık Kalma Süresi: {total_open_time*1000:.2f} milisaniye")
            print(f"Kapı Başına Ortalama Geçiş Penceresi: {(total_open_time/gate_count)*1000:.4f} ms")
            print(f"Tahmini Bilgi Aktarım Kapasitesi (UST): Sonsuz/Senkron")
            print(f"---------------------------")

        plt.show()

except Exception as e:
    print(f"Hata: {e}")
