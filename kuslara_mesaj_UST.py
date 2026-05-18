import numpy as np
from scipy.io import wavfile

# UST Temel Sabitleri
N_b = 0.63354460
sample_rate = 44100

def ust_tone(dr, duration_ms=200):
    # Frekans formülü: f_DR = Nb * dr * 100
    freq = N_b * dr * 100
    t = np.linspace(0, duration_ms/1000, int(sample_rate * duration_ms/1000))
    # Ses dalgası üretimi
    return (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)

# UST Türkçe Harf -> DR Değeri Eşleşme Tablosu [1]
ust_dr_map = {
    'A': 1, 'B': 7, 'C': 9, 'Ç': 8, 'D': 7, 'E': 1, 'F': 5, 'G': 6, 'Ğ': 6, 'H': 6,
    'I': 2, 'İ': 2, 'J': 9, 'K': 8, 'L': 3, 'M': 3, 'N': 3, 'O': 4, 'Ö': 4, 'P': 8,
    'R': 5, 'S': 9, 'Ş': 9, 'T': 8, 'U': 4, 'Ü': 4, 'V': 5, 'Y': 5, 'Z': 7
}

# Göndermek istediğiniz mesaj
mesaj = "merhaba merhaba nasılsınız ? iyi niyetli iseniz ve barışçılsanız buyrun size çekirdek vereyim yemek iin"

# İşlemleri kolaylaştırmak için mesajı büyük harfe çeviriyoruz
mesaj = mesaj.upper()

audio_list = []

print("Frekanslar oluşturuluyor, lütfen bekleyin...")

for char in mesaj:
    if char in ust_dr_map:
        # Harfler için DR değerini bul ve 200 ms standart süreyle çal [2]
        dr = ust_dr_map[char]
        audio_list.append(ust_tone(dr, duration_ms=200))
    elif char == ' ':
        # Boşluklar için (Omnium - DR 9) 100 ms süreyle çal [2]
        audio_list.append(ust_tone(9, duration_ms=100))
    elif char == '?':
        # Soru işareti için (Omnium - DR 9) 100 ms süreyle çal [2]
        audio_list.append(ust_tone(9, duration_ms=100))

# Üretilen tonları uç uca ekle
audio = np.concatenate(audio_list)

# WAV dosyası olarak dışa aktar
wavfile.write('kuslara_mesaj_UST.wav', sample_rate, audio)
print("kuslara_mesaj_UST.wav başarıyla oluşturuldu! Artık kuşlara dinletebilirsiniz.")