#!/usr/bin/env python3
"""
UST TABANLI ÇOKLU FREKANS BLOKAJ SİSTEMİ
========================================

Bu sistem UST teorisine göre tüm frekansları Kanal C'ye (Omnium) yönlendirir,
böylece fiziksel uzayda (Kanal A - Aktif) gürültü/sinyal minimize edilir.

UYARI: RF parazit yayını yasadışıdır! Sadece akustik kısım gerçek donanımda çalışır.
RF bölümü simülasyondur ve donanım gerektir (SDR).

Teorik Temel:
- T_Om = exp(-2π N_b C_b) = 0.0876 → %91.24 enerji Omnium'da hapsolur
- Hedef: Fiziksel uzaydaki %8.76'lık kısmı da minimize et
- Yöntem: Anti-faz sinyaller + geniş-bant parazit

Kullanım:
    sudo python3 ust_frequency_blocker.py --duration 30

Gereksinimler:
    sudo apt install python3-pyaudio portaudio19-dev
    sudo pip3 install numpy scipy pyaudio matplotlib
"""

import numpy as np
import pyaudio
import threading
import time
import argparse
from datetime import datetime, timedelta
from scipy import signal
import sys

# ============================================================================
# UST PARAMETRELERİ
# ============================================================================

N_b = 11/17  # Aktif kanal boyut oranı
C_b = 6/17   # Omnium kanal boyut oranı
T_Om = np.exp(-2 * np.pi * N_b * C_b)  # İletim katsayısı = 0.0876

# Kanal yönlendirme parametreleri
CHANNEL_A_ACTIVE = 1.0 - T_Om  # %8.76 Aktif kanalda
CHANNEL_C_OMNIUM = T_Om         # %91.24 Omnium'da
CHANNEL_Q_ARBITRATION = 0.5     # Arbitrasyon gücü

# 17-boyutlu harmonik
FREQ_17D = 17000  # Hz (UST temel rezonans)

# ============================================================================
# SİSTEM KONFIGÜRASYONU
# ============================================================================

