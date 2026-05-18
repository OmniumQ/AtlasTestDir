"""
HMDA Mortgage Dataset — Kapsamlı ML Pipeline
=============================================
Kapsam:
  1. Veri İndirme & Yükleme
  2. Veri Ön İşleme & Temizleme
  3. Keşifsel Veri Analizi (EDA)
  4. Sınıflandırma  (action_taken tahmini)
  5. Kümeleme       (K-Means + DBSCAN)
  6. Anomali Tespiti (Isolation Forest + LOF)
  7. Boyut İndirgeme (PCA + UMAP)
  8. Zaman Serisi Analizi (yıllık trend)
  9. Sonuç Raporlama

Gereksinimler:
  pip install pandas numpy scikit-learn matplotlib seaborn umap-learn requests tqdm
"""

# ─────────────────────────────────────────────
# 0. IMPORTS
# ─────────────────────────────────────────────
import os
import warnings
import requests
import zipfile
import io

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from tqdm import tqdm
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder, label_binarize
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

# Sınıflandırma
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, ConfusionMatrixDisplay
)

# Kümeleme
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

# Anomali tespiti
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

# Zaman serisi
from sklearn.linear_model import LinearRegression

warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8-whitegrid")
SEED = 42
np.random.seed(SEED)

OUTPUT_DIR = "hmda_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. VERİ İNDİRME & YÜKLEME
# ─────────────────────────────────────────────
def download_hmda(year: int = 2022, sample_rows: int = 500_000) -> pd.DataFrame:
    """
    FFIEC HMDA LAR verisini indirir.
    Tam dosya ~3GB olduğu için stream ile okunur ve sample_rows kadar alınır.
    Alternatif: Consumer Financial Protection Bureau (CFPB) API
    """
    # CFPB HMDA API — filtresiz, ilk N kayıt
    api_url = (
        f"https://ffiec.cfpb.gov/v2/data-browser-api/view/csv"
        f"?years={year}&actions_taken=1,2,3&limit={sample_rows}"
    )
    print(f"[1/9] HMDA {year} verisi indiriliyor (ilk {sample_rows:,} satır)...")
    try:
        resp = requests.get(api_url, stream=True, timeout=120)
        resp.raise_for_status()
        chunks = []
        for chunk in tqdm(resp.iter_content(chunk_size=1024 * 512), unit="chunk"):
            chunks.append(chunk)
        df = pd.read_csv(io.BytesIO(b"".join(chunks)), low_memory=False)
        print(f"   ✓ İndirildi: {df.shape[0]:,} satır, {df.shape[1]} kolon")
        return df
    except Exception as e:
        print(f"   ✗ İndirme hatası: {e}")
        print("   → Sentetik demo verisi üretiliyor...")
        return _generate_synthetic(sample_rows)


def _generate_synthetic(n: int = 500_000) -> pd.DataFrame:
    """API erişimi yoksa gerçekçi sentetik HMDA verisi üretir."""
    rng = np.random.default_rng(SEED)
    loan_types    = [1, 2, 3, 4]
    prop_types    = [1, 2, 31, 32, 41]
    purposes      = [1, 2, 31, 32]
    races         = [1, 2, 3, 4, 5, 6]
    ethnicities   = [1, 11, 12, 13, 14, 2, 3]
    sexes         = [1, 2, 3, 4]
    actions       = [1, 2, 3, 4, 5, 6, 7, 8]   # 1=Originated, 3=Denied

    df = pd.DataFrame({
        "activity_year":         rng.choice(range(2018, 2023), n),
        "loan_type":             rng.choice(loan_types, n),
        "property_type":         rng.choice(prop_types, n),
        "loan_purpose":          rng.choice(purposes, n),
        "loan_amount_000s":      rng.lognormal(12, 0.6, n).astype(int),
        "applicant_income_000s": np.where(
                                     rng.random(n) < 0.03, np.nan,
                                     rng.lognormal(11, 0.7, n).astype(int)
                                 ),
        "applicant_race_1":      rng.choice(races, n),
        "applicant_ethnicity":   rng.choice(ethnicities, n),
        "applicant_sex":         rng.choice(sexes, n),
        "action_taken":          rng.choice(actions, n, p=[0.45,0.05,0.12,0.05,0.12,0.08,0.08,0.05]),
        "county_code":           rng.integers(1000, 9999, n),
        "census_tract":          rng.integers(100000, 999999, n),
        "msamd":                 rng.choice([10180,10420,10580,11244,11460], n),
        "hud_median_family_income": rng.integers(40000, 150000, n),
        "population":            rng.integers(500, 500000, n),
        "minority_population":   rng.uniform(0, 100, n).round(2),
        "number_of_owner_occupied_units": rng.integers(100, 50000, n),
        "number_of_1_to_4_family_units":  rng.integers(100, 60000, n),
        "lien_status":           rng.choice([1, 2, 3, 4], n),
        "rate_spread":           np.where(rng.random(n) < 0.7, np.nan,
                                          rng.uniform(1.5, 8.0, n).round(2)),
    })
    print(f"   ✓ Sentetik veri üretildi: {df.shape[0]:,} satır, {df.shape[1]} kolon")
    return df


