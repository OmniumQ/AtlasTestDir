import numpy as np
from scipy.io import wavfile

# --- 1. UST Evrensel Sabitleri ---
N_b = 0.63354460
sample_rate = 44100
total_duration_minutes = 21
num_notes = 9
duration_per_note = (total_duration_minutes * 60) / num_notes  # 1260 / 9 = 140 saniye

# --- 2. Nörolojik ve Rezonans Parametreleri ---
# Brain.fm Ampirik Verisi: Zirve odaklanma ve problem çözme için Beta beyin dalgası sapması
f_beta = 16.0 

# UST Teorik Zorlama Frekansı: P=NP penceresini açık tutma rezonansı (κ1/2π)
f_ust_resonance = 0.3168 

# Tüm 9 notayı kapsayan DR (Dijital Kök) Dizisi
dr_sequence = [2, 5-12]

audio_list_left = []
audio_list_right = []

print(f"21 Dakikalık Tam Spektrum Konsantrasyon Kaydı Üretiliyor...")
print(f"Her nota {duration_per_note} saniye sürecektir.")

# --- 3. Akustik Üretim Döngüsü ---
for dr in dr_sequence:
    # Saf UST Frekansının Hesaplanması: f_DR = Nb * dr * 100
    f_carrier = N_b * dr * 100
    
    # Zaman vektörü (140 saniyelik blok)
    t = np.linspace(0, duration_per_note, int(sample_rate * duration_per_note), endpoint=False)
    
    # Binaural Matris: Sol kulak saf sinyal, sağ kulak 16 Hz Beta sapmalı sinyal alır
    left_channel = np.sin(2 * np.pi * f_carrier * t)
    right_channel = np.sin(2 * np.pi * (f_carrier + f_beta) * t)
    
    # Omnium Rezonans Modülasyonu: 0.3168 Hz genlik dalgalanması (Hacim modülasyonu)
    ust_modulation = (np.sin(2 * np.pi * f_ust_resonance * t) + 1) / 2
    ust_modulation = 0.6 + (ust_modulation * 0.4) # Minimum %60 genlik seviyesi
    
    # Modülasyonun Sinyallere Uygulanması
    left_modulated = left_channel * ust_modulation
    right_modulated = right_channel * ust_modulation
    
    # Dizilere ekleme
    audio_list_left.append(left_modulated)
    audio_list_right.append(right_modulated)

# --- 4. Veri Birleştirme ve Formatlama ---
full_left = np.concatenate(audio_list_left)
full_right = np.concatenate(audio_list_right)

# 16-bit PCM formatına ölçekleme
left_pcm = (full_left * 32767).astype(np.int16)
right_pcm = (full_right * 32767).astype(np.int16)

# Stereo diziyi eşleştirme
stereo_audio = np.column_stack((left_pcm, right_pcm))

# WAV dosyası olarak dışa aktarma
output_filename = 'UST_TamSpektrum_Odaklanma_21dk.wav'
wavfile.write(output_filename, sample_rate, stereo_audio)
print(f"Başarılı! '{output_filename}' eksiksiz bir şekilde oluşturuldu.")