"""
UST Omnium Tunnelling – Enerji Bilinçli Optimizasyon Çekirdeği
--------------------------------------------------------------
Bu sürüm:
- Çoklu R desteği
- Linear, Poly2, Poly3 modeller
- Ağırlıklandırılmış loss
- Enerji/ısı maliyeti terimi (computational cost)
- Grid search + continuous optimization + multi-start
- Parametre sınırları
- Early stopping
- FLOP proxy ile hesaplama maliyeti ölçümü
- Kuantum optimizasyona bağlanabilir soyut arayüz
"""

import numpy as np
import time

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("[UYARI] scipy bulunamadı, sadece grid search kullanılacak.")


# =========================================================
# 1. KONFİGÜRASYON
# =========================================================

class Config:
    # --- Fiziksel parametreler ---
    R_list = [1.005613, 1.005610, 1.005620]
    T_target = -4.292560e-4

    # Model tipi: "linear", "poly2", "poly3"
    model_type = "poly2"

    # Loss tipi: "mse" veya "mae"
    loss_type = "mse"

    # Ağırlıklar
    weights = None

    # --- Parametre sınırları ---
    bounds_linear = [(-1e-3, 1e-3), (-1e-3, 1e-3)]
    bounds_poly2 = [(-1e-3, 1e-3), (-1e-3, 1e-3), (-1e-3, 1e-3)]
    bounds_poly3 = [(-1e-3, 1e-3), (-1e-3, 1e-3), (-1e-3, 1e-3), (-1e-3, 1e-3)]

    # --- Optimizasyon ayarları ---
    optimizer_method = "L-BFGS-B"
    max_iter = 2000
    tol = 1e-15

    use_grid_search = True
    grid_points = 101

    use_multistart = True
    multistart_runs = 8
    random_seed = 42

    # Enerji/ısı maliyeti katsayısı
    lambda_comp = 1e-18

    # Early stopping eşiği
    early_stop_threshold = 1e-20

    verbose = True


# =========================================================
# 2. MODEL FONKSİYONU
# =========================================================

def tunneling_model(R, params, cfg: Config):
    R = np.array(R, dtype=float)

    if cfg.model_type == "linear":
        a, b = params
        return a * R + b

    elif cfg.model_type == "poly2":
        a, b, c = params
        return a * R**2 + b * R + c

    elif cfg.model_type == "poly3":
        a, b, c, d = params
        return a * R**3 + b * R**2 + c * R + d

    else:
        raise NotImplementedError("Desteklenmeyen model tipi.")


# =========================================================
# 3. LOSS FONKSİYONU
# =========================================================

def physical_loss(params, R_list, T_target, cfg: Config):
    T_pred = tunneling_model(R_list, params, cfg)
    T_target_arr = np.full_like(T_pred, T_target)

    if cfg.weights is None:
        w = np.ones_like(T_pred)
    else:
        w = np.array(cfg.weights)

    diff = T_pred - T_target_arr

    if cfg.loss_type == "mse":
        return np.mean(w * diff**2)
    elif cfg.loss_type == "mae":
        return np.mean(w * np.abs(diff))
    else:
        raise NotImplementedError("Desteklenmeyen loss tipi.")


# =========================================================
# 4. HESAPLAMA MALİYETİ (ENERJİ/ISI PROXY)
# =========================================================

def computational_cost(params, cfg: Config):
    """
    Enerji/ısı tüketimi için proxy:
    - Parametre sayısı
    - Parametre büyüklüğü
    - Model karmaşıklığı
    """
    param_count = len(params)
    magnitude_penalty = np.sum(np.abs(params))
    model_complexity = {"linear": 1, "poly2": 2, "poly3": 3}[cfg.model_type]

    return param_count + 0.1 * magnitude_penalty + model_complexity


# =========================================================
# 5. TOPLAM LOSS
# =========================================================

def total_loss(params, R_list, T_target, cfg: Config):
    phys = physical_loss(params, R_list, T_target, cfg)
    comp = computational_cost(params, cfg)
    return phys + cfg.lambda_comp * comp


# =========================================================
# 6. GRID SEARCH
# =========================================================