# ─────────────────────────────────────────────
# 2. ÖN İŞLEME & TEMİZLEME
# ─────────────────────────────────────────────
NUMERIC_COLS = [
    "loan_amount_000s", "applicant_income_000s",
    "hud_median_family_income", "population",
    "minority_population", "number_of_owner_occupied_units",
    "number_of_1_to_4_family_units", "rate_spread"
]

CATEGORICAL_COLS = [
    "loan_type", "property_type", "loan_purpose",
    "applicant_race_1", "applicant_ethnicity",
    "applicant_sex", "lien_status"
]

TARGET_COL = "action_taken"
# Basitleştir: 1=Onaylandı, 0=Reddedildi/Diğer
BINARY_MAP = {1: 1, 6: 1, 2: 0, 3: 0, 4: 0, 5: 0, 7: 0, 8: 0}


def preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    print("\n[2/9] Ön işleme...")

    # Yalnızca mevcut kolonları tut
    all_cols = NUMERIC_COLS + CATEGORICAL_COLS + [TARGET_COL]
    available = [c for c in all_cols if c in df.columns]
    df = df[available].copy()

    # Hedef
    df[TARGET_COL] = df[TARGET_COL].map(BINARY_MAP)
    df = df.dropna(subset=[TARGET_COL])
    y = df[TARGET_COL].astype(int)
    df = df.drop(columns=[TARGET_COL])

    # Eksik doldurma
    num_cols = [c for c in NUMERIC_COLS if c in df.columns]
    cat_cols = [c for c in CATEGORICAL_COLS if c in df.columns]

    num_imp = SimpleImputer(strategy="median")
    cat_imp = SimpleImputer(strategy="most_frequent")

    if num_cols:
        df[num_cols] = num_imp.fit_transform(df[num_cols])
    if cat_cols:
        df[cat_cols] = cat_imp.fit_transform(df[cat_cols])
        for c in cat_cols:
            df[c] = LabelEncoder().fit_transform(df[c].astype(str))

    # Mühendislik özellikleri
    if "loan_amount_000s" in df.columns and "applicant_income_000s" in df.columns:
        df["dti_proxy"] = df["loan_amount_000s"] / (df["applicant_income_000s"] + 1)
    if "minority_population" in df.columns:
        df["high_minority_area"] = (df["minority_population"] > 50).astype(int)

    print(f"   ✓ Özellik matrisi: {df.shape}")
    print(f"   ✓ Hedef dağılımı: {y.value_counts().to_dict()}")
    return df, y


