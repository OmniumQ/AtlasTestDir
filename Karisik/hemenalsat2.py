import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

def ust_master_matris_olustur():
    # 1. Kaynak Düğüm Yolları (Dosyalar)
    dosya_yollari = [
        r"C:\Users\info\Downloads\fintables_hisse_senetleri.xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (1).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (2).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (3).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (4).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (5).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (6).xlsx",
        r"C:\Users\info\Downloads\fintables_hisse_senetleri (7).xlsx"
    ]
    
    print("Modüller çekirdek belleğe yükleniyor ve Master Matris oluşturuluyor...")
    
    master_df = pd.DataFrame()
    
    # 2. Veri Okuma ve Kolon Çakışmalarını Önleyerek Birleştirme
    for yol in dosya_yollari:
        if not os.path.exists(yol):
            print(f"Uyarı - Kanal Kapalı (Dosya Bulunamadı): {yol}")
            continue
            
        try:
            df = pd.read_excel(yol)
            # Kolon isimlerindeki boşlukları temizle
            df.columns = df.columns.str.strip()
            
            # Şirket kolonunu standartlaştır
            sirket_col = [col for col in df.columns if "şirket" in col.lower() or "kod" in col.lower()][0]
            df = df.rename(columns={sirket_col: "Şirket"})
            
            if master_df.empty:
                master_df = df
            else:
                # Sadece Master Matris'te olmayan yeni kolonları al (Tekrarı engelle)
                yeni_kolonlar = df.columns.difference(master_df.columns).tolist() + ["Şirket"]
                # Outer merge ile hiçbir şirketi kaybetmeden birleştir
                master_df = pd.merge(master_df, df[yeni_kolonlar], on="Şirket", how="outer")
                
        except Exception as e:
            print(f"Hata - Veri Okuma Başarısız: {yol} -> {e}")

    # 3. Veri Temizleme (Metinleri Matematiksel Float Değerlere Çevirme)
    def veri_temizle(val):
        if pd.isna(val): return np.nan
        if isinstance(val, str):
            val = val.replace('%', '').replace('.', '').replace(',', '.').strip()
            if val in ['-', '', 'A/D']: return np.nan
            try: return float(val)
            except: return val # Sayı yapılamıyorsa (örn: sektör adı) metin bırak
        return float(val)

    print("Matematiksel dönüşümler ve temizlik yapılıyor...")
    for col in master_df.columns:
        if col != "Şirket":
            master_df[col] = master_df[col].apply(veri_temizle)

    # 4. UST Algoritmik Analiz Motoru
    print("UST Rasyonel Sinyal Motoru çalıştırılıyor...")
    
    sinyaller = []
    girisler = []
    stoplar = []
    hedefler = []
    detaylar = []
    alpha = 1/137 # UST Sönümleme Katsayısı
    
    for index, row in master_df.iterrows():
        # Verileri güvenli şekilde çek, yoksa NaN dön
        fiyat = row.get('Fiyat', np.nan)
        gunluk = row.get('Gün %', np.nan)
        haftalik = row.get('Getiri % (Son 1 hafta)', np.nan)
        aylik = row.get('Getiri % (Son 1 ay)', np.nan)
        fk = row.get('F/K', np.nan)
        kaldirac = row.get('Kaldıraç Oranı', np.nan)
        kar_degisim = row.get('Net Kar Dğş %', np.nan)
        
        sinyal = "NÖTR"
        detay = "Belirgin bir fiyat/temel ayrışması yok."
        giris = stop = hedef = np.nan
        
        # Sadece yeterli verisi olanları analiz et
        if pd.notna(fiyat) and pd.notna(aylik) and pd.notna(haftalik):
            # A. ALIM STRATEJİSİ
            if aylik < -8 and haftalik > 1 and pd.notna(gunluk) and gunluk > 0:
                if pd.notna(fk) and 0 < fk < 25 and pd.notna(kaldirac) and kaldirac < 75:
                    sinyal = "HEMEN AL"
                    detay = "Aşırı satım bitti. Temel sağlam (Düşük Borç, Uygun F/K)."
                    giris = fiyat * (1 - alpha)
                    stop = fiyat * 0.92
                    hedef = fiyat * 1.13
                else:
                    sinyal = "AL (RİSKLİ)"
                    detay = "Dipten dönüş var ama temel veriler (F/K veya Borç) yüksek."
                    giris = fiyat * (1 - alpha)
                    stop = fiyat * 0.95
                    hedef = fiyat * 1.08
                    
            # B. SATIM STRATEJİSİ
            elif aylik > 13 and haftalik < -2:
                if (pd.notna(fk) and fk > 30) or (pd.notna(kar_degisim) and kar_degisim < 0):
                    sinyal = "HEMEN SAT"
                    detay = "Aşırı alım sonrası düşüş. Şirket pahalı veya kârı düşüyor."
                else:
                    sinyal = "SAT (Kısmi Kar Al)"
                    detay = "Fiyat tepeden dönüyor ancak karlılık devam ediyor."

        sinyaller.append(sinyal)
        detaylar.append(detay)
        girisler.append(round(giris, 2) if pd.notna(giris) else "-")
        stoplar.append(round(stop, 2) if pd.notna(stop) else "-")
        hedefler.append(round(hedef, 2) if pd.notna(hedef) else "-")

    # 5. Analiz Sonuçlarını Ana Matrise Entegre Et
    master_df.insert(1, "UST Sinyali", sinyaller)
    master_df.insert(2, "Rasyonel Giriş", girisler)
    master_df.insert(3, "Zarar Kes", stoplar)
    master_df.insert(4, "Kar Hedefi", hedefler)
    master_df.insert(5, "Analiz Gerekçesi", detaylar)

    # 6. Çıktıyı Dosyaya Yazdırma
    siralama_map = {"HEMEN AL": 1, "AL (RİSKLİ)": 2, "HEMEN SAT": 3, "SAT (Kısmi Kar Al)": 4, "NÖTR": 5}
    master_df['Sıra_Key'] = master_df['UST Sinyali'].map(siralama_map)
    master_df = master_df.sort_values(by=['Sıra_Key', 'Şirket']).drop(columns=['Sıra_Key'])
    
    cikti_yolu = r"C:\Users\info\Downloads\UST_Master_Analiz_Matrisi.xlsx"
    master_df.to_excel(cikti_yolu, index=False)
    
    print(f"\n[BAŞARILI] İşlem tamamlandı. Tüm veriler ve analizler birleştirildi.")
    print(f"Toplam listelenen hisse sayısı: {len(master_df)}")
    print(f"Dosya şu adrese kaydedildi: {cikti_yolu}")

if __name__ == "__main__":
    ust_master_matris_olustur()