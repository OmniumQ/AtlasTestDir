from astropy.io import fits

file_path = r"C:\AtlasTest\randoms-1-hp-99.fits"

try:
    with fits.open(file_path) as hdul:
        print("=== FITS Dosyası Yapısı (HDU Info) ===")
        hdul.info()  # Dosyanın genel topolojisini yazdırır
        
        print("\n=== Veri Sütunları (Columns) ===")
        # Veri içeren tüm uzantıları (extensions) güvenli bir şekilde tarar
        table_found = False
        for i, hdu in enumerate(hdul):
            if hasattr(hdu, 'columns'):
                print(f"Uzantı (Extension) {i} Sütun Adları:")
                print(hdu.columns.names)
                table_found = True
                
        if not table_found:
            print("Uyarı: Dosya içinde okunabilir bir tablo (BinTableHDU/TableHDU) bulunamadı.")
            
except Exception as e:
    print(f"Sistem Hatası: {e}")