# ─────────────────────────────────────────────
# 3. KEŞİFSEL VERİ ANALİZİ (EDA)
# ─────────────────────────────────────────────
def run_eda(df_raw: pd.DataFrame) -> None:
    print("\n[3/9] EDA...")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("HMDA Mortgage Dataset — EDA", fontsize=16, fontweight="bold")

    # Aksiyon dağılımı
    if "action_taken" in df_raw.columns:
        action_labels = {
            1:"Originated", 2:"Approved/Not Accepted",
            3:"Denied", 4:"Withdrawn", 5:"Incomplete",
            6:"Purchased", 7:"Pre-denial", 8:"Pre-approved/Not Accepted"
        }
        counts = df_raw["action_taken"].value_counts().sort_index()
        counts.index = [action_labels.get(i, i) for i in counts.index]
        axes[0,0].barh(counts.index, counts.values, color=sns.color_palette("Blues_d", len(counts)))
        axes[0,0].set_title("Başvuru Sonuçları (action_taken)")
        axes[0,0].set_xlabel("Adet")

    # Kredi miktarı dağılımı
    if "loan_amount_000s" in df_raw.columns:
        vals = df_raw["loan_amount_000s"].dropna()
        vals = vals[vals < vals.quantile(0.99)]
        axes[0,1].hist(vals, bins=60, color="#4472C4", edgecolor="none")
        axes[0,1].set_title("Kredi Miktarı Dağılımı ($000s)")
        axes[0,1].set_xlabel("Miktar ($000s)")

    # Gelir dağılımı
    if "applicant_income_000s" in df_raw.columns:
        vals = df_raw["applicant_income_000s"].dropna()
        vals = vals[vals < vals.quantile(0.99)]
        axes[0,2].hist(vals, bins=60, color="#ED7D31", edgecolor="none")
        axes[0,2].set_title("Başvurucu Geliri Dağılımı ($000s)")
        axes[0,2].set_xlabel("Gelir ($000s)")

    # Kredi türü
    if "loan_type" in df_raw.columns:
        lt = df_raw["loan_type"].value_counts()
        lt.index = ["Conventional","FHA","VA","FSA/RHS"][:len(lt)]
        axes[1,0].pie(lt.values, labels=lt.index, autopct="%1.1f%%",
                      colors=sns.color_palette("pastel"))
        axes[1,0].set_title("Kredi Türü Dağılımı")

    # Azınlık nüfus vs onay
    if "minority_population" in df_raw.columns and "action_taken" in df_raw.columns:
        approved = df_raw[df_raw["action_taken"] == 1]["minority_population"].dropna()
        denied   = df_raw[df_raw["action_taken"] == 3]["minority_population"].dropna()
        axes[1,1].hist(approved.sample(min(5000, len(approved))), bins=40,
                       alpha=0.6, label="Onaylandı", color="green")
        axes[1,1].hist(denied.sample(min(5000, len(denied))), bins=40,
                       alpha=0.6, label="Reddedildi", color="red")
        axes[1,1].set_title("Azınlık Nüfusu vs Karar")
        axes[1,1].set_xlabel("Azınlık Nüfusu (%)")
        axes[1,1].legend()

    # Yıllık trend
    if "activity_year" in df_raw.columns and "action_taken" in df_raw.columns:
        trend = df_raw.groupby("activity_year")["action_taken"].apply(
            lambda x: (x == 1).sum() / len(x) * 100
        )
        axes[1,2].plot(trend.index, trend.values, marker="o", color="#5B9BD5", linewidth=2)
        axes[1,2].set_title("Yıllık Onay Oranı (%)")
        axes[1,2].set_xlabel("Yıl")
        axes[1,2].set_ylabel("Onay %")

    plt.tight_layout()
    path = f"{OUTPUT_DIR}/eda.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"   ✓ EDA grafiği kaydedildi: {path}")


