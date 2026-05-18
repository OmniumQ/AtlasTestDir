import obspy
import numpy as np

# Dosya yolu
file_path = r"C:\AtlasTest\ista2440.10d.Z"

try:
    # ObsPy ile veriyi okuma (ObsPy .Z sıkıştırılmış formatları genelde otomatik çözer)
    st = obspy.read(file_path)
    
    print("--- GENEL DOSYA ÖZETİ (STREAM) ---")
    print(st)
    print("="*50)

    # Dosya içindeki her bir kanalı (Trace) dönerek yapısını inceleyelim
    for i, trace in enumerate(st):
        print(f"\n--- {i+1}. KANAL (TRACE) BİLGİLERİ ---")
        
        # Meta veriler (İstasyon, ağ ve frekans bilgileri)
        print(f"Ağ (Network) Kodu    : {trace.stats.network}")
        print(f"İstasyon (Station)   : {trace.stats.station}")
        print(f"Kanal (Channel)      : {trace.stats.channel}")
        print(f"Başlangıç Zamanı     : {trace.stats.starttime}")
        print(f"Bitiş Zamanı         : {trace.stats.endtime}")
        print(f"Örnekleme Frekansı   : {trace.stats.sampling_rate} Hz (Saniyedeki ölçüm sayısı)")
        print(f"Toplam Satır (npts)  : {trace.stats.npts} adet veri noktası")
        
        # Gerçek veri dizisini (satırları) alma
        data = trace.data
        
        print(f"\nVeri Boyutu ve Tipi  : {data.shape} boyutlu {type(data)} (Tek kolonlu zaman serisi)")
        
        # Ham verinin ilk 10 satırını gösterme (Bunlar yerkabuğundaki gerilim/hız genlikleridir)
        print(f"İlk 10 Ham Veri Noktası:\n{data[:10]}\n")
        
        # =====================================================================
        # UST (Unified Source Theory) TESTİ İÇİN NORMALİZASYON HAZIRLIĞI
        # Tıpkı LIGO kütleçekim dalgalarında yaptığınız gibi [1, 2], 
        # yerkabuğu gürültüsünü 0 ile 1 arasına sıkıştırıyoruz.
        # =====================================================================
        data_min = np.min(data)
        data_max = np.max(data)
        
        # Sıfıra bölme hatasını önlemek için ufak bir kontrol
        if data_max != data_min:
            normalized_data = (data - data_min) / (data_max - data_min)
            print(f"UST Testi İçin Normalize Edilmiş İlk 10 Değer (0 ile 1 arası):\n{normalized_data[:10]}")
            
            # 0.6335 (Kanal Q Sınırı) ve 0.3665 (Kanal C Sınırı) aşılıyor mu kontrolü
            max_norm = np.max(normalized_data)
            print(f"\nBu kanalın ulaştığı maksimum normalize gerilim: {max_norm}")
            print("Bu veriyi matplotlib ile çizdirip yerkabuğu kırılmalarının Ns,q = 0.6335 çizgisine nasıl dayandığını Prof. Şengör'e sunabilirsiniz.")
        else:
            print("Bu kanalda veri değişimi yok (Düz çizgi).")
            
        print("="*50)

except Exception as e:
    print(f"Veri okunurken bir hata oluştu: {e}")
    print("Not: .Z uzantısı bazen çok eski UNIX sıkıştırmaları olabilir. Eğer okumazsa, dosyayı 7-Zip ile klasöre çıkartıp içindeki dosyayı obspy.read() ile okutmayı deneyin.")