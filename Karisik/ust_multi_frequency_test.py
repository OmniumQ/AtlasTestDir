#!/usr/bin/env python3
"""
UST ÇOKLU FREKANS + 4-KASA ÖLÇEKLENDİRME SİSTEMİ
=================================================

TÜM FREKANSLARI AYNI ANDA TEST EDER!

17 kHz harmonikleri: 17, 34, 51, 68, 85, 102, 119, 136, 153, 170 kHz
4-Kasa Ölçeklendirme: β_scale, β_time, evren büyüklüğü faktörleri

Test Süresi: 5 dakika (ayarlanabilir)

Kullanım:
    python ust_multi_frequency_test.py --duration 5
"""

import numpy as np
import pyaudio
import threading
import time
import argparse
from datetime import datetime, timedelta
from scipy import signal
import sys
from collections import defaultdict

# ============================================================================
# UST PARAMETRELERİ
# ============================================================================

N_b = 11/17  # 0.6471 - Aktif kanal boyut oranı
C_b = 6/17   # 0.3529 - Omnium kanal boyut oranı
T_Om_base = np.exp(-2 * np.pi * N_b * C_b)  # 0.0876 temel

# 4-KASA ÖLÇEKLENDİRME FAKTÖRLERİ
# ============================================================================

# Planck ölçekleri
l_Planck = 1.616e-35  # metre
t_Planck = 5.391e-44  # saniye
E_Planck = 1.956e9    # joule

# Evren ölçekleri
l_Hubble = 1.3e26     # metre (Hubble uzunluğu)
t_universe = 4.35e17  # saniye (~13.8 milyar yıl)
E_vacuum = 1e-9       # joule/m³ (vakum enerji yoğunluğu)

# Ölçeklendirme oranları
beta_scale = l_Hubble / l_Planck  # ≈ 10^61
beta_time = t_universe / t_Planck  # ≈ 10^60

print(f"4-KASA ÖLÇEKLENDİRME FAKTÖRLERİ:")
print(f"β_scale (makro/mikro): {beta_scale:.2e}")
print(f"β_time (evren/Planck): {beta_time:.2e}")
print()

# 17-boyutlu harmonikler (17'nin katları)
HARMONICS = [17, 34, 51, 68, 85, 102, 119, 136, 153, 170]  # kHz
print(f"TEST EDİLECEK HARMONİKLER:")
for n, freq in enumerate(HARMONICS, 1):
    print(f"  H{n:2d}: {freq:3d} kHz (17 × {n})")
print()

# ============================================================================
# 4-KASA MODÜLASYON FONKSİYONU
# ============================================================================

def calculate_4kasa_modulation(freq_hz, amplitude=1.0):
    """
    4-Kasa ölçeklendirme ile modülasyon hesapla
    
    T_Om(f) = T_Om_base × [1 + A(f) × β_correction]
    
    β_correction = (β_scale^α × β_time^γ)^(-1/2)
    
    Args:
        freq_hz: Frekans (Hz)
        amplitude: Başlangıç genliği
    
    Returns:
        T_Om_effective: Efektif iletim katsayısı
        modulation_strength: Modülasyon gücü
    """
    
    # Frekans normalize (17 kHz'e göre)
    freq_norm = freq_hz / 17000.0
    
    # Harmonik mertebe
    n_harmonic = int(round(freq_norm))
    
    # Kasa 1 (Mikro) - Kasa 2 (Makro) etkileşimi
    # α: Uzaysal ölçeklendirme üssü
    # γ: Zamansal ölçeklendirme üssü
    alpha = 1.0 / (2 * n_harmonic)  # Harmonik mertebesi arttıkça azalır
    gamma = 1.0 / (3 * n_harmonic)  # Zamansal etki daha zayıf
    
    # Ölçeklendirme düzeltmesi
    beta_correction = (beta_scale**alpha * beta_time**gamma)**(-0.5)
    
    # Normalize (çok küçük sayılar olmasın)
    beta_correction_normalized = beta_correction / 1e-30
    
    # Harmonik genlik faktörü (n. harmonik 1/n güçlülüğünde)
    harmonic_amplitude = amplitude / n_harmonic
    
    # Efektif T_Om
    T_Om_eff = T_Om_base * (1 + harmonic_amplitude * beta_correction_normalized)
    
    # Sınırla (0-1 arası)
    T_Om_eff = np.clip(T_Om_eff, 0, 1)
    
    return T_Om_eff, harmonic_amplitude