# ─────────────────────────────────────────────
# 4. SINIFLANDIRMA
# ─────────────────────────────────────────────
def run_classification(X: pd.DataFrame, y: pd.Series) -> None:
    print("\n[4/9] Sınıflandırma...")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X_scaled, y, test_size=0.2, random_state=SEED, stratify=y
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=500, random_state=SEED),
        "Random Forest":       RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=SEED),
        "Gradient Boosting":   GradientBoostingClassifier(n_estimators=100, random_state=SEED),
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Sınıflandırma — Karmaşıklık Matrisleri", fontsize=14, fontweight="bold")

    results = {}
    for idx, (name, model) in enumerate(models.items()):
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)
        y_prob = model.predict_proba(X_te)[:, 1] if hasattr(model, "predict_proba") else None

        auc = roc_auc_score(y_te, y_prob) if y_prob is not None else None
        results[name] = {
            "report": classification_report(y_te, y_pred, output_dict=True),
            "auc":    auc,
            "model":  model,
            "y_prob": y_prob,
        }

        ConfusionMatrixDisplay.from_predictions(y_te, y_pred, ax=axes[idx], colorbar=False)
        axes[idx].set_title(f"{name}\nAUC={auc:.4f}" if auc else name)
        print(f"   {name}: AUC={auc:.4f}, F1={results[name]['report']['macro avg']['f1-score']:.4f}")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/classification_cm.png", dpi=150, bbox_inches="tight")
    plt.close()

    # ROC eğrileri
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ["#4472C4", "#ED7D31", "#70AD47"]
    for (name, res), color in zip(results.items(), colors):
        if res["y_prob"] is not None:
            fpr, tpr, _ = roc_curve(y_te, res["y_prob"])
            ax.plot(fpr, tpr, label=f"{name} (AUC={res['auc']:.4f})", color=color, linewidth=2)
    ax.plot([0,1],[0,1], "k--", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Eğrileri")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/roc_curves.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Özellik önemleri (RF)
    rf = results["Random Forest"]["model"]
    importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    importances.tail(15).plot(kind="barh", ax=ax, color="#4472C4")
    ax.set_title("Random Forest — Özellik Önemleri (Top 15)")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/feature_importance.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("   ✓ Sınıflandırma grafikleri kaydedildi.")


# ─────────────────────────────────────────────
# 5. KÜMELEME
# ─────────────────────────────────────────────
def run_clustering(X: pd.DataFrame, sample_n: int = 50_000) -> np.ndarray:
    print("\n[5/9] Kümeleme...")
    idx = np.random.choice(len(X), min(sample_n, len(X)), replace=False)
    X_s = StandardScaler().fit_transform(X.iloc[idx])

    # Elbow
    inertias, sils = [], []
    K_range = range(2, 10)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=SEED, n_init=5)
        labels = km.fit_predict(X_s)
        inertias.append(km.inertia_)
        sils.append(silhouette_score(X_s, labels, sample_size=5000))

    best_k = K_range[np.argmax(sils)]
    print(f"   En iyi K (silhouette): {best_k}")

    km_best = KMeans(n_clusters=best_k, random_state=SEED, n_init=10)
    km_labels = km_best.fit_predict(X_s)

    # DBSCAN (PCA-2D üzerinde)
    pca2 = PCA(n_components=2, random_state=SEED)
    X_2d = pca2.fit_transform(X_s)
    db = DBSCAN(eps=1.5, min_samples=50, n_jobs=-1)
    db_labels = db.fit_predict(X_2d)
    n_clusters_db = len(set(db_labels)) - (1 if -1 in db_labels else 0)
    print(f"   DBSCAN küme sayısı: {n_clusters_db}, gürültü: {(db_labels == -1).sum()}")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Kümeleme Analizi", fontsize=14, fontweight="bold")

    # Elbow
    axes[0].plot(K_range, inertias, marker="o", color="#4472C4", linewidth=2)
    axes[0].axvline(best_k, color="red", linestyle="--", label=f"En iyi K={best_k}")
    axes[0].set_title("Elbow Yöntemi")
    axes[0].set_xlabel("K"); axes[0].set_ylabel("İnertia"); axes[0].legend()

    # Silhouette
    axes[1].plot(K_range, sils, marker="s", color="#ED7D31", linewidth=2)
    axes[1].axvline(best_k, color="red", linestyle="--")
    axes[1].set_title("Silhouette Skoru")
    axes[1].set_xlabel("K"); axes[1].set_ylabel("Skor")

    # K-Means 2D
    scatter = axes[2].scatter(X_2d[:, 0], X_2d[:, 1], c=km_labels,
                               cmap="tab10", alpha=0.4, s=5)
    axes[2].set_title(f"K-Means (K={best_k}) — PCA 2D")
    axes[2].set_xlabel("PC1"); axes[2].set_ylabel("PC2")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/clustering.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("   ✓ Kümeleme grafikleri kaydedildi.")
    return km_labels


# ─────────────────────────────────────────────
# 6. ANOMALİ TESPİTİ
# ─────────────────────────────────────────────
def run_anomaly(X: pd.DataFrame, sample_n: int = 30_000) -> None:
    print("\n[6/9] Anomali tespiti...")
    idx = np.random.choice(len(X), min(sample_n, len(X)), replace=False)
    X_s = StandardScaler().fit_transform(X.iloc[idx])
    pca2 = PCA(n_components=2, random_state=SEED)
    X_2d = pca2.fit_transform(X_s)

    # Isolation Forest
    iso = IsolationForest(contamination=0.05, n_jobs=-1, random_state=SEED)
    iso_labels = iso.fit_predict(X_s)   # -1 = anomali
    iso_scores = iso.score_samples(X_s)

    # LOF
    lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05, n_jobs=-1)
    lof_labels = lof.fit_predict(X_s)
    lof_scores = lof.negative_outlier_factor_

    iso_anom = (iso_labels == -1).sum()
    lof_anom = (lof_labels == -1).sum()
    print(f"   Isolation Forest anomalileri: {iso_anom} ({iso_anom/len(X_s)*100:.1f}%)")
    print(f"   LOF anomalileri: {lof_anom} ({lof_anom/len(X_s)*100:.1f}%)")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Anomali Tespiti", fontsize=14, fontweight="bold")

    for ax, labels, title in zip(
        axes[:2],
        [iso_labels, lof_labels],
        ["Isolation Forest", "Local Outlier Factor"]
    ):
        colors = np.where(labels == -1, "red", "#4472C4")
        ax.scatter(X_2d[:, 0], X_2d[:, 1], c=colors, alpha=0.3, s=5)
        ax.scatter([], [], c="red",    label="Anomali", s=20)
        ax.scatter([], [], c="#4472C4", label="Normal", s=20)
        ax.set_title(title)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
        ax.legend(markerscale=2)

    # Skor dağılımı
    axes[2].hist(iso_scores, bins=60, color="#4472C4", alpha=0.7, label="IF Skoru")
    ax2 = axes[2].twinx()
    ax2.hist(lof_scores, bins=60, color="#ED7D31", alpha=0.5, label="LOF Skoru")
    axes[2].set_title("Anomali Skor Dağılımları")
    axes[2].set_xlabel("Skor")
    axes[2].legend(loc="upper left")
    ax2.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/anomaly.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("   ✓ Anomali grafikleri kaydedildi.")


