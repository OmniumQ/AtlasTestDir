import gzip

dosya = r"C:\AtlasTest\GnomPrg\gb270.gene_list.gss.txt.gz"

with gzip.open(dosya, 'rt', encoding='utf-8', errors='ignore') as f:
    satirlar = []
    for i, satir in enumerate(f):
        satirlar.append(satir.strip())
        if i >= 20:
            break

print(f"İlk 20 satır:")
for s in satirlar:
    print(s)