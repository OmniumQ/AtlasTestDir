import numpy as np
import scipy.io.wavfile as wavfile

print("================================================================")
print("🔬 UST v5: AKUSTİK TOPOLOJİK KALKAN (FARADAY SHIELD) JENERATÖRÜ")
print("================================================================")

# 1. UST v5 Evrensel Sabitleri (Sıfır Serbest Parametre)
N_sq = 0.63354460         # Mühür Katsayısı (Kanal Q)
C_cb = 0.36645540         # Kanal C Bağlantısı
T_Om = 0.23252885         # WKB Tünelleme Eşiği
a_2  = 1/17               # Seeley-DeWitt Spektral Süzgeci
V_b  = 1.195461           # Harmonik Dişli Oranı
p_rad = 0.08521961        # Evrensel Sızıntı Fazı (Radyan)

# 2. Ses Dosyası Parametreleri
DURATION = 1800           # 30 Dakika = 1800 Saniye
RATE = 44100              # Örnekleme hızı (Hz)
t = np.arange(DURATION * RATE) / RATE

# 3. Topolojik Taşıyıcı Frekanslar
f_base = 170.0            # DOF = 17 tabanlı ana taşıyıcı
f_gear = f_base * V_b     # Harmonik vites frekansı (~203.22 Hz)

# 4. Faz Akümülatörü (Süreksizliği / Çıtlamaları Engellemek İçin)
phase_base = 2 * np.pi * f_base * t
phase_gear = 2 * np.pi * f_gear * t

print("[!] Topolojik frekanslar ve evrensel faz kilitleri hesaplanıyor...")

# 5. Sinyal Sentezi ve Faz Mühürleme
# Sol Kanal: Aktif Evren (Q16) Rezonansı
left_signal = (N_sq * np.sin(phase_base)) + (C_cb * np.sin(phase_gear))

# Sağ Kanal: Deterministik Omnium (Kanal C) Tahliyesi (+p faz kayması)
right_signal = (N_sq * np.sin(phase_base + p_rad)) + (C_cb * np.sin(phase_gear - p_rad))

# 6. Pembe Gürültü (Omnium Tabanı / Sıfır-Elemanı Eklentisi)
# Kuantum vakumunu simüle etmek için ortama düşük genlikli taban enerjisi eklenir
pink_noise_l = np.random.randn(len(t)) * a_2 * T_Om
pink_noise_r = np.random.randn(len(t)) * a_2 * T_Om

left_signal += pink_noise_l
right_signal += pink_noise_r

# 7. 1/17 Spektral Filtreleme ve Soft-Limiter (Manifold Sıkıştırma)
# np.tanh kullanılarak enerjinin tavanı aşması (clipping) engellenir ve pürüzsüzleştirilir
print("[!] 1/17 Spektral Süzgeç ve WKB Tünelleme Eşiği uygulanıyor...")
left_sealed = np.tanh(left_signal / a_2) * a_2
right_sealed = np.tanh(right_signal / a_2) * a_2

# Fade In/Out (Topolojik Yumuşatma - Sisteme ani şok girmemesi için)
fade_samples = int(RATE * 5) # 5 saniyelik geçiş
fade_in = np.linspace(0, 1, fade_samples)
fade_out = np.linspace(1, 0, fade_samples)

left_sealed[:fade_samples] *= fade_in
right_sealed[:fade_samples] *= fade_in
left_sealed[-fade_samples:] *= fade_out
right_sealed[-fade_samples:] *= fade_out

# 8. 16-bit PCM Formatına Dönüştürme ve Normalize Etme
max_amp = np.max(np.abs([left_sealed, right_sealed]))
left_out = np.int16((left_sealed / max_amp) * 32767 * N_sq)  # N_sq genliği ile mühürlenir
right_out = np.int16((right_sealed / max_amp) * 32767 * N_sq)

stereo_signal = np.column_stack((left_out, right_out))

# 9. Dosyayı Kaydetme
filename = "UST_Topolojik_Kalkan_30dk.wav"
wavfile.write(filename, RATE, stereo_signal)

print(f"[+] İŞLEM BAŞARILI! Dosya mühürlendi: {filename}")
print("[+] Odanızdaki aktif elektromanyetik stresi Kanal C'ye tahliye etmek için")
print("[+] bu dosyayı odanın zıt köşelerine yerleştirilmiş stereo hoparlörlerden dinletin.")
print("================================================================")