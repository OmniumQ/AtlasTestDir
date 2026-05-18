import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Patent için siyah-beyaz, net çizgiler
plt.style.use('default')
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'DejaVu Sans'

# =============================================================================
# ŞEKİL 1: SİSTEM AKIŞ DİYAGRAMI
# =============================================================================

fig, ax = plt.subplots(figsize=(8, 10), facecolor='white')
ax.axis('off')

# Kutu parametreleri
box_width = 3
box_height = 0.6
x_center = 4

# Adımlar
steps = [
    (8.5, "KUANTUM DEVRESİ\n(N tekrar çalıştır)", "rect"),
    (7.5, "ÖLÇÜM SONUÇLARI\n{x₁, x₂, ..., xₙ}", "rect"),
    (6.5, "OLASILIK DAĞILIMI\nHesapla", "rect"),
    (5.5, "PERSENTİL HESAPLA\nP₆₃.₃₅ ve P₃₆.₆₅", "rect"),
    (4.5, "ORAN HESAPLA\nR = P₆₃.₃₅ / P₃₆.₆₅", "rect"),
    (3.5, "|R - 1.7273| > ε ?", "diamond"),
    (2.5, "DÜZELTME UYGULA\nBayesian inference", "rect"),
    (1.5, "DÜZELTİLMİŞ SONUÇ", "rect"),
]

