import pandas as pd
import numpy as np

# -------------------------------------------------------------------
# 1. UST BİLGİ KANALLARI (VERİ YÜKLEME VE BİRLEŞTİRME)
# -------------------------------------------------------------------
def load_and_merge_ust_data():
    file_paths = [
        r"C:\Users\info\Downloads\fintables_hisse_senetleri.xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (1).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (2).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (3).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (4).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (5).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (6).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (7).xlsx"
    ]
    
    print("UST Bilgi Kanalları başlatılıyor... Dosyalar okunuyor.")
    
    merged_df = None
    for path in file_paths:
        try:
            df = pd.read_excel(path)
            if merged_df is None:
                merged_df = df
            else:
                # "Şirket" (veya Kod) kolonuna göre matrisleri senkronize et
                common_col = [col for col in df.columns if "şirket" in col.lower() or "kod" in col.lower()][0]
                merged_col = [col for col in merged_df.columns if "şirket" in col.lower() or "kod" in col.lower()][0]
                
                # Sadece ortak şirketleri al ve tekrar eden kolonları sil
                df = df.rename(columns={common_col: "Şirket"})
                merged_df = merged_df.rename(columns={merged_col: "Şirket"})
                
                cols_to_use = df.columns.difference(merged_df.columns).tolist() + ["Şirket"]
                merged_df = pd.merge(merged_df, df[cols_to_use], on="Şirket", how="inner")
        except Exception as e:
            print(f"Hata - Kanal Okunamadı: {path} -> {e}")
            
    return merged_df

