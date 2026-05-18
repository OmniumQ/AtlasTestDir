# UST Deneysel Veri Analiz Kodu
# Dosya Yolu: C:\AtlasTest\
# Dosya Formatları: ROOT, HDF5, FITS, VOTable

import os
import sys

# Gerekli kütüphaneleri kontrol et ve yükle
def check_and_import():
    required = {
        'uproot': 'ROOT dosyaları için',
        'h5py': 'HDF5 dosyaları için', 
        'astropy': 'FITS ve VOTable dosyaları için',
        'numpy': 'Genel veri işleme',
        'pandas': 'Tablo işleme'
    }
    
    missing = []
    for lib, desc in required.items():
        try:
            __import__(lib)
            print(f"✅ {lib}: Yüklü ({desc})")
        except ImportError:
            missing.append(lib)
            print(f"❌ {lib}: EKSİK ({desc})")
    
    if missing:
        print(f"\n⚠️ Eksik kütüphaneleri yüklemek için:")
        print(f"pip install {' '.join(missing)}")
        return False
    return True

# Ana analiz fonksiyonları
print("=" * 70)
print("UST v5 - DENEYSEL VERİ ANALİZ ARACI")
print("=" * 70)

# Dosya yolu
BASE_PATH = r"C:\AtlasTest"

# Dosya listesi
FILES = {
    "ROOT": "ODEO_FEB2025_v0_2J2LMET30_data16_periodI.2J2LMET30.root",
    "HDF5": "H-H1_GWOSC_O4a_16KHZ_R1-1368993792-4096.hdf5",
    "FITS": "hlsp_wide_jwst_nirspec_aegis-2020007552_f170lp-g235h_v1.0_2nod-spec2d.fits",
    "VOT": "c5f0d03b-22cd-11f1-8a0e-e8ebd3edb7d7-TPDR-result.vot"
}

print(f"\n📂 Dosya Yolu: {BASE_PATH}")
print("-" * 70)

# Dosya varlık kontrolü
for ftype, fname in FILES.items():
    fpath = os.path.join(BASE_PATH, fname)
    exists = "✅ MEVCUT" if os.path.exists(fpath) else "❌ BULUNAMADI"
    size = ""
    if os.path.exists(fpath):
        size_bytes = os.path.getsize(fpath)
        if size_bytes > 1e9:
            size = f"({size_bytes/1e9:.2f} GB)"
        elif size_bytes > 1e6:
            size = f"({size_bytes/1e6:.2f} MB)"
        else:
            size = f"({size_bytes/1e3:.2f} KB)"
    print(f"[{ftype}] {fname[:50]}... {exists} {size}")

print("\n" + "=" * 70)
print("DETAYLI ANALİZ BAŞLIYOR...")
print("=" * 70)

#==============================================================================
# 1. ROOT DOSYASI ANALİZİ (CERN/LHC Verisi)
#==============================================================================
def analyze_root_file(filepath):
    """ROOT dosyasını analiz et - CERN parçacık fiziği verisi"""
    print("\n" + "=" * 70)
    print("📊 1. ROOT DOSYASI ANALİZİ (CERN/LHC)")
    print("=" * 70)
    
    try:
        import uproot
        import numpy as np
        
        print(f"📂 Dosya: {os.path.basename(filepath)}")
        
        # ROOT dosyasını aç
        file = uproot.open(filepath)
        
        print(f"\n📁 ROOT İçerik Yapısı:")
        print("-" * 50)
        
        # Tüm anahtarları listele
        all_keys = file.keys()
        print(f"Toplam Anahtar Sayısı: {len(all_keys)}")
        
        # İlk 20 anahtarı göster
        print(f"\n🔑 Anahtarlar (İlk 20):")
        for i, key in enumerate(all_keys[:20]):
            obj = file[key]
            obj_type = type(obj).__name__
            print(f"  {i+1}. {key} [{obj_type}]")
        
        if len(all_keys) > 20:
            print(f"  ... ve {len(all_keys) - 20} anahtar daha")
        
        # TTree'leri bul ve analiz et
        print(f"\n🌲 TTree Analizi:")
        print("-" * 50)
        
        tree_count = 0
        for key in all_keys:
            obj = file[key]
            if hasattr(obj, 'keys') and hasattr(obj, 'num_entries'):
                tree_count += 1
                print(f"\n  📌 Tree: {key}")
                print(f"     Satır Sayısı (entries): {obj.num_entries}")
                
                # Branch (kolon) listesi
                branches = obj.keys()
                print(f"     Kolon Sayısı (branches): {len(branches)}")
                
                print(f"\n     📋 Kolonlar (İlk 30):")
                for j, branch in enumerate(branches[:30]):
                    try:
                        branch_obj = obj[branch]
                        dtype = str(branch_obj.interpretation) if hasattr(branch_obj, 'interpretation') else "?"
                        print(f"        {j+1}. {branch} [{dtype}]")
                    except:
                        print(f"        {j+1}. {branch}")
                
                if len(branches) > 30:
                    print(f"        ... ve {len(branches) - 30} kolon daha")
                
                # İlk birkaç satırı örnek olarak göster
                if obj.num_entries > 0:
                    print(f"\n     📊 Örnek Veri (İlk 5 Satır, İlk 5 Kolon):")
                    sample_branches = branches[:5]
                    try:
                        arrays = obj.arrays(sample_branches, library="np", entry_stop=5)
                        for branch in sample_branches:
                            if branch in arrays:
                                print(f"        {branch}: {arrays[branch][:5]}")
                    except Exception as e:
                        print(f"        Örnek veri alınamadı: {e}")
        
        if tree_count == 0:
            print("  TTree bulunamadı")
        
        file.close()
        return True
        
    except ImportError:
        print("❌ 'uproot' kütüphanesi yüklü değil. Yüklemek için: pip install uproot")
        return False
    except Exception as e:
        print(f"❌ ROOT dosyası analiz hatası: {e}")
        return False