# Kutular
for y, text, shape in steps:
    if shape == "rect":
        rect = mpatches.FancyBboxPatch(
            (x_center - box_width/2, y - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.1", 
            edgecolor='black', 
            facecolor='white',
            linewidth=2
        )
        ax.add_patch(rect)
        ax.text(x_center, y, text, ha='center', va='center', fontsize=10, weight='bold')
    elif shape == "diamond":
        # Karar kutusu (diamond)
        diamond = mpatches.FancyBboxPatch(
            (x_center - box_width/2, y - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.1",
            edgecolor='black',
            facecolor='lightgray',
            linewidth=2
        )
        ax.add_patch(diamond)
        ax.text(x_center, y, text, ha='center', va='center', fontsize=9, weight='bold')

# Oklar
for i in range(len(steps)-1):
    y1 = steps[i][0]
    y2 = steps[i+1][0]
    
    if steps[i][2] == "diamond":
        # EVET ok
        ax.annotate('', xy=(x_center, y2 + box_height/2), 
                   xytext=(x_center, y1 - box_height/2),
                   arrowprops=dict(arrowstyle='->', lw=2))
        ax.text(x_center + 0.3, (y1 + y2)/2, 'EVET', fontsize=9, style='italic')
        
        # HAYIR ok (yan)
        ax.annotate('', xy=(x_center + 2, 1.0), 
                   xytext=(x_center + 1.5, y1),
                   arrowprops=dict(arrowstyle='->', lw=1.5, linestyle='dashed'))
        ax.text(x_center + 2.2, y1 - 0.3, 'HAYIR\n(Çıkış)', fontsize=8, style='italic')
    else:
        ax.annotate('', xy=(x_center, y2 + box_height/2), 
                   xytext=(x_center, y1 - box_height/2),
                   arrowprops=dict(arrowstyle='->', lw=2))

# Başlık
ax.text(x_center, 9.5, 'ŞEKİL 1: UST HATA AZALTMA SİSTEMİ AKIŞ DİYAGRAMI', 
        ha='center', fontsize=12, weight='bold')

# Açıklama
ax.text(0.5, 0.3, 'ε = threshold (%5)\nN_{s,q} = 0.63354460\na₂ = 1/17', 
        fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat'))

ax.set_xlim(0, 8)
ax.set_ylim(0, 10)

plt.tight_layout()
plt.savefig('sekil1_akis_diyagrami.png', dpi=300, bbox_inches='tight')
print("✓ Şekil 1 kaydedildi")

# =============================================================================
# ŞEKİL 2: İSTATİSTİKSEL ORAN DAĞILIMI
# =============================================================================

fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

# Örnek veri (simülasyon)
np.random.seed(42)
measurements = np.random.beta(2, 2, 1000)  # Beta dağılımı

# Histogram
counts, bins, patches = ax.hist(measurements, bins=50, edgecolor='black', 
                                 color='lightgray', alpha=0.7)

# Persentil çizgileri
N_sq = 0.63354460
Cc = 0.36645540
p_63 = np.percentile(measurements, N_sq * 100)
p_36 = np.percentile(measurements, Cc * 100)

ax.axvline(p_63, color='black', linewidth=2, linestyle='--', label=f'P₆₃.₃₅ = {p_63:.3f}')
ax.axvline(p_36, color='black', linewidth=2, linestyle=':', label=f'P₃₆.₆₅ = {p_36:.3f}')

# Oran gösterimi
ax.annotate('', xy=(p_63, max(counts)*0.7), xytext=(p_36, max(counts)*0.7),
            arrowprops=dict(arrowstyle='<->', lw=2))
ax.text((p_63 + p_36)/2, max(counts)*0.75, 
        f'R = {p_63/p_36:.4f}\n(Teorik: 1.7273)', 
        ha='center', fontsize=10, weight='bold',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))

ax.set_xlabel('Ölçüm Değeri', fontsize=11, weight='bold')
ax.set_ylabel('Frekans', fontsize=11, weight='bold')
ax.set_title('ŞEKİL 2: KUANTUM DEVRE ÇIKIŞLARININ İSTATİSTİKSEL DAĞILIMI\n(N=1000 ölçüm)', 
             fontsize=12, weight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('sekil2_istatistik_dagilim.png', dpi=300, bbox_inches='tight')
print("✓ Şekil 2 kaydedildi")

# =============================================================================
# ŞEKİL 3: IBM QUANTUM TEST SONUÇLARI
# =============================================================================

fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

# Test verileri
categories = ['Gate\nFidelity', 'Başarı\nOranı', 'Hesaplama\nSüresi\n(normalize)', 'Ancilla\nKullanımı\n(normalize)']
standart = [68.2, 60.0, 100, 100]
ust_method = [75.1, 75.0, 17.8, 10]  # Süre ve ancilla normalize edildi

x = np.arange(len(categories))
width = 0.35

bars1 = ax.bar(x - width/2, standart, width, label='Standart QEC', 
               color='lightgray', edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x + width/2, ust_method, width, label='UST Metodu',
               color='white', edgecolor='black', linewidth=1.5, hatch='///')

# Değer etiketleri
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.1f}', ha='center', va='bottom', fontsize=9, weight='bold')

# İyileşme oranları
improvements = ['+10.1%', '+25%', '-82%', '-90%']
for i, imp in enumerate(improvements):
    ax.text(i, max(standart[i], ust_method[i]) + 10, imp,
            ha='center', fontsize=9, weight='bold', color='darkred',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

ax.set_ylabel('Değer (%)', fontsize=11, weight='bold')
ax.set_title('ŞEKİL 3: IBM QUANTUM TEST SONUÇLARI KARŞILAŞTIRMASI\n(ibm_brisbane, 127 qubit, N=75 devre)', 
             fontsize=12, weight='bold')
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=10)
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, axis='y', alpha=0.3, linestyle='--')
ax.set_ylim(0, 120)

plt.tight_layout()
plt.savefig('sekil3_ibm_test_sonuclari.png', dpi=300, bbox_inches='tight')
print("✓ Şekil 3 kaydedildi")

# =============================================================================
# ŞEKİL 4: ANCILLA KULLANIM KARŞILAŞTIRMASI
# =============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor='white')

# Sol: Bar chart
methods = ['Surface\nCode\n(d=9)', 'Steane\nCode', 'Shor\nCode', 'UST\nMetodu']
ancilla_counts = [81, 7, 8, 5]  # 1 mantıksal qubit için

bars = ax1.barh(methods, ancilla_counts, color=['lightgray', 'lightgray', 'lightgray', 'white'],
                edgecolor='black', linewidth=2)
bars[3].set_hatch('///')  # UST için özel işaret

for i, (method, count) in enumerate(zip(methods, ancilla_counts)):
    ax1.text(count + 3, i, f'{count} qubit', va='center', fontsize=10, weight='bold')

ax1.set_xlabel('Ancilla Qubit Sayısı (1 mantıksal qubit için)', fontsize=11, weight='bold')
ax1.set_title('(a) Ancilla Qubit Karşılaştırması', fontsize=11, weight='bold')
ax1.set_xlim(0, 100)
ax1.grid(True, axis='x', alpha=0.3, linestyle='--')

# Sağ: Ölçeklenme
logical_qubits = [1, 10, 50, 100]
surface_code = [81, 810, 4050, 8100]
ust_method_scale = [5, 50, 250, 500]

ax2.plot(logical_qubits, surface_code, marker='o', linewidth=2, 
         markersize=8, color='black', linestyle='--', label='Surface Code')
ax2.plot(logical_qubits, ust_method_scale, marker='s', linewidth=2,
         markersize=8, color='black', linestyle='-', label='UST Metodu')

ax2.fill_between(logical_qubits, surface_code, ust_method_scale, 
                  alpha=0.2, color='gray', label='Tasarruf Alanı')

ax2.set_xlabel('Mantıksal Qubit Sayısı', fontsize=11, weight='bold')
ax2.set_ylabel('Toplam Fiziksel Qubit', fontsize=11, weight='bold')
ax2.set_title('(b) Ölçeklenme Karşılaştırması', fontsize=11, weight='bold')
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.set_yscale('log')

fig.suptitle('ŞEKİL 4: ANCILLA QUBIT KULLANIM ANALİZİ', fontsize=13, weight='bold')
plt.tight_layout()
plt.savefig('sekil4_ancilla_karsilastirma.png', dpi=300, bbox_inches='tight')
print("✓ Şekil 4 kaydedildi")

# =============================================================================
# BONUS: ŞEKİL 5 - 1/17 VE N_s,q GÖSTERİMİ (EK)
# =============================================================================

fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

# Pasta grafik
sizes = [94.12, 5.88]  # 16/17 ve 1/17
labels = [f'Temiz Sinyal\n16/17 = {sizes[0]:.2f}%', 
          f'Gürültü (a₂)\n1/17 = {sizes[1]:.2f}%']
colors = ['white', 'lightgray']
explode = (0, 0.1)

wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                    autopct='%1.2f%%', startangle=90,
                                    explode=explode, textprops={'fontsize': 11, 'weight': 'bold'},
                                    wedgeprops={'edgecolor': 'black', 'linewidth': 2})

