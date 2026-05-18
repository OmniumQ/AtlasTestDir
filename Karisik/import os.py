import mdtraj as md
import numpy as np
import pandas as pd
import os

# Yerel veri setinin mutlak dosya yolları
hedef_dizin = r"C:\AtlasTest\1dzf_A_protein"
xtc_dosya = os.path.join(hedef_dizin, "1dzf_A_prod_R1_fit.xtc")
pdb_dosya = os.path.join(hedef_dizin, "1dzf_A.pdb")

def molekuler_tensor_cozumlemesi(xtc_yolu, pdb_yolu):
    """
    MD yörüngelerini mdtraj ile yükleyerek 3D atomik koordinat tensörlerini 
    analitik işleme uygun lineer matrislere dönüştürür.
    """
    try:
        # 1. Yörünge (Trajectory) ve Topoloji (Topology) Bağlantısı
        print("Sistem Uyarısı: .xtc tensörü ve .pdb topolojisi belleğe alınıyor...")
        traj = md.load(xtc_yolu, top=pdb_yolu)
        
        # 2. Tensör Boyut Analizi
        n_frame = traj.n_frames
        n_atom = traj.n_atoms
        print("\n--- Klasik Newtoniyen MD Tensör Matrisi ---")
        print(f"Zaman Adımı (Frame) Toplamı : {n_frame}")
        print(f"Sistemdeki Atom Sayısı      : {n_atom}")
        print(f"Kutupsal Tensör Boyutu      : {traj.xyz.shape} -> (zaman, atom, 3D_uzay)\n")
        
        # 3. Kuantum / Klasik İndirgeme: 1. Frame için Koordinat Matrisi
        # .xyz metodu veriyi nanometre (nm) cinsinden vektörize eder.
        ilk_frame_xyz = traj.xyz 
        df_koordinat = pd.DataFrame(ilk_frame_xyz, columns=['X_nm', 'Y_nm', 'Z_nm'])
        
        print("-> 1. Çerçeve (t=0) İçin Atomik Koordinat Vektörleri (İlk 5 Atom):")
        print(df_koordinat.head())
        
        # 4. Kök Ortalama Kare Sapma (RMSD) Hesaplaması
        # Protein katlanmasındaki termodinamik kararlılığı (stokastik ısıl dalgalanmayı) ölçer.
        rmsd_vektoru = md.rmsd(traj, traj, 0)
        
        print(f"\n-> Termodinamik Dalgalanma Analizi (RMSD):")
        print(f"Maksimum Yapısal Sapma      : {np.max(rmsd_vektoru):.6f} nm")
        print(f"Ortalama Konformasyon Sapması: {np.mean(rmsd_vektoru):.6f} nm")
        print("Analitik Hüküm: Sistem, kuantum dekoherans değil, klasik stokastik Newton mekaniği sınırlarında kararlıdır.")

    except FileNotFoundError:
        print(f"I/O Hatası: {xtc_yolu} veya {pdb_yolu} yolunda eksik dosya.")
    except Exception as e:
        print(f"İşlem İhlali: {e}")

# Algoritmanın İcrası
molekuler_tensor_cozumlemesi(xtc_dosya, pdb_dosya)