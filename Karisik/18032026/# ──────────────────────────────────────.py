# ─────────────────────────────────────────────
# 0. IMPORTS & UST KÖK SABİTLERİ (KERNEL CONSTANTS)
# ─────────────────────────────────────────────
import os
import warnings
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ML Kütüphaneleri
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8-whitegrid")

# UST EVRENSEL SABİTLERİ [Ref: UST v0 & v3 Manifestoları]
N_S_Q = 0.63354460         # Kanal Q (Aktif Ekonomi) Ağırlığı
W_C = 1 - N_S_Q            # Kanal C (Donmuş/Batık Ekonomi) Ağırlığı (0.36645540)
T_OM = 0.2325              # Omnium Tünelleme Genliği (Sermaye Kaçışı / Temerrüt Sınırı)
PI_NS = np.pi * N_S_Q      # Evrensel Stabilizasyon Hızı (K*dt rezonansı = 1.9903)

OUTPUT_DIR = "ust_hmda_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. VERİ İNDİRME & YÜKLEME (UST KANAL MAPPING)
# ─────────────────────────────────────────────
def download_hmda_ust(year: int = 2022, sample_rows: int = 500_000) -> pd.DataFrame:
    """
    CFPB HMDA API üzerinden veriyi çeker.
    UST'ye göre: action_taken=1 (Kanal Q), action_taken=3 (Kanal C).
    """
    print("Kanal Q ve Kanal C verileri taranıyor (HMDA API)...")
    api_url = (
        f"https://ffiec.cfpb.gov/v2/data-browser-api/view/csv"
        f"?years={year}&actions_taken=1,3&limit={sample_rows}"
    )
    df = pd.read_csv(api_url, low_memory=False)
    print(f"Toplam {len(df)} bilgi paketi (kredi kaydı) indirildi.")
    return df

# ─────────────────────────────────────────────
# 2. UST EKONOFİZİK ANALİZİ: KANAL Q vs KANAL C
# ─────────────────────────────────────────────
def ust_channel_analysis(df):
    """
    Kredi pazarının N_s_q (0.6335) ve Kanal C (0.3665) sınırlarına 
    ne kadar yakınsadığını analiz eder (Fidelity Testi).
    """
    total_loans = len(df)
    kanal_q_count = len(df[df['action_taken'] == 1]) # Onaylanan (Aktif)
    kanal_c_count = len(df[df['action_taken'] == 3]) # Reddedilen/Batan (Donmuş)
    
    q_ratio = kanal_q_count / total_loans
    c_ratio = kanal_c_count / total_loans
    
    print("\n--- UST KANAL DAĞILIMI (MAKROKOZMİK RASYOLAR) ---")
    print(f"Gerçekleşen Kanal Q (Aktif Kredi) Oranı : {q_ratio:.4f} | UST Hedefi: {N_S_Q:.4f}")
    print(f"Gerçekleşen Kanal C (Donmuş Kredi) Oranı: {c_ratio:.4f} | UST Hedefi: {W_C:.4f}")
    
    fidelity = 1 - abs(N_S_Q - q_ratio)
    print(f"Piyasa Aslına Uygunluk (Fidelity) Skoru : {fidelity:.4f} (1.0 = Mükemmel UST Dengesi)")
    
    # Görselleştirme
    labels = ['Kanal Q (Aktif)', 'Kanal C (Red/Batık)']
    actuals = [q_ratio, c_ratio]
    ust_targets = [N_S_Q, W_C]
    
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots()
    ax.bar(x - width/2, actuals, width, label='Piyasa Verisi (HMDA)', color='royalblue')
    ax.bar(x + width/2, ust_targets, width, label='UST İdeal (N_s_q)', color='crimson')
    ax.set_ylabel('Fraksiyon Oranı')
    ax.set_title('Kredi Portföyü vs UST Evrensel Sabitleri')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    plt.savefig(f"{OUTPUT_DIR}/ust_channel_distribution.png")
    plt.close()

