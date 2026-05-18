import numpy as np
from scipy.io import wavfile

# UST Temel Sabitleri
N_b = 0.63354460
sample_rate = 44100

def ust_tone(dr, duration_ms=200):
    # Frekans hesaplaması: f_DR = Nb * dr * 100
    freq = N_b * dr * 100
    t = np.linspace(0, duration_ms/1000, int(sample_rate * duration_ms/1000))
    return (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)

# MERHABA NASILSIN sekansı (DR değerleri)
# M(3) E(1) R(5) H(6) A(1) B(7) A(1) [boşluk](9) N(3) A(1) S(9) I(2) L(3) S(9) I(2) N(3) [?](9)
sequence = [1, 2, 5, 6, 9-11]

audio_list = []
for dr in sequence:
    # Kaynakta boşluk ve noktalama işaretleri için daha kısa süre önerilmiştir (örn. 100 ms veya 50 ms)
    if dr == 9:
        audio_list.append(ust_tone(dr, duration_ms=100))
    else:
        # Harfler için standart süre 200 ms
        audio_list.append(ust_tone(dr, duration_ms=200))

# Üretilen tonları birleştir
audio = np.concatenate(audio_list)

# WAV dosyası olarak dışa aktar
wavfile.write('merhaba_nasilsin_UST.wav', sample_rate, audio)
print("merhaba_nasilsin_UST.wav başarıyla oluşturuldu!")