#==============================================================================
# 2. HDF5 DOSYASI ANALİZİ (LIGO Gravitasyonel Dalga)
#==============================================================================
def analyze_hdf5_file(filepath):
    """HDF5 dosyasını analiz et - LIGO gravitasyonel dalga verisi"""
    print("\n" + "=" * 70)
    print("📊 2. HDF5 DOSYASI ANALİZİ (LIGO/Gravitasyonel Dalga)")
    print("=" * 70)
    
    try:
        import h5py
        import numpy as np
        
        print(f"📂 Dosya: {os.path.basename(filepath)}")
        
        # HDF5 dosyasını aç
        with h5py.File(filepath, 'r') as f:
            
            def print_hdf5_structure(name, obj, indent=0):
                """HDF5 yapısını recursive olarak yazdır"""
                prefix = "  " * indent
                if isinstance(obj, h5py.Group):
                    print(f"{prefix}📁 {name}/ (Grup)")
                    return None  # Alt elemanları da tara
                elif isinstance(obj, h5py.Dataset):
                    shape = obj.shape
                    dtype = obj.dtype
                    print(f"{prefix}📊 {name} [shape={shape}, dtype={dtype}]")
                    return None
            
            print(f"\n📁 HDF5 İçerik Yapısı:")
            print("-" * 50)
            
            # Kök seviye elemanları
            print(f"Kök Elemanları: {list(f.keys())}")
            
            # Tüm yapıyı recursive listele
            all_items = []
            def collect_items(name, obj):
                all_items.append((name, obj))
            f.visititems(collect_items)
            
            print(f"\nToplam Eleman Sayısı: {len(all_items)}")
            
            # Grupları ve veri setlerini ayır
            groups = [(n, o) for n, o in all_items if isinstance(o, h5py.Group)]
            datasets = [(n, o) for n, o in all_items if isinstance(o, h5py.Dataset)]
            
            print(f"  - Grup Sayısı: {len(groups)}")
            print(f"  - Dataset Sayısı: {len(datasets)}")
            
            # Grupları listele
            print(f"\n📁 Gruplar:")
            for name, obj in groups[:20]:
                print(f"  📁 /{name}")
            if len(groups) > 20:
                print(f"  ... ve {len(groups) - 20} grup daha")
            
            # Veri setlerini listele (kolonlar)
            print(f"\n📊 Veri Setleri (Kolonlar):")
            print("-" * 50)
            for name, obj in datasets[:30]:
                shape = obj.shape
                dtype = obj.dtype
                size_mb = np.prod(shape) * obj.dtype.itemsize / 1e6
                print(f"  📊 /{name}")
                print(f"     Shape: {shape}, Dtype: {dtype}, Size: {size_mb:.2f} MB")
                
                # Örnek veri
                if len(shape) > 0 and shape[0] > 0:
                    try:
                        if len(shape) == 1:
                            sample = obj[:min(5, shape[0])]
                        else:
                            sample = obj[:min(3, shape[0])]
                        print(f"     Örnek: {sample}")
                    except:
                        pass
            
            if len(datasets) > 30:
                print(f"  ... ve {len(datasets) - 30} dataset daha")
            
            # Önemli LIGO meta verileri
            print(f"\n🔬 LIGO Meta Verileri:")
            print("-" * 50)
            
            # Strain verisini bul
            strain_paths = [n for n, _ in datasets if 'strain' in n.lower()]
            if strain_paths:
                print(f"  Strain veri yolları: {strain_paths}")
                for sp in strain_paths[:3]:
                    ds = f[sp]
                    print(f"    {sp}: shape={ds.shape}, dtype={ds.dtype}")
            
            # GPS zamanı bul
            gps_paths = [n for n, _ in datasets if 'gps' in n.lower() or 'time' in n.lower()]
            if gps_paths:
                print(f"  GPS/Zaman yolları: {gps_paths[:5]}")
            
        return True
        
    except ImportError:
        print("❌ 'h5py' kütüphanesi yüklü değil. Yüklemek için: pip install h5py")
        return False
    except Exception as e:
        print(f"❌ HDF5 dosyası analiz hatası: {e}")
        return False

