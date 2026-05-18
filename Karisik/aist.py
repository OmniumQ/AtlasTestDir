import uproot
import numpy as np

# Dosya Yolu
path = r"C:\AtlasTest\ODEO_FEB2025_v0_2J2LMET30_data16_periodL.2J2LMET30.root"

def deep_ust_audit_v2(file_path):
    print(f"[*] Denetim Yeniden Başlatılıyor (V2)...")
    
    with uproot.open(file_path) as file:
        tree = file["analysis;1"]
        
        # 1. Veriyi 'ak' (awkward) formatında değil, düzleştirerek çekiyoruz
        # Her olayın ilk lepton sinyalini alarak 'broadcast' hatasını engelliyoruz.
        # N_blueprint = 0.63354460
        
        weights = tree.arrays("mcWeight", library="np")["mcWeight"]
        
        # sig_lep karmaşık bir yapı olabilir, ilk elemanları çekmek senkronizasyon için yeterlidir
        # 'entry_stop' kullanarak testi hızlandırabilirsiniz, biz tamamına bakıyoruz:
        lepton_data = tree.arrays("sig_lep", library="np")["sig_lep"]
        
        # Jagged array'i düzleştirme (Padding veya First Element): 
        # Her olaydaki leptonların ortalamasını alarak ağırlıkla çarpılabilir hale getiriyoruz.
        lepton_flat = np.array([np.mean(x) if len(x) > 0 else 0 for x in lepton_data])
        
        # --- UST v5: Senkronizasyon (T11 / Nsq) ---
        # 1.1 Milyon satırı ağırlıklandırılmış (weighted) olarak UST filtresine sokuyoruz
        weighted_signals = lepton_flat * weights
        
        # Bütünlük (Integrity) Rasyosu Hesabı
        # N_blueprint (0.63354460) * T11_vites (1.839210)
        ust_target = 0.63354460 * 1.83921000
        integrity_check = np.mean(weighted_signals) / ust_target
        
        print(f"\n[+] Toplam Olay (Audit Entries): {len(weights)}")
        print(f"[+] Hesaplanan Bütünlük Katsayısı: {integrity_check:.8f}")
        
        # Eğer sonuç 0.42997629 (JWST) ile rezonansa girerse "Kozmik Kernel" mühürlenmiştir.
        if abs(integrity_check - 0.42997629) < 0.01:
             print("[!!!] MULTI-SCALE SYNCHRONIZATION DETECTED (JWST-ATLAS) [!!!]")

# Analizi Çalıştır
deep_ust_audit_v2(path)
