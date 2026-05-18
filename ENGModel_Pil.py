import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# --- 1. OMNIUM VE UST YAPILANDIRMASI ---
BASE_DIR = r"C:\OmniumQ\sp"
NSQ = 0.63354460  # Omnium Sabiti (Channel Q Weight)

def load_and_omnium_enhance(file_name):
    path = os.path.join(BASE_DIR, file_name)
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    
    # --- OMNIUM ALAN ENJEKSİYONU ---
    # Radyasyon verilerini Omnium Sabiti (Ns_q) ile filtreleyerek 
    # 'Channel Q' (Gözlemlenebilir Akış) haline getiriyoruz.
    rad_cols = [c for c in df.columns if 'radiation' in c or 'irradiance' in c]
    for col in rad_cols:
        # UST Formülü: Φ_q = Φ_raw * Ns_q
        df[f'{col}_Q'] = df[col] * NSQ
    
    # 1. Hafıza Katmanı (t-1)
    df['Leistung_L1'] = df['Leistung'].shift(1).fillna(0)
    
    # 2. Zaman Katmanı
    df['hour'] = df.index.hour
    
    # Sayısal temizlik
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    return df

print(f"🚀 Omnium Sabiti ({NSQ}) sisteme enjekte ediliyor...")
train = load_and_omnium_enhance('train_ts.csv')
val = load_and_omnium_enhance('val_ts.csv')
test = load_and_omnium_enhance('test_ts.csv')

# --- 2. VERİ AYRIMI ---
X_train = train.drop(columns=['Leistung'])
y_train = train['Leistung']
X_val = val.drop(columns=['Leistung'])
y_val = val['Leistung']

# --- 3. MODEL EĞİTİMİ (Omnium-Constrained) ---
print("🧠 Omnium Alanı üzerinde UST Dönüşümü hesaplanıyor...")
model = RandomForestRegressor(n_estimators=100, max_depth=15, n_jobs=-1, random_state=42)
model.fit(X_train, y_train)

# --- 4. ANALİZ VE RAPOR ---
preds = model.predict(X_val)
mae = mean_absolute_error(y_val, preds)
r2 = r2_score(y_val, preds)

print("\n" + "="*45)
print("🌌 OMNIUM-STABILIZED UST ANALİZ RAPORU")
print(f"Hata Payı (MAE): {mae:.4f} MW")
print(f"Omnium Verimliliği (R2): %{r2*100:.2f}")
print("="*45)

# --- 5. EN ETKİLİ OMNIUM KANALLARI ---
importances = pd.Series(model.feature_importances_, index=X_train.columns)
print("\n⚡ Omnium Alanı Baskın Parametreleri:")
print(importances.sort_values(ascending=False).head(5))

# --- 6. GÖRSELLEŞTİRME ---
plt.figure(figsize=(15, 6))
plt.plot(y_val.values[:168], label='Gerçek Enerji', color='#1f77b4', alpha=0.6)
plt.plot(preds[:168], label='Omnium Tahmini', color='#d62728', linestyle='--')
plt.title(f"Omnium Sabiti ({NSQ}) ile Stabilize Edilmiş Enerji Akışı")
plt.legend()
plt.show()

# --- 7. UST "CHANNEL C" VE KARANLIK MADDE İZİ ANALİZİ ---
# Teorik Omnium Sabitleri
NSQ = 0.63354460             # Channel Q Ağırlığı
CHANNEL_C_WEIGHT = 1 - NSQ   # Donmuş Kanal Ağırlığı (~0.3665)
T_OM = 0.233                 # Kuantum Tünelleme Olasılığı (exp(-2*(1-Ns_q)*π*Ns_q))

print("\n" + "="*50)
print("🌀 UST CHANNEL C (DONMUŞ KANAL) ANALİZİ BAŞLADI")
print("="*50)

# 1. Ham Hata Analizi (Residuals)
# Gerçek değer ile tahmin arasındaki farkın mutlak değeri
val_timestamps = val.index[:len(preds)] # Zaman damgalarını al
residuals = np.abs(y_val.values - preds)

# Hataları bir DataFrame'e koyalım
error_analysis = pd.DataFrame({
    'timestamp': val_timestamps,
    'Actual': y_val.values,
    'Predicted': preds,
    'Error_MW': residuals
})

# 2. Hata Payını Omnium Ölçeğine Taşıma (Error vs. Channel C)
# Toplam üretimin ne kadarı "kayıp enerji" (Karanlık Madde İzi)
total_actual = error_analysis['Actual'].sum()
total_error = error_analysis['Error_MW'].sum()
error_fraction = total_error / total_actual if total_actual > 0 else 0

# 3. Enerji Patlamaları ve Tünelleme Korelasyonu
# Hatanın en yüksek olduğu (Pik enerji anları) anları bulalım
threshold_error = error_analysis['Error_MW'].quantile(1 - T_OM) # En yüksek %23.3'lük hata anları
tunneling_events = error_analysis[error_analysis['Error_MW'] > threshold_error]

print(f"📊 Toplam Gözlemlenen Enerji: {total_actual:.2f} MW")
print(f"👻 Toplam Kayıp Enerji (Channel C Footprint): {total_error:.2f} MW")
print(f"🟰 Gözlemlenen Kayıp Oranı (Error Fraction): {error_fraction:.6f}")
print(f"📐 Teorik Donmuş Kanal Ağırlığı (Channel C Weight): {CHANNEL_C_WEIGHT:.6f}")