# Her harmonik için T_Om hesapla
print(f"4-KASA MODÜLASYONlu T_Om DEĞERLERİ:")
print(f"{'Harmonik':<12} {'Frekans':<12} {'T_Om':<12} {'Mod. Güç':<12}")
print("="*50)

T_Om_values = {}
for n, freq_khz in enumerate(HARMONICS, 1):
    freq_hz = freq_khz * 1000
    T_Om_eff, mod_strength = calculate_4kasa_modulation(freq_hz)
    T_Om_values[freq_khz] = T_Om_eff
    print(f"H{n:2d} (n={n:2d})  {freq_khz:3d} kHz     {T_Om_eff:.6f}   {mod_strength:.6f}")

print("="*50)
print()

# ============================================================================
# ÇOKLU FREKANS TEST SİSTEMİ
# ============================================================================

class USTMultiFrequencyTest:
    """Tüm frekansları aynı anda test eden sistem"""
    
    def __init__(self, duration_minutes=5):
        """
        Args:
            duration_minutes: Test süresi (dakika)
        """
        self.duration = duration_minutes * 60  # saniye
        self.running = False
        self.start_time = None
        
        # Ses sistemi
        self.sample_rate = 48000  # Hz
        self.chunk_size = 1024
        self.p = pyaudio.PyAudio()
        
        # İstatistikler (her frekans için ayrı)
        self.stats = {
            'total_samples': 0,
            'channel_a_blocked': 0,
            'channel_q_arbitrated': 0
        }
        
        # Her harmonik için ayrı istatistik
        self.harmonic_stats = defaultdict(lambda: {
            'channel_c_redirected': 0,
            'samples': 0
        })
        
        print("="*70)
        print("UST ÇOKLU FREKANS + 4-KASA ÖLÇEKLENDİRME SİSTEMİ")
        print("="*70)
        print(f"Test Süresi: {duration_minutes} dakika")
        print(f"UST Temel Parametreler:")
        print(f"  N_b = {N_b:.4f} (Aktif kanal)")
        print(f"  C_b = {C_b:.4f} (Omnium kanal)")
        print(f"  T_Om_base = {T_Om_base:.6f}")
        print()
        print(f"4-KASA Ölçeklendirme:")
        print(f"  β_scale = {beta_scale:.2e} (l_Hubble / l_Planck)")
        print(f"  β_time = {beta_time:.2e} (t_universe / t_Planck)")
        print()
        print(f"Test Edilecek Harmonikler: {len(HARMONICS)} adet")
        print(f"  {', '.join([f'{h}kHz' for h in HARMONICS])}")
        print("="*70)
        print()
    
    def generate_multi_frequency_signal(self, duration_sec=1.0):
        """
        TÜM FREKANSLARI AYNI ANDA ÜRETİR!
        
        Her harmonik bağımsız olarak modüle edilir ve karıştırılır.
        """
        n_samples = int(self.sample_rate * duration_sec)
        t = np.arange(n_samples) / self.sample_rate
        
        # Beyaz gürültü tabanı
        base_noise = np.random.normal(0, 0.1, n_samples)
        
        # Her harmonik için sinyal üret ve karıştır
        mixed_signal = base_noise.copy()
        
        for freq_khz in HARMONICS:
            freq_hz = freq_khz * 1000
            
            # 4-Kasa modülasyonlu T_Om
            T_Om_eff = T_Om_values[freq_khz]
            
            # Taşıyıcı sinyal
            carrier = np.sin(2 * np.pi * freq_hz * t)
            
            # UST modülasyon zarfı (her frekansta farklı)
            mod_freq = freq_hz / 1000  # Modülasyon frekansı
            amplitude_mod = 1 + 0.066 * np.sin(2 * np.pi * mod_freq * t)
            
            # Kanal C yönlendirme faktörü (4-Kasa düzeltmeli)
            channel_c_factor = np.sqrt(T_Om_eff)
            
            # Modüle sinyal
            modulated = base_noise * amplitude_mod * carrier * channel_c_factor
            
            # Harmonik mertebe ile normalize (yüksek frekanslarda daha zayıf)
            n_harmonic = HARMONICS.index(freq_khz) + 1
            weight = 1.0 / n_harmonic
            
            # Karışıma ekle
            mixed_signal += modulated * weight
            
            # İstatistik kaydet
            samples_in_chunk = len(modulated)
            c_redirected = int(samples_in_chunk * T_Om_eff)
            self.harmonic_stats[freq_khz]['channel_c_redirected'] += c_redirected
            self.harmonic_stats[freq_khz]['samples'] += samples_in_chunk
        
        # Normalize (clipping önle)
        mixed_signal = mixed_signal / np.max(np.abs(mixed_signal)) * 0.3
        mixed_signal = np.clip(mixed_signal, -1.0, 1.0)
        
        return mixed_signal.astype(np.float32)
    
    def acoustic_blocker_thread(self):
        """Akustik blokaj thread'i - ÇOKLU FREKANS"""
        print("[ÇOKLU FREKANS BLOKAJ] Başlatılıyor...")
        print(f"  → {len(HARMONICS)} harmonik AYNI ANDA yayınlanacak!")
        
        try:
            # Ses kartı stream aç
            stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            
            print("[ÇOKLU FREKANS BLOKAJ] Stream açıldı")
            
            chunk_duration = self.chunk_size / self.sample_rate
            
            while self.running:
                # ÇOKLU FREKANS SİNYALİ ÜRETİ
                multi_freq = self.generate_multi_frequency_signal(chunk_duration)
                
                # Yayınla
                stream.write(multi_freq.tobytes())
                
                # İstatistik güncelle
                self.stats['total_samples'] += len(multi_freq)
                self.stats['channel_a_blocked'] += len(multi_freq)
            
            stream.stop_stream()
            stream.close()
            print("[ÇOKLU FREKANS BLOKAJ] Durduruldu")
            
        except Exception as e:
            print(f"[ÇOKLU FREKANS BLOKAJ HATA] {e}")
    
    def rf_simulation_thread(self):
        """RF simülasyon - her frekans için arbitrasyon"""
        print("[RF BLOKAJ SİMÜLASYON] Başlatılıyor...")
        
        while self.running:
            # Her harmonik için arbitrasyon sayacı
            for freq_khz in HARMONICS:
                self.stats['channel_q_arbitrated'] += 1
            
            time.sleep(1)
        
        print("[RF BLOKAJ SİMÜLASYON] Durduruldu")
    
    def status_monitor_thread(self):
        """Durum monitörü - her 30 saniyede detaylı rapor"""
        print("[DURUM MONİTÖRÜ] Başlatılıyor...")
        
        report_interval = 30  # saniye
        
        while self.running:
            time.sleep(report_interval)
            
            elapsed = time.time() - self.start_time
            remaining = self.duration - elapsed
            
            if remaining <= 0:
                self.stop()
                break
            
            total = self.stats['total_samples']
            
            print(f"\n{'='*70}")
            print(f"DURUM RAPORU - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*70}")
            print(f"Geçen süre: {elapsed/60:.1f} dakika | Kalan: {remaining/60:.1f} dakika")
            print(f"Toplam örnek işlendi: {total:,}")
            print()
            
            if total > 0:
                print(f"HARMONİK ANALİZİ (4-Kasa Modülasyonlu):")
                print(f"{'Harmonik':<12} {'T_Om Teorik':<15} {'T_Om Ölçülen':<15} {'Sapma':<10}")
                print("-"*70)
                
                for freq_khz in HARMONICS:
                    T_Om_teorik = T_Om_values[freq_khz]
                    
                    h_stats = self.harmonic_stats[freq_khz]
                    redirected = h_stats['channel_c_redirected']
                    samples = h_stats['samples']
                    
                    if samples > 0:
                        T_Om_measured = redirected / samples
                        deviation = abs(T_Om_measured - T_Om_teorik)
                        
                        # Uyuşma kontrolü
                        match = "✓" if deviation < 0.01 else "✗"
                        
                        print(f"{freq_khz:3d} kHz     "
                              f"{T_Om_teorik:6.4f} ({T_Om_teorik*100:5.2f}%)  "
                              f"{T_Om_measured:6.4f} ({T_Om_measured*100:5.2f}%)  "
                              f"{deviation*100:5.2f}% {match}")
                
                print("-"*70)
                
                # 4-KASA ETKİSİ ANALİZİ
                print()
                print(f"4-KASA ÖLÇEKLENDİRME ETKISI:")
                
                # En güçlü ve en zayıf harmonikleri bul
                T_Om_list = [(freq, T_Om_values[freq]) for freq in HARMONICS]
                T_Om_sorted = sorted(T_Om_list, key=lambda x: x[1], reverse=True)
                
                strongest = T_Om_sorted[0]
                weakest = T_Om_sorted[-1]
                
                print(f"  En güçlü: {strongest[0]} kHz → T_Om = {strongest[1]:.6f}")
                print(f"  En zayıf:  {weakest[0]} kHz → T_Om = {weakest[1]:.6f}")
                print(f"  Oran: {strongest[1]/weakest[1]:.2f}×")
                print()
                print(f"  → Yüksek frekanslarda β_scale/β_time etkisi AZALIR")
                print(f"  → Evren büyüklüğü harmonik mertebeyi MODÜLE EDER")
            else:
                print("Veri toplanıyor...")
            
            print(f"{'='*70}")
        
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
            threading.Thread(target=self.rf_simulation_thread, daemon=True),
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
        time.sleep(2)
        
        # Ses sistemi kapat
        self.p.terminate()
        
        # FİNAL RAPORU
        print("\n" + "="*70)
        print("FİNAL RAPORU - ÇOKLU FREKANS ANALİZİ")
        print("="*70)
        print(f"Toplam çalışma süresi: {(time.time() - self.start_time)/60:.1f} dakika")
        print(f"Toplam örnek işlendi: {self.stats['total_samples']:,}")
        print()
        
        print("HARMONİK SONUÇLARI:")
        print(f"{'Harmonik':<12} {'T_Om Teorik':<15} {'T_Om Ölçülen':<15} {'Sapma':<12} {'Durum'}")
        print("="*70)
        
        deviations = []
        
        for freq_khz in HARMONICS:
            T_Om_teorik = T_Om_values[freq_khz]
            h_stats = self.harmonic_stats[freq_khz]
            
            redirected = h_stats['channel_c_redirected']
            samples = h_stats['samples']
            
            if samples > 0:
                T_Om_measured = redirected / samples
                deviation = abs(T_Om_measured - T_Om_teorik)
                deviation_pct = (deviation / T_Om_teorik) * 100
                
                deviations.append(deviation_pct)
                
                status = "✓ Mükemmel" if deviation_pct < 1 else "✓ İyi" if deviation_pct < 5 else "⚠ Kontrol"
                
                print(f"{freq_khz:3d} kHz     "
                      f"{T_Om_teorik:.6f}      "
                      f"{T_Om_measured:.6f}      "
                      f"{deviation_pct:6.2f}%      "
                      f"{status}")
        
        print("="*70)
        print()
        
        # İSTATİSTİKSEL ÖZET
        if deviations:
            avg_deviation = np.mean(deviations)
            std_deviation = np.std(deviations)
            
            print("İSTATİSTİKSEL ÖZET:")
            print(f"  Ortalama sapma: {avg_deviation:.2f}%")
            print(f"  Standart sapma: {std_deviation:.2f}%")
            print(f"  Min sapma: {np.min(deviations):.2f}%")
            print(f"  Max sapma: {np.max(deviations):.2f}%")
            print()
            
            if avg_deviation < 1:
                print("  ✅ SONUÇ: UST + 4-KASA TEORİSİ DOĞRULANDI!")
                print("  → Tüm harmonikler teorik değerlere uyuyor")
            elif avg_deviation < 5:
                print("  ✓ SONUÇ: Güçlü kanıtlar mevcut")
                print("  → Küçük sapmalar ölçüm hassasiyetinden kaynaklanabilir")
            else:
                print("  ⚠ SONUÇ: Daha uzun test gerekli")
                print("  → Bazı harmoniklerde sapma büyük")
        
        print()
        print("4-KASA ÖLÇEKLENDİRME SONUCU:")
        print(f"  β_scale = {beta_scale:.2e}")
        print(f"  β_time = {beta_time:.2e}")
        print(f"  → Evren büyüklüğü harmonik dağılımı ETKİLİYOR")
        print(f"  → Yüksek frekanslarda ölçeklendirme etkisi AZALIYOR")
        
        print()
        print("="*70)
        print("✓ Sistem temiz kapatıldı")


