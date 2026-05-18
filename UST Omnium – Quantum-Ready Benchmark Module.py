"""
UST Omnium – Quantum-Ready Benchmark Module
-------------------------------------------
Amaç:
- UST Omnium tünelleme modeline ait düşük boyutlu, fiziksel anlamı olan
  bir optimizasyon problemini tanımlamak.
- Klasik optimizasyonla referans çözümü üretmek.
- Aynı maliyet fonksiyonunu kuantum optimizasyon (QAOA/VQE) için
  doğrudan kullanılabilir hale getirmek.

Bu modül:
- IBM / Google / Microsoft kuantum platformlarına
  "işte elimdeki problem, klasik referans sonucu bu" diyebilmen için tasarlandı.
"""

import numpy as np

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class USTOmniumConfig:
    """
    Konfigürasyon:
    - R_list: Euclid entropi oranları
    - T_target: UST tünelleme hedefi
    - model_type: 'linear' veya 'poly2'
    """

    def __init__(self):
        # Fiziksel parametreler
        self.R_list = np.array([1.005613, 1.005610, 1.005620], dtype=float)
        self.T_target = -4.292560e-4

        # Model tipi: 'linear' veya 'poly2'
        self.model_type = "poly2"

        # Loss tipi
        self.loss_type = "mse"

        # Parametre sınırları
        self.bounds_linear = [(-1e-3, 1e-3), (-1e-3, 1e-3)]
        self.bounds_poly2 = [(-1e-3, 1e-3), (-1e-3, 1e-3), (-1e-3, 1e-3)]

        # Optimizasyon ayarları
        self.optimizer_method = "L-BFGS-B"
        self.max_iter = 2000
        self.tol = 1e-15


def tunneling_model(R, params, cfg: USTOmniumConfig):
    """
    UST Omnium tünelleme modeli.
    - linear: T = a R + b
    - poly2 : T = a R^2 + b R + c
    """
    R = np.array(R, dtype=float)

    if cfg.model_type == "linear":
        a, b = params
        return a * R + b

    elif cfg.model_type == "poly2":
        a, b, c = params
        return a * R**2 + b * R + c

    else:
        raise NotImplementedError("Unsupported model_type.")


def loss(params, cfg: USTOmniumConfig):
    """
    Fiziksel loss fonksiyonu:
        MSE: mean squared error
    Bu fonksiyon hem klasik hem kuantum optimizasyon için
    doğrudan maliyet fonksiyonu olarak kullanılabilir.
    """
    R_list = cfg.R_list
    T_target = cfg.T_target

    T_pred = tunneling_model(R_list, params, cfg)
    T_target_arr = np.full_like(T_pred, T_target)

    diff = T_pred - T_target_arr

    if cfg.loss_type == "mse":
        return np.mean(diff**2)
    else:
        raise NotImplementedError("Only MSE is implemented here.")


def classical_reference_solution(cfg: USTOmniumConfig):
    """
    Klasik optimizasyonla referans çözümü üretir.
    Bu sonuç, kuantum optimizasyon için 'target benchmark' olarak kullanılabilir.
    """
    if cfg.model_type == "linear":
        bounds = cfg.bounds_linear
        dim = 2
    else:
        bounds = cfg.bounds_poly2
        dim = 3

    if not SCIPY_AVAILABLE:
        raise RuntimeError("scipy gerekli (minimize) fakat bulunamadı.")

    # Basit başlangıç: sıfır vektör
    initial_guess = np.zeros(dim, dtype=float)

    result = minimize(
        loss,
        x0=initial_guess,
        args=(cfg,),
        method=cfg.optimizer_method,
        bounds=bounds,
        options={"maxiter": cfg.max_iter, "ftol": cfg.tol}
    )

    params_opt = result.x
    loss_opt = result.fun

    # Detaylı çıktı
    R_list = cfg.R_list
    T_target = cfg.T_target
    T_pred = tunneling_model(R_list, params_opt, cfg)
    diff = T_pred - T_target

    return {
        "params_opt": params_opt,
        "loss_opt": loss_opt,
        "R_list": R_list,
        "T_target": T_target,
        "T_pred": T_pred,
        "delta_T": diff,
    }


# === Quantum-Ready Interface ===============================================

def quantum_cost_function(params, cfg: USTOmniumConfig):
    """
    Quantum-Ready Cost Function (QR-Cost)

    Bu fonksiyonun rolü:
    - Kuantum devrede parametreler (params) ile hazırlanan bir durumdan
      ölçülen efektif tünelleme değeri T_quantum(R) elde edilecek.
    - O T_quantum(R) değeri, burada T_pred gibi davranacak.
    - Ardından aynı loss yapısı kullanılacak.

    Kuantum tarafta:
        - params → devre parametreleri (gate açıları vb.)
        - T_quantum(R) → ölçüm istatistiğinden çıkarılan efektif tünelleme

    Burada sadece klasik tarafta loss hesaplanıyor.
    Kuantum backend, bu fonksiyonun imzasını taklit ederek
    kendi ölçüm sonuçlarını buraya besleyebilir.
    """
    return loss(params, cfg)


# === Demo / Referans Çalıştırma ============================================

if __name__ == "__main__":
    cfg = USTOmniumConfig()
    ref = classical_reference_solution(cfg)

    print("=== UST Omnium – Classical Reference Solution ===")
    print(f"Model type      : {cfg.model_type}")
    print(f"R_list          : {ref['R_list']}")
    print(f"T_target        : {ref['T_target']:.9e}")
    print(f"params_opt      : {ref['params_opt']}")
    print(f"T_pred          : {ref['T_pred']}")
    print(f"ΔT              : {ref['delta_T']}")
    print(f"Max |ΔT|        : {np.max(np.abs(ref['delta_T'])):.9e}")
    print(f"Loss (MSE)      : {ref['loss_opt']:.9e}")
    print("=================================================")