def grid_search(R_list, T_target, cfg: Config):
    if cfg.model_type == "linear":
        bounds = cfg.bounds_linear
        dim = 2
    elif cfg.model_type == "poly2":
        bounds = cfg.bounds_poly2
        dim = 3
    else:
        bounds = cfg.bounds_poly3
        dim = 4

    # Sadece ilk iki parametre için grid search
    a_vals = np.linspace(bounds[0][0], bounds[0][1], cfg.grid_points)
    b_vals = np.linspace(bounds[1][0], bounds[1][1], cfg.grid_points)

    best_loss = np.inf
    best_params = None

    for a in a_vals:
        for b in b_vals:
            if dim == 2:
                params = (a, b)
            elif dim == 3:
                params = (a, b, 0.0)
            else:
                params = (a, b, 0.0, 0.0)

            current_loss = total_loss(params, R_list, T_target, cfg)
            if current_loss < best_loss:
                best_loss = current_loss
                best_params = params

    return np.array(best_params), best_loss


# =========================================================
# 7. SÜREKLİ OPTİMİZASYON
# =========================================================

def continuous_optimization(R_list, T_target, cfg: Config, initial_guess):
    if not SCIPY_AVAILABLE:
        raise RuntimeError("scipy yok.")

    if cfg.model_type == "linear":
        bounds = cfg.bounds_linear
    elif cfg.model_type == "poly2":
        bounds = cfg.bounds_poly2
    else:
        bounds = cfg.bounds_poly3

    result = minimize(
        total_loss,
        x0=initial_guess,
        args=(R_list, T_target, cfg),
        method=cfg.optimizer_method,
        bounds=bounds,
        options={"maxiter": cfg.max_iter, "ftol": cfg.tol}
    )

    return result


# =========================================================
# 8. MULTI-START
# =========================================================

def multistart_optimization(R_list, T_target, cfg: Config):
    rng = np.random.default_rng(cfg.random_seed)

    if cfg.model_type == "linear":
        bounds = cfg.bounds_linear
        dim = 2
    elif cfg.model_type == "poly2":
        bounds = cfg.bounds_poly2
        dim = 3
    else:
        bounds = cfg.bounds_poly3
        dim = 4

    best_loss = np.inf
    best_params = None

    for i in range(cfg.multistart_runs):
        initial_guess = np.array([rng.uniform(*bounds[j]) for j in range(dim)])
        result = continuous_optimization(R_list, T_target, cfg, initial_guess)

        if result.fun < best_loss:
            best_loss = result.fun
            best_params = result.x

        if best_loss < cfg.early_stop_threshold:
            break

    return best_params, best_loss


# =========================================================
# 9. ANA OPTİMİZASYON AKIŞI
# =========================================================

def optimize_params(cfg: Config):
    R_list = np.array(cfg.R_list)
    T_target = cfg.T_target

    # Grid search
    if cfg.use_grid_search:
        grid_params, grid_loss = grid_search(R_list, T_target, cfg)
        initial_guess = grid_params
    else:
        initial_guess = np.zeros(4)

    # Continuous optimization
    if SCIPY_AVAILABLE:
        result_single = continuous_optimization(R_list, T_target, cfg, initial_guess)
        best_params = result_single.x
        best_loss = result_single.fun
    else:
        return grid_params, grid_loss

    # Multi-start
    if cfg.use_multistart:
        ms_params, ms_loss = multistart_optimization(R_list, T_target, cfg)
        if ms_loss < best_loss:
            best_params, best_loss = ms_params, ms_loss

    return best_params, best_loss


# =========================================================
# 10. RAPORLAMA
# =========================================================

def report_results(cfg: Config, best_params, best_loss):
    R_list = np.array(cfg.R_list)
    T_target = cfg.T_target

    T_pred = tunneling_model(R_list, best_params, cfg)
    diff = T_pred - T_target

    print("\n=== Enerji Bilinçli Nihai Optimizasyon Sonuçları ===")
    print(f"Model tipi: {cfg.model_type}")
    print(f"R_list: {R_list}")
    print(f"T_target: {T_target:.9e}")
    print(f"Parametreler: {best_params}")
    print(f"T_pred: {T_pred}")
    print(f"ΔT: {diff}")
    print(f"Max |ΔT|: {np.max(np.abs(diff)):.9e}")
    print(f"Loss: {best_loss:.9e}")
    print("====================================================\n")


# =========================================================
# 11. MAIN
# =========================================================

def main():
    cfg = Config()
    best_params, best_loss = optimize_params(cfg)
    report_results(cfg, best_params, best_loss)


if __name__ == "__main__":
    main()