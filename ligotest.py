#!/usr/bin/env python3
"""
UST v5 - LIGO Gravitational Wave Data Analysis
Tests T_Om threshold filtering on real GW150914 data
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftfreq
import requests
import h5py
from io import BytesIO

# UST v5 Constants
T_OM = 0.232529  # Tunneling threshold
C_CB = 0.366455  # Channel connection
N_SQ = 0.633545  # Active seal

class USTLIGOAnalyzer:
    def __init__(self):
        self.sample_rate = 4096  # Hz
        self.t_om = T_OM
        
    def download_ligo_data(self):
        """Download real LIGO GW150914 data"""
        print("Downloading LIGO GW150914 data...")
        
        # GWOSC (Gravitational Wave Open Science Center) URL
        url = "https://www.gw-openscience.org/eventapi/html/GWTC-1-confident/GW150914/v3/H-H1_GWOSC_4KHZ_R1-1126259447-32.hdf5"
        
        try:
            response = requests.get(url, timeout=30)
            with h5py.File(BytesIO(response.content), 'r') as f:
                strain = f['strain']['Strain'][:]
                
            print(f"✓ Downloaded {len(strain)} samples")
            return strain
            
        except Exception as e:
            print(f"Download failed: {e}")
            print("Generating synthetic test data...")
            return self.generate_synthetic_gw()
    
    def generate_synthetic_gw(self):
        """Generate synthetic gravitational wave for testing"""
        t = np.linspace(0, 4, self.sample_rate * 4)
        
        # Chirp signal (simplified)
        f0, f1 = 35, 250  # Hz
        chirp = signal.chirp(t, f0, t[-1], f1, method='quadratic')
        
        # Add noise
        noise = np.random.normal(0, 0.5, len(t))
        
        return chirp * 1e-21 + noise * 1e-21
    
    def apply_ust_filter(self, data):
        """Apply UST topological filter"""
        # FFT
        fft_data = fft(data)
        freqs = fftfreq(len(data), 1/self.sample_rate)
        
        # Calculate noise threshold
        noise_median = np.median(np.abs(fft_data))
        threshold = self.t_om * noise_median
        
        # UST Filter: Zero out sub-threshold (Omnium channel)
        fft_filtered = fft_data.copy()
        mask = np.abs(fft_data) < threshold
        fft_filtered[mask] = 0
        
        # Back to time domain
        filtered_data = np.fft.ifft(fft_filtered).real
        
        # Calculate statistics
        original_size = len(data) * 8  # bytes
        ust_size = np.sum(~mask) * 8
        compression = (1 - ust_size/original_size) * 100
        
        return filtered_data, compression, mask
    
    def calculate_snr(self, signal_data, noise_data):
        """Calculate Signal-to-Noise Ratio"""
        signal_power = np.mean(signal_data**2)
        noise_power = np.mean(noise_data**2)
        
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = np.inf
            
        return snr
    
    def analyze(self):
        """Main analysis pipeline"""
        # Get data
        strain = self.download_ligo_data()
        
        # Apply UST filter
        filtered, compression, mask = self.apply_ust_filter(strain)
        
        # Calculate SNR
        snr_original = self.calculate_snr(strain, strain[:1000])
        snr_ust = self.calculate_snr(filtered, filtered[:1000])
        snr_loss = snr_original - snr_ust
        
        # Results
        print("\n" + "="*60)
        print("UST v5 LIGO ANALYSIS RESULTS")
        print("="*60)
        print(f"Data compression: {compression:.2f}%")
        print(f"SNR (Original):   {snr_original:.2f} dB")
        print(f"SNR (UST):        {snr_ust:.2f} dB")
        print(f"SNR Loss:         {snr_loss:.2f} dB")
        print(f"T_Om threshold:   {self.t_om:.6f}")
        print("="*60)
        
        # Expected: ~31% compression, <1 dB SNR loss
        if 25 < compression < 40 and snr_loss < 2:
            print("✓ UST PREDICTION CONFIRMED!")
        else:
            print("⚠ Results differ from UST prediction")
        
        # Plot
        self.plot_results(strain, filtered, mask)
        
        return {
            'compression': compression,
            'snr_original': snr_original,
            'snr_ust': snr_ust,
            'snr_loss': snr_loss
        }
    
    def plot_results(self, original, filtered, mask):
        """Visualize results"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        t = np.arange(len(original)) / self.sample_rate
        
        # Time domain
        axes[0].plot(t[:2000], original[:2000], 'b-', alpha=0.7, label='Original')
        axes[0].plot(t[:2000], filtered[:2000], 'r-', alpha=0.9, label='UST Filtered')
        axes[0].set_xlabel('Time (s)')
        axes[0].set_ylabel('Strain')
        axes[0].set_title('LIGO Strain Data - Time Domain')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Frequency domain
        fft_orig = np.abs(fft(original))
        fft_filt = np.abs(fft(filtered))
        freqs = fftfreq(len(original), 1/self.sample_rate)
        
        valid = (freqs > 0) & (freqs < 500)
        axes[1].loglog(freqs[valid], fft_orig[valid], 'b-', alpha=0.7, label='Original')
        axes[1].loglog(freqs[valid], fft_filt[valid], 'r-', alpha=0.9, label='UST Filtered')
        axes[1].set_xlabel('Frequency (Hz)')
        axes[1].set_ylabel('Amplitude')
        axes[1].set_title('Frequency Domain - UST T_Om Filtering')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Filtered fraction
        axes[2].plot(freqs[valid], mask[valid].astype(int), 'k-', linewidth=2)
        axes[2].fill_between(freqs[valid], 0, mask[valid].astype(int), alpha=0.3)
        axes[2].set_xlabel('Frequency (Hz)')
        axes[2].set_ylabel('Filtered (1=yes)')
        axes[2].set_title('UST Omnium Channel Assignment')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('ust_ligo_analysis.png', dpi=300, bbox_inches='tight')
        print("\n✓ Plot saved: ust_ligo_analysis.png")
        plt.show()


# Run analysis
if __name__ == "__main__":
    analyzer = USTLIGOAnalyzer()
    results = analyzer.analyze()
    
    print("\nResults dictionary:")
    print(results)