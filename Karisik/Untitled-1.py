#!/usr/bin/env python3
"""
UST v5 - ATLAS Analysis (FIXED)
Handles already-flat arrays
"""

import numpy as np
import matplotlib.pyplot as plt
import uproot
import awkward as ak
import os

C_CB = 0.366455

class USTATLASAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.c_cb = C_CB
        
    def analyze(self):
        """Load and analyze ROOT file"""
        print("="*70)
        print("UST v5 - LHC ATLAS Missing ET Analysis")
        print("="*70)
        print(f"Loading: {self.filepath}\n")
        
        try:
            # Open file
            file = uproot.open(self.filepath)
            tree = file["analysis"]
            print("✓ Tree loaded")
            
            # Get arrays (already flat - no need for ak.flatten!)
            met_array = tree["met"].array()
            truth_met_array = tree["truth_met"].array()
            
            # Convert to numpy
            met = ak.to_numpy(met_array)
            truth_met = ak.to_numpy(truth_met_array)
            
            print(f"\n✓ Data loaded:")
            print(f"  Events: {len(met)}")
            print(f"  MET range: {np.min(met):.1f} - {np.max(met):.1f} GeV")
            print(f"  Truth MET range: {np.min(truth_met):.1f} - {np.max(truth_met):.1f} GeV")
            
            # Calculate statistics
            met_mean = np.mean(met)
            truth_met_mean = np.mean(truth_met)
            
            print(f"\nMET Statistics:")
            print(f"  MET mean: {met_mean:.2f} GeV")
            print(f"  Truth MET mean: {truth_met_mean:.2f} GeV")
            print(f"  MET median: {np.median(met):.2f} GeV")
            print(f"  MET std: {np.std(met):.2f} GeV")
            
            # Calculate MET / Truth_MET ratio
            # Only use events where truth_met > 0
            valid = truth_met > 1.0  # Avoid division by very small numbers
            
            if np.sum(valid) > 0:
                ratio = met[valid] / truth_met[valid]
                
                ratio_mean = np.mean(ratio)
                ratio_median = np.median(ratio)
                ratio_std = np.std(ratio)
                
                print(f"\nMET / Truth_MET Ratio:")
                print(f"  Valid events: {np.sum(valid)}/{len(met)}")
                print(f"  Mean: {ratio_mean:.4f}")
                print(f"  Median: {ratio_median:.4f}")
                print(f"  Std: {ratio_std:.4f}")
                print(f"  UST C_cb prediction: {self.c_cb:.4f}")
                print(f"  Difference: {abs(ratio_mean - self.c_cb):.4f}")
                
                # UST Test
                print("\n" + "="*70)
                if abs(ratio_mean - self.c_cb) < 0.15:
                    print("✅ RATIO CLOSE TO UST PREDICTION!")
                    print(f"Agreement: {(1 - abs(ratio_mean - self.c_cb)/self.c_cb)*100:.1f}%")
                else:
                    print(f"⚠ Ratio differs from UST C_cb")
                    print(f"  Expected: {self.c_cb:.4f}")
                    print(f"  Measured: {ratio_mean:.4f}")
                print("="*70)
            else:
                ratio = None
                ratio_mean = None
                print("\n⚠ Not enough valid events for ratio calculation")
            
            # Alternative UST test: High MET fraction
            # UST predicts ~36% of energy goes to Omnium
            # Look at missing energy in high-pT events
            
            high_met_threshold = 50  # GeV
            high_met_events = met > high_met_threshold
            high_met_fraction = np.sum(high_met_events) / len(met)
            
            print(f"\nHigh MET Events (>{high_met_threshold} GeV):")
            print(f"  Fraction: {high_met_fraction:.4f}")
            print(f"  Count: {np.sum(high_met_events)}/{len(met)}")
            
            # Plot results
            self.plot_results(met, truth_met, ratio, valid)
            
            return {
                'met_mean': met_mean,
                'truth_met_mean': truth_met_mean,
                'ratio_mean': ratio_mean if ratio is not None else None,
                'high_met_fraction': high_met_fraction,
                'c_cb': self.c_cb,
                'n_events': len(met)
            }
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def plot_results(self, met, truth_met, ratio, valid_mask):
        """Plot comprehensive analysis"""
        
        fig = plt.figure(figsize=(16, 10))
        
        # Create grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. MET distribution
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(met, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax1.set_xlabel('Missing ET (GeV)', fontsize=11)
        ax1.set_ylabel('Events', fontsize=11)
        ax1.set_title('Reconstructed MET Distribution', fontsize=12, fontweight='bold')
        ax1.set_yscale('log')
        ax1.grid(True, alpha=0.3)
        ax1.axvline(np.mean(met), color='red', linestyle='--', 
                   label=f'Mean = {np.mean(met):.1f} GeV')
        ax1.legend(fontsize=9)
        
        # 2. Truth MET distribution
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.hist(truth_met, bins=50, alpha=0.7, color='green', edgecolor='black')
        ax2.set_xlabel('Truth Missing ET (GeV)', fontsize=11)
        ax2.set_ylabel('Events', fontsize=11)
        ax2.set_title('Truth MET Distribution', fontsize=12, fontweight='bold')
        ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3)
        ax2.axvline(np.mean(truth_met), color='red', linestyle='--',
                   label=f'Mean = {np.mean(truth_met):.1f} GeV')
        ax2.legend(fontsize=9)
        
        # 3. MET vs Truth MET scatter
        ax3 = fig.add_subplot(gs[0, 2])
        # Downsample for speed if too many points
        n_plot = min(5000, len(met))
        indices = np.random.choice(len(met), n_plot, replace=False)
        ax3.scatter(truth_met[indices], met[indices], alpha=0.3, s=2, color='purple')
        max_val = max(np.max(met), np.max(truth_met))
        ax3.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Perfect agreement')
        ax3.set_xlabel('Truth MET (GeV)', fontsize=11)
        ax3.set_ylabel('Reconstructed MET (GeV)', fontsize=11)
        ax3.set_title('MET Correlation', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)
        
        # 4. Ratio distribution (UST TEST!)
        ax4 = fig.add_subplot(gs[1, :])
        if ratio is not None and len(ratio) > 0:
            # Remove outliers for better visualization
            ratio_clean = ratio[(ratio > 0.1) & (ratio < 3.0)]
            
            ax4.hist(ratio_clean, bins=60, alpha=0.7, color='orange', 
                    edgecolor='black', label='Data')
            ax4.axvline(self.c_cb, color='red', linestyle='--', linewidth=3,
                       label=f'UST C_cb = {self.c_cb:.4f}')
            ax4.axvline(np.mean(ratio), color='blue', linestyle=':', linewidth=3,
                       label=f'Data Mean = {np.mean(ratio):.4f}')
            ax4.set_xlabel('MET / Truth_MET Ratio', fontsize=12)
            ax4.set_ylabel('Events', fontsize=12)
            ax4.set_title('🎯 UST OMNIUM TEST: MET/Truth_MET Ratio vs C_cb Prediction', 
                         fontsize=13, fontweight='bold')
            ax4.legend(fontsize=11, loc='upper right')
            ax4.grid(True, alpha=0.3)
            ax4.set_xlim([0, 2.5])
        else:
            ax4.text(0.5, 0.5, 'Insufficient data for ratio', 
                    ha='center', va='center', fontsize=14)
        
        # 5. MET difference distribution
        ax5 = fig.add_subplot(gs[2, 0])
        met_diff = met - truth_met
        ax5.hist(met_diff, bins=50, alpha=0.7, color='cyan', edgecolor='black')
        ax5.axvline(0, color='red', linestyle='--', linewidth=2)
        ax5.set_xlabel('MET - Truth_MET (GeV)', fontsize=11)
        ax5.set_ylabel('Events', fontsize=11)
        ax5.set_title('MET Residuals', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # 6. High MET tail
        ax6 = fig.add_subplot(gs[2, 1])
        bins = np.logspace(np.log10(1), np.log10(max(met)), 40)
        ax6.hist(met, bins=bins, alpha=0.7, color='magenta', edgecolor='black')
        ax6.axvline(50, color='green', linestyle='--', linewidth=2, 
                   label='High MET threshold')
        ax6.set_xlabel('Missing ET (GeV)', fontsize=11)
        ax6.set_ylabel('Events', fontsize=11)
        ax6.set_title('MET Distribution (Log Scale)', fontsize=12, fontweight='bold')
        ax6.set_xscale('log')
        ax6.set_yscale('log')
        ax6.legend(fontsize=9)
        ax6.grid(True, alpha=0.3)
        
        # 7. Summary text
        ax7 = fig.add_subplot(gs[2, 2])
        ax7.axis('off')
        
        summary_text = f"""
        UST v5 ATLAS Analysis
        ══════════════════════
        
        Events: {len(met):,}
        
        MET Mean: {np.mean(met):.2f} GeV
        Truth MET Mean: {np.mean(truth_met):.2f} GeV
        
        """
        
        if ratio is not None:
            summary_text += f"""Ratio Mean: {np.mean(ratio):.4f}
        UST C_cb: {self.c_cb:.4f}
        
        Difference: {abs(np.mean(ratio) - self.c_cb):.4f}
        
        """
            if abs(np.mean(ratio) - self.c_cb) < 0.15:
                summary_text += "✅ MATCHES UST!"
            else:
                summary_text += "⚠ Differs from UST"
        
        ax7.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
                verticalalignment='center')
        
        plt.suptitle('ATLAS Missing ET Analysis - UST Omnium Leakage Test', 
                    fontsize=15, fontweight='bold', y=0.995)
        
        output_file = 'ust_atlas_complete_analysis.png'
        plt.savefig(output_file, dpi=250, bbox_inches='tight')
        print(f"\n✓ Plot saved: {output_file}")
        
        plt.show()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    data_path = r"C:\AtlasTest\ODEO_FEB2025_v0_2J2LMET30_data15_periodD.2J2LMET30.root"
    
    analyzer = USTATLASAnalyzer(data_path)
    results = analyzer.analyze()
    
    if results:
        print("\n" + "="*70)
        print("📊 FINAL SUMMARY")
        print("="*70)
        print(f"Total Events: {results['n_events']:,}")
        print(f"MET Mean: {results['met_mean']:.2f} GeV")
        print(f"Truth MET Mean: {results['truth_met_mean']:.2f} GeV")
        
        if results['ratio_mean']:
            print(f"\nMET/Truth_MET Ratio: {results['ratio_mean']:.4f}")
            print(f"UST C_cb Prediction: {results['c_cb']:.4f}")
            diff_pct = abs(results['ratio_mean'] - results['c_cb']) / results['c_cb'] * 100
            print(f"Difference: {diff_pct:.1f}%")
            
            if diff_pct < 15:
                print("\n✅✅✅ UST PREDICTION CONFIRMED!")
            else:
                print(f"\n⚠ Ratio differs by {diff_pct:.1f}%")
        
        print(f"\nHigh MET Fraction: {results['high_met_fraction']:.4f}")
        print("="*70)