# ─────────────────────────────────────────────
# 7. BOYUT İNDİRGEME
# ─────────────────────────────────────────────
def run_dimensionality(X: pd.DataFrame, y: pd.Series, sample_n: int = 20_000) -> None:
    print("\n[7/9] Boyut indirgeme...")
    idx = np.random.choice(len(X), min(sample_n, len(X)), replace=False)
    X_s = StandardScaler().fit_transform(X.iloc[idx])
    y_s = y.iloc[idx].values

    # PCA — açıklanan varyans
    pca_full = PCA(random_state=SEED)
    pca_full.fit(X_s)
    cumvar = np.cumsum(pca_full.explained_variance_ratio_)
    n95 = np.searchsorted(cumvar, 0.95) + 1
    print(f"   PCA: %95 varyans için {n95} bileşen gerekli")

    # PCA 2D & 3D
    pca2 = PCA(n_components=2, random_state=SEED)
    X_pca2 = pca2.fit_transform(X_s)

    # UMAP (opsiyonel)
    try:
        import umap
        reducer = umap.UMAP(n_components=2, random_state=SEED, n_neighbors=30)
        X_umap = reducer.fit_transform(X_s)
        has_umap = True
        print("   ✓ UMAP tamamlandı")
    except ImportError:
        has_umap = False
        print("   ⚠ umap-learn yüklü değil, UMAP atlanıyor")

    fig, axes = plt.subplots(1, 3 if has_umap else 2, figsize=(18 if has_umap else 12, 5))
    fig.suptitle("Boyut İndirgeme", fontsize=14, fontweight="bold")

    # Kümülatif varyans
    axes[0].plot(range(1, len(cumvar)+1), cumvar, color="#4472C4", linewidth=2)
    axes[0].axhline(0.95, color="red", linestyle="--", label="%95 eşiği")
    axes[0].axvline(n95, color="orange", linestyle=":", label=f"{n95} bileşen")
    axes[0].set_title("PCA — Kümülatif Açıklanan Varyans")
    axes[0].set_xlabel("Bileşen Sayısı"); axes[0].set_ylabel("Kümülatif Varyans")
    axes[0].legend()

    # PCA 2D
    sc = axes[1].scatter(X_pca2[:, 0], X_pca2[:, 1], c=y_s,
                          cmap="RdYlGn", alpha=0.4, s=5)
    plt.colorbar(sc, ax=axes[1], label="Onay=1, Red=0")
    axes[1].set_title("PCA 2D — Onay/Red")
    axes[1].set_xlabel("PC1"); axes[1].set_ylabel("PC2")

    # UMAP
    if has_umap:
        sc2 = axes[2].scatter(X_umap[:, 0], X_umap[:, 1], c=y_s,
                               cmap="RdYlGn", alpha=0.4, s=5)
        plt.colorbar(sc2, ax=axes[2], label="Onay=1, Red=0")
        axes[2].set_title("UMAP 2D — Onay/Red")
        axes[2].set_xlabel("UMAP-1"); axes[2].set_ylabel("UMAP-2")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/dimensionality.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("   ✓ Boyut indirgeme grafikleri kaydedildi.")


