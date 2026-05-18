import pandas as pd
import numpy as np

# 1. VERİ YÜKLEME
# 'atlas-higgs-challenge-2014-v2.csv' dosyasını yükleyin.
dosya_yolu = 'C:\\AtlasTest\\atlas-higgs-challenge-2014-v2.csv'
df = pd.read_csv(dosya_yolu)

# atlas-higgs-challenge-2014.pdf'e göre: 'Weight' ve 'KaggleWeight' simülatörün 
# yapay düzeltme ağırlıklarıdır. UST "sıfır serbest parametre" kuralı gereği DIŞLANIR.
# Doğrudan Ham Tau Enine Momentumu (PRI_tau_pt) veya Toplam Momentum (DER_pt_tot) alınır.
kolon = 'PRI_tau_pt' 
data = df[kolon].dropna()
n_samples = len(data)

# =====================================================================
# UST v5 KÖK SABİTLERİ (Kuantum-Kütleçekim Asimptotları)
# =====================================================================
N_b  = 0.63354460       # Blueprint Sabiti (Kanal Q aktif sınırı)
N_m  = 0.63353522       # Manifest Sabiti 
T_Om = 0.23252885       # Kanal C - WKB Tünelleme Genliği (Dondurulmuş Arka Plan)
C_cb = 0.36645540       # Kanal C ağırlığı (1 - N_b)
R_A  = N_b - N_m        # Kuantum Boşluğu (9.38e-6)
R_A2 = R_A**2           # CMB Skaler Genlik Tabanı (24 * R_A^2)
T11_hedef = 1.839210    # p_Q / p_C Hadronik Köprü Oranı

# Harmonik Vitesler (Gear 1 ve Gear 2)
kappa_1 = np.pi * N_b          # 1.990339
kappa_2 = 2 * np.pi * N_b      # 3.980678
V_b     = (1 + N_b) / (2 - N_b)# 1.195461

print("="*65)
print(f"ATLAS HIGGS 2014 SİMÜLASYONU VE UST v5 ONTOLOJİK TESTİ")
print(f"Toplam Olay: {n_samples} | İncelenen Değişken: {kolon}")
print("="*65)

# =====================================================================
# 1. OMNIUM NUMBER LINE (ONL) BÖLÜNMESİ
# =====================================================================
print("\n[ADIM 1] ONL ÜÇ-BÖLGE PARTİSYONU")
thr_TOm = np.percentile(data, T_Om * 100)
thr_Nb  = np.percentile(data, N_b * 100)

f_C  = len(data[data < thr_TOm]) / n_samples
f_Om = len(data[(data >= thr_TOm) & (data < thr_Nb)]) / n_samples
f_Q  = len(data[data >= thr_Nb]) / n_samples

print(f"Kanal C (Kütleçekim Gölgesi) : {f_C:.6f} (UST: {T_Om:.6f})")
print(f"0-Eleman (Omnium Geçişi)     : {f_Om:.6f} (UST: {(N_b - T_Om):.6f})")
print(f"Kanal Q (Aktif Evren)        : {f_Q:.6f} (UST: {C_cb:.6f})")
print("* Not: Yüzdelik dilimle bölündüğü için dairesel olarak eşleşecektir.")

# =====================================================================
# 2. R_A KUANTUM ÇÖZÜNÜRLÜK (SÜREKLİLİK) TESTİ
# =====================================================================
print("\n[ADIM 2] R_A PLANCK-ALTI METRİK ÇÖZÜNÜRLÜK TESTİ")
p_Q_Nb = np.percentile(data, N_b * 100)
p_Q_Nm = np.percentile(data, N_m * 100)
veri_farki_RA = p_Q_Nb - p_Q_Nm

print(f"Teorik R_A (Blueprint-Manifest)  : {R_A:.8f}")
print(f"Kaggle Simülasyonundaki Fark     : {veri_farki_RA:.8f} GeV")
if veri_farki_RA == 0.0:
    print(">>> KRİTİK ÇÖKÜŞ: Simülatör enerjiyi ayrık (discrete) havuzlara bölmüştür.")
    print(">>> UST'nin alt-eV sürekli uzay-zaman çözünürlüğü bu sanal veride YOKTUR.")

# =====================================================================
# 3. T11 HADRONİK KÖPRÜ (KANAL C-Q İLETİŞİMİ)
# =====================================================================
print("\n[ADIM 3] T11 KANAL Q / KANAL C ÇİFT YÖNLÜ İLETİŞİM")
p_C = np.percentile(data, C_cb * 100)
iletisim_orani = p_Q_Nb / p_C
delta_yuzde = abs(iletisim_orani - T11_hedef) / T11_hedef * 100

print(f"Kanal Q Momentum Eşiği (p_Q) : {p_Q_Nb:.6f} GeV")
print(f"Kanal C Momentum Eşiği (p_C) : {p_C:.6f} GeV")
print(f"Hesaplanan Oran              : {iletisim_orani:.6f}")
print(f"UST v5 Evrensel Asimptotu    : {T11_hedef:.6f}")
print(f"Sapma (Delta %)              : %{delta_yuzde:.4f}")

if delta_yuzde > 1.0:
    print(">>> FALSİFİKASYON: Kanal Q ve C arası iletişim bu simülasyonda kopmuştur.")
    print(">>> Simülatör (Kaggle verisi), evrensel kütleçekim kilitlenmesini YANSITMAMAKTADIR.")

# =====================================================================
# 4. HARMONİK VİTESLER
# =====================================================================
print("\n[ADIM 4] HARMONİK VİTESLER (GEAR) ASİMPTOTLARI")
print(f"Gear 1 (κ1) : {kappa_1:.6f} | Gear 2 (κ2) : {kappa_2:.6f} | Geçiş (V_b) : {V_b:.6f}")
print("=================================================================")