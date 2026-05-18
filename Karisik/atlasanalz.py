"""
UST v5 - LHC Missing ET Analysis
Tests C_cb ratio in proton-proton collisions
"""

import uproot  # LHC ROOT file reader
import numpy as np
import matplotlib.pyplot as plt

class USTLHCAnalyzer:
    def __init__(self):
        self.c_cb = 0.366455
        
    def analyze_root_file(self, filename):
        """Analyze LHC ATLAS ROOT file"""
        
        # Open ROOT file
        file = uproot.open(filename)
        tree = file["CollectionTree"]
        
        # Get Missing ET
        met = tree["MET_RefFinal_et"].array()
        total_et = tree["CaloCellContainer"].array()
        
        # Calculate ratio
        ratio = met / total_et
        
        # Test UST prediction
        mean_ratio = np.mean(ratio)
        
        print(f"Missing ET / Total ET: {mean_ratio:.4f}")
        print(f"UST Prediction (C_cb): {self.c_cb:.4f}")
        print(f"Difference: {abs(mean_ratio - self.c_cb):.4f}")
        
        # Plot histogram
        plt.hist(ratio, bins=50, alpha=0.7)
        plt.axvline(self.c_cb, color='r', linestyle='--', 
                   label=f'UST C_cb = {self.c_cb:.3f}')
        plt.xlabel('Missing ET Fraction')
        plt.ylabel('Events')
        plt.title('LHC ATLAS - UST Omnium Sızıntısı Testi')
        plt.legend()
        plt.savefig('ust_lhc_analysis.png', dpi=300)
        plt.show()

# Kullanım:
# analyzer = USTLHCAnalyzer()
# analyzer.analyze_root_file("ATLAS_data.root")