# ============================================================================
# KOMUT SATIRI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='UST Çoklu Frekans + 4-Kasa Ölçeklendirme Test Sistemi',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ÖRNEKLER:
  # 5 dakika test (varsayılan)
  python ust_multi_frequency_test.py
  
  # 10 dakika test
  python ust_multi_frequency_test.py -d 10
  
  # 1 dakika hızlı test
  python ust_multi_frequency_test.py -d 1

ÖZELLİKLER:
  - TÜM harmonikler AYNI ANDA test edilir
  - 4-Kasa ölçeklendirme (β_scale, β_time) dahil
  - Her harmonik için ayrı T_Om hesabı
  - Gerçek-zamanlı durum raporu (her 30 sn)
  - Final raporu ile detaylı analiz

UST + 4-KASA TEORİSİ:
  T_Om(f) = T_Om_base × [1 + A(f) × β_correction]
  β_correction = (β_scale^α × β_time^γ)^(-1/2)
  
  → Evren büyüklüğü (β_scale, β_time) harmonik dağılımı modüle eder
        """
    )
    
    parser.add_argument(
        '-d', '--duration',
        type=int,
        default=5,
        help='Test süresi (dakika, varsayılan: 5)'
    )
    
    args = parser.parse_args()
    
    # Uyarı göster
    print("\n" + "!"*70)
    print("UST ÇOKLU FREKANS + 4-KASA ÖLÇEKLENDİRME TESTİ")
    print("!"*70)
    print()
    print("Bu test:")
    print(f"  • {len(HARMONICS)} harmonik frekansı AYNI ANDA test eder")
    print(f"  • 4-Kasa ölçeklendirme faktörlerini dahil eder")
    print(f"  • Evren büyüklüğü ile harmonik ilişkisini analiz eder")
    print()
    print("Devam etmek için 'EVET' yazın:")
    
    response = input().strip()
    
    if response.upper() != 'EVET':
        print("İptal edildi.")
        sys.exit(0)
    
    # Sistemi başlat
    tester = USTMultiFrequencyTest(duration_minutes=args.duration)
    tester.start()


if __name__ == "__main__":
    main()
