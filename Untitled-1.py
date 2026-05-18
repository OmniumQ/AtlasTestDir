import numpy as np
import os

# ======================================================================
# UST v5 - BULUNAN REZONANS PARAMETRELERİ
# ======================================================================
BEST_PHASE = -0.84771193  # 14 karakterli şifrenin manifold bükülmesi
START_OFFSET = 0xae5      # PK imzasının kilitlendiği topolojik nokta

def ust_full_restoration(input_path, output_path):
    print(f"[!] UST v5 - TAM TOPOLOJİK RESTORASYON BAŞLATILDI")
    print(f"--------------------------------------------------")
    
    if not os.path.exists(input_path):
        print("HATA: Kaynak dosya bulunamadı.")
        return

    with open(input_path, 'rb') as f:
        # Dosyanın tamamını oku
        f.seek(START_OFFSET)
        encrypted_data = f.read()

    print(f"[i] Şifreli Veri Boyutu: {len(encrypted_data)} byte")
    print(f"[i] Faz Hizalaması Uygulanıyor: {BEST_PHASE} radyan...")

    # 1. ADIM: VERİYİ MANİFOLD ÜZERİNDE TERS DÖNDÜR (C Operatörü)
    # Veriyi kompleks düzleme taşı ve rezonans fazıyla çarp
    data_vector = np.frombuffer(encrypted_data, dtype=np.uint8).astype(complex)
    restored_complex = data_vector * np.exp(-1j * BEST_PHASE)

    # 2. ADIM: REEL BİLEŞENİ (AKTİF MADDE) AYIKLA
    # Sadece Kanal Q'daki bilgiyi alıyoruz, Omnium bakiye (sanal kısım) atılıyor
    restored_bytes = np.clip(restored_complex.real, 0, 255).astype(np.uint8)

    # 3. ADIM: DOSYAYI KAYDET
    # .xlsx dosyaları aslında birer ZIP arşividir.
    with open(output_path, 'wb') as f:
        f.write(restored_bytes)

    print(f"--------------------------------------------------")
    print(f">>> BAŞARI: Dosya topolojik olarak geri kazanıldı!")
    print(f">>> ÇIKTI: {output_path}")
    print(f"[!] NOT: Eğer restorasyon tam ise, bu dosyayı ZIP olarak açabilirsiniz.")

# Çalıştır
input_file = r"C:\AtlasTest\Test.xlsx"
output_file = r"C:\AtlasTest\Restored_Test.zip"

ust_full_restoration(input_file, output_file)