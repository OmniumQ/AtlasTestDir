import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def ust_derin_analiz_motoru():
    # 1. Kullanıcının Belirttiği Dosya Yolları
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
    
    print("Veri matrisleri okunuyor ve 'Şirket' kolonuna göre birleştiriliyor...")
    
    merged_df = None
    for path in file_paths:
        try:
            df = pd.read_excel(path)
            # Tüm kolonlardaki boşlukları temizle
            df.columns = df.columns.str.strip()
            
            if merged_df is None:
                merged_df = df
            else:
                # Kesişen şirketleri baz al
                cols_to_use = df.columns.difference(merged_df.columns).tolist() + ['Şirket']
                merged_df = pd.merge(merged_df, df[cols_to_use], on='Şirket', how='inner')
        except Exception as e:
            print(f"Uyarı - Dosya okunamadı: {path} -> {e}")

    # 2. Veri Temizleme: Metinsel oranları (%, virgül) matematiksel float değerlere dönüştür
    def to_float(val):
        if pd.isna(val): return np.nan
        if isinstance(val, str):
            val = val.replace('%', '').replace('.', '').replace(',', '.').strip()
            if val in ['-', '', 'A/D']: return np.nan
            try: return float(val)
            except: return np.nan
        return float(val)

    # Analiz için gerekli spesifik kolonlar
    cols_to_clean = ['Fiyat', 'Gün %', 'Getiri % (Son 1 hafta)', 'Getiri % (Son 1 ay)',
                     'F/K', 'Kaldıraç Oranı', 'Net Kar Dğş %', 'Net Dönem Karı']
    
    for c in cols_to_clean:
        if c in merged_df.columns:
            merged_df[c] = merged_df[c].apply(to_float)

    # 3. Analiz Döngüsü
    sonuclar = []
    
    for index, row in merged_df.iterrows():
        sirket = row.get('Şirket', 'Bilinmiyor')
        fiyat = row.get('Fiyat', np.nan)
        gun_getiri = row.get('Gün %', np.nan)
        hafta_getiri = row.get('Getiri % (Son 1 hafta)', np.nan)
        ay_getiri = row.get('Getiri % (Son 1 ay)', np.nan)
        
        fk = row.get('F/K', np.nan)
        kaldirac = row.get('Kaldıraç Oranı', np.nan)
        kar_degisim = row.get('Net Kar Dğş %', np.nan)
        
        # Eksik veri kontrolü
        if pd.isna(fiyat) or pd.isna(ay_getiri) or pd.isna(hafta_getiri):
            continue
            
        sinyal = "BEKLE"
        aciklama = "Nötr bölge. Fiyat ve temel veriler stabil."
        
        # --- ALIM SENARYOLARI ---
        # Mantık: 1 Aylık sert düşüş (<-%8), ancak son 1 haftada dipten dönüş başlamış (>%1)
        if ay_getiri < -8 and hafta_getiri > 1 and gun_getiri > 0:
            # DERİN ANALİZ KONTROLÜ
            if pd.notna(fk) and 0 < fk < 25 and pd.notna(kaldirac) and kaldirac < 75:
                sinyal = "HEMEN AL"
                aciklama = "Aşırı satım sonrası momentum dönüşü ONAYLANDI. Şirketin borcu düşük ve F/K'sı ucuz."
            else:
                sinyal = "AL (RİSKLİ)"
                aciklama = "Dipten dönüş var ancak şirket riskli. Ya borcu (%75+) yüksek ya da F/K çok pahalı/negatif."
                
        # --- SATIM SENARYOLARI ---
        # Mantık: 1 Aylık aşırı yükseliş (>%13), ancak son 1 haftada tepeyi bulup düşmeye başlamış (<-%2)
        elif ay_getiri > 13 and hafta_getiri < -2:
            # DERİN ANALİZ KONTROLÜ
            if (pd.notna(fk) and fk > 30) or (pd.notna(kar_degisim) and kar_degisim < 0):
                sinyal = "HEMEN SAT"
                aciklama = "Hisse şişmiş ve düşüş başlamış. Temel analiz bozuk (Karlılık düşüyor veya aşırı pahalı)."
            else:
                sinyal = "SAT (Kısmi Kar Al)"
                aciklama = "Fiyat momentumu negatife dönüyor ancak şirketin temeli (karlılık) hala sağlam. Kısmi satış yapılabilir."

        # Aksiyon olanları listeye ekle
        if sinyal != "BEKLE":
            # UST İnce Yapı Sabiti (1/137) ve Fibonacci Sönümlemeleri
            giris = fiyat * (1 - (1/137)) if "AL" in sinyal else fiyat
            stop_loss = fiyat * 0.92 if "AL" in sinyal else np.nan
            kar_al = fiyat * 1.13 if "AL" in sinyal else np.nan
            
            sonuclar.append({
                "Şirket": sirket,
                "Aksiyon Sinyali": sinyal,
                "Güncel Fiyat": fiyat,
                "Rasyonel Giriş Fiyatı": round(giris, 2),
                "Zarar Kes (Stop-Loss)": round(stop_loss, 2) if pd.notna(stop_loss) else "-",
                "Rasyonel Hedef": round(kar_al, 2) if pd.notna(kar_al) else "-",
                "Derin Analiz Gerekçesi": aciklama
            })

    # 4. Raporlama
    rapor_df = pd.DataFrame(sonuclar)
    
    if not rapor_df.empty:
        # Sinyal türüne göre sırala (Önce Hemen Al, sonra Al, sonra Satışlar)
        rapor_df = rapor_df.sort_values(by="Aksiyon Sinyali")
        output_path = r"C:\Users\info\Downloads\UST_Derin_Analiz_Sinyalleri.xlsx"
        rapor_df.to_excel(output_path, index=False)
        print(f"\nAnaliz Tamamlandı! {len(rapor_df)} adet hisse için aksiyon sinyali üretildi.")
        print(f"Rapor şuraya kaydedildi: {output_path}")
    else:
        print("Mevcut piyasa koşullarında algoritma hiçbir rasyonel aksiyon sinyali tetiklemedi.")

if __name__ == "__main__":
    ust_derin_analiz_motoru()