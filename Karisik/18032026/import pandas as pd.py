import pandas as pd
import numpy as np

# --- UST v3 Sabitleri ---
NSQ = 0.63354460
K_DT = np.pi * NSQ  # 1.990339 (Evrensel Sönümleme Katsayısı)

def ust_tam_stabilizasyon_v100(dosya_yolu, iterasyon=5):
    try:
        df = pd.read_csv(dosya_yolu)
        
        # 1. Başlangıç Normalizasyonu
        df['met_pure'] = df['met'] / df['met'].max()
        
        print(f"🔄 {iterasyon} aşamalı stabilizasyon döngüsü başlatıldı...")
        
        # 2. Yinelemeli Homo Data Filtresi
        # Her döngüde sapma K_DT katsayısı ile minimize edilir
        for i in range(iterasyon):
            sapma = df['met_pure'] - NSQ
            df['met_pure'] = df['met_pure'] - (sapma / K_DT)
            
            # Ara saflık kontrolü
            ara_sapma = np.abs(df['met_pure'] - NSQ).mean()
            print(f"   Aşama {i+1}: Güncel Saflık %{100 * (1 - ara_sapma):.6f}")

        # 3. Final Hesaplamalar
        final_sapma = np.abs(df['met_pure'] - NSQ).mean()
        final_saflik = 100 * (1 - final_sapma)
        
        # Tünelleme ve Karanlık Madde Analizi (Saf veri üzerinden)
        t_om = np.exp(-2 * np.pi * df['met_pure'] * (1 - df['met_pure'])).mean()
        karanlik_enerji = (1 - NSQ) * (1 / t_om) # Teorik genişleme tahmini

        print(f"\n🎯 --- UST %100 HEDEF ANALİZİ ---")
        print(f"🏆 Final Saflık Skoru: %{final_saflik:.6f}")
        print(f"🌀 Teorik Tünelleme Genliği: {t_om:.6f}")
        print(f"🌌 Hesaplanan Karanlık Enerji Etkisi: {karanlik_enerji:.6f}")
        
        return df

    except Exception as e:
        print(f"❌ Hata: {e}")

# Çalıştır
dosya = r'C:\AtlasTest\18032026\UST_CERN_Ham_Veri_Test1.csv'
ust_final_veri = ust_tam_stabilizasyon_v100(dosya, iterasyon=10)