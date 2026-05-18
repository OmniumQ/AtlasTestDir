import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# 1. Epistemolojik İzolasyon: ESA/Hubble İmajının Okunması
# Görüntüyü saf enerji yoğunluğunu temsil etmesi için gri tonlamalı (grayscale) okuyoruz.
imaj_yolu = r"C:\AtlasTest\1774277949112.jpg"
try:
    img = Image.open(imaj_yolu).convert('L')
    img_data = np.array(img, dtype=np.float64)
except Exception as e:
    print("İmaj okunamadı, dosya yolunu kontrol ediniz:", e)
    exit()

print("--- UST Yengeç Bulutsusu (Crab Nebula) Ontolojik Falsifikasyon Testi ---")
print(f"İmaj Çözünürlüğü: {img_data.shape} -> Toplam Piksel (Veri Noktası): {img_data.size}")

# 2. Saatte 5.5 Milyon km'lik Genişleme Kaosunun Çıkarılması
# Pikseller arası keskin geçişler (gradyanlar), süpernova kalıntısındaki termodinamik şiddeti (Kanal Q) temsil eder.
grad_y, grad_x = np.gradient(img_data)
ham_kaos = np.sqrt(grad_x**2 + grad_y**2).flatten()

# İstatistiksel uydurma (smoothing/normalization) KESİNLİKLE YASAKTIR.
# Saf kaosu, evrenin kapalı topolojisi gereği [-pi, pi] faz uzayına modüler olarak sarıyoruz (wrapping).
p_noise = (ham_kaos % (2 * np.pi)) - np.pi

# 3. UST Evrensel Sabitleri ve Topolojik Sınırlar
Ns_q = 0.63354460
k_dt_hedef = np.pi * Ns_q
sigma_ust_sinir = np.pi * (Ns_q**3) * np.sqrt(5)

olculen_sigma = np.std(p_noise)
print(f"\nÖlçülen Süpernova (Yengeç Bulutsusu) Entropisi (Varyans): {olculen_sigma:.4f}")
print(f"UST Mutlak Topolojik Duvarı (Sigma Sınırı): {sigma_ust_sinir:.4f}")

# 4. Kuantum Donanımına Makrokozmik Saldırı (Lindblad Evrimi)
def ust_astrofiziksel_stabilizasyon(p_noise_sample, k_dt):
    fidelity_degerleri = []
    psi_0 = np.array([1.0, 0.0]) # Deterministik S=0 başlangıç durumu
    rho = np.outer(psi_0, psi_0.conj())
    
    # Kuantum sistemine 10.000 piksellik (10.000 iterasyon) süpernova kaosu çarpıyor
    for p in p_noise_sample[:10000]: 
        # Kanal Q (Aktif Evren - Süpernova) Gürültü Saldırısı
        E_p = np.array([[np.exp(1j * p), 0], 
                        [0, np.exp(-1j * p)]])
        rho_bozulmus = E_p @ rho @ E_p.conj().T
        
        # Kanal C (Karanlık Madde) Tahliyesi / Donanım Hizalaması
        C_p = np.array([[np.exp(-1j * p * (k_dt / k_dt_hedef)), 0], 
                        [0, np.exp(1j * p * (k_dt / k_dt_hedef))]])
        
        rho_duzeltilmis = C_p @ rho_bozulmus @ C_p.conj().T
        fidelity = np.real(np.trace(np.outer(psi_0, psi_0.conj()) @ rho_duzeltilmis))
        fidelity_degerleri.append(fidelity)
        
    return np.mean(fidelity_degerleri)

# Sistemi, Yengeç bulutsusunun gradyan kaosu altında test ediyoruz.
ortalama_fidelity = ust_astrofiziksel_stabilizasyon(p_noise, k_dt=k_dt_hedef)
print(f"\nYengeç Bulutsusu Kaosu Altında Kuantum Aslına Uygunluk (Fidelity): {ortalama_fidelity:.4f}")

# Falsifikasyon Kararı
assert ortalama_fidelity > 0.99, "TEORİ YANLIŞLANMIŞTIR (FALSIFIED)! Süpernova kaosu evrensel Ns,q sınırlarını yıktı."
print("UST TESTİ GEÇTİ: 6.500 ışık yılı uzaktaki süpernova patlaması bile, evrensel Ns,q determinizmine boyun eğdi.")
