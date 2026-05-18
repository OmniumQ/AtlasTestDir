import h5py
import numpy as np

# UST v5 Parametreleri
A2 = 1/17
TOM = 0.232529135

def live_ust_compression(file_path):
    # 1. Gerçek LIGO HDF5 Dosyasını Aç
    with h5py.File(file_path, 'r') as f:
        raw_strain = f['strain']['Strain'][:]
        
    # 2. FFT (Kanal Q'ya Projeksiyon)
    freq_data = np.fft.rfft(raw_strain)
    amplitudes = np.abs(freq_data)
    
    # 3. UST Topolojik Süzgeç (Thresholding)
    # TOm altındaki enerjileri 'donmuş bilgi' (C) olarak ayır
    threshold = np.median(amplitudes) * (A2 / TOM)
    mask = amplitudes > threshold
    
    # 4. Sıkıştırma (Sadece gerekli indisleri ve değerleri sakla)
    compressed_indices = np.where(mask)[0].astype(np.uint32)
    compressed_values = freq_data[mask].astype(np.complex64)
    
    # SONUÇLARI YAZDIR
    orig_size = raw_strain.nbytes / (1024*1024)
    comp_size = (compressed_indices.nbytes + compressed_values.nbytes) / (1024*1024)
    
    print(f"Orijinal HDF5 Blok Boyutu: {orig_size:.2f} MB")
    print(f"UST Sıkıştırılmış Boyut: {comp_size:.2f} MB")
    print(f"Sıkıştırma Oranı: %{(1 - comp_size/orig_size)*100:.2f}")
    
    return compressed_indices, compressed_values

# Kullanım:
indices, values = live_ust_compression('I.Know.What.You.Did.Last.Summer.2025.1080p.WEBRip.x264.AAC5.1-[YTS.MX].mp4')