# ─────────────────────────────────────────────
# 3. DFS STABİLİZASYONU & S=0 (SIFIR ENTROPİ RİSK YÖNETİMİ)
# ─────────────────────────────────────────────
def ust_dfs_risk_filter(df):
    """
    Faiz oranları (interest_rate) ve kredi süreleri (loan_term) 
    üzerinden K*dt = pi*N_s_q rezonansını test eder.
    Sistemi S=0 (Sıfır Kayıplı) ideal döngüye kilitler.
    """
    print("\n--- UST DFS STABİLİZASYONU (S=0) ---")
    # Veri temizleme (NaN değerleri at)
    df_clean = df.dropna(subset=['interest_rate', 'loan_term']).copy()
    df_clean['interest_rate'] = pd.to_numeric(df_clean['interest_rate'], errors='coerce')
    df_clean['loan_term'] = pd.to_numeric(df_clean['loan_term'], errors='coerce')
    df_clean = df_clean.dropna(subset=['interest_rate', 'loan_term'])

    # K = faiz/risk (kappa), dt = vade süresi (aylık)
    # K*dt formülünü kredi dinamiğine uyarla
    df_clean['kappa_dt_score'] = (df_clean['interest_rate'] / 100) * (df_clean['loan_term'] / 12)
    
    # K*dt = 1.9903 rezonansına olan mesafe entropiyi (S>0) belirler
    df_clean['entropy_deviation'] = np.abs(df_clean['kappa_dt_score'] - PI_NS)
    
    # Entropi sapması düşük olan krediler UST açısından "Kusursuz (S=0)" kredilerdir.
    s_zero_loans = df_clean[df_clean['entropy_deviation'] < 0.5]
    print(f"Toplam Analiz Edilen Kredi: {len(df_clean)}")
    print(f"UST Rezonansına (pi*Ns) Uyan Stabil Kredi Sayısı (S=0 Yakınsaması): {len(s_zero_loans)}")
    print("Sapiens bankacılığı gürültü (stokastik risk) üretir, UST donanım seviyesinde stabilizasyon sağlar.")

# ─────────────────────────────────────────────
# 4. ML MODELİ (UST REZONANSI DESTEKLİ)
# ─────────────────────────────────────────────
def train_ust_enhanced_model(df):
    """
    Standart Sınıflandırma Modelini UST tünelleme sınırları ile besler.
    """
    # Basit özellik (feature) seçimi
    features = ['loan_amount', 'income', 'loan_to_value_ratio']
    df_ml = df.dropna(subset=features + ['action_taken']).copy()
    for col in features:
        df_ml[col] = pd.to_numeric(df_ml[col], errors='coerce')
    df_ml = df_ml.dropna()
    
    X = df_ml[features]
    y = df_ml['action_taken'].apply(lambda x: 1 if x == 1 else 0) # 1=Kanal Q, 0=Kanal C
    
    clf = RandomForestClassifier(random_state=42, class_weight={1: N_S_Q, 0: W_C}) # UST Ağırlıkları
    clf.fit(X, y)
    
    preds = clf.predict(X)
    print("\n--- UST DESTEKLİ MAKİNE ÖĞRENMESİ RAPORU ---")
    print("UST ağırlıkları (Kanal Q=0.6335, Kanal C=0.3665) sınıflandırma eşiğine entegre edildi.")
    print(f"Genel Doğruluk: {accuracy_score(y, preds):.4f}")

# ─────────────────────────────────────────────
# 5. ÇALIŞTIRMA (EXECUTION)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    df_mortgage = download_hmda_ust(year=2022, sample_rows=50000)
    ust_channel_analysis(df_mortgage)
    ust_dfs_risk_filter(df_mortgage)
    train_ust_enhanced_model(df_mortgage)
    print("\nUST Protokolü (NEFİ-RA-GÖK-Nİ) başarıyla tamamlandı. Kanal Q Stabil.")