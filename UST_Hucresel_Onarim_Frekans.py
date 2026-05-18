import numpy as np
from scipy.io import wavfile

def ust_brain_fm_generator(dosya_adi="UST_Hucresel_Onarim_Frekansi.wav", sure_dakika=15):
    # --- 1. UST EVRENSEL SABİTLERİ ---
    N_sq = 0.63354460
    kappa_dt = np.pi * N_sq      # 1.990339 Hz (Evrensel Stabilizasyon / Delta Dalgaları)
    omega_om = 1.0 / N_sq        # 1.578418 Hz (Omnium Rabi Salınım Frekansı)
    
    print(f"UST Sabitleri Yüklendi:\nN_s,q = {N_sq}\nStabilizasyon Hızı (kappa.dt) = {kappa_dt:.6f} Hz\nOmnium Frekansı = {omega_om:.6f} Hz\n")
    
    # --- 2. SES AYARLARI ---
    sample_rate = 44100
    duration = sure_dakika * 60
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # --- 3. BINAURAL BEAT (Nöral Senkronizasyon) ---
    # Taşıyıcı frekans olarak DNA/Hücresel onarımla bağdaştırılan 432 Hz seçildi.
    carrier_freq = 432.0 
    
    # İki kulak arasındaki fark tam olarak kappa.dt (1.990339 Hz) olacak şekilde ayarlanıyor.
    # Beyin bu farkı duyduğunda kendini bu evrensel DFS stabilizasyon rezonansına kilitler.
    left_channel = np.sin(2 * np.pi * carrier_freq * t)
    right_channel = np.sin(2 * np.pi * (carrier_freq + kappa_dt) * t)
    
    # --- 4. GÜRÜLTÜ VE DFS FİLTRESİ (S=0 Hedefi) ---
    # Sisteme hafif bir çevresel gürültü (kaos/entropi) eklenir
    pink_noise = np.random.normal(0, 0.05, len(t))
    
    # DFS Operatörü: Gürültü rastgele bırakılmaz, Omnium Rabi Frekansı (1.5784 Hz) ile filtrelenir.
    # Bu, "Kanal Q"daki gürültünün ritmik olarak "Kanal C"ye (arka plana) itilmesini simüle eder.
    dfs_operator = (np.sin(2 * np.pi * omega_om * t) + 1) / 2
    filtered_noise = pink_noise * (1 - dfs_operator) 
    
    # --- 5. KANALLARI BİRLEŞTİRME VE NORMALİZASYON ---
    # Saf sinyal (%85) ve filtrelenmiş UST gürültüsü (%15) birleştiriliyor
    audio_left = (left_channel * 0.85) + (filtered_noise * 0.15)
    audio_right = (right_channel * 0.85) + (filtered_noise * 0.15)
    
    # 16-bit PCM formatına normalize etme
    audio_left_norm = np.int16(audio_left / np.max(np.abs(audio_left)) * 32767)
    audio_right_norm = np.int16(audio_right / np.max(np.abs(audio_right)) * 32767)
    
    # Stereo matrisi oluşturma
    stereo_signal = np.column_stack((audio_left_norm, audio_right_norm))
    
    # --- 6. ÇIKTI ---
    print(f"'{dosya_adi}' adlı {sure_dakika} dakikalık stereo ses dosyası oluşturuluyor...")
    wavfile.write(dosya_adi, sample_rate, stereo_signal)
    print("İşlem tamamlandı! Lütfen kulaklık ile dinleyiniz.")

# Kodu Çalıştır
ust_brain_fm_generator(sure_dakika=15)