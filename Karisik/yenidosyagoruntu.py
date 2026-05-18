from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

# FITS aç
hdul = fits.open(r"C:\AtlasTest\Euclid-VIS-ERO-Perseus-Flattened.v9-004.fits")

# 1. METADATA
print("📊 DOSYA BİLGİSİ:")
print(hdul.info())

# 2. GÖRÜNTÜ VERİSİ
data = hdul[0].data
print(f"\n🖼️ GÖRÜNTÜ: {data.shape}")
print(f"Min: {np.nanmin(data):.2f}")
print(f"Max: {np.nanmax(data):.2f}")
print(f"Mean: {np.nanmean(data):.2f}")

# 3. UST ANALİZİ (HIZLI)
# N_b = 0.633 pattern var mı?
intensity = data.flatten()
intensity = intensity[~np.isnan(intensity)]

percentile_63 = np.percentile(intensity, 63.3)
percentile_36 = np.percentile(intensity, 36.6)

print(f"\n🔬 UST ANALİZ:")
print(f"63.3%ile: {percentile_63:.2f}")
print(f"36.6%ile: {percentile_36:.2f}")
print(f"Ratio: {percentile_63/percentile_36:.3f}")

# 4. VİZUALİZE
plt.figure(figsize=(10, 10))
plt.imshow(data, cmap='gray', origin='lower')
plt.colorbar(label='Intensity')
plt.title('Euclid Perseus Cluster')
plt.tight_layout()
plt.savefig('perseus_euclid.png', dpi=150)
print("\n✅ Görüntü kaydedildi: perseus_euclid.png")

hdul.close()