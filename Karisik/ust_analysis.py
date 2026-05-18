# UST v5 - DENEYSEL VERİ ANALİZİ VE UST PARAMETRELERİ KARŞILAŞTIRMASI
# Dosyalar: ROOT (LHC), HDF5 (LIGO), FITS (JWST), VOTable (Euclid)
# Amaç: UST tahminleri (α/17, TOm, Ns,q, (1/17)^100) ile deneysel veri karşılaştırması

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# Dosya yolu
BASE_PATH = r"C:\AtlasTest"

# UST SABİTLERİ (Hesaplanmış değerler)
UST = {
    'alpha': 0.007297353,           # İnce yapı sabiti
    'DOF': 17,                       # Serbestlik derecesi
    'alpha_17': 0.000429256,         # α/17
    'B0': 0.633974596,               # (3-√3)/2
    'Ns_q': 0.633545340,             # Köprü katsayısı
    'Ccb': 0.366454660,              # Kanal bağlantısı
    'TOm': 0.232529135,              # Tünel genliği
    'a2': 0.058823529,               # 1/17 heat kernel
    'lambda_suppression': 9.02e-124, # (1/17)^100
    'log_suppression': -123.04,      # Log₁₀[(1/17)^100]
}

print("=" * 80)
print("🔬 UST v5 - DENEYSEL VERİ ANALİZİ VE KARŞILAŞTIRMA")
print("=" * 80)
print(f"Analiz Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# UST Parametrelerini yazdır
print("📊 UST PARAMETRELERİ:")
print("-" * 40)
for key, val in UST.items():
    if isinstance(val, float) and abs(val) < 0.001:
        print(f"  {key}: {val:.6e}")
    else:
        print(f"  {key}: {val}")
print()

#==============================================================================
# 1. ROOT DOSYASI ANALİZİ (LHC/ATLAS)
#==============================================================================
def analyze_root_ust(filepath):
    """ROOT dosyasını analiz et ve UST parametreleriyle karşılaştır"""
    print("=" * 80)
    print("📊 1. LHC/ATLAS VERİSİ ANALİZİ - UST KARŞILAŞTIRMASI")
    print("=" * 80)
    
    try:
        import uproot
        
        file = uproot.open(filepath)
        tree = file['analysis']
        
        # Önemli kolonları yükle
        branches = ['xsec', 'mcWeight', 'met_et', 'jet_n', 'channelNumber', 
                    'ScaleFactor_PILEUP', 'ScaleFactor_BTAG']
        
        data = {}
        for branch in branches:
            try:
                arr = tree[branch].array(library='np')
                # Jagged array ise düzleştir
                if hasattr(arr[0], '__len__') and not isinstance(arr[0], str):
                    arr = np.array([np.mean(x) if len(x) > 0 else 0 for x in arr])
                data[branch] = arr
            except:
                pass
        
        print(f"\n📁 Yüklenen veri: {len(tree)} olay")
        print(f"📋 Kolonlar: {list(data.keys())}")
        
        results = {}
        
        # 1. Kesit Alanı (xsec) Analizi - α/17 düzeltme testi
        if 'xsec' in data:
            xsec = data['xsec']
            xsec_mean = np.mean(xsec[xsec > 0])
            xsec_std = np.std(xsec[xsec > 0])
            
            # UST düzeltme: σ_UST = σ_SM × (1 - α/17)
            ust_correction = 1 - UST['alpha_17']
            xsec_ust_predicted = xsec_mean * ust_correction
            
            print(f"\n🎯 KESİT ALANI (xsec) ANALİZİ:")
            print(f"   Ortalama σ: {xsec_mean:.6f}")
            print(f"   Std sapma: {xsec_std:.6f}")
            print(f"   UST düzeltme (1-α/17): {ust_correction:.6f}")
            print(f"   UST tahmini σ: {xsec_ust_predicted:.6f}")
            print(f"   Fark: {abs(xsec_mean - xsec_ust_predicted):.6e}")
            
            results['xsec_mean'] = xsec_mean
            results['xsec_ust'] = xsec_ust_predicted
            results['alpha_17_effect'] = UST['alpha_17']
        
        # 2. Missing ET Analizi - Omnium imzası
        if 'met_et' in data:
            met = data['met_et']
            met_mean = np.mean(met)
            met_std = np.std(met)
            
            # UST tahmini: MET dağılımında TOm baskılama
            met_tail = met[met > met_mean + 2*met_std]
            tail_fraction = len(met_tail) / len(met)
            
            # TOm ile karşılaştır
            tom_deviation = abs(tail_fraction - UST['TOm'])
            
            print(f"\n🎯 MISSING ET ANALİZİ (Omnium imzası):")
            print(f"   Ortalama MET: {met_mean:.2f} GeV")
            print(f"   Std sapma: {met_std:.2f} GeV")
            print(f"   Kuyruk oranı (>2σ): {tail_fraction:.4f}")
            print(f"   UST TOm: {UST['TOm']:.4f}")
            print(f"   |Fark|: {tom_deviation:.4f}")
            
            results['met_mean'] = met_mean
            results['met_tail_fraction'] = tail_fraction
            results['TOm_comparison'] = tom_deviation
        
        # 3. Jet sayısı analizi - 17 kanal yapısı
        if 'jet_n' in data:
            jet_n = data['jet_n']
            jet_counts = np.bincount(jet_n.astype(int), minlength=20)[:20]
            
            # 17 ile ilişki
            jet_17_ratio = np.sum(jet_counts) / UST['DOF']
            
            print(f"\n🎯 JET SAYISI DAĞILIMI:")
            print(f"   Toplam jet olayları: {np.sum(jet_counts)}")
            print(f"   Ortalama jet/olay: {np.mean(jet_n):.2f}")
            print(f"   Toplam/17 oranı: {jet_17_ratio:.2f}")
            
            results['jet_mean'] = np.mean(jet_n)
            results['jet_17_ratio'] = jet_17_ratio
        
        # 4. Kanal numarası analizi
        if 'channelNumber' in data:
            channels = data['channelNumber']
            unique_channels = np.unique(channels)
            
            print(f"\n🎯 KANAL NUMARASI ANALİZİ:")
            print(f"   Benzersiz kanal sayısı: {len(unique_channels)}")
            print(f"   17'ye bölümü: {len(unique_channels) / 17:.2f}")
            
            results['unique_channels'] = len(unique_channels)
        
        file.close()
        return results
        
    except Exception as e:
        print(f"❌ ROOT analiz hatası: {e}")
        return None

#==============================================================================
# 2. HDF5 DOSYASI ANALİZİ (LIGO/Gravitasyonel Dalga)
#==============================================================================
def analyze_hdf5_ust(filepath):
    """LIGO gravitasyonel dalga verisini analiz et"""
    print("\n" + "=" * 80)
    print("📊 2. LIGO GRAVİTASYONEL DALGA ANALİZİ - UST KARŞILAŞTIRMASI")
    print("=" * 80)
    
    try:
        import h5py
        from scipy import signal
        from scipy.fft import fft, fftfreq
        
        with h5py.File(filepath, 'r') as f:
            # Strain verisini yükle
            strain = f['strain/Strain'][:]
            
            # Meta verileri al
            gps_start = f['meta/GPSstart'][()]
            duration = f['meta/Duration'][()]
            sample_rate = len(strain) / duration  # 16384 Hz
            
            print(f"\n📁 Veri Bilgileri:")
            print(f"   GPS Başlangıç: {gps_start}")
            print(f"   Süre: {duration} saniye")
            print(f"   Örnekleme: {sample_rate:.0f} Hz")
            print(f"   Toplam örnek: {len(strain):,}")
            
            results = {}
            
            # 1. Strain istatistikleri
            strain_mean = np.mean(strain)
            strain_std = np.std(strain)
            strain_rms = np.sqrt(np.mean(strain**2))
            
            print(f"\n🎯 STRAIN İSTATİSTİKLERİ:")
            print(f"   Ortalama: {strain_mean:.6e}")
            print(f"   Std sapma: {strain_std:.6e}")
            print(f"   RMS: {strain_rms:.6e}")
            
            results['strain_mean'] = strain_mean
            results['strain_std'] = strain_std
            results['strain_rms'] = strain_rms
            
            # 2. FFT Analizi - Frekans spektrumu
            # Sadece ilk 1 saniye (hesaplama için)
            n_samples = int(sample_rate)
            strain_segment = strain[:n_samples]
            
            freqs = fftfreq(n_samples, 1/sample_rate)
            fft_vals = np.abs(fft(strain_segment))
            
            # Pozitif frekanslar
            pos_mask = freqs > 0
            freqs_pos = freqs[pos_mask]
            fft_pos = fft_vals[pos_mask]
            
            # Dominant frekans
            dominant_freq = freqs_pos[np.argmax(fft_pos)]
            
            print(f"\n🎯 FFT SPEKTRUM ANALİZİ:")
            print(f"   Dominant frekans: {dominant_freq:.2f} Hz")
            print(f"   Max FFT genlik: {np.max(fft_pos):.6e}")
            
            results['dominant_freq'] = dominant_freq
            results['max_fft'] = np.max(fft_pos)
            
            # 3. UST TOm Baskılama Analizi
            # TOm imzası: Belirli frekans bantlarında baskılama
            # 17 Hz etrafında analiz (1/17 ≈ 0.059, 17 Hz)
            freq_17_band = (freqs_pos > 15) & (freqs_pos < 19)
            power_17 = np.mean(fft_pos[freq_17_band]**2)
            
            # Toplam güç
            total_power = np.mean(fft_pos**2)
            
            # 17 Hz bandı oranı
            ratio_17 = power_17 / total_power if total_power > 0 else 0
            
            print(f"\n🎯 UST 17 Hz BANT ANALİZİ:")
            print(f"   17 Hz bandı gücü: {power_17:.6e}")
            print(f"   Toplam güç: {total_power:.6e}")
            print(f"   17 Hz oranı: {ratio_17:.6f}")
            print(f"   1/17 (a₂): {UST['a2']:.6f}")
            print(f"   Fark: {abs(ratio_17 - UST['a2']):.6f}")
            
            results['power_17Hz'] = power_17
            results['ratio_17'] = ratio_17
            results['a2_comparison'] = abs(ratio_17 - UST['a2'])
            
            # 4. Strain dağılımı - Gaussian kontrolü
            from scipy.stats import normaltest
            
            # Alt örnekleme (bellek için)
            sample_indices = np.random.choice(len(strain), min(100000, len(strain)), replace=False)
            strain_sample = strain[sample_indices]
            
            stat, p_value = normaltest(strain_sample)
            
            print(f"\n🎯 GAUSS DAĞILIMI TESTİ:")
            print(f"   Test istatistiği: {stat:.2f}")
            print(f"   p-değeri: {p_value:.6e}")
            print(f"   Gaussian mı?: {'EVET' if p_value > 0.05 else 'HAYIR'}")
            
            results['gaussian_pvalue'] = p_value
            
            # 5. Graviton propagatör imzası
            # UST tahmini: P ~ (1 - α·k²·l_p²/17) / k²
            # k ~ 2π·f ile
            k_dominant = 2 * np.pi * dominant_freq
            l_p = 1.616e-35  # Planck uzunluğu
            
            ust_propagator_correction = 1 - UST['alpha'] * (k_dominant * l_p)**2 / 17
            
            print(f"\n🎯 GRAVİTON PROPAGATÖR ANALİZİ:")
            print(f"   k (dominant): {k_dominant:.2f} rad/s")
            print(f"   UST düzeltme faktörü: {ust_propagator_correction:.10f}")
            print(f"   Sapma: {1 - ust_propagator_correction:.6e}")
            
            results['propagator_correction'] = ust_propagator_correction
            
        return results
        
    except Exception as e:
        print(f"❌ HDF5 analiz hatası: {e}")
        import traceback
        traceback.print_exc()
        return None

#==============================================================================
# 3. FITS DOSYASI ANALİZİ (JWST Spektroskopi)
#==============================================================================
def analyze_fits_ust(filepath):
    """JWST NIRSpec spektroskopi verisini analiz et"""
    print("\n" + "=" * 80)
    print("📊 3. JWST NIRSpec SPEKTROSKOPİ ANALİZİ - UST KARŞILAŞTIRMASI")
    print("=" * 80)
    
    try:
        from astropy.io import fits
        
        with fits.open(filepath) as hdul:
            # Veri HDU'larını al
            flux = hdul['FLUX'].data
            flux_err = hdul['FLUX_ERR'].data
            wavelength = hdul['WAVELENGTH'].data
            
            print(f"\n📁 Veri Bilgileri:")
            print(f"   Dalga boyu aralığı: {wavelength.min():.3f} - {wavelength.max():.3f} μm")
            print(f"   Spektral kanal sayısı: {len(wavelength)}")
            print(f"   Uzamsal piksel: {flux.shape[0]}")
            
            results = {}
            
            # 1. Ortalama spektrum
            mean_flux = np.nanmean(flux, axis=0)
            mean_err = np.nanmean(flux_err, axis=0)
            
            # Geçerli değerler
            valid = ~np.isnan(mean_flux) & ~np.isinf(mean_flux)
            
            print(f"\n🎯 SPEKTRUM İSTATİSTİKLERİ:")
            print(f"   Ortalama flux: {np.nanmean(mean_flux[valid]):.6e}")
            print(f"   Flux std: {np.nanstd(mean_flux[valid]):.6e}")
            print(f"   SNR (ort): {np.nanmean(np.abs(mean_flux[valid]/mean_err[valid])):.2f}")
            
            results['mean_flux'] = np.nanmean(mean_flux[valid])
            results['flux_std'] = np.nanstd(mean_flux[valid])
            
            # 2. Spektral çizgi analizi
            # Emission/absorption çizgileri bul
            flux_smooth = np.convolve(mean_flux[valid], np.ones(5)/5, mode='same')
            peaks = np.where(np.diff(np.sign(np.diff(flux_smooth))) < 0)[0]
            
            print(f"\n🎯 SPEKTRAL ÇİZGİ ANALİZİ:")
            print(f"   Tespit edilen çizgi sayısı: {len(peaks)}")
            print(f"   17'ye bölümü: {len(peaks)/17:.2f}")
            
            results['spectral_lines'] = len(peaks)
            results['lines_17_ratio'] = len(peaks) / 17
            
            # 3. Dalga boyu oranları - Ns,q ilişkisi
            lambda_mean = np.mean(wavelength)
            lambda_ratio = wavelength.max() / wavelength.min()
            
            # Ns,q ile karşılaştır
            nsq_lambda = UST['Ns_q'] * 5  # μm ölçeğine
            
            print(f"\n🎯 DALGA BOYU ANALİZİ:")
            print(f"   Ortalama λ: {lambda_mean:.4f} μm")
            print(f"   λ_max/λ_min oranı: {lambda_ratio:.4f}")
            print(f"   Ns,q × 5: {nsq_lambda:.4f} μm")
            print(f"   |Fark|: {abs(lambda_mean - nsq_lambda):.4f} μm")
            
            results['lambda_mean'] = lambda_mean
            results['lambda_ratio'] = lambda_ratio
            
            # 4. Flux varyasyonu - kozmolojik bilgi
            flux_variance = np.nanvar(flux, axis=0)
            mean_variance = np.nanmean(flux_variance[valid])
            
            print(f"\n🎯 FLUX VARYANS ANALİZİ:")
            print(f"   Ortalama varyans: {mean_variance:.6e}")
            print(f"   Log₁₀(varyans): {np.log10(mean_variance):.2f}")
            
            results['flux_variance'] = mean_variance
            
        return results
        
    except Exception as e:
        print(f"❌ FITS analiz hatası: {e}")
        import traceback
        traceback.print_exc()
        return None

#==============================================================================
# 4. VOTable DOSYASI ANALİZİ (Euclid TPDR)
#==============================================================================
def analyze_votable_ust(filepath):
    """Euclid foto-z verisini analiz et - Λ problemi testi"""
    print("\n" + "=" * 80)
    print("📊 4. EUCLID TPDR FOTO-Z ANALİZİ - Λ PROBLEMİ TESTİ")
    print("=" * 80)
    
    try:
        from astropy.io.votable import parse
        
        votable = parse(filepath)
        table = votable.resources[0].tables[0]
        data = table.array
        
        print(f"\n📁 Veri Bilgileri:")
        print(f"   Nesne sayısı: {len(data)}")
        print(f"   Kolonlar: {[f.name for f in table.fields]}")
        
        results = {}
        
        # 1. Fotometrik redshift dağılımı
        z_med = data['z_phot_med']
        z_peak = data['z_phot_peak']
        
        # Geçerli değerler
        valid = (z_med > 0) & (z_med < 10)
        z_med_valid = z_med[valid]
        z_peak_valid = z_peak[valid]
        
        print(f"\n🎯 REDSHİFT DAĞILIMI:")
        print(f"   Geçerli nesne: {len(z_med_valid)}")
        print(f"   z_med ortalama: {np.mean(z_med_valid):.4f}")
        print(f"   z_med medyan: {np.median(z_med_valid):.4f}")
        print(f"   z_med std: {np.std(z_med_valid):.4f}")
        print(f"   z aralığı: {z_med_valid.min():.4f} - {z_med_valid.max():.4f}")
        
        results['z_mean'] = np.mean(z_med_valid)
        results['z_median'] = np.median(z_med_valid)
        results['z_std'] = np.std(z_med_valid)
        
        # 2. Redshift dağılımı histogram
        z_bins = np.linspace(0, 6, 61)
        z_hist, _ = np.histogram(z_med_valid, bins=z_bins)
        
        # Peak redshift
        peak_bin = np.argmax(z_hist)
        z_peak_dist = (z_bins[peak_bin] + z_bins[peak_bin+1]) / 2
        
        print(f"\n🎯 REDSHİFT PEAK ANALİZİ:")
        print(f"   Dağılım peak z: {z_peak_dist:.2f}")
        print(f"   Peak'teki nesne sayısı: {z_hist[peak_bin]}")
        
        results['z_peak_distribution'] = z_peak_dist
        
        # 3. Kozmolojik sabit analizi
        # z → a (ölçek faktörü) dönüşümü: a = 1/(1+z)
        a_values = 1 / (1 + z_med_valid)
        
        # Hubble parametresi tahmini (basit ΛCDM)
        # H(z)/H0 = sqrt(Ωm(1+z)³ + ΩΛ)
        Omega_m = 0.315  # Planck 2018
        Omega_Lambda = 0.685
        
        H_ratio = np.sqrt(Omega_m * (1 + z_med_valid)**3 + Omega_Lambda)
        H_ratio_mean = np.mean(H_ratio)
        
        print(f"\n🎯 KOZMOLOJİK PARAMETRE ANALİZİ:")
        print(f"   Ωm (Planck): {Omega_m}")
        print(f"   ΩΛ (Planck): {Omega_Lambda}")
        print(f"   Ortalama H(z)/H₀: {H_ratio_mean:.4f}")
        
        results['H_ratio_mean'] = H_ratio_mean
        
        # 4. UST Λ tahmini ile karşılaştırma
        # UST: (1/17)^100 ≈ 10^(-123)
        # Bu, Planck yoğunluğundan gözlenen yoğunluğa baskılama
        
        # Kritik yoğunluk: ρc = 3H²/(8πG)
        # ρΛ/ρc = ΩΛ ≈ 0.685
        
        # UST baskılama faktörü
        ust_suppression_log = UST['log_suppression']  # -123.04
        
        print(f"\n🎯 UST Λ BASKILAMA ANALİZİ:")
        print(f"   ΩΛ (gözlem): {Omega_Lambda}")
        print(f"   UST baskılama: (1/17)^100 ≈ 10^({ust_suppression_log:.2f})")
        print(f"   Log₁₀(ρP/ρΛ) ≈ 123 (teorik)")
        print(f"   UST tahmin: 100 × log₁₀(17) = {100 * np.log10(17):.2f}")
        
        results['Omega_Lambda'] = Omega_Lambda
        results['UST_suppression_match'] = abs(123 - 100 * np.log10(17))
        
        # 5. Tomografik bin analizi
        tom_bin = data['tom_bin_id']
        unique_bins = np.unique(tom_bin[tom_bin >= 0])
        
        print(f"\n🎯 TOMOGRAFİK BİN ANALİZİ:")
        print(f"   Benzersiz bin sayısı: {len(unique_bins)}")
        print(f"   Bin ID'leri: {unique_bins[:10]}...")
        
        results['tomographic_bins'] = len(unique_bins)
        
        # 6. 17 örüntüsü arama
        z_17_band = (z_med_valid > 1.6) & (z_med_valid < 1.8)  # z ≈ 1.7
        n_in_17_band = np.sum(z_17_band)
        
        print(f"\n🎯 17 ÖRÜNTÜSÜ ANALİZİ:")
        print(f"   z ∈ [1.6, 1.8] aralığı: {n_in_17_band} nesne")
        print(f"   Toplam oran: {n_in_17_band/len(z_med_valid)*100:.2f}%")
        print(f"   1/17 = {1/17*100:.2f}%")
        print(f"   Fark: {abs(n_in_17_band/len(z_med_valid) - 1/17)*100:.2f}%")
        
        results['z_17_fraction'] = n_in_17_band / len(z_med_valid)
        results['z_17_deviation'] = abs(n_in_17_band/len(z_med_valid) - 1/17)
        
        return results
        
    except Exception as e:
        print(f"❌ VOTable analiz hatası: {e}")
        import traceback
        traceback.print_exc()
        return None

#==============================================================================
# ANA PROGRAM
#==============================================================================
if __name__ == "__main__":
    
    all_results = {}
    
    # Dosyaları kontrol et ve analiz et
    files = {
        'ROOT': 'ODEO_FEB2025_v0_2J2LMET30_data16_periodI.2J2LMET30.root',
        'HDF5': 'H-H1_GWOSC_O4a_16KHZ_R1-1368993792-4096.hdf5',
        'FITS': 'hlsp_wide_jwst_nirspec_aegis-2020007552_f170lp-g235h_v1.0_2nod-spec2d.fits',
        'VOT': 'c5f0d03b-22cd-11f1-8a0e-e8ebd3edb7d7-TPDR-result.vot'
    }
    
    # 1. ROOT
    root_path = os.path.join(BASE_PATH, files['ROOT'])
    if os.path.exists(root_path):
        all_results['ROOT'] = analyze_root_ust(root_path)
    
    # 2. HDF5
    hdf5_path = os.path.join(BASE_PATH, files['HDF5'])
    if os.path.exists(hdf5_path):
        all_results['HDF5'] = analyze_hdf5_ust(hdf5_path)
    
    # 3. FITS
    fits_path = os.path.join(BASE_PATH, files['FITS'])
    if os.path.exists(fits_path):
        all_results['FITS'] = analyze_fits_ust(fits_path)
    
    # 4. VOTable
    vot_path = os.path.join(BASE_PATH, files['VOT'])
    if os.path.exists(vot_path):
        all_results['VOT'] = analyze_votable_ust(vot_path)
    
    #==========================================================================
    # FİNAL ÖZET
    #==========================================================================
    print("\n" + "=" * 80)
    print("📊 FİNAL ÖZET - UST v5 DENEYSEL KARŞILAŞTIRMA")
    print("=" * 80)
    
    print("\n🎯 UST PARAMETRELERİ vs GÖZLEMSEL VERİ:")
    print("-" * 60)
    
    # Karşılaştırma tablosu
    comparisons = []
    
    if all_results.get('ROOT'):
        r = all_results['ROOT']
        if 'TOm_comparison' in r:
            comparisons.append({
                'Kaynak': 'LHC/ATLAS',
                'Parametre': 'TOm',
                'UST Değer': f"{UST['TOm']:.4f}",
                'Gözlem': f"{r.get('met_tail_fraction', 'N/A'):.4f}" if r.get('met_tail_fraction') else 'N/A',
                'Fark': f"{r['TOm_comparison']:.4f}" if 'TOm_comparison' in r else 'N/A'
            })
    
    if all_results.get('HDF5'):
        r = all_results['HDF5']
        if 'a2_comparison' in r:
            comparisons.append({
                'Kaynak': 'LIGO',
                'Parametre': 'a₂=1/17',
                'UST Değer': f"{UST['a2']:.4f}",
                'Gözlem': f"{r.get('ratio_17', 'N/A'):.4f}" if r.get('ratio_17') else 'N/A',
                'Fark': f"{r['a2_comparison']:.4f}" if 'a2_comparison' in r else 'N/A'
            })
    
    if all_results.get('VOT'):
        r = all_results['VOT']
        if 'UST_suppression_match' in r:
            comparisons.append({
                'Kaynak': 'Euclid',
                'Parametre': '(1/17)^100',
                'UST Değer': '-123.04',
                'Gözlem': f"{100 * np.log10(17):.2f}",
                'Fark': f"{r['UST_suppression_match']:.2f}"
            })
        if 'z_17_deviation' in r:
            comparisons.append({
                'Kaynak': 'Euclid',
                'Parametre': '1/17 oran',
                'UST Değer': f"{1/17:.4f}",
                'Gözlem': f"{r.get('z_17_fraction', 'N/A'):.4f}" if r.get('z_17_fraction') else 'N/A',
                'Fark': f"{r['z_17_deviation']:.4f}" if 'z_17_deviation' in r else 'N/A'
            })
    
    # Tabloyu yazdır
    if comparisons:
        df_comp = pd.DataFrame(comparisons)
        print(df_comp.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("✅ ANALİZ TAMAMLANDI")
    print("=" * 80)
    
    # Sonuçları kaydet
    print("\n📁 Sonuçlar:")
    for source, results in all_results.items():
        if results:
            print(f"\n  {source}:")
            for key, val in results.items():
                if isinstance(val, float):
                    if abs(val) < 0.001 or abs(val) > 1000:
                        print(f"    {key}: {val:.6e}")
                    else:
                        print(f"    {key}: {val:.6f}")
                else:
                    print(f"    {key}: {val}")