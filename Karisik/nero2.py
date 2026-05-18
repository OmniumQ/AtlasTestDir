import nibabel as nib
import numpy as np

# fMRI BOLD veri dosyasının yolu (Önceki doğrulanan dosya)
file_path = r"C:\AtlasTest\S1200.All.MyelinMap_BC_MSMAll.32k_fs_LR.dscalar.nii"

try:
    print("Veri yükleniyor... (Bu işlem dosya boyutuna göre birkaç saniye sürebilir)")
    img = nib.load(file_path)
    
    # Veriyi 1 Boyutlu (1D) sürekli matrise düzleştirme ve olası NaN/Sıfır hatalarını temizleme
    data = img.get_fdata().flatten()
    data = data[~np.isnan(data)]
    
    # UST v5 Evrensel Sabitleri
    T_Om = 0.23252885
    N_b  = 0.63354460
    C_cb = 1 - N_b
    
    print("\n--- 1. FİZİKSEL EŞİK (COHEN'S D) VE STANDART SAPMA HARİTALAMASI ---")
    mean_val = np.mean(data)
    std_val = np.std(data)
    print(f"Ağın Ortalama Aktivasyonu: {mean_val:.6f}")
    print(f"Ağın Standart Sapması (1 Sigma): {std_val:.6f}")
    
    # Yüzdelik Dilim (Percentile) Eşiklerinin Hesaplanması
    thr_TOm = np.percentile(data, T_Om * 100)
    thr_Nb = np.percentile(data, N_b * 100)
    
    print(f"\nKanal C Eşiği (T_Om - %23.25): {thr_TOm:.6f} Cohen's d")
    print(f"Kanal Q Eşiği (N_b - %63.35): {thr_Nb:.6f} Cohen's d")
    
    print("\n--- 2. ADIM 1: ONL ÜÇ BÖLGELİ BÖLÜMLEME (DÖNGÜSEL TEST KONTROLÜ) ---")
    # Ağdaki verilerin belirlenen eşiklere göre fraksiyonlara (bölgelere) ayrılması
    count_C = np.sum(data < thr_TOm)
    count_Om = np.sum((data >= thr_TOm) & (data < thr_Nb))
    count_Q = np.sum(data >= thr_Nb)
    total_nodes = len(data)
    
    f_C = count_C / total_nodes
    f_Om = count_Om / total_nodes
    f_Q = count_Q / total_nodes
    
    print(f"Kanal C (Dondurulmuş Arka Plan) Oranı   : {f_C:.6f} | UST Teorik: {T_Om:.6f} | Fark: {abs(f_C - T_Om):.6f}")
    print(f"0-Element (Omnium Geçiş Bölgesi) Oranı  : {f_Om:.6f} | UST Teorik: {(N_b - T_Om):.6f} | Fark: {abs(f_Om - (N_b - T_Om)):.6f}")
    print(f"Kanal Q (Aktif Enformasyon Akışı) Oranı : {f_Q:.6f} | UST Teorik: {C_cb:.6f} | Fark: {abs(f_Q - C_cb):.6f}")

    print("\n--- 3. METODOLOJİK UYARI ---")
    print("Fraksiyonların teorik değerlerle kusursuz eşleşmesi matematiksel bir konstrüksiyondur (döngüsel test).")
    print("Fiziğin asıl doğrulaması, Cohen's d fiziksel eşiklerinin sıfır noktası veya sigma değerleriyle olan simetrisinde aranmalıdır.")

except Exception as e:
    print("Bir hata oluştu:", str(e))