# ─────────────────────────────────────────────
# 8. ZAMAN SERİSİ ANALİZİ
# ─────────────────────────────────────────────
def run_time_series(df_raw: pd.DataFrame) -> None:
    print("\n[8/9] Zaman serisi analizi...")
    if "activity_year" not in df_raw.columns or "action_taken" not in df_raw.columns:
        print("   ⚠ Gerekli kolonlar yok, atlanıyor.")
        return

    ts = df_raw.groupby("activity_year").agg(
        total=("action_taken", "count"),
        approved=("action_taken", lambda x: (x == 1).sum()),
        denied=("action_taken", lambda x: (x == 3).sum()),
    )
    ts["approval_rate"] = ts["approved"] / ts["total"] * 100
    ts["denial_rate"]   = ts["denied"]  / ts["total"] * 100

    # Lineer trend
    years = ts.index.values.reshape(-1, 1)
    lr = LinearRegression().fit(years, ts["approval_rate"].values)
    trend_vals = lr.predict(years)
    slope = lr.coef_[0]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Zaman Serisi Analizi — HMDA Yıllık Trend", fontsize=14, fontweight="bold")

    # Hacim
    axes[0].bar(ts.index, ts["total"], color="#4472C4", edgecolor="none")
    axes[0].set_title("Yıllık Toplam Başvuru Hacmi")
    axes[0].set_xlabel("Yıl"); axes[0].set_ylabel("Başvuru Sayısı")
    for bar, val in zip(axes[0].patches, ts["total"]):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height()+500,
                     f"{val:,}", ha="center", va="bottom", fontsize=9)

    # Onay & Red oranı
    axes[1].plot(ts.index, ts["approval_rate"], marker="o", label="Onay %",
                  color="#70AD47", linewidth=2)
    axes[1].plot(ts.index, ts["denial_rate"], marker="s", label="Red %",
                  color="#FF0000", linewidth=2, linestyle="--")
    axes[1].plot(ts.index, trend_vals, linestyle=":", color="gray",
                  label=f"Trend (β={slope:.2f}%/yıl)")
    axes[1].set_title("Yıllık Onay / Red Oranları")
    axes[1].set_xlabel("Yıl"); axes[1].set_ylabel("Oran (%)")
    axes[1].legend()

    # Kredi türü trendi (eğer varsa)
    if "loan_type" in df_raw.columns:
        lt_ts = df_raw.groupby(["activity_year", "loan_type"]).size().unstack(fill_value=0)
        lt_ts.plot(ax=axes[2], marker="o", linewidth=2)
        axes[2].set_title("Kredi Türü Yıllık Dağılımı")
        axes[2].set_xlabel("Yıl"); axes[2].set_ylabel("Adet")
        axes[2].legend(title="Kredi Türü", labels=["Conventional","FHA","VA","FSA"][:lt_ts.shape[1]])
    else:
        axes[2].text(0.5, 0.5, "loan_type kolonu yok", ha="center", va="center",
                     transform=axes[2].transAxes)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/time_series.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"   ✓ Zaman serisi grafiği kaydedildi. Trend: {slope:.3f}%/yıl")


# ─────────────────────────────────────────────
# 9. SONUÇ RAPORU
# ─────────────────────────────────────────────
def print_summary() -> None:
    print("\n[9/9] Pipeline tamamlandı!")
    print("=" * 55)
    print(f"  Çıktılar: ./{OUTPUT_DIR}/")
    files = {
        "eda.png":              "Keşifsel Veri Analizi",
        "classification_cm.png":"Sınıflandırma Karmaşıklık Matrisleri",
        "roc_curves.png":       "ROC Eğrileri (3 model)",
        "feature_importance.png":"Özellik Önemleri (RF)",
        "clustering.png":       "Kümeleme (K-Means + Elbow)",
        "anomaly.png":          "Anomali Tespiti (IF + LOF)",
        "dimensionality.png":   "Boyut İndirgeme (PCA + UMAP)",
        "time_series.png":      "Zaman Serisi Trendi",
    }
    for fname, desc in files.items():
        status = "✓" if os.path.exists(f"{OUTPUT_DIR}/{fname}") else "✗"
        print(f"  {status} {fname:<30} {desc}")
    print("=" * 55)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # 1. İndir
    df_raw = download_hmda(year=2022, sample_rows=500_000)

    # 2. EDA (ham veri üzerinde)
    run_eda(df_raw)

    # 3. Ön işle
    X, y = preprocess(df_raw)

    # 4. Sınıflandırma
    run_classification(X, y)

    # 5. Kümeleme
    run_clustering(X, sample_n=50_000)

    # 6. Anomali
    run_anomaly(X, sample_n=30_000)

    # 7. Boyut indirgeme
    run_dimensionality(X, y, sample_n=20_000)

    # 8. Zaman serisi
    run_time_series(df_raw)

    # 9. Özet
    print_summary()