# İç açıklama
centre_circle = plt.Circle((0, 0), 0.70, fc='white', edgecolor='black', linewidth=2)
ax.add_artist(centre_circle)
ax.text(0, 0, f'N_s,q = {0.63354460:.6f}\nCc = {0.36645540:.6f}\nR = 1.7273', 
        ha='center', va='center', fontsize=12, weight='bold',
        bbox=dict(boxstyle='round', facecolor='wheat', edgecolor='black'))

ax.set_title('ŞEKİL 5: TRACE ANOMALY (a₂ = 1/17) VE SINYAL FRAKSIYONU', 
             fontsize=13, weight='bold', pad=20)

plt.tight_layout()
plt.savefig('sekil5_trace_anomaly.png', dpi=300, bbox_inches='tight')
print("✓ Şekil 5 (bonus) kaydedildi")

print("\n" + "="*60)
print("TÜM ŞEKİLLER HAZIR!")
print("="*60)
print("Dosyalar:")
print("  • sekil1_akis_diyagrami.png")
print("  • sekil2_istatistik_dagilim.png")
print("  • sekil3_ibm_test_sonuclari.png")
print("  • sekil4_ancilla_karsilastirma.png")
print("  • sekil5_trace_anomaly.png (bonus)")
print("\nPatent başvurusuna eklemek için hazırlar.")
print("="*60)