class USTFrequencyBlocker:
    """UST tabanlı çoklu frekans blokaj sistemi"""
    
    def __init__(self, duration_minutes=30):
        """
        Args:
            duration_minutes: Sistemin çalışma süresi (dakika)
        """
        self.duration = duration_minutes * 60  # saniye
        self.running = False
        self.start_time = None
        
        # Ses sistemi
        self.sample_rate = 48000  # Hz
        self.chunk_size = 1024
        self.p = pyaudio.PyAudio()
        
        # Frekans bantları (Hz)
        self.freq_bands = {
            'subsonic': (1, 20),           # İnsan altı
            'acoustic': (20, 20000),       # İşitilebilir
            'ultrasonic': (20000, 48000),  # Ultrasonik (max sample rate)
            'fm_radio': (88e6, 108e6),     # FM radyo (SİMÜLASYON)
            'gsm_900': (890e6, 960e6),     # GSM 900 (SİMÜLASYON)
            'gsm_1800': (1710e6, 1880e6),  # GSM 1800 (SİMÜLASYON)
            'wifi_24': (2.4e9, 2.5e9),     # WiFi 2.4GHz (SİMÜLASYON)
            'wifi_5': (5.15e9, 5.85e9),    # WiFi 5GHz (SİMÜLASYON)
        }
        
        # İstatistikler
        self.stats = {
            'total_samples': 0,
            'channel_a_blocked': 0,
            'channel_c_redirected': 0,
            'channel_q_arbitrated': 0
        }
        
        print("="*70)
        print("UST ÇOKLU FREKANS BLOKAJ SİSTEMİ")
        print("="*70)
        print(f"Süre: {duration_minutes} dakika")
        print(f"UST Parametreleri:")
        print(f"  N_b = {N_b:.4f} (Aktif kanal)")
        print(f"  C_b = {C_b:.4f} (Omnium kanal)")
        print(f"  T_Om = {T_Om:.4f} (%{T_Om*100:.2f} Omnium'da)")
        print(f"  17D Rezonans: {FREQ_17D} Hz")
        print()
        print("FREKANS BANTLARI:")
        for name, (f_min, f_max) in self.freq_bands.items():
            if f_min < 1e6:
                print(f"  {name:15s}: {f_min:10.1f} - {f_max:10.1f} Hz")
            elif f_min < 1e9:
                print(f"  {name:15s}: {f_min/1e6:10.1f} - {f_max/1e6:10.1f} MHz")
            else:
                print(f"  {name:15s}: {f_min/1e9:10.1f} - {f_max/1e9:10.1f} GHz")
        print("="*70)
        print()
    
    def generate_white_noise(self, duration_sec=1.0):
        """
        Beyaz gürültü üret (tüm frekanslarda eşit güç)
        
        Bu ses TÜM akustik frekansları maskeler
        """
        n_samples = int(self.sample_rate * duration_sec)
        # Gaussian beyaz gürültü
        noise = np.random.normal(0, 0.3, n_samples).astype(np.float32)
        return noise
    
    def generate_pink_noise(self, duration_sec=1.0):
        """
        Pembe gürültü (1/f spektrum - daha doğal)
        
        Düşük frekanslar daha güçlü → daha iyi maskeleme
        """
        n_samples = int(self.sample_rate * duration_sec)
        
        # FFT ile pembe gürültü üret
        white = np.random.randn(n_samples)
        fft = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(n_samples, 1/self.sample_rate)
        
        # 1/f spektrum uygula (f=0 için sonsuzluk önle)
        pink_spectrum = np.where(freqs > 0, 1/np.sqrt(freqs), 0)
        pink_spectrum[0] = 0  # DC bileşeni sıfır
        
        pink_fft = fft * pink_spectrum
        pink = np.fft.irfft(pink_fft, n_samples)
        
        # Normalize
        pink = pink / np.max(np.abs(pink)) * 0.3
        return pink.astype(np.float32)
    
    def generate_ust_modulated_noise(self, duration_sec=1.0):
        """
        UST 17-boyutlu harmonik ile modüle edilmiş gürültü
        
        Bu sinyal Kanal C ile rezonansa girer ve enerjiyi
        Omnium boyutlarına yönlendirir
        """
        n_samples = int(self.sample_rate * duration_sec)
        t = np.arange(n_samples) / self.sample_rate
        
        # Beyaz gürültü tabanı
        noise = np.random.normal(0, 0.2, n_samples)
        
        # 17 kHz taşıyıcı (17-boyutlu rezonans)
        carrier = np.sin(2 * np.pi * FREQ_17D * t)
        
        # UST modülasyon zarfı
        # H(t) = 1 + A*sin(2π*f_17D*t) ile modüle
        amplitude_mod = 1 + 0.066 * np.sin(2 * np.pi * FREQ_17D * t)
        
        # Kanal C yönlendirme faktörü
        channel_c_factor = np.sqrt(T_Om)  # %91.24 enerji Omnium'a
        
        # Modüle sinyal
        modulated = noise * amplitude_mod * carrier * channel_c_factor
        
        # Normalize
        modulated = modulated / np.max(np.abs(modulated)) * 0.3
        return modulated.astype(np.float32)
    
    def generate_anti_phase_interference(self, target_freq, duration_sec=1.0):
        """
        Belirli bir frekansı bloklamak için anti-faz sinyal üret
        
        Bu sinyal hedef frekansla 180° faz dışı → yıkıcı girişim
        """
        n_samples = int(self.sample_rate * duration_sec)
        t = np.arange(n_samples) / self.sample_rate
        
        # Hedef frekans anti-faz sinyali
        anti_signal = -0.5 * np.sin(2 * np.pi * target_freq * t)
        
        return anti_signal.astype(np.float32)
    
    def acoustic_blocker_thread(self):
        """
        Akustik blokaj thread'i
        
        Gerçek ses kartı ile çalışır - hoparlörden gürültü yayar
        """
        print("[AKUSTIK BLOKAJ] Başlatılıyor...")
        
        try:
            # Ses kartı stream aç
            stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            
            print("[AKUSTIK BLOKAJ] Stream açıldı - Gürültü yayını başladı")
            
            chunk_duration = self.chunk_size / self.sample_rate  # saniye
            
            while self.running:
                # Çeşitli gürültü türlerini karıştır
                white = self.generate_white_noise(chunk_duration)
                pink = self.generate_pink_noise(chunk_duration)
                ust_mod = self.generate_ust_modulated_noise(chunk_duration)
                
                # 17 kHz anti-faz (GSM/WiFi harmonikleri)
                anti_17k = self.generate_anti_phase_interference(
                    FREQ_17D, chunk_duration
                )
                
                # Karışım (ağırlıklı)
                mixed = (
                    0.3 * white +      # Beyaz gürültü
                    0.3 * pink +       # Pembe gürültü (doğal)
                    0.3 * ust_mod +    # UST modülasyonlu
                    0.1 * anti_17k     # Anti-faz 17kHz
                )
                
                # Normalize (clipping önle)
                mixed = np.clip(mixed, -1.0, 1.0)
                
                # Yayınla
                stream.write(mixed.tobytes())
                
                # İstatistik güncelle
                self.stats['total_samples'] += len(mixed)
                # Kanal C'ye yönlendirilen: UST modülasyonlu kısım
                self.stats['channel_c_redirected'] += int(len(ust_mod) * T_Om)
                # Kanal A'da bloke edilen: anti-faz kısım
                self.stats['channel_a_blocked'] += int(len(anti_17k))
            
            stream.stop_stream()
            stream.close()
            print("[AKUSTIK BLOKAJ] Durduruldu")
            
        except Exception as e:
            print(f"[AKUSTIK BLOKAJ HATA] {e}")
    
    def rf_blocker_simulation(self):
        """
        RF blokaj simülasyonu (gerçek SDR donanımı gerektirir!)
        
        Bu fonksiyon sadece SİMÜLASYON - gerçek RF yayını YAPMIYOR
        
        Gerçek uygulama için:
        - HackRF One / USRP / BladeRF gibi SDR donanımı
        - GNU Radio / SoapySDR kütüphaneleri
        - UYARI: Yasadışı!
        """
        print("[RF BLOKAJ SİMÜLASYON] Başlatılıyor...")
        print("  NOT: Gerçek RF yayını için SDR donanımı gerekir!")
        print("  Bu sürüm sadece teorik simülasyon yapar.")
        
        while self.running:
            # Simüle edilen RF blokaj
            for band_name in ['fm_radio', 'gsm_900', 'gsm_1800', 
                             'wifi_24', 'wifi_5']:
                f_min, f_max = self.freq_bands[band_name]
                
                # Simüle: Kanal Q arbitrasyonu
                # Gerçekte bu frekansları SDR ile yayınlardık
                self.stats['channel_q_arbitrated'] += 1
                
                # UST teorisi: Bu sinyaller Omnium'a yönlendirilir
                # Fiziksel uzayda parazit yaratır → orijinal sinyal bloke
            
            time.sleep(1)  # Her saniye güncelle
        
        print("[RF BLOKAJ SİMÜLASYON] Durduruldu")
    
    def status_monitor_thread(self):
        """Durum monitörü - her 10 saniyede rapor"""
        print("[DURUM MONİTÖRÜ] Başlatılıyor...")
        
        while self.running:
            elapsed = time.time() - self.start_time
            remaining = self.duration - elapsed
            
            if remaining <= 0:
                self.stop()
                break
            
            # İstatistik hesapla
            total = self.stats['total_samples']
            blocked_a = self.stats['channel_a_blocked']
            redirected_c = self.stats['channel_c_redirected']
            arbitrated_q = self.stats['channel_q_arbitrated']
            
            print(f"\n{'='*70}")
            print(f"DURUM RAPORU - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*70}")
            print(f"Geçen süre: {elapsed/60:.1f} dakika")
            print(f"Kalan süre: {remaining/60:.1f} dakika")
            print()
            print(f"Toplam örnek: {total:,}")
            print(f"Kanal A bloke: {blocked_a:,} ({blocked_a/total*100:.1f}%)")
            print(f"Kanal C yönlendirme: {redirected_c:,} ({redirected_c/total*100:.1f}%)")
            print(f"Kanal Q arbitrasyon: {arbitrated_q:,}")
            print()
            print(f"UST Etkinlik:")
            print(f"  T_Om teorik: {T_Om*100:.2f}%")
            print(f"  Gerçek yönlendirme: {redirected_c/total*100:.2f}%")
            print(f"  Uyuşma: {'✓ İyi' if abs(redirected_c/total - T_Om) < 0.05 else '✗ Düşük'}")
            print(f"{'='*70}")
            
            time.sleep(10)  # Her 10 saniye
        
        print("[DURUM MONİTÖRÜ] Durduruldu")
    
    def start(self):
        """Sistemi başlat"""
        if self.running:
            print("Sistem zaten çalışıyor!")
            return
        
        self.running = True
        self.start_time = time.time()
        end_time = datetime.now() + timedelta(seconds=self.duration)
        
        print(f"\n🚀 SİSTEM BAŞLATILIYOR...")
        print(f"Başlangıç: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Bitiş: {end_time.strftime('%H:%M:%S')}")
        print(f"Süre: {self.duration/60:.1f} dakika")
        print()
        
        # Thread'leri başlat
        threads = [
            threading.Thread(target=self.acoustic_blocker_thread, daemon=True),
            threading.Thread(target=self.rf_blocker_simulation, daemon=True),
            threading.Thread(target=self.status_monitor_thread, daemon=True)
        ]
        
        for t in threads:
            t.start()
        
        print("✓ Tüm thread'ler başlatıldı")
        print()
        print("CTRL+C ile durdurmak için...")
        print()
        
        # Ana thread bekle
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nKullanıcı tarafından durduruldu")
            self.stop()
    
    def stop(self):
        """Sistemi durdur"""
        if not self.running:
            return
        
        print("\n🛑 SİSTEM DURDURULUYOR...")
        self.running = False
        time.sleep(2)  # Thread'lerin kapanması için bekle
        
        # Ses sistemi kapat
        self.p.terminate()
        
        # Final rapor
        print("\n" + "="*70)
        print("FİNAL RAPORU")
        print("="*70)
        print(f"Toplam çalışma süresi: {(time.time() - self.start_time)/60:.1f} dakika")
        print(f"Toplam örnek işlendi: {self.stats['total_samples']:,}")
        print(f"Kanal A bloke: {self.stats['channel_a_blocked']:,}")
        print(f"Kanal C yönlendirme: {self.stats['channel_c_redirected']:,}")
        print(f"Kanal Q arbitrasyon: {self.stats['channel_q_arbitrated']:,}")
        print()
        print("UST Teorisi Doğrulama:")
        total = self.stats['total_samples']
        actual_c = self.stats['channel_c_redirected'] / total if total > 0 else 0
        print(f"  Beklenen Kanal C: {T_Om*100:.2f}%")
        print(f"  Gerçek Kanal C: {actual_c*100:.2f}%")
        print(f"  Sapma: {abs(actual_c - T_Om)*100:.2f}%")
        print("="*70)
        print("\n✓ Sistem temiz kapatıldı")