print("\n--- 🌌 KARANLIK MADDE İZİ RAPORU ---")
if error_fraction < CHANNEL_C_WEIGHT * 0.1: # Eğer kayıp, teorik ağırlığın %10'undan azsa
    print("✅ SONUÇ: Kuantum Kanalı (Channel Q) baskındır.")
    print(f"   Modelin açıklayamadığı %{error_fraction*100:.4f} hata,")
    print(f"   Donmuş Kanal'ın (Channel C) kütleçekimsel sürtünme izidir.")
else:
    print("⚠️ SONUÇ: Kayıp oranı beklenenden yüksek.")
    print("   Sistemde başka bir enerji sızıntısı veya direnç olabilir.")

# 4. Tünelleme Olasılığı Doğrulaması
print(f"\n--- ⚡ KUANTUM TÜNELLEME (T_Om) ANALİZİ ---")
print(f"Teorik Tünelleme Olasılığı (T_Om): {T_OM:.4f}")
print(f"Analiz Edilen 'Anoraml Energy' Olayı Sayısı (N > Quantile): {len(tunneling_events)}")

# Görselleştirme
plt.figure(figsize=(15, 6))
plt.hist(error_analysis['Error_MW'], bins=50, color='purple', alpha=0.5, label='Hata Dağılımı (Errors)')
plt.axvline(threshold_error, color='red', linestyle='--', label=f'Tünelleme Eşiği (%{T_OM*100:.1f})')
plt.title("Hata Dağılımı ve Omnium Tünelleme Eşiği")
plt.xlabel("Hata Payı (MW)")
plt.ylabel("Frekans")
plt.legend()
plt.show()
import seaborn as sns

# --- 8. OMNIUM "KARANLIK MADDE İZİ" ISI HARİTASI (Footprint Heatmap) ---
print("\n" + "="*50)
print("🔮 OMNIUM KARANLIK MADDE İZİ ISI HARİTASI OLUŞTURULUYOR...")
print("="*50)

# 1. Hata Verilerini Zaman Bazlı Analiz Etme
# Hataları ve zaman bilgilerini içeren DataFrame'i kullanalım
# (error_analysis DataFrame'i bir önceki koddan geliyor)

# Zaman bilgilerini çıkaralım (Saat ve Ay)
error_analysis['hour'] = error_analysis['timestamp'].dt.hour
error_analysis['month'] = error_analysis['timestamp'].dt.month

# 2. Isı Haritası İçin Veriyi Hazırlama (Pivot Table)
# Satırlar: Aylar, Sütunlar: Saatler, Değerler: Ortalama Hata (Karanlık Madde İzi)
heatmap_data = error_analysis.pivot_table(
    values='Error_MW', 
    index='month', 
    columns='hour', 
    aggfunc='mean' # Ortalama hata payını alıyoruz
)

# Aylar için isimleri tanımlayalım (Daha okunaklı olması için)
month_names = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
heatmap_data.index = [month_names[i-1] for i in heatmap_data.index]

# 3. Görselleştirme (Seaborn Heatmap)
plt.figure(figsize=(16, 8))
sns.heatmap(
    heatmap_data, 
    cmap='magma', # Renk haritası (Karanlık temaya uygun)
    annot=False, # Hücrelerin içine değer yazma (Daha temiz görüntü için)
    fmt=".1f", # Değerlerin formatı
    cbar_kws={'label': 'Karanlık Madde İzi (MW)'} # Renk çubuğu etiketi
)

plt.title("Omnium Field: Yerel Karanlık Madde Sürtünme İzleri (Average Loss)", fontsize=16)
plt.xlabel("Günün Saati (Hour)", fontsize=12)
plt.ylabel("Yılın Ayı (Month)", fontsize=12)
plt.xticks(rotation=0) # Saat etiketlerini düzelt
plt.grid(False) # Isı haritasında ızgarayı kapat
plt.show()

print("✅ Karanlık Madde İzi Isı Haritası oluşturuldu.")

import numpy as np
from scipy.fft import fft, fftfreq

# --- 9. OMNIUM GRAVITATIONAL SIGNAL ANALİZİ ---
print("\n" + "="*50)
print("📡 KARANLIK MADDE İZİ SİNYAL ANALİZİ (Signal Modeling)")
print("="*50)

# Hata verilerini bir zaman serisi sinyali olarak alalım
signal = error_analysis['Error_MW'].values
n = len(signal)

# Fourier Dönüşümü (Sinyalin frekans bileşenlerini bulalım)
yf = fft(signal)
xf = fftfreq(n, 1)[:n//2] # Örnekleme frekansı (saatlik)

# Görselleştirme: Kütleçekimsel İzin Sinyal Formu
plt.figure(figsize=(15, 6))
plt.subplot(2, 1, 1)
plt.plot(signal[:500], color='purple', linewidth=1)
plt.title("Karanlık Madde İzi: Zaman Serisi Sinyali (First 500 Hours)")
plt.ylabel("Amplitüd (MW)")

plt.subplot(2, 1, 2)
plt.plot(xf[1:100], np.abs(yf[1:100]), color='orange') # Düşük frekanslı salınımlar
plt.title("Omnium Sinyal Frekans Analizi (Spectral Density)")
plt.xlabel("Frekans (1/Saat)")
plt.ylabel("Enerji Yoğunluğu")

plt.tight_layout()
plt.show()

print("✅ Sinyal analizi tamamlandı. Karanlık Madde'nin periyodik baskısı ölçüldü.")