#==============================================================================
# 3. FITS DOSYASI ANALİZİ (JWST Spektroskopi)
#==============================================================================
def analyze_fits_file(filepath):
    """FITS dosyasını analiz et - JWST uzay teleskopu verisi"""
    print("\n" + "=" * 70)
    print("📊 3. FITS DOSYASI ANALİZİ (JWST Spektroskopi)")
    print("=" * 70)
    
    try:
        from astropy.io import fits
        import numpy as np
        
        print(f"📂 Dosya: {os.path.basename(filepath)}")
        
        # FITS dosyasını aç
        with fits.open(filepath) as hdul:
            
            print(f"\n📁 FITS HDU (Header Data Unit) Listesi:")
            print("-" * 50)
            hdul.info()
            
            print(f"\nToplam HDU Sayısı: {len(hdul)}")
            
            # Her HDU'yu analiz et
            for i, hdu in enumerate(hdul):
                print(f"\n{'='*50}")
                print(f"📌 HDU {i}: {hdu.name}")
                print(f"   Tip: {type(hdu).__name__}")
                
                # Header bilgileri
                header = hdu.header
                print(f"   Header Anahtar Sayısı: {len(header)}")
                
                # Önemli header bilgileri
                important_keys = ['NAXIS', 'NAXIS1', 'NAXIS2', 'BITPIX', 'EXTNAME', 
                                  'TELESCOP', 'INSTRUME', 'FILTER', 'EXPTIME',
                                  'DATE-OBS', 'TARGNAME', 'RA_TARG', 'DEC_TARG']
                print(f"\n   📋 Önemli Header Bilgileri:")
                for key in important_keys:
                    if key in header:
                        print(f"      {key}: {header[key]}")
                
                # Veri boyutları
                if hdu.data is not None:
                    data = hdu.data
                    if hasattr(data, 'shape'):
                        print(f"\n   📊 Veri:")
                        print(f"      Shape: {data.shape}")
                        print(f"      Dtype: {data.dtype}")
                        
                        # Tablo mu?
                        if hasattr(data, 'columns'):
                            print(f"      Kolon Sayısı: {len(data.columns)}")
                            print(f"\n      📋 Kolonlar:")
                            for j, col in enumerate(data.columns[:20]):
                                print(f"         {j+1}. {col.name} [{col.format}]")
                            if len(data.columns) > 20:
                                print(f"         ... ve {len(data.columns) - 20} kolon daha")
                            
                            # Satır sayısı
                            print(f"\n      Satır Sayısı: {len(data)}")
                            
                            # Örnek veri
                            print(f"\n      📊 Örnek Veri (İlk 3 Satır):")
                            for row in data[:3]:
                                print(f"         {row}")
                        else:
                            # Görüntü verisi
                            print(f"      Min: {np.nanmin(data):.6e}")
                            print(f"      Max: {np.nanmax(data):.6e}")
                            print(f"      Mean: {np.nanmean(data):.6e}")
                else:
                    print(f"   📊 Veri: Yok (Header Only)")
        
        return True
        
    except ImportError:
        print("❌ 'astropy' kütüphanesi yüklü değil. Yüklemek için: pip install astropy")
        return False
    except Exception as e:
        print(f"❌ FITS dosyası analiz hatası: {e}")
        return False

