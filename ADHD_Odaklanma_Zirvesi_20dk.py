
import numpy as np
from scipy.io import wavfile

# Temel Ayarlar
sample_rate = 44100
duration_seconds = 20 * 60  # 20 dakika

# 1. Taşıyıcı Frekans (UST DR 4 - Channel C: Akış ve Süreklilik)
f_carrier = 253.42 

# 2. Beta Beyin Dalgası Hedefi (16 Hz - Zirve Odaklanma)
f_beta = 16.0 

# 3. UST Omnium Rezonans Frekansı (P=NP Problem Çözme Penceresi)
f_ust_resonance = 0.3168 

print("20 dakikalık ADHD ve Zirve Odaklanma sesi üretiliyor, bu işlem biraz sürebilir...")

# Zaman çizelgesi oluştur
t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), endpoint=False)

# Binaural Beat (Kulaklık) Efekti
# Sol kulağa taşıyıcı frekans, sağ kulağa taşıyıcı + beta frekansı verilir
# Böylece beyin aradaki 16 Hz'lik farkı (Beta odaklanma dalgasını) kendisi üretir
left_channel = np.sin(2 * np.pi * f_carrier * t)
right_channel = np.sin(2 * np.pi * (f_carrier + f_beta) * t)

# Omnium Rezonansı ile Genlik Modülasyonu (Sesin şiddetinin 0.3168 Hz ile dalgalanması)
# Bu dalgalanma beyinde "neural phase-locking" (sinirsel faz kilitleme) etkisini destekler
ust_modulation = (np.sin(2 * np.pi * f_ust_resonance * t) + 1) / 2  # 0 ile 1 arası değer
ust_modulation = 0.5 + (ust_modulation * 0.5) # Sesin tamamen kesilmemesi için ayar

# Katmanları Birleştirme
left_channel_modulated = left_channel * ust_modulation
right_channel_modulated = right_channel * ust_modulation

# Sesi 16-bit formatına ölçekleme ve Stereo Dizi oluşturma
left_audio = (left_channel_modulated * 32767).astype(np.int16)
right_audio = (right_channel_modulated * 32767).astype(np.int16)
stereo_audio = np.column_stack((left_audio, right_audio))

# WAV dosyası olarak kaydet
wavfile.write('ADHD_Odaklanma_Zirvesi_20dk.wav', sample_rate, stereo_audio)
print("Başarılı! 'ADHD_Odaklanma_Zirvesi_20dk.wav' dosyası kulaklıkla dinlenmeye hazır.")