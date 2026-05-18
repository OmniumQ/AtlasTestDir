import mdtraj as md
import pandas as pd
import os

# Yerel veri seti mutlak yolları
hedef_dizin = r"C:\AtlasTest\1dzf_A_protein"
xtc_dosya = os.path.join(hedef_dizin, "1dzf_A_prod_R1_fit.xtc")
pdb_dosya = os.path.join(hedef_dizin, "1dzf_A.pdb")

def ham_veri_matrisi_olustur(xtc_yolu, pdb_yolu):
    """
    Sıkıştırılmış MD yörünge tensöründen t=0 zaman adımı için 
    uzaysal koordinatların çekilmesi ve 2D matris formunda okunması.
    """
    try:
        # Yörünge (Trajectory) ve topoloji matrislerinin birleştirilmesi
        traj = md.load(xtc_yolu, top=pdb_yolu)
        
        # Sistem değişkenlerinin ve tensör sınırlarının tespiti
        print("--- GROMACS Ham Veri Sınırları ---")
        print(f"Zaman Adımı (Frame) Sayısı : {traj.n_frames}")
        print(f"Partikül (Atom) Sayısı     : {traj.n_atoms}")
        print(f"Tensör Boyut Dağılımı      : {traj.xyz.shape} -> (Zaman, Atom, Koordinat)\n")
        
        # 3D Tensörden [N_frame, N_atom, 3] t=0 zaman adımının [N_atom, 3] boyutuna indirgenmesi
        ilk_frame_xyz = traj.xyz
        
        # Yapılandırılmış analitik format (DataFrame) dönüşümü
        kolon_vektorleri = ['X_nm', 'Y_nm', 'Z_nm']
        df_koordinat = pd.DataFrame(ilk_frame_xyz, columns=kolon_vektorleri)
        
        print("--- t=0 Zaman Adımı İçin Atomik Koordinat Matrisi (İlk 10 Gözlem) ---")
        print(df_koordinat.head(100000).to_string())

    except FileNotFoundError:
        print(f"I/O İhlali: {xtc_yolu} veya {pdb_yolu} hedefinde veri bulunamadı.")
    except Exception as e:
        print(f"Sistem İhlali: {e}")

# Algoritmanın İcrası
ham_veri_matrisi_olustur(xtc_dosya, pdb_dosya)