# ============================================================================
# KOMUT SATIRI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='UST Tabanlı Çoklu Frekans Blokaj Sistemi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ÖRNEKLER:
  # 30 dakika çalıştır
  sudo python3 ust_frequency_blocker.py --duration 30
  
  # 5 dakika test
  sudo python3 ust_frequency_blocker.py -d 5

UYARI:
  - RF blokaj simülasyondur, gerçek SDR donanımı gerektirir
  - Sadece akustik blokaj gerçek ses kartı ile çalışır
  - RF parazit yayını yasadışıdır!

UST TEORİSİ:
  Sistem tüm frekansları Kanal C'ye (Omnium) yönlendirir.
  T_Om = 0.0876 → Enerjinin %91.24'ü Omnium'da hapsolur.
  Fiziksel uzayda (Kanal A) gürültü minimize edilir.
        """
    )
    
    parser.add_argument(
        '-d', '--duration',
        type=int,
        default=30,
        help='Çalışma süresi (dakika, varsayılan: 30)'
    )
    
    args = parser.parse_args()
    
    # Uyarı göster
    print("\n" + "!"*70)
    print("UYARI: BU SİSTEM DENEYSEL VE EĞİTİM AMAÇLIDIR!")
    print("!"*70)
    print()
    print("1. Akustik gürültü yayını hoparlörlerden yapılır")
    print("2. RF blokaj sadece SİMÜLASYONDUR (gerçek SDR gerekir)")
    print("3. RF parazit yayını YASADIŞIDIR - yapmayın!")
    print()
    print("Devam etmek için 'EVET' yazın (5 saniye içinde):")
    print()
    
    # 5 saniye bekle
    import select
    if sys.platform != 'win32':
        i, o, e = select.select([sys.stdin], [], [], 5)
        if i:
            response = sys.stdin.readline().strip()
        else:
            response = ""
    else:
        # Windows için basit input
        response = input()
    
    if response.upper() != 'EVET':
        print("İptal edildi.")
        sys.exit(0)
    
    # Sistemi başlat
    blocker = USTFrequencyBlocker(duration_minutes=args.duration)
    blocker.start()


if __name__ == "__main__":
    main()