#==============================================================================
# 4. VOTable DOSYASI ANALİZİ (Sanal Gözlemevi)
#==============================================================================
def analyze_votable_file(filepath):
    """VOTable dosyasını analiz et - Sanal gözlemevi verisi"""
    print("\n" + "=" * 70)
    print("📊 4. VOTable DOSYASI ANALİZİ (Sanal Gözlemevi)")
    print("=" * 70)
    
    try:
        from astropy.io.votable import parse
        import numpy as np
        
        print(f"📂 Dosya: {os.path.basename(filepath)}")
        
        # VOTable dosyasını aç
        votable = parse(filepath)
        
        print(f"\n📁 VOTable İçerik Yapısı:")
        print("-" * 50)
        
        # Kaynakları listele
        print(f"Kaynak (Resource) Sayısı: {len(votable.resources)}")
        
        for r_idx, resource in enumerate(votable.resources):
            print(f"\n📌 Resource {r_idx}:")
            print(f"   Tablo Sayısı: {len(resource.tables)}")
            
            for t_idx, table in enumerate(resource.tables):
                print(f"\n   📊 Tablo {t_idx}:")
                print(f"      ID: {table.ID}")
                print(f"      Name: {table.name}")
                
                # Kolonları listele
                fields = table.fields
                print(f"      Kolon Sayısı: {len(fields)}")
                
                print(f"\n      📋 Kolonlar:")
                for f_idx, field in enumerate(fields[:30]):
                    name = field.name
                    dtype = field.datatype
                    unit = field.unit if field.unit else "-"
                    desc = field.description[:50] if field.description else "-"
                    print(f"         {f_idx+1}. {name}")
                    print(f"            Dtype: {dtype}, Unit: {unit}")
                    if desc != "-":
                        print(f"            Desc: {desc}...")
                
                if len(fields) > 30:
                    print(f"         ... ve {len(fields) - 30} kolon daha")
                
                # Veri
                data = table.array
                if data is not None:
                    print(f"\n      📊 Veri:")
                    print(f"         Satır Sayısı: {len(data)}")
                    
                    # Örnek veri
                    print(f"\n      📊 Örnek Veri (İlk 5 Satır):")
                    col_names = [f.name for f in fields[:5]]
                    for row in data[:5]:
                        row_data = {col: row[col] for col in col_names if col in data.dtype.names}
                        print(f"         {row_data}")
        
        return True
        
    except ImportError:
        print("❌ 'astropy' kütüphanesi yüklü değil. Yüklemek için: pip install astropy")
        return False
    except Exception as e:
        print(f"❌ VOTable dosyası analiz hatası: {e}")
        return False

#==============================================================================
# ANA PROGRAM
#==============================================================================
if __name__ == "__main__":
    
    print("\n" + "=" * 70)
    print("KÜTÜPHANE KONTROLÜ")
    print("=" * 70)
    
    if not check_and_import():
        print("\n⚠️ Eksik kütüphaneler var. Önce bunları yükleyin.")
        print("pip install uproot h5py astropy numpy pandas awkward")
        sys.exit(1)
    
    print("\n✅ Tüm kütüphaneler hazır!")
    
    # Dosyaları analiz et
    results = {}
    
    # 1. ROOT
    root_path = os.path.join(BASE_PATH, FILES["ROOT"])
    if os.path.exists(root_path):
        results["ROOT"] = analyze_root_file(root_path)
    else:
        print(f"\n❌ ROOT dosyası bulunamadı: {root_path}")
        results["ROOT"] = False
    
    # 2. HDF5
    hdf5_path = os.path.join(BASE_PATH, FILES["HDF5"])
    if os.path.exists(hdf5_path):
        results["HDF5"] = analyze_hdf5_file(hdf5_path)
    else:
        print(f"\n❌ HDF5 dosyası bulunamadı: {hdf5_path}")
        results["HDF5"] = False
    
    # 3. FITS
    fits_path = os.path.join(BASE_PATH, FILES["FITS"])
    if os.path.exists(fits_path):
        results["FITS"] = analyze_fits_file(fits_path)
    else:
        print(f"\n❌ FITS dosyası bulunamadı: {fits_path}")
        results["FITS"] = False
    
    # 4. VOTable
    vot_path = os.path.join(BASE_PATH, FILES["VOT"])
    if os.path.exists(vot_path):
        results["VOT"] = analyze_votable_file(vot_path)
    else:
        print(f"\n❌ VOTable dosyası bulunamadı: {vot_path}")
        results["VOT"] = False
    
    # Özet
    print("\n" + "=" * 70)
    print("📊 ANALİZ ÖZETİ")
    print("=" * 70)
    
    for ftype, success in results.items():
        status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
        print(f"  {ftype}: {status}")
    
    print("\n" + "=" * 70)
    print("UST v5 - ANALİZ TAMAMLANDI")
    print("=" * 70)