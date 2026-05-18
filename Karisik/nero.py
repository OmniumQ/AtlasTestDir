import nibabel as nib
import numpy as np

# Dosya yolunu belirleme
file_path = r"C:\AtlasTest\S1200.All.MyelinMap_BC_MSMAll.32k_fs_LR.dscalar.nii"

# NIfTI/CIFTI dosyasını ve veri matrisini belleğe yükleme
try:
    img = nib.load(file_path)
    data = img.get_fdata()
    
    print("--- 1. BOYUT VE TOPOLOJİK AĞ BÜYÜKLÜĞÜ ---")
    print("Veri Matrisi Boyutu (Shape):", data.shape)
    print("Toplam Düğüm (Node) Sayısı:", data.size)
    print("\n")

    print("--- 2. VERİ DAĞILIMI (UST ADIM 1 İÇİN KRİTİK TEST) ---")
    unique_values = np.unique(data)
    print("Toplam Benzersiz Değer Sayısı:", len(unique_values))
    print("Benzersiz Veri Değerlerinden Örnekler (İlk 50):", unique_values[:50])
    print("Min Değer:", np.min(data), "| Max Değer:", np.max(data))
    print("\n")

    print("--- 3. METAVERİ VE KOLON/PARSELASYON İSİMLERİ ---")
    header = img.header
    # CIFTI formatında etiketleri (Label) çekme denemesi
    if isinstance(img, nib.cifti2.cifti2.Cifti2Image):
        axis = header.get_axis(0)
        try:
            # Sadece ilk haritadaki etiketleri yazdırır
            for map_name, label_dict in axis.label.items():
                print(f"ID: {map_name} -> Bölge Adı/Değer: {label_dict}")
        except AttributeError:
             print("Dosyada isimlendirilmiş bir etiket ekseni bulunamadı.")
    else:
        print("Bu dosya CIFTI-2 formatında değil, standart NIfTI formatında.")

except Exception as e:
    print("Dosya okunurken bir hata oluştu:", str(e))