# -------------------------------------------------------------------
# 2. VERİ TEMİZLEME VE NÜMERİK TRANSFORMASYON
# -------------------------------------------------------------------
def clean_numeric_data(val):
    if isinstance(val, str):
        val = val.replace('%', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(val)
        except:
            return np.nan
    return val

# -------------------------------------------------------------------
# 3. P-ADİK RİSK VE UZUN VADE HESAPLAMA (SPEC-Z)
# -------------------------------------------------------------------
def calculate_long_term_risk(row):
    risk_score = 0
    
    # 1. Çarpan Riskleri (Değerleme Balonu Filtresi)
    fk = row.get('F/K', np.nan)
    pddd = row.get('PD/DD', np.nan)
    
    if pd.notna(fk) and (fk < 0 or fk > 25): risk_score += 2
    if pd.notna(pddd) and (pddd > 8): risk_score += 1
    
    # 2. Finansal Borç ve Kaldıraç Uyumsuzluğu
    kaldirac = row.get('Kaldıraç Oranı', np.nan)
    if pd.notna(kaldirac) and kaldirac > 70: risk_score += 2
    
    # 3. Uzun Vade Getiri Tutarlılığı (1, 3, 5 Yıl)
    getiri_5y = row.get('5 Yıl Getiri %', np.nan)
    getiri_3y = row.get('3 Yıl Getiri %', np.nan)
    
    if pd.notna(getiri_5y) and getiri_5y < 0: risk_score += 2
    if pd.notna(getiri_3y) and getiri_3y < 0: risk_score += 1

    # Karar Matrisi
    if risk_score >= 3:
        return "RİSKLİ (Uzak Dur)"
    elif risk_score == 0:
        return "RİSKSİZ (Temel Sağlam)"
    else:
        return "NÖTR (Gözlemde)"

# -------------------------------------------------------------------
# 4. OPTİMAL COUPLING KISA VADE SİNYALLER VE FİBONACCİ SEVİYELERİ
# -------------------------------------------------------------------
def calculate_short_term_signals(row):
    # Fiyat ve kısa vade ivme
    fiyat = row.get('Fiyat', np.nan)
    getiri_1a = row.get('1 Ay Getiri %', np.nan)
    getiri_1h = row.get('1 Hafta Getiri %', np.nan)
    
    if pd.isna(fiyat) or fiyat <= 0:
        return "VERİ YOK", 0, 0, 0
        
    sinyal = "BEKLE"
    
    # İvme (Momentum) kontrolü
    if pd.notna(getiri_1a) and pd.notna(getiri_1h):
        # Eğer hisse 1 ayda çok düşmüş ama 1 haftada toparlıyorsa -> Dip Dönüşü (Al)
        if getiri_1a < -10 and getiri_1h > 2:
            sinyal = "HEMEN AL"
        # Eğer hisse 1 ayda çok şişmiş ve 1 haftada eksiye geçmişse -> Tepe Dönüşü (Sat)
        elif getiri_1a > 20 and getiri_1h < -2:
            sinyal = "HEMEN SAT"
        elif getiri_1a > 0 and getiri_1h > 0:
            sinyal = "KADEMELİ AL"

    # UST Fibonacci Modülasyonu ile Seviyeler
    # Fiyatın belirli katsayıları ile destek/direnç izolasyonu
    fiyat = float(fiyat)
    
    if sinyal in ["HEMEN AL", "KADEMELİ AL"]:
        # Giriş için %3'lük p-adik geri çekilme payı bırak
        uygun_alim_noktasi = fiyat * 0.97 
        # Zarar Kes (Fibonacci %8 sönümleme)
        stop_loss = fiyat * 0.92 
        # Kar Al (Fibonacci %13 genişleme)
        kar_al = fiyat * 1.13
    elif sinyal == "HEMEN SAT":
        uygun_alim_noktasi = fiyat * 0.85 # Çok düşmeden alma
        stop_loss = 0 # Elde tutma
        kar_al = 0
    else:
        uygun_alim_noktasi = fiyat
        stop_loss = fiyat * 0.95
        kar_al = fiyat * 1.05

    return sinyal, uygun_alim_noktasi, stop_loss, kar_al

# -------------------------------------------------------------------
# 5. ANA YÜRÜTME MOTORU (MAIN)
# -------------------------------------------------------------------
def generate_ust_report():
    df = load_and_merge_ust_data()
    
    if df is None or df.empty:
        print("Hata: Veri matrisi oluşturulamadı. Dosya yollarını kontrol edin.")
        return

    # Sadece analiz için gerekli tüm kolonları nümeriğe çevir
    for col in df.columns:
        if col != "Şirket":
            df[col] = df[col].apply(clean_numeric_data)

    # Rapor kolonlarını oluştur
    rapor_listesi = []
    
    for index, row in df.iterrows():
        sirket = row.get('Şirket', 'Bilinmeyen')
        fiyat = row.get('Fiyat', np.nan)
        
        # 1. Uzun Vade P-Adik Risk
        uzun_vade_durum = calculate_long_term_risk(row)
        
        # 2. Kısa Vade Alfa Sinyalleri ve Seviyeler
        sinyal, alim_noktasi, stop_loss, kar_al = calculate_short_term_signals(row)
        
        rapor_listesi.append({
            "Şirket": sirket,
            "Güncel Fiyat": fiyat,
            "Uzun Vade Rasyonel Durum": uzun_vade_durum,
            "Kısa Vade Aksiyon Sinyali": sinyal,
            "Uygun Alım Noktası": round(alim_noktasi, 2) if alim_noktasi else "-",
            "Zarar Kes (Stop-Loss)": round(stop_loss, 2) if stop_loss else "-",
            "Rasyonel Kar Hedefi": round(kar_al, 2) if kar_al else "-"
        })

    # Sonuç Matrisi
    rapor_df = pd.DataFrame(rapor_listesi)
    
    # Filtreleme: Hem uzun vade RİSKSİZ hem de kısa vade AL veren en iyi senaryoları öne çıkar
    rapor_df = rapor_df.sort_values(by=["Uzun Vade Rasyonel Durum", "Kısa Vade Aksiyon Sinyali"])
    
    # Excel olarak dışa aktar
    output_path = r"C:\Users\info\Downloads\UST_Finansal_Rapor.xlsx"
    rapor_df.to_excel(output_path, index=False)
    
    print("\n--- UST RASYONEL KARAR MATRİSİ ÖZETİ ---")
    print(rapor_df.head(15).to_string(index=False))
    print(f"\nİşlem Tamamlandı. Tam analiz raporu buraya kaydedildi: {output_path}")

if __name__ == "__main